"""
Монте-Карло модель инициатив роста ARPU архивной базы Ucell.

Запуск:  python model/arpu_model.py
Выход:   model/output/results.json, model/output/results.md

Логика (помесячно, горизонт HORIZON_MONTHS):
  * ARPU считается по КОГОРТЕ «архивные абоненты на дату T0» — мигрировавшие на
    актуальные ТП остаются в когорте. Иначе миграция «выносит» ценных абонентов
    из архива и формально снижает ARPU архива (ловушка метрики).
  * adoption: инкрементальные адоптеры = N_elig × reach × takeup × (1 − cannibal),
    линейный набор за ramp месяцев с месяца launch.
  * reprice: с месяца launch целевая группа делится на stay / downgrade / churn.
  * relative: прирост выручки всей когорты на rel_uplift с линейным набором.
  * Успех (основной критерий) = накопленный вклад за 24 мес. > 0 И прирост ARPU
    когорты на 12-й мес. после запуска > 0 («окупилось и подняло ARPU»).
  * Строгий критерий «бизнес-кейс» = вклад ≥ 70% плана И ΔARPU ≥ 70% плана, где план —
    расчёт на модальных значениях параметров.
  * Итоговый шанс = P(критерий по модели) × exec_prob (вероятность запуска как задумано).
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import assumptions as A  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def tri(rng, t, n):
    lo, mode, hi = t
    if hi == lo:
        return np.full(n, float(lo))
    return rng.triangular(lo, mode, hi, n)


def mode_of(t):
    return float(t[1]) if isinstance(t, (tuple, list)) else float(t)


def draw(rng, p, key, n, deterministic):
    v = p.get(key, 0)
    if isinstance(v, (tuple, list)):
        return np.full(n, mode_of(v)) if deterministic else tri(rng, v, n)
    return np.full(n, float(v))


def base_cohort():
    b = A.BASE
    n_arch = b["total_subs"] * b["archive_share"] * b["archive_active_ratio"]
    arpu0 = sum(s["share"] * s["arpu"] for s in A.SEGMENTS.values())
    return n_arch, arpu0


def ramp_frac(m, launch, ramp):
    k = m - launch + 1
    if k <= 0:
        return 0.0
    return min(k / ramp, 1.0)


def simulate(key, n=A.N_SIMS, seed=A.SEED, deterministic=False):
    """Возвращает dict массивов (n,) с помесячными итогами."""
    p = A.INITIATIVES[key]
    rng = np.random.default_rng(seed + sum(map(ord, key)))
    H = A.HORIZON_MONTHS
    N, arpu0 = base_cohort()
    c = A.BASE["monthly_churn"]
    if deterministic:
        n = 1

    rev = np.zeros((H, n))        # инкрементальная выручка когорты (net VAT)
    rev_ext = np.zeros((H, n))    # выручка новых линий вне когорты (B2)
    cost = np.zeros((H, n))
    dsubs = np.zeros((H, n))      # изменение числа абонентов когорты
    dsubs_ext = np.zeros((H, n))  # новые линии (доля рынка)

    one_time = draw(rng, p, "one_time", n, deterministic)
    margin = draw(rng, p, "margin", n, deterministic)
    opex_m = draw(rng, p, "opex_m", n, deterministic)
    launch, ramp = p["launch"], p["ramp"]
    # разовые затраты распределяем равномерно на период до запуска
    build = max(launch - 1, 1)
    for m in range(1, build + 1):
        cost[m - 1] += one_time / build

    t = p["type"]
    if t == "adoption":
        elig = N * draw(rng, p, "eligible_share", n, deterministic)
        reach = draw(rng, p, "reach", n, deterministic)
        takeup = draw(rng, p, "takeup", n, deterministic)
        cannibal = draw(rng, p, "cannibal", n, deterministic)
        delta = draw(rng, p, "delta", n, deterministic)
        churn_incr = draw(rng, p, "churn_incr", n, deterministic)
        churn_red = draw(rng, p, "churn_red", n, deterministic)
        cpa_once = draw(rng, p, "cost_per_adopter_once", n, deterministic)
        var_m = draw(rng, p, "var_cost_m", n, deterministic)
        seg_arpu = p["segment_arpu"]
        contacted = elig * reach
        a_final = contacted * takeup * (1 - cannibal)
        lost_total = contacted * churn_incr
        # затухание реактивированных (A6)
        if "adopter_decay_6m" in p:
            surv6 = draw(rng, p, "adopter_decay_6m", n, deterministic)
            decay_m = 1 - surv6 ** (1 / 6)
        else:
            decay_m = np.zeros(n)
        new_lines = draw(rng, p, "new_lines", n, deterministic) if "new_lines" in p else np.zeros(n)
        nl_arpu = p.get("new_line_arpu", 0)

        # A — пул адоптеров, получающих delta: уходит с пониженным оттоком c·(1−churn_red)
        #     и (для A6) «засыпает» обратно с темпом decay_m.
        # R — абоненты, которые без инициативы ушли бы (эффект удержания), платят seg_arpu.
        # L — потерянные из-за инициативы (без неё часть ушла бы и так → затухает с c).
        pool = np.zeros(n)
        retained = np.zeros(n)
        lost = np.zeros(n)
        prev_target = np.zeros(n)
        K = 3  # раздражение от контакта распределено на 3 мес. после старта
        for m in range(1, H + 1):
            f = ramp_frac(m, launch, ramp)
            target = a_final * f
            new_adopt = np.maximum(target - prev_target, 0)
            prev_target = target
            retained = retained * (1 - c) + pool * c * churn_red
            pool = pool * (1 - decay_m) * (1 - c * (1 - churn_red)) + new_adopt
            lost = lost * (1 - c) + (lost_total / K if launch <= m < launch + K else 0)
            rev[m - 1] = pool * delta + retained * seg_arpu - lost * seg_arpu
            dsubs[m - 1] = retained - lost
            rev_ext[m - 1] = pool * new_lines * nl_arpu
            dsubs_ext[m - 1] = pool * new_lines
            cost[m - 1] += new_adopt * cpa_once + pool * var_m
            if m == launch:
                cost[m - 1] += contacted * p.get("cost_per_contact", 0)
            if m >= launch:
                cost[m - 1] += opex_m

    elif t == "reprice":
        elig = N * draw(rng, p, "eligible_share", n, deterministic)
        up_net = draw(rng, p, "price_up_gross", n, deterministic) / (1 + A.VAT)
        dg = draw(rng, p, "downgrade", n, deterministic)
        dg_delta = draw(rng, p, "downgrade_delta", n, deterministic)
        ch = draw(rng, p, "churn_incr", n, deterministic)
        data_cost = draw(rng, p, "data_cost_m", n, deterministic)
        savings = draw(rng, p, "opex_savings_m", n, deterministic) if "opex_savings_m" in p else np.zeros(n)
        seg_arpu = p["segment_arpu"]
        stay = elig * (1 - dg - ch)
        down = elig * dg
        churners_total = elig * ch
        lost = np.zeros(n)
        for m in range(1, H + 1):
            if m < launch:
                continue
            decay = (1 - c) ** (m - launch)  # естественный отток группы
            # отток по уведомлению — за 2 мес.; без изменения часть ушла бы и так → затухает с c
            lost = lost * (1 - c) + (churners_total / 2 if m < launch + 2 else 0)
            rev[m - 1] = (stay * up_net + down * dg_delta) * decay - lost * seg_arpu
            dsubs[m - 1] = -lost
            cost[m - 1] += stay * data_cost * decay + opex_m - savings
            if m == launch:
                cost[m - 1] += elig * p.get("cost_per_contact", 0)

    elif t == "relative":
        rel = draw(rng, p, "rel_uplift", n, deterministic)
        cr = draw(rng, p, "churn_red_base", n, deterministic)
        retained = np.zeros(n)
        for m in range(1, H + 1):
            f = ramp_frac(m, launch, ramp)
            base_subs_m = N * (1 - c) ** m
            base_rev_m = base_subs_m * arpu0
            retained = retained * (1 - c) + base_subs_m * c * cr * f
            rev[m - 1] = base_rev_m * rel * f + retained * arpu0
            dsubs[m - 1] = retained
            if m >= launch:
                cost[m - 1] += opex_m
    else:
        raise ValueError(t)

    contrib = rev * margin + rev_ext * margin - cost
    # ARPU когорты: (R0 + dR) / (S0 + dS)
    months = np.arange(1, H + 1)
    s0 = N * (1 - c) ** months
    r0 = s0 * arpu0
    arpu_new = (r0[:, None] + rev) / (s0[:, None] + dsubs)
    arpu_uplift = arpu_new / arpu0 - 1
    pre_launch_cost = cost[: max(launch - 1, 1)].sum(0)
    return {
        "rev": rev, "rev_ext": rev_ext, "cost": cost, "contrib": contrib,
        "pre_launch_cost": pre_launch_cost,
        "dsubs": dsubs, "dsubs_ext": dsubs_ext, "arpu_uplift": arpu_uplift,
        "r0": r0, "s0": s0,
    }


def pct(x, q):
    return float(np.percentile(x, q))


def summarize(key, sim, det):
    p = A.INITIATIVES[key]
    H = A.HORIZON_MONTHS
    rev_y1 = sim["rev"][:12].sum(0) + sim["rev_ext"][:12].sum(0)
    rev_y2 = sim["rev"][12:].sum(0) + sim["rev_ext"][12:].sum(0)
    contrib_24 = sim["contrib"].sum(0)
    cost_24 = sim["cost"].sum(0)
    run_rate = (sim["rev"][H - 1] + sim["rev_ext"][H - 1]) * 12
    eval_m = min(p["launch"] + 11, H) - 1   # 12-й месяц после запуска
    upl = sim["arpu_uplift"][eval_m]
    upl_24 = sim["arpu_uplift"][H - 1]
    rev_upl_24 = sim["rev"][H - 1] / sim["r0"][H - 1]
    subs_24 = sim["dsubs"][H - 1] + sim["dsubs_ext"][H - 1]
    share_pp = subs_24 / A.BASE["market_total_subs"] * 100
    roi = np.where(cost_24 > 0, contrib_24 / np.maximum(cost_24, 1), np.nan)
    plan_contrib = float(det["contrib"].sum())
    plan_upl = float(det["arpu_uplift"][eval_m][0])
    success = (contrib_24 > 0) & (upl > 0)
    p_model = float(success.mean())
    if plan_contrib > 0 and plan_upl > 0:
        bc = (contrib_24 >= 0.7 * plan_contrib) & (upl >= 0.7 * plan_upl)
    else:
        bc = contrib_24 > 0
    p_bc = float(bc.mean())
    fx = A.FX_UZS_PER_USD
    return {
        "key": key, "name": p["name"], "group": p["group"], "complexity": p["complexity"],
        "launch_month": p["launch"], "exec_prob": p["exec_prob"],
        "plan_contrib_24_bn": plan_contrib / 1e9,
        "plan_arpu_uplift": plan_upl,
        "rev_y1_bn": [pct(rev_y1, q) / 1e9 for q in (10, 50, 90)],
        "rev_y2_bn": [pct(rev_y2, q) / 1e9 for q in (10, 50, 90)],
        "run_rate_bn": [pct(run_rate, q) / 1e9 for q in (10, 50, 90)],
        "run_rate_musd": [pct(run_rate, q) / fx / 1e6 for q in (10, 50, 90)],
        "contrib_24_bn": [pct(contrib_24, q) / 1e9 for q in (10, 50, 90)],
        "cost_24_bn": pct(cost_24, 50) / 1e9,
        "roi_24_p50": float(np.nanmedian(roi)),
        "arpu_uplift_12m_after_launch": [pct(upl, q) for q in (10, 50, 90)],
        "arpu_uplift_m24": [pct(upl_24, q) for q in (10, 50, 90)],
        "revenue_uplift_m24": [pct(rev_upl_24, q) for q in (10, 50, 90)],
        "subs_delta_m24": [pct(subs_24, q) for q in (10, 50, 90)],
        "market_share_pp_m24": [pct(share_pp, q) for q in (10, 50, 90)],
        "p_contrib_positive": float((contrib_24 > 0).mean()),
        "p_model_success": p_model,
        "p_business_case": p_bc,
        "success_chance": p_model * p["exec_prob"],
        "business_case_chance": p_bc * p["exec_prob"],
    }


def portfolio(sims, keys, n=A.N_SIMS, seed=A.SEED):
    """Портфель: каждая инициатива запускается с вероятностью exec_prob, минус перекрытие."""
    rng = np.random.default_rng(seed + 7)
    H = A.HORIZON_MONTHS
    haircut = tri(rng, A.PORTFOLIO_OVERLAP_HAIRCUT, n)
    rev = np.zeros((H, n))
    rev_ext = np.zeros((H, n))
    contrib = np.zeros((H, n))
    dsubs = np.zeros((H, n))
    dsubs_ext = np.zeros((H, n))
    for k in keys:
        s = sims[k]
        launched = rng.random(n) < A.INITIATIVES[k]["exec_prob"]
        # не запущенная инициатива: выручки нет, но 50% затрат на разработку уже потрачено
        rev += s["rev"] * launched
        rev_ext += s["rev_ext"] * launched
        # перекрытие режет маржу от выручки, но не затраты: вклад = маржа·(1−h) − затраты
        gross_margin = s["contrib"] + s["cost"]
        contrib += (gross_margin * (1 - haircut) - s["cost"]) * launched
        contrib[0] -= 0.5 * s["pre_launch_cost"] * (~launched)
        dsubs += s["dsubs"] * launched
        dsubs_ext += s["dsubs_ext"] * launched
    rev *= (1 - haircut)
    rev_ext *= (1 - haircut)
    dsubs *= (1 - haircut)
    s0 = sims[keys[0]]["s0"]
    r0 = sims[keys[0]]["r0"]
    arpu0 = r0[0] / s0[0]
    arpu_new = (r0[:, None] + rev) / (s0[:, None] + dsubs)
    upl = arpu_new / arpu0 - 1
    rev_y1 = rev[:12].sum(0) + rev_ext[:12].sum(0)
    rev_y2 = rev[12:].sum(0) + rev_ext[12:].sum(0)
    run_rate = (rev[H - 1] + rev_ext[H - 1]) * 12
    share_pp = (dsubs[H - 1] + dsubs_ext[H - 1]) / A.BASE["market_total_subs"] * 100
    c24 = contrib.sum(0)
    fx = A.FX_UZS_PER_USD
    return {
        "keys": keys,
        "arpu_uplift_m12": [pct(upl[11], q) for q in (10, 50, 90)],
        "arpu_uplift_m24": [pct(upl[H - 1], q) for q in (10, 50, 90)],
        "arpu_m24_uzs": [pct(arpu_new[H - 1], q) for q in (10, 50, 90)],
        "rev_y1_bn": [pct(rev_y1, q) / 1e9 for q in (10, 50, 90)],
        "rev_y2_bn": [pct(rev_y2, q) / 1e9 for q in (10, 50, 90)],
        "run_rate_bn": [pct(run_rate, q) / 1e9 for q in (10, 50, 90)],
        "run_rate_musd": [pct(run_rate, q) / fx / 1e6 for q in (10, 50, 90)],
        "contrib_24_bn": [pct(c24, q) / 1e9 for q in (10, 50, 90)],
        "market_share_pp_m24": [pct(share_pp, q) for q in (10, 50, 90)],
        "p_contrib_positive": float((c24 > 0).mean()),
        "p_uplift_m24_ge": {str(t): float((upl[H - 1] >= t).mean()) for t in (0.05, 0.10, 0.15, 0.20, 0.25)},
        "p_uplift_m12_ge": {str(t): float((upl[11] >= t).mean()) for t in (0.05, 0.10, 0.15, 0.20)},
        "monthly_uplift_p50": [pct(upl[m], 50) for m in range(H)],
    }


def tornado(key, metric="contrib24"):
    """Чувствительность: каждый параметр → min/max при остальных на моде."""
    p = A.INITIATIVES[key]
    base = simulate(key, deterministic=True)
    base_v = float(base["contrib"].sum())
    rows = []
    for k, v in p.items():
        if not isinstance(v, (tuple, list)) or v[0] == v[2]:
            continue
        vals = []
        for side in (0, 2):
            orig = p[k]
            p[k] = (v[side], v[side], v[side])
            s = simulate(key, deterministic=True)
            vals.append(float(s["contrib"].sum()))
            p[k] = orig
        rows.append({"param": k, "low": vals[0] / 1e9, "high": vals[1] / 1e9,
                     "swing": abs(vals[1] - vals[0]) / 1e9})
    rows.sort(key=lambda r: -r["swing"])
    return {"key": key, "base_bn": base_v / 1e9, "rows": rows}


def ab_sample_size(cv=1.2, mde=0.03, alpha_z=1.96, power_z=0.8416):
    """Размер группы для t-теста разности средних ARPU (двусторонний, alpha=5%, power=80%)."""
    return int(np.ceil(2 * (alpha_z + power_z) ** 2 * cv ** 2 / mde ** 2))


def fmt_rng(v, f="{:,.1f}"):
    return f"{f.format(v[1])} ({f.format(v[0])} … {f.format(v[2])})"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    N, arpu0 = base_cohort()
    keys = list(A.INITIATIVES)
    sims = {k: simulate(k) for k in keys}
    det = {k: simulate(k, deterministic=True) for k in keys}
    res = [summarize(k, sims[k], det[k]) for k in keys]
    for r in res:
        d = det[r["key"]]
        r["det_contrib_24_bn"] = float(d["contrib"].sum()) / 1e9
        r["det_rev_y1_bn"] = float(d["rev"][:12].sum() + d["rev_ext"][:12].sum()) / 1e9
    core = [k for k in keys if not A.INITIATIVES[k].get("optional")
            and not A.INITIATIVES[k].get("not_recommended")]
    easy = [k for k in core if A.INITIATIVES[k]["group"] == "EASY"]
    hard = [k for k in core if A.INITIATIVES[k]["group"] == "HARD"]
    port_all = portfolio(sims, core)
    port_stretch = portfolio(sims, [k for k in keys if not A.INITIATIVES[k].get("not_recommended")])
    port_easy = portfolio(sims, easy)
    port_hard = portfolio(sims, hard)
    torn = [tornado("A1"), tornado("A2"), tornado("B1")]
    ab = [
        {"test": "ARPU, MDE 3%, CV 1.2", "n_per_arm": ab_sample_size(1.2, 0.03)},
        {"test": "ARPU, MDE 5%, CV 1.2", "n_per_arm": ab_sample_size(1.2, 0.05)},
        {"test": "ARPU, MDE 2%, CV 1.0", "n_per_arm": ab_sample_size(1.0, 0.02)},
    ]
    # конверсия (пропорция): p=10%, MDE +1 п.п.
    p1, p2 = 0.10, 0.11
    pbar = (p1 + p2) / 2
    n_conv = int(np.ceil((1.96 * np.sqrt(2 * pbar * (1 - pbar)) + 0.8416 * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2))
    ab.append({"test": "Конверсия 10% → 11%", "n_per_arm": n_conv})
    # отток: 1.5% → 2.0% (guardrail)
    p1, p2 = 0.015, 0.020
    pbar = (p1 + p2) / 2
    n_ch = int(np.ceil((1.96 * np.sqrt(2 * pbar * (1 - pbar)) + 0.8416 * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2))
    ab.append({"test": "Отток 1,5% → 2,0% (guardrail)", "n_per_arm": n_ch})

    out = {
        "base": {
            "archive_active_subs": N, "arpu0_uzs": arpu0,
            "arpu0_usd": arpu0 / A.FX_UZS_PER_USD,
            "monthly_revenue_bn": N * arpu0 / 1e9,
            "annual_revenue_bn": N * arpu0 * 12 / 1e9,
            "annual_revenue_musd": N * arpu0 * 12 / A.FX_UZS_PER_USD / 1e6,
        },
        "initiatives": res,
        "portfolio_all": port_all, "portfolio_easy": port_easy, "portfolio_hard": port_hard,
        "portfolio_stretch": port_stretch,
        "tornado": torn, "ab_sample_sizes": ab,
    }
    with open(os.path.join(OUT_DIR, "results.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # ---- Markdown отчёт ----
    L = []
    L.append("# Результаты модели (Монте-Карло, 20 000 прогонов)\n")
    L.append("> Сгенерировано `python model/arpu_model.py`. Все суммы — млрд сум без НДС, "
             "если не указано иное. Формат: **P50 (P10 … P90)**.\n")
    b = out["base"]
    L.append("## База (гипотеза до получения данных)\n")
    L.append(f"- Активная архивная когорта: **{b['archive_active_subs']/1e6:.2f} млн** абонентов")
    L.append(f"- ARPU когорты: **{b['arpu0_uzs']:,.0f} сум** (≈ ${b['arpu0_usd']:.2f})")
    L.append(f"- Выручка когорты: **{b['monthly_revenue_bn']:,.1f} млрд сум/мес**, "
             f"{b['annual_revenue_bn']:,.0f} млрд сум/год (≈ ${b['annual_revenue_musd']:.0f} млн)\n")
    L.append("## Инициативы\n")
    L.append("| # | Инициатива | Группа | Старт, мес | Выручка Y1 | Run-rate/год (мес 24) | Вклад 24 мес | ROI 24м | ΔARPU через 12 мес после старта | P(вклад>0) | P(запуск) | **Шанс успеха** | Шанс ≥70% бизнес-кейса |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in res:
        L.append(
            f"| {r['key']} | {r['name']} | {r['group']} | {r['launch_month']} | "
            f"{fmt_rng(r['rev_y1_bn'])} | {fmt_rng(r['run_rate_bn'])} | {fmt_rng(r['contrib_24_bn'])} | "
            f"{r['roi_24_p50']:.1f}x | {fmt_rng([x*100 for x in r['arpu_uplift_12m_after_launch']], '{:.1f}%')} | "
            f"{r['p_contrib_positive']*100:.0f}% | {r['exec_prob']*100:.0f}% | "
            f"**{r['success_chance']*100:.0f}%** | {r['business_case_chance']*100:.0f}% |")
    L.append("")
    for title, pr in (("Базовый (рекомендуемый: без опции A8 и без B4)", port_all), ("Только EASY", port_easy),
                      ("Только HARD", port_hard), ("Stretch = базовый + A8 (индексация, волна 2)", port_stretch)):
        L.append(f"## Портфель: {title}\n")
        L.append(f"- ΔARPU когорты, мес 12: **{fmt_rng([x*100 for x in pr['arpu_uplift_m12']], '{:.1f}%')}**")
        L.append(f"- ΔARPU когорты, мес 24: **{fmt_rng([x*100 for x in pr['arpu_uplift_m24']], '{:.1f}%')}**")
        L.append(f"- ARPU когорты, мес 24: {fmt_rng(pr['arpu_m24_uzs'], '{:,.0f}')} сум")
        L.append(f"- Инкрементальная выручка Y1: {fmt_rng(pr['rev_y1_bn'])} млрд сум; Y2: {fmt_rng(pr['rev_y2_bn'])} млрд сум")
        L.append(f"- Run-rate на мес 24: {fmt_rng(pr['run_rate_bn'])} млрд сум/год ≈ ${fmt_rng(pr['run_rate_musd'])} млн")
        L.append(f"- Накопленный вклад 24 мес: {fmt_rng(pr['contrib_24_bn'])} млрд сум; P(вклад>0) = {pr['p_contrib_positive']*100:.0f}%")
        L.append(f"- Δ доли рынка (абоненты), мес 24: {fmt_rng(pr['market_share_pp_m24'], '{:+.2f}')} п.п.")
        L.append("- Вероятность достичь ΔARPU к мес 24: " + ", ".join(
            f"≥{float(t)*100:.0f}% — **{v*100:.0f}%**" for t, v in pr["p_uplift_m24_ge"].items()))
        L.append("")
    L.append("## Чувствительность (tornado, вклад за 24 мес, млрд сум)\n")
    for t in torn:
        L.append(f"**{t['key']}** — база {t['base_bn']:,.1f}\n")
        L.append("| Параметр | Мин. значение | Макс. значение | Размах |")
        L.append("|---|---|---|---|")
        for r in t["rows"][:6]:
            L.append(f"| {r['param']} | {r['low']:,.1f} | {r['high']:,.1f} | {r['swing']:,.1f} |")
        L.append("")
    L.append("## Размер выборки для A/B (alpha 5%, power 80%, двусторонний)\n")
    L.append("| Тест | N на группу |")
    L.append("|---|---|")
    for a in ab:
        L.append(f"| {a['test']} | {a['n_per_arm']:,} |")
    with open(os.path.join(OUT_DIR, "results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
