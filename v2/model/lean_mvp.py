"""
Lean MVP Ucell Club: бюджет без внешней разработки (своя команда) и размер выборки,
при котором MVP однозначно подтверждает или опровергает гипотезы.

Запуск:  python v2/model/lean_mvp.py
Выход:   v2/model/output/lean_mvp.md, lean_mvp.json

Логика: механика и опыт участника как при масштабе (кэшбэк, сундук, те же шансы на одного человека),
меняется только размер тестовой группы. Контрольная группа (holdout) ничего не получает и ничего не стоит.
"""
from __future__ import annotations

import json
import math
import os
import sys
from statistics import NormalDist

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assumptions_v2 as A  # noqa: E402
import model_v2 as Mv  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
M = A.M
L = A.LOYALTY
md = Mv.mode

Z_A = NormalDist().inv_cdf(0.975)   # α = 5%, двусторонний
Z_B = NormalDist().inv_cdf(0.80)    # мощность 80%

# Допущения lean MVP (HYPOTHESIS — уточнить у закупок, логистики, юристов)
LEAN = {
    "months": 3,                                  # 12–13 недель, как в базовом MVP
    "arms": [10_000, 20_000, 30_000, 50_000],     # размер тестовой группы = размер контроля
    "monthly_prize": A.PRIZES["iphone17"]["price"] * (1 + A.GRAND_OVERHEAD),  # приз месяца в MVP — iPhone 17
    "ops_month": 15 * M,          # фулфилмент призов, упаковка, нотариус на розыгрыш, печать правил
    "launch_comms": 20 * M,       # креативы; push / SMS / баннер — собственные каналы
    "contingency": 0.10,
    "prize_mult": 1.0,            # призы на участника как при масштабе → те же шансы на человека
    "arpu_cv": 1.2,               # вариативность ARPU (как в основной модели)
    "cuped_rho": 0.8,             # корреляция ARPU до и во время теста (CUPED)
    "upgrade_p0": 0.003,          # переходы на ТП ≥ 60 тыс. за 3 мес. без программы
    "upgrade_p1": 0.006,          # цель
    "ontime_target_pp": 0.02,
    "arpu_target": 0.02,
    "join_rate_optin": 0.5,       # если вступление добровольное — эффект «размывается»
}


# --------------------------------------------------------------------------- статистика
def n_prop(p1: float, p2: float) -> float:
    pb = (p1 + p2) / 2
    return (Z_A * math.sqrt(2 * pb * (1 - pb)) + Z_B * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2


def mde_prop(p0: float, n: int, down: bool = False) -> float:
    """Минимальный обнаружимый сдвиг доли (абсолютный), N на группу."""
    lo, hi = 1e-7, (p0 if down else 1 - p0) - 1e-7
    for _ in range(80):
        mid = (lo + hi) / 2
        if n_prop(p0, p0 - mid if down else p0 + mid) > n:
            lo = mid
        else:
            hi = mid
    return hi


def n_mean(cv: float, mde: float, rho: float = 0.0) -> float:
    return 2 * (Z_A + Z_B) ** 2 * cv ** 2 * (1 - rho ** 2) / mde ** 2


def mde_mean(cv: float, n: int, rho: float = 0.0) -> float:
    return (Z_A + Z_B) * cv * math.sqrt(2 / n) * math.sqrt(1 - rho ** 2)


def cum_churn(c_month: float, months: int) -> float:
    return 1 - (1 - c_month) ** months


# --------------------------------------------------------------------------- расчёт
def unit_costs():
    st = Mv.loyalty_member_stats()
    pb = Mv.prize_budgets()
    full = A.BASE["total_subs"] * md(L["app_mau_share"]) * md(L["enroll_of_mau"])
    coin_cost = (1 - md(L["breakage"])) * md(L["redeem_cost_ratio"])
    cashback = md(L["ontime_share"]) * st["earn"] * coin_cost
    drops = md(L["drops_dau_share"]) * 30 * pb["drop_digital_cost"]
    prizes = (pb["drops_inventory_week"] + pb["weekly_wins_week"]) * Mv.WEEKS_PER_MONTH / full * LEAN["prize_mult"]
    # доля «живых денег»: в погашении монет наружу уходит только мерч / партнёры (20% × 0,7 из 0,515)
    cash_share_coins = 0.20 * 0.70 / md(L["redeem_cost_ratio"])
    coins_in_drop = A.DROP_TABLE[0][2]
    return {
        "members_full": full, "earn": st["earn"], "coin_cost": coin_cost,
        "cashback": cashback, "drops": drops, "prizes": prizes,
        "var_total": cashback + drops + prizes,
        "cash_share_coins": cash_share_coins,
        "cash_var": cashback * cash_share_coins + coins_in_drop * cash_share_coins * md(L["drops_dau_share"]) * 30 + prizes,
        "weekly_winners_per_10k": pb["weekly_items"] / full * 10_000,
    }


def arm_cost(n: int, u: dict) -> dict:
    mo = LEAN["months"]
    var = n * mo * u["var_total"]
    fixed = mo * (LEAN["monthly_prize"] + LEAN["ops_month"]) + LEAN["launch_comms"]
    total = (var + fixed) * (1 + LEAN["contingency"])
    cash = (n * mo * u["cash_var"] + fixed) * (1 + LEAN["contingency"])
    return {
        "n": n, "cashback": n * mo * u["cashback"], "drops": n * mo * u["drops"], "prizes": n * mo * u["prizes"],
        "monthly_prize": mo * LEAN["monthly_prize"], "ops": mo * LEAN["ops_month"], "comms": LEAN["launch_comms"],
        "contingency": (var + fixed) * LEAN["contingency"], "total": total, "cash": cash,
        "per_participant_month": total / n / mo,
    }


def base_mvp_without_dev():
    det = Mv.simulate_loyalty(det=True, scale=False)
    k_end = L["mvp_start"] + L["mvp_months"] - 1
    comp = {k: float(det[k][:k_end].sum()) for k in
            ["c_cashback", "c_drops_digital", "c_drops_inventory", "c_weekly", "c_grand", "c_build", "c_opex", "c_marketing"]}
    total = sum(comp.values())
    return {"components": comp, "total": total, "without_build": total - comp["c_build"]}


def power_tables():
    p_on = md(L["ontime_share"])
    c = L["member_churn_base"]
    red = md(L["churn_reduction"])
    churn = {t: (cum_churn(c, t), cum_churn(c * (1 - red), t)) for t in (3, 6)}
    req = {
        "ontime": n_prop(p_on, p_on + LEAN["ontime_target_pp"]),
        "upgrade": n_prop(LEAN["upgrade_p0"], LEAN["upgrade_p1"]),
        "churn3": n_prop(*churn[3]),
        "churn6": n_prop(*churn[6]),
        "churn_monthly": n_prop(c, c * (1 - red)),
        "arpu": n_mean(LEAN["arpu_cv"], LEAN["arpu_target"]),
        "arpu_cuped": n_mean(LEAN["arpu_cv"], LEAN["arpu_target"], LEAN["cuped_rho"]),
    }
    rows = []
    for n in LEAN["arms"]:
        rows.append({
            "n": n,
            "ontime_pp": mde_prop(p_on, n) * 100,
            "upgrade_to": (LEAN["upgrade_p0"] + mde_prop(LEAN["upgrade_p0"], n)) * 100,
            "churn3_rel": mde_prop(churn[3][0], n, down=True) / churn[3][0] * 100,
            "churn6_rel": mde_prop(churn[6][0], n, down=True) / churn[6][0] * 100,
            "arpu_cuped": mde_mean(LEAN["arpu_cv"], n, LEAN["cuped_rho"]) * 100,
            "arpu": mde_mean(LEAN["arpu_cv"], n) * 100,
            "dau_ci_pp": Z_A * math.sqrt(md(L["drops_dau_share"]) * (1 - md(L["drops_dau_share"])) / n) * 100,
        })
    return {"p_on": p_on, "churn": churn, "red": red, "required": req, "rows": rows}


# --------------------------------------------------------------------------- вывод
def sp(x, f="{:,.0f}"):
    return f.format(x).replace(",", " ").replace(".", ",")


def mln(x, f="{:,.0f}"):
    return sp(x / M, f)


def ok(mde: float, target: float) -> str:
    """✅ — цель видна надёжно; ≈ — на грани (мощность ~75–80%); ❌ — может утонуть в шуме."""
    if mde <= target:
        return "✅"
    return "≈" if mde <= target * 1.05 else "❌"


def main():
    u = unit_costs()
    arms = [arm_cost(n, u) for n in LEAN["arms"]]
    base = base_mvp_without_dev()
    base_lean = arm_cost(L["mvp_participants"], u)
    pw = power_tables()
    req = pw["required"]
    red = pw["red"] * 100
    fx = A.FX_UZS_PER_USD

    out = ["# Lean MVP Ucell Club — бюджет без внешней разработки и размер выборки\n",
           "> `python v2/model/lean_mvp.py`. Сумы, 3 месяца теста. Контрольная группа такого же размера "
           "ничего не получает и ничего не стоит. Все вводные — модальные значения основной модели.\n"]

    out.append("## 1. Базовый MVP (150 тыс.) — что остаётся без разработки\n")
    names = {"c_cashback": "Кэшбэк", "c_drops_digital": "Сундуки: цифровые призы", "c_drops_inventory": "Сундуки: инвентарь",
             "c_weekly": "Weekly Wins", "c_grand": "Приз месяца", "c_build": "Разработка (внешняя оценка)",
             "c_opex": "Команда, лицензии, фулфилмент, КЦ", "c_marketing": "Маркетинг"}
    out.append("| Статья | млн сум |\n|---|---|")
    for k, v in base["components"].items():
        out.append(f"| {names[k]} | {mln(v)} |")
    out.append(f"| **Итого** | **{mln(base['total'])}** |")
    out.append(f"| **Без разработки** | **{mln(base['without_build'])}** (≈ ${sp(base['without_build'] / fx / 1e3)} тыс.) |\n")

    out.append("## 2. Стоимость на одного участника в месяц (как при масштабе)\n")
    out.append("| Статья | сум | Как считается |\n|---|---|---|")
    out.append(f"| Кэшбэк | {sp(u['cashback'])} | 85% платят вовремя × {sp(u['earn'])} монет × {sp(u['coin_cost'], '{:.3f}')} сум за монету |")
    out.append(f"| Сундуки (цифровые) | {sp(u['drops'])} | 30% открывают каждый день × 30 дней × 52,5 сум |")
    out.append(f"| Призы недели и инвентарь | {sp(u['prizes'])} | фонды масштаба / {sp(u['members_full'])} участников → те же шансы на человека |")
    out.append(f"| **Итого** | **{sp(u['var_total'])}** | из них «живыми деньгами» ≈ {sp(u['cash_var'])} сум; остальное — наши ГБ, минуты и скидка на счёт |\n")
    out.append(f"Фиксированные: приз месяца (iPhone 17) {mln(LEAN['monthly_prize'], '{:,.2f}')} млн/мес.; "
               f"операционные {mln(LEAN['ops_month'])} млн/мес.; запуск (креативы) {mln(LEAN['launch_comms'])} млн; резерв {LEAN['contingency']*100:.0f}%.\n")

    out.append("## 3. Бюджет lean MVP по размеру тестовой группы (3 мес., без разработки)\n")
    out.append("| Тест + контроль | Кэшбэк | Сундуки | Призы | Приз месяца | Операц. | Запуск | Резерв | **Итого** | ≈ $ | Живыми деньгами | На участника в мес. |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for a in arms + [base_lean]:
        lab = f"{sp(a['n'])} + {sp(a['n'])}" if a["n"] != L["mvp_participants"] else f"{sp(a['n'])} (для сравнения)"
        out.append(f"| {lab} | {mln(a['cashback'])} | {mln(a['drops'])} | {mln(a['prizes'])} | {mln(a['monthly_prize'])} | "
                   f"{mln(a['ops'])} | {mln(a['comms'])} | {mln(a['contingency'])} | **{mln(a['total'])}** | "
                   f"{sp(a['total'] / fx / 1e3)} тыс. | {mln(a['cash'])} | {sp(a['per_participant_month'])} |")
    out.append("\nМлн сум. Призы недели на 10 000 участников: "
               f"≈ {sp(u['weekly_winners_per_10k'])} победителей в неделю (шанс тот же, что при масштабе).\n")

    out.append("## 4. Какой размер нужен, чтобы гипотеза подтвердилась статистически\n")
    out.append(f"α = 5%, мощность 80%, тест против контроля того же размера. Отток: база {sp(L['member_churn_base']*100, '{:.1f}')}%/мес., "
               f"цель −{red:.0f}%.\n")
    out.append("| Гипотеза | Цель | Нужно на группу |\n|---|---|---|")
    out.append(f"| H1 Оплата вовремя | {pw['p_on']*100:.0f}% → {(pw['p_on']+LEAN['ontime_target_pp'])*100:.0f}% | {sp(req['ontime'])} |")
    out.append(f"| H2 Переход на ТП ≥ 60 тыс. за 3 мес. | {sp(LEAN['upgrade_p0']*100, '{:.1f}')}% → {sp(LEAN['upgrade_p1']*100, '{:.1f}')}% | {sp(req['upgrade'])} |")
    c3, c6 = pw["churn"][3], pw["churn"][6]
    out.append(f"| H3 Отток, накопленный за 3 мес. | {sp(c3[0]*100, '{:.2f}')}% → {sp(c3[1]*100, '{:.2f}')}% | {sp(req['churn3'])} |")
    out.append(f"| H3 Отток, накопленный за 6 мес. | {sp(c6[0]*100, '{:.2f}')}% → {sp(c6[1]*100, '{:.2f}')}% | {sp(req['churn6'])} |")
    out.append(f"| H3 Отток, замер одного месяца | {sp(L['member_churn_base']*100, '{:.1f}')}% → "
               f"{sp(L['member_churn_base']*(1-pw['red'])*100, '{:.2f}')}% | {sp(req['churn_monthly'])} |")
    out.append(f"| H4 ARPU участников | +{LEAN['arpu_target']*100:.0f}% | {sp(req['arpu'])}; с CUPED — {sp(req['arpu_cuped'])} |")
    out.append("| H5 Вовлечённость (DAU сундука ≥ 25%) | без контроля | хватает 2 000 |\n")

    out.append("### Что увидим при каждом размере (минимальный обнаружимый эффект)\n")
    out.append("| На группу | Оплата вовремя | Переходы (с 0,3% до) | Отток 3 мес. | Отток 6 мес. | ARPU (CUPED) | DAU ± |")
    out.append("|---|---|---|---|---|---|---|")
    for r in pw["rows"]:
        out.append(f"| {sp(r['n'])} | +{sp(r['ontime_pp'], '{:.1f}')} п.п. {ok(r['ontime_pp'], LEAN['ontime_target_pp']*100)} | "
                   f"{sp(r['upgrade_to'], '{:.2f}')}% {ok(r['upgrade_to'], LEAN['upgrade_p1']*100)} | "
                   f"−{sp(r['churn3_rel'], '{:.0f}')}% {ok(r['churn3_rel'], red)} | "
                   f"−{sp(r['churn6_rel'], '{:.0f}')}% {ok(r['churn6_rel'], red)} | "
                   f"+{sp(r['arpu_cuped'], '{:.1f}')}% {ok(r['arpu_cuped'], LEAN['arpu_target']*100)} | "
                   f"{sp(r['dau_ci_pp'], '{:.1f}')} п.п. ✅ |")
    out.append(f"\n✅ — цель модели (оплата +2 п.п., переходы до 0,6%, отток −{red:.0f}%, ARPU +2%) видна надёжно; "
               "≈ — на грани (мощность ~75–80%); ❌ — эффект такого размера может «утонуть» в шуме.\n")
    j = LEAN["join_rate_optin"]
    out.append(f"**Важно:** расчёт верен, если всех из тестовой группы включают в программу автоматически. Если вступление "
               f"добровольное и вступит {j*100:.0f}%, эффект на группу «размывается» в {1/j:.0f} раза, а нужная выборка растёт "
               f"в {1/j**2:.0f} раза. Сравнивать только вступивших с невступившими нельзя: туда сами приходят лояльные "
               "(так у T-Mobile получилось −27%).\n")

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "lean_mvp.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    with open(os.path.join(OUT_DIR, "lean_mvp.json"), "w", encoding="utf-8") as f:
        json.dump({"lean": LEAN, "unit": u, "arms": arms, "base_150k": base, "base_150k_lean": base_lean,
                   "power": {"required": req, "rows": pw["rows"]}}, f, ensure_ascii=False, indent=2, default=float)
    print("\n".join(out))


if __name__ == "__main__":
    main()
