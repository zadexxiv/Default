"""
v2: Монте-Карло модель 4 инициатив роста ARPU архивной базы Ucell + бюджет Loyalty program.

Запуск:  python v2/model/model_v2.py
Выход:   v2/model/output/results_v2.md, results_v2.json

Горизонт 36 мес. (M1 = ноябрь 2026). ARPU — по когорте архивных абонентов T0
(мигрировавшие остаются в когорте). Loyalty считается двумя уровнями:
  * программа целиком (участники со всей базы Ucell) — P&L, бюджет, окупаемость;
  * вклад в ARPU архивной когорты (только архивные участники).
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assumptions_v2 as A  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
H = A.HORIZON_MONTHS
WEEKS_PER_MONTH = 52 / 12


# --------------------------------------------------------------------------- utils
def tri(rng, t, n):
    lo, mo, hi = t
    if hi == lo:
        return np.full(n, float(lo))
    return rng.triangular(lo, mo, hi, n)


def mode(v):
    return float(v[1]) if isinstance(v, (tuple, list)) else float(v)


def draw(rng, p, key, n, det, default=0.0):
    v = p.get(key, default)
    if isinstance(v, (tuple, list)):
        return np.full(n, mode(v)) if det else tri(rng, v, n)
    return np.full(n, float(v))


def pct(x, q):
    return float(np.percentile(x, q))


def p3(x, scale=1.0):
    return [pct(x, q) / scale for q in (10, 50, 90)]


def cohort():
    b = A.BASE
    n = b["total_subs"] * b["archive_share"] * b["archive_active_ratio"]
    return n, b["archive_arpu"]


def ramp_frac(m, launch, ramp):
    k = m - launch + 1
    return 0.0 if k <= 0 else min(k / ramp, 1.0)


# --------------------------------------------------------------------------- prize budgets
def prize_budgets():
    P = A.PRIZES
    weekly = sum(P[k]["price"] * q * (1 - co) for k, q, co in A.WEEKLY_WINS)
    weekly_items = sum(q for _, q, _ in A.WEEKLY_WINS)
    drops = sum(P[k]["price"] * q * (1 - co) for k, q, co in A.DROPS_INVENTORY)
    drops_items = sum(q * (2 if k == "cinema_pair" else 1) for k, q, _ in A.DROPS_INVENTORY)
    grand_items = []
    for g in A.MONTHLY_GRAND:
        if g == "iphone17_x5":
            grand_items.append(("5 × iPhone 17", 5 * P["iphone17"]["price"]))
        elif g == "free_year_x10":
            grand_items.append(("10 × год связи бесплатно", 10 * P["free_year"]["price"]))
        else:
            grand_items.append((P[g]["name"], P[g]["price"]))
    grand_year = sum(v for _, v in grand_items)
    grand_month = grand_year / 12 * (1 + A.GRAND_OVERHEAD)
    drop_digital = sum(pr * c for _, pr, c, _ in A.DROP_TABLE)
    return {
        "weekly_wins_week": weekly, "weekly_items": weekly_items,
        "drops_inventory_week": drops, "drops_items": drops_items,
        "grand_items": grand_items, "grand_year": grand_year, "grand_month": grand_month,
        "drop_digital_cost": drop_digital, "drop_prob_sum": sum(pr for _, pr, _, _ in A.DROP_TABLE),
    }


# --------------------------------------------------------------------------- initiatives 1–3
def simulate_initiative(key, n=A.N_SIMS, det=False):
    p = A.INITIATIVES[key]
    rng = np.random.default_rng(A.SEED + sum(map(ord, key)))
    if det:
        n = 1
    N, arpu0 = cohort()
    c = A.BASE["monthly_churn"]
    rev = np.zeros((H, n))
    cost = np.zeros((H, n))
    dsubs = np.zeros((H, n))
    one_time = draw(rng, p, "one_time", n, det)
    opex = draw(rng, p, "opex_m", n, det)
    margin = p["margin"]

    if p["type"] == "reprice":
        waves = p["waves"]
        first = waves[0][0]
        elig = N * draw(rng, p, "eligible_share", n, det)
        if "price_up_pct" in p:
            up_net = p["base_fee_gross"] * draw(rng, p, "price_up_pct", n, det) / (1 + A.VAT)
        else:
            up_net = draw(rng, p, "price_up_gross", n, det) / (1 + A.VAT)
        dg = draw(rng, p, "downgrade", n, det)
        dgd = draw(rng, p, "downgrade_delta", n, det)
        ch = draw(rng, p, "churn_incr", n, det)
        ups = draw(rng, p, "upsell_share", n, det)
        upsd = draw(rng, p, "upsell_delta", n, det)
        dcost = draw(rng, p, "data_cost_m", n, det)
        sav = draw(rng, p, "opex_savings_m", n, det)
        stay = elig * (1 - dg - ch)
        down = elig * dg
        churners = elig * ch
        build = max(first - 1, 1)
        lost = np.zeros(n)
        for m in range(1, H + 1):
            if m <= build:
                cost[m - 1] += one_time / build
            new_lost = np.zeros(n)
            cum_frac = 0.0
            for L, fr in waves:
                if m >= L:
                    cum_frac += fr
                    decay = (1 - c) ** (m - L)
                    rev[m - 1] += fr * (stay * up_net + elig * ups * upsd + down * dgd) * decay
                    cost[m - 1] += fr * stay * dcost * decay
                if L <= m < L + 2:
                    new_lost = new_lost + fr * churners / 2
                if m == L:
                    cost[m - 1] += fr * elig * p.get("cost_per_contact", 0)
            lost = lost * (1 - c) + new_lost
            rev[m - 1] -= lost * p["segment_arpu"]
            dsubs[m - 1] = -lost
            if m >= first:
                cost[m - 1] += opex - sav * cum_frac
    else:  # adoption
        launch, ramp = p["launch"], p["ramp"]
        elig = N * draw(rng, p, "eligible_share", n, det)
        contacted = elig * draw(rng, p, "reach", n, det)
        a_final = contacted * draw(rng, p, "takeup", n, det) * (1 - draw(rng, p, "cannibal", n, det))
        delta = draw(rng, p, "delta", n, det)
        lost_total = contacted * draw(rng, p, "churn_incr", n, det)
        cr = draw(rng, p, "churn_red", n, det)
        cpa = draw(rng, p, "cost_per_adopter_once", n, det)
        var = draw(rng, p, "var_cost_m", n, det)
        build = max(launch - 1, 1)
        pool = np.zeros(n)
        R = np.zeros(n)
        L = np.zeros(n)
        prev = np.zeros(n)
        for m in range(1, H + 1):
            if m <= build:
                cost[m - 1] += one_time / build
            tgt = a_final * ramp_frac(m, launch, ramp)
            new = np.maximum(tgt - prev, 0)
            prev = tgt
            R = R * (1 - c) + pool * c * cr
            pool = pool * (1 - c * (1 - cr)) + new
            L = L * (1 - c) + (lost_total / 3 if launch <= m < launch + 3 else 0)
            rev[m - 1] = pool * delta + R * p["segment_arpu"] - L * p["segment_arpu"]
            dsubs[m - 1] = R - L
            cost[m - 1] += new * cpa + pool * var
            if m == launch:
                cost[m - 1] += contacted * p.get("cost_per_contact", 0)
            if m >= launch:
                cost[m - 1] += opex
    contrib = rev * margin - cost
    return {"rev": rev, "cost": cost, "contrib": contrib, "dsubs": dsubs}


# --------------------------------------------------------------------------- loyalty
def loyalty_member_stats():
    b = A.BANDS
    arpu_gross = sum(v["member_share"] * v["fee"] for v in b.values())
    earn = sum(v["member_share"] * v["fee"] * v["cb"] for v in b.values())
    below60 = b["lt30"]["member_share"] + b["30_59"]["member_share"]
    a_earn = sum(v["archive_share"] * v["fee"] * v["cb"] for v in b.values())
    a_below60 = b["lt30"]["archive_share"] + b["30_59"]["archive_share"]
    return {"arpu_net": arpu_gross / (1 + A.VAT), "earn": earn, "below60": below60,
            "archive_earn": a_earn, "archive_below60": a_below60,
            "avg_cb_rate": earn / arpu_gross}


def simulate_loyalty(n=A.N_SIMS, det=False, scale=True):
    L = A.LOYALTY
    pb = prize_budgets()
    rng = np.random.default_rng(A.SEED + 99)
    if det:
        n = 1
    st = loyalty_member_stats()
    g = lambda k, d=0.0: draw(rng, L, k, n, det, d)  # noqa: E731

    full = A.BASE["total_subs"] * g("app_mau_share") * g("enroll_of_mau")
    arch_share = g("archive_share_members")
    ontime = g("ontime_share")
    breakage = g("breakage")
    rcr = g("redeem_cost_ratio")
    dau = g("drops_dau_share")
    ddc = np.full(n, pb["drop_digital_cost"]) if det else rng.triangular(
        pb["drop_digital_cost"] * 0.7, pb["drop_digital_cost"], pb["drop_digital_cost"] * 1.35, n)
    inv_w = np.full(n, pb["drops_inventory_week"]) if det else rng.triangular(
        pb["drops_inventory_week"] * 0.75, pb["drops_inventory_week"], pb["drops_inventory_week"] * 1.25, n)
    ww_w = np.full(n, pb["weekly_wins_week"]) if det else rng.triangular(
        pb["weekly_wins_week"] * 0.8, pb["weekly_wins_week"], pb["weekly_wins_week"] * 1.3, n)
    grand = np.full(n, pb["grand_month"]) if det else rng.triangular(
        pb["grand_month"] * 0.8, pb["grand_month"], pb["grand_month"] * 1.35, n)
    mvp_build, scale_build = g("mvp_build"), g("scale_build")
    opex, mvp_opex, mkt = g("opex_m"), g("mvp_opex_m"), g("marketing_m")
    launch_mkt, mvp_mkt = g("launch_marketing"), g("mvp_marketing")
    cr, ont_up = g("churn_reduction"), g("ontime_rev_uplift")
    up_rate, up_delta = g("upgrade_rate_m"), g("upgrade_delta")
    pass_ad, eng = g("pass_adoption"), g("engagement_upsell")
    partner = g("partner_cash_m")
    a_up_rate, a_up_delta = g("archive_upgrade_rate_m"), g("archive_upgrade_delta")

    ms, mm = L["mvp_start"], L["mvp_months"]
    ss, sr = L["scale_start"], L["scale_ramp"]
    c, ca = L["member_churn_base"], L["archive_churn_base"]
    arpu, a_arpu = st["arpu_net"], L["archive_member_arpu"]
    pass_net = L["pass_price_gross"] / (1 + A.VAT)
    mvp_n = L["mvp_participants"]

    keys = ["members", "c_cashback", "c_drops_digital", "c_drops_inventory", "c_weekly", "c_grand",
            "c_build", "c_opex", "c_marketing", "b_retention", "b_ontime", "b_upgrade", "b_pass",
            "b_engagement", "b_partner", "a_rev", "a_dsubs", "a_members"]
    out = {k: np.zeros((H, n)) for k in keys}
    R = np.zeros(n)
    U = np.zeros(n)
    Ra = np.zeros(n)
    Ua = np.zeros(n)
    prev_members = np.zeros(n)
    prev_am = np.zeros(n)
    for m in range(1, H + 1):
        i = m - 1
        # участники
        if m < ms:
            mem = np.zeros(n)
        elif m < ss or not scale:
            mem = np.full(n, float(mvp_n))
        else:
            mem = np.maximum(mvp_n, full * min((m - ss + 1) / sr, 1.0))
        prize_f = np.where(mem > 0, np.maximum(L["mvp_prize_share"], mem / full), 0.0) if scale else \
            np.where(mem > 0, L["mvp_prize_share"], 0.0)
        out["members"][i] = mem
        # затраты
        build_mvp_months = list(range(2, ms))            # декабрь–февраль
        build_scale_months = list(range(ms + mm, ss))    # июнь–август
        if m in build_mvp_months:
            out["c_build"][i] += mvp_build / len(build_mvp_months)
        if scale and m in build_scale_months:
            out["c_build"][i] += scale_build / len(build_scale_months)
        if ms <= m < ss or (not scale and m >= ms):
            out["c_opex"][i] += mvp_opex
        if scale and m >= ss:
            out["c_opex"][i] += opex
            out["c_marketing"][i] += mkt
            if m in (ss, ss + 1):
                out["c_marketing"][i] += launch_mkt / 2
        if m == ms:
            out["c_marketing"][i] += mvp_mkt
        out["c_cashback"][i] = mem * ontime * st["earn"] * (1 - breakage) * rcr
        out["c_drops_digital"][i] = mem * dau * 30 * ddc
        out["c_drops_inventory"][i] = inv_w * WEEKS_PER_MONTH * prize_f
        out["c_weekly"][i] = ww_w * WEEKS_PER_MONTH * prize_f
        out["c_grand"][i] = grand * prize_f
        # эффекты (вся программа)
        R = R * (1 - c) + prev_members * c * cr
        U = U * (1 - c) + mem * st["below60"] * up_rate
        out["b_retention"][i] = R * arpu
        out["b_ontime"][i] = mem * arpu * ont_up
        out["b_upgrade"][i] = U * up_delta
        out["b_pass"][i] = mem * st["below60"] * pass_ad * pass_net
        out["b_engagement"][i] = mem * arpu * eng * dau / 0.30   # допродажи растут с ежедневной активностью
        if scale and m >= ss + 6:
            out["b_partner"][i] = partner
        # архивная когорта
        am = mem * arch_share
        out["a_members"][i] = am
        Ra = Ra * (1 - ca) + prev_am * ca * cr
        Ua = Ua * (1 - ca) + am * a_up_rate
        contra = am * ontime * st["archive_earn"] * (1 - breakage) * 0.30  # погашение кэшбэком части счёта
        out["a_rev"][i] = (Ra * a_arpu + Ua * a_up_delta + am * a_arpu * ont_up
                           + am * st["archive_below60"] * pass_ad * pass_net + am * a_arpu * eng * dau / 0.30 - contra)
        out["a_dsubs"][i] = Ra
        prev_members, prev_am = mem, am

    cost_keys = [k for k in keys if k.startswith("c_")]
    out["cost"] = sum(out[k] for k in cost_keys)
    out["benefit_rev"] = out["b_retention"] + out["b_ontime"] + out["b_upgrade"] + out["b_engagement"]
    out["contrib"] = (out["benefit_rev"] * L["margin"] + out["b_pass"] * (1 - L["pass_value_cost"])
                      + out["b_partner"] - out["cost"])
    out["full_members"] = full
    return out


# --------------------------------------------------------------------------- summaries
def arpu_path(rev, dsubs):
    N, arpu0 = cohort()
    c = A.BASE["monthly_churn"]
    months = np.arange(1, H + 1)
    s0 = N * (1 - c) ** months
    r0 = s0 * arpu0
    return (r0[:, None] + rev) / (s0[:, None] + dsubs) / arpu0 - 1, r0, s0


def summarize_initiative(key, sim, det):
    p = A.INITIATIVES[key]
    upl, r0, _ = arpu_path(sim["rev"], sim["dsubs"])
    dupl, _, _ = arpu_path(det["rev"], det["dsubs"])
    first = p["waves"][0][0] if p["type"] == "reprice" else p["launch"]
    ev = min(first + 11, H) - 1
    c24 = sim["contrib"][:24].sum(0)
    c36 = sim["contrib"].sum(0)
    plan_c24 = float(det["contrib"][:24].sum())
    plan_upl = float(dupl[ev][0])
    succ = (c24 > 0) & (upl[ev] > 0)
    bc = (c24 >= 0.7 * plan_c24) & (upl[ev] >= 0.7 * plan_upl) if plan_c24 > 0 else c24 > 0
    fx = A.FX_UZS_PER_USD
    return {
        "key": key, "name": p["name"], "short": p["short"], "complexity": p["complexity"],
        "first_month": first, "exec_prob": p["exec_prob"],
        "rev_y1_bn": p3(sim["rev"][:12].sum(0), 1e9), "rev_y2_bn": p3(sim["rev"][12:24].sum(0), 1e9),
        "rev_y3_bn": p3(sim["rev"][24:].sum(0), 1e9),
        "run_rate_bn": p3(sim["rev"][23] * 12, 1e9), "run_rate_musd": p3(sim["rev"][23] * 12, 1e6 * fx),
        "contrib_24_bn": p3(c24, 1e9), "contrib_36_bn": p3(c36, 1e9),
        "cost_24_bn": pct(sim["cost"][:24].sum(0), 50) / 1e9,
        "arpu_uplift_eval": p3(upl[ev]), "arpu_uplift_m24": p3(upl[23]),
        "subs_m24": p3(sim["dsubs"][23]),
        "plan_contrib_24_bn": plan_c24 / 1e9, "plan_arpu_uplift": plan_upl,
        "p_contrib_pos": float((c24 > 0).mean()), "p_model": float(succ.mean()),
        "success_chance": float(succ.mean()) * p["exec_prob"],
        "business_case_chance": float(bc.mean()) * p["exec_prob"],
    }


def summarize_loyalty(sim, det, sim_mvp):
    L = A.LOYALTY
    a_upl, _, _ = arpu_path(sim["a_rev"], sim["a_dsubs"])
    d_upl, _, _ = arpu_path(det["a_rev"], det["a_dsubs"])
    c24 = sim["contrib"][:24].sum(0)
    c36 = sim["contrib"].sum(0)
    cum = np.cumsum(sim["contrib"], axis=0)
    neg = cum < -1e6
    last_neg = np.where(neg.any(0), H - 1 - np.argmax(neg[::-1], axis=0), -1)
    be = np.where(last_neg == H - 1, 99, last_neg + 2)
    monthly_pos = sim["contrib"][23] > 0
    succ = (c36 > 0) & (a_upl[23] > 0)
    plan_c36 = float(det["contrib"].sum())
    bc = (c36 >= 0.7 * plan_c36) & (a_upl[23] >= 0.7 * float(d_upl[23][0])) if plan_c36 > 0 else c36 > 0
    ex = L["exec_mvp"] * L["exec_scale_given_mvp"]
    fx = A.FX_UZS_PER_USD
    comp = {}
    for k in ["c_cashback", "c_drops_digital", "c_drops_inventory", "c_weekly", "c_grand", "c_build",
              "c_opex", "c_marketing", "b_retention", "b_ontime", "b_upgrade", "b_pass", "b_engagement", "b_partner"]:
        comp[k] = {"y1": float(det[k][:12].sum()) / 1e9, "y2": float(det[k][12:24].sum()) / 1e9,
                   "y3": float(det[k][24:].sum()) / 1e9, "m24": float(det[k][23][0]) / 1e9}
    # MVP (только MVP, без масштаба): затраты за мес. 2–7
    mvp_cost = sim_mvp["cost"][:L["mvp_start"] + L["mvp_months"] - 1].sum(0)
    det_mvp = simulate_loyalty(det=True, scale=False)
    mvp_comp = {k: float(det_mvp[k][:L["mvp_start"] + L["mvp_months"] - 1].sum()) / 1e9
                for k in ["c_cashback", "c_drops_digital", "c_drops_inventory", "c_weekly", "c_grand",
                          "c_build", "c_opex", "c_marketing"]}
    members_full = det["full_members"][0]
    m24_cost = float(det["cost"][23][0])
    return {
        "name": L["name"], "exec_prob": ex,
        "members_full_p50": pct(sim["full_members"], 50), "members_full_det": members_full,
        "archive_members_m24": p3(sim["a_members"][23]),
        "cost_y1_bn": p3(sim["cost"][:12].sum(0), 1e9), "cost_y2_bn": p3(sim["cost"][12:24].sum(0), 1e9),
        "cost_y3_bn": p3(sim["cost"][24:].sum(0), 1e9),
        "cost_month_scale_bn": p3(sim["cost"][23], 1e9), "cost_month_scale_musd": p3(sim["cost"][23], 1e6 * fx),
        "cost_per_member_month": m24_cost / det["members"][23][0],
        "benefit_rev_y2_bn": p3(sim["benefit_rev"][12:24].sum(0), 1e9),
        "contrib_24_bn": p3(c24, 1e9), "contrib_36_bn": p3(c36, 1e9),
        "contrib_month24_bn": p3(sim["contrib"][23], 1e9),
        "breakeven_month": p3(be.astype(float)),
        "p_monthly_positive_m24": float(monthly_pos.mean()), "p_c36_pos": float((c36 > 0).mean()),
        "archive_arpu_uplift_m24": p3(a_upl[23]), "archive_arpu_uplift_m36": p3(a_upl[35]),
        "archive_rev_y2_bn": p3(sim["a_rev"][12:24].sum(0), 1e9),
        "p_model": float(succ.mean()), "success_chance": float(succ.mean()) * ex,
        "business_case_chance": float(bc.mean()) * ex,
        "components_det": comp,
        "mvp_cost_bn": p3(mvp_cost, 1e9), "mvp_cost_musd": p3(mvp_cost, 1e6 * fx), "mvp_components_det": mvp_comp,
        "plan_contrib_36_bn": plan_c36 / 1e9,
    }


def portfolio(sims, loy, n=A.N_SIMS):
    rng = np.random.default_rng(A.SEED + 5)
    hc = tri(rng, A.PORTFOLIO_OVERLAP_HAIRCUT, n)
    rev = np.zeros((H, n))
    dsubs = np.zeros((H, n))
    contrib = np.zeros((H, n))
    for k, s in sims.items():
        on = rng.random(n) < A.INITIATIVES[k]["exec_prob"]
        rev += s["rev"] * on * (1 - hc)
        dsubs += s["dsubs"] * on * (1 - hc)
        gm = s["contrib"] + s["cost"]
        contrib += (gm * (1 - hc) - s["cost"]) * on
    L = A.LOYALTY
    on_l = rng.random(n) < L["exec_mvp"] * L["exec_scale_given_mvp"]
    rev_a = rev + loy["a_rev"] * on_l
    dsubs_a = dsubs + loy["a_dsubs"] * on_l
    contrib_all = contrib + loy["contrib"] * on_l
    upl, r0, _ = arpu_path(rev_a, dsubs_a)
    upl13, _, _ = arpu_path(rev, dsubs)
    fx = A.FX_UZS_PER_USD
    res = {
        "arpu_uplift_m12": p3(upl[11]), "arpu_uplift_m24": p3(upl[23]), "arpu_uplift_m36": p3(upl[35]),
        "arpu_uplift_m24_i1_3": p3(upl13[23]),
        "archive_rev_y1_bn": p3(rev_a[:12].sum(0), 1e9), "archive_rev_y2_bn": p3(rev_a[12:24].sum(0), 1e9),
        "archive_rev_y3_bn": p3(rev_a[24:].sum(0), 1e9),
        "archive_run_rate_musd": p3(rev_a[23] * 12, 1e6 * fx),
        "contrib_24_bn": p3(contrib_all[:24].sum(0), 1e9), "contrib_36_bn": p3(contrib_all.sum(0), 1e9),
        "p_contrib36_pos": float((contrib_all.sum(0) > 0).mean()),
        "p_uplift_m24_ge": {str(t): float((upl[23] >= t).mean()) for t in (0.05, 0.08, 0.10, 0.12, 0.15)},
        "monthly_uplift_p50": [pct(upl[m], 50) for m in range(H)],
    }
    return res


def threshold_analysis():
    """Стационарный режим масштаба (12 мес. после полного набора), детерминированно."""
    L = A.LOYALTY
    st = loyalty_member_stats()
    pb = prize_budgets()
    members = A.BASE["total_subs"] * mode(L["app_mau_share"]) * mode(L["enroll_of_mau"])
    below = st["below60"]
    above = 1 - below
    c = L["member_churn_base"]
    acc = sum((1 - c) ** k for k in range(12))         # накопление за 12 мес.
    arpu = st["arpu_net"]
    cr = mode(L["churn_reduction"])
    margin = L["margin"]
    a_members = members * mode(L["archive_share_members"])
    a_up_base = mode(L["archive_upgrade_rate_m"])
    a_factor = {"O1": 0.5, "O2": 0.8, "O3": 0.6, "O4": 0.7, "O5": 1.0}
    p_block = {"O1": 0.02, "O2": 0.03, "O3": 0.05, "O4": 0.40, "O5": 0.05}
    rows = {}
    for k, o in A.THRESHOLD_OPTIONS.items():
        eng_w = above + below * o["engagement_below"]
        retention = members * c * cr * eng_w * acc * arpu * margin
        upgrades = members * below * o["upgrade_rate"] * acc * mode(L["upgrade_delta"]) * margin
        pass_rev = members * below * o["pass_adoption"] * o["pass_price"] / (1 + A.VAT) * (1 - L["pass_value_cost"])
        paid = members * below * o["paid_entry_share"] * o["paid_entry_price"] / (1 + A.VAT)
        prizes = (pb["weekly_wins_week"] * WEEKS_PER_MONTH + pb["grand_month"])
        net = retention + upgrades + pass_rev + paid - prizes
        players = members * (above + below * o["play_share_below"])
        a_players = a_members * (0.03 + 0.97 * o["play_share_below"])
        a_upg = a_members * a_up_base * a_factor[k] * acc * mode(L["archive_upgrade_delta"])
        rows[k] = {
            "name": o["name"], "players": players, "players_share": players / members,
            "archive_players_share": a_players / a_members,
            "retention_bn": retention / 1e9, "upgrades_bn": upgrades / 1e9, "pass_bn": pass_rev / 1e9,
            "paid_entry_bn": paid / 1e9, "prizes_bn": prizes / 1e9, "net_bn": net / 1e9,
            "risk_adj_net_bn": net * (1 - p_block[k]) / 1e9, "p_block": p_block[k],
            "archive_upgrade_rev_bn": a_upg / 1e9,
            "odds_weekly": (pb["weekly_items"]) / max(players, 1),
            "legal_risk": o["legal_risk"], "pr_risk": o["pr_risk"],
        }
    return {"members": members, "rows": rows}


LOYALTY_SENS_KEYS = ["upgrade_rate_m", "churn_reduction", "ontime_rev_uplift", "engagement_upsell", "drops_dau_share",
                     "breakage", "redeem_cost_ratio", "enroll_of_mau", "app_mau_share", "opex_m", "pass_adoption",
                     "scale_build", "marketing_m"]


def loyalty_tornado():
    base = float(simulate_loyalty(det=True)["contrib"].sum())
    rows = []
    for k in LOYALTY_SENS_KEYS:
        v = A.LOYALTY[k]
        vals = []
        for side in (0, 2):
            A.LOYALTY[k] = (v[side], v[side], v[side])
            vals.append(float(simulate_loyalty(det=True)["contrib"].sum()))
            A.LOYALTY[k] = v
        rows.append({"param": k, "low": vals[0] / 1e9, "high": vals[1] / 1e9, "swing": abs(vals[1] - vals[0]) / 1e9})
    rows.sort(key=lambda r: -r["swing"])
    return {"base_bn": base / 1e9, "rows": rows}


def ab_n_prop(p1, p2):
    pb = (p1 + p2) / 2
    return math.ceil((1.96 * math.sqrt(2 * pb * (1 - pb)) + 0.8416 * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
                     / (p2 - p1) ** 2)


def ab_n_mean(cv, mde):
    return math.ceil(2 * (1.96 + 0.8416) ** 2 * cv ** 2 / mde ** 2)


def sp(x, f="{:,.0f}"):
    """Число с пробелом-разделителем тысяч и запятой-десятичной (рус.)."""
    return f.format(x).replace(",", " ").replace(".", ",")


def fr(v, f="{:,.1f}"):
    return f"{sp(v[1], f)} ({sp(v[0], f)} … {sp(v[2], f)})"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    N, arpu0 = cohort()
    keys = list(A.INITIATIVES)
    sims = {k: simulate_initiative(k) for k in keys}
    dets = {k: simulate_initiative(k, det=True) for k in keys}
    res = {k: summarize_initiative(k, sims[k], dets[k]) for k in keys}
    loy = simulate_loyalty()
    loy_det = simulate_loyalty(det=True)
    loy_mvp = simulate_loyalty(scale=False)
    lres = summarize_loyalty(loy, loy_det, loy_mvp)
    port = portfolio(sims, loy)
    th = threshold_analysis()
    torn = loyalty_tornado()
    pb = prize_budgets()
    st = loyalty_member_stats()
    ab = {
        "MVP: отток участников 1,2% → 1,0% (−17%)": ab_n_prop(0.012, 0.010),
        "MVP: доля оплат вовремя 85% → 87%": ab_n_prop(0.85, 0.87),
        "MVP: переход на ТП ≥ 60 тыс. 0,3% → 0,6% за 3 мес.": ab_n_prop(0.003, 0.006),
        "MVP: ARPU участников +2% (CV 1,2)": ab_n_mean(1.2, 0.02),
        "I2 More-for-More: ARPU +3% (CV 1,2)": ab_n_mean(1.2, 0.03),
        "I1/I2 guardrail: отток 1,5% → 2,0%": ab_n_prop(0.015, 0.020),
    }
    # детерминированный план портфеля (все запущены, перекрытие на моде)
    h = mode(A.PORTFOLIO_OVERLAP_HAIRCUT)
    rev_plan = sum(d["rev"] for d in dets.values()) * (1 - h) + loy_det["a_rev"]
    ds_plan = sum(d["dsubs"] for d in dets.values()) * (1 - h) + loy_det["a_dsubs"]
    plan_upl, _, _ = arpu_path(rev_plan, ds_plan)
    plan = {"arpu_uplift_m12": float(plan_upl[11][0]), "arpu_uplift_m24": float(plan_upl[23][0]),
            "arpu_uplift_m36": float(plan_upl[35][0])}

    out = {"base": {"cohort": N, "arpu0": arpu0, "annual_rev_bn": N * arpu0 * 12 / 1e9},
           "initiatives": res, "loyalty": lres, "portfolio": port, "plan": plan,
           "threshold": th, "prizes": pb, "member_stats": st, "ab": ab, "loyalty_tornado": torn}
    with open(os.path.join(OUT_DIR, "results_v2.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=float)

    Lm = []
    Lm.append("# v2 — результаты модели (Монте-Карло, 20 000 прогонов, горизонт 36 мес.)\n")
    Lm.append("> `python v2/model/model_v2.py`. Млрд сум без НДС. Формат **P50 (P10 … P90)**. M1 = ноябрь 2026.\n")
    Lm.append(f"Архивная когорта: **{sp(N/1e6, '{:.2f}')} млн**, ARPU **{sp(arpu0)} сум**, выручка {sp(N*arpu0*12/1e9)} млрд/год.\n")
    Lm.append("## Инициативы 1–3 (архивная когорта)\n")
    Lm.append("| # | Инициатива | Старт | Выручка Y1 | Выручка Y2 | Вклад 24м | ΔARPU (12 мес. после старта) | P(запуск) | **Шанс успеха** | Шанс ≥70% плана |")
    Lm.append("|---|---|---|---|---|---|---|---|---|---|")
    for k in keys:
        r = res[k]
        Lm.append(f"| {k} | {r['short']} | M{r['first_month']} | {fr(r['rev_y1_bn'])} | {fr(r['rev_y2_bn'])} | "
                  f"{fr(r['contrib_24_bn'])} | {fr([x*100 for x in r['arpu_uplift_eval']], '{:.1f}%')} | "
                  f"{r['exec_prob']*100:.0f}% | **{r['success_chance']*100:.0f}%** | {r['business_case_chance']*100:.0f}% |")
    Lm.append("\n## I4 Loyalty program\n")
    l = lres
    Lm.append(f"- Участников при полном масштабе: **{sp(l['members_full_p50']/1e6, '{:.2f}')} млн** (план {sp(l['members_full_det']/1e6, '{:.2f}')} млн); архивных участников к M24: {fr([x/1e3 for x in l['archive_members_m24']], '{:,.0f}')} тыс.")
    Lm.append(f"- Средняя ставка кэшбэка: {sp(st['avg_cb_rate']*100, '{:.2f}')}% от АП; начисляется {sp(st['earn'])} монет/участник/мес.")
    Lm.append(f"- Бюджет MVP (3 мес., {sp(A.LOYALTY['mvp_participants'])} участников, вкл. разработку): **{fr(l['mvp_cost_bn'])} млрд сум** ≈ ${fr(l['mvp_cost_musd'], '{:.2f}')} млн")
    Lm.append(f"- Затраты программы в месяц при масштабе (M24): **{fr(l['cost_month_scale_bn'], '{:.2f}')} млрд сум** ≈ ${fr(l['cost_month_scale_musd'], '{:.2f}')} млн; на участника {sp(l['cost_per_member_month'])} сум/мес.")
    Lm.append(f"- Затраты Y1 / Y2 / Y3: {fr(l['cost_y1_bn'])} / {fr(l['cost_y2_bn'])} / {fr(l['cost_y3_bn'])} млрд")
    Lm.append(f"- Вклад программы за 24 мес.: {fr(l['contrib_24_bn'])} млрд; за 36 мес.: **{fr(l['contrib_36_bn'])} млрд**; P(36м > 0) = {l['p_c36_pos']*100:.0f}%")
    Lm.append(f"- Месячный вклад на M24: {fr(l['contrib_month24_bn'], '{:.2f}')} млрд; P(> 0) = {l['p_monthly_positive_m24']*100:.0f}%; точка окупаемости (накоп.): месяц {fr(l['breakeven_month'], '{:.0f}')}")
    Lm.append(f"- Вклад в ARPU архивной когорты: M24 {fr([x*100 for x in l['archive_arpu_uplift_m24']], '{:.2f}%')}, M36 {fr([x*100 for x in l['archive_arpu_uplift_m36']], '{:.2f}%')}")
    Lm.append(f"- P(запуск MVP и масштаба) = {l['exec_prob']*100:.0f}%; **шанс успеха {l['success_chance']*100:.0f}%**; ≥70% плана — {l['business_case_chance']*100:.0f}%\n")
    Lm.append("| Компонент (план) | Y1 | Y2 | Y3 | Месяц 24 |")
    Lm.append("|---|---|---|---|---|")
    names = {"c_cashback": "Кэшбэк (себестоимость погашений)", "c_drops_digital": "Daily Drops — цифровые призы",
             "c_drops_inventory": "Daily Drops — инвентарь", "c_weekly": "Weekly Wins", "c_grand": "Monthly Grand",
             "c_build": "Разработка (MVP + масштаб)", "c_opex": "Операционные затраты", "c_marketing": "Маркетинг",
             "b_retention": "Эффект: удержание (выручка)", "b_ontime": "Эффект: оплаты вовремя",
             "b_upgrade": "Эффект: переходы на ТП ≥ 60 тыс.", "b_pass": "Эффект: Club+ Pass",
             "b_engagement": "Эффект: допродажи в приложении", "b_partner": "Эффект: платные размещения партнёров"}
    for k, v in l["components_det"].items():
        Lm.append(f"| {names[k]} | {sp(v['y1'], '{:.2f}')} | {sp(v['y2'], '{:.2f}')} | {sp(v['y3'], '{:.2f}')} | {sp(v['m24'], '{:.3f}')} |")
    Lm.append("\n### Призовые фонды (масштаб)\n")
    Lm.append(f"- Weekly Wins: {sp(pb['weekly_wins_week']/1e6, '{:,.1f}')} млн сум/нед. ({sp(pb['weekly_items'])} призов) ≈ {sp(pb['weekly_wins_week']*WEEKS_PER_MONTH/1e6)} млн/мес.")
    Lm.append(f"- Daily Drops инвентарь: {sp(pb['drops_inventory_week']/1e6, '{:,.1f}')} млн сум/нед. ({sp(pb['drops_items'])} ед.) ≈ {sp(pb['drops_inventory_week']*WEEKS_PER_MONTH/1e6)} млн/мес.")
    Lm.append(f"- Daily Drops цифровые: {sp(pb['drop_digital_cost'], '{:.1f}')} сум за открытие (сумма вероятностей {pb['drop_prob_sum']*100:.0f}%)")
    Lm.append(f"- Monthly Grand: {sp(pb['grand_year']/1e9, '{:.2f}')} млрд сум/год + {A.GRAND_OVERHEAD*100:.0f}% накладные ≈ {sp(pb['grand_month']/1e6, '{:.1f}')} млн/мес.")
    Lm.append("\n## Порог участия: сравнение вариантов (стационарный режим, млн сум/мес)\n")
    Lm.append("| Вариант | Играют в Weekly/Monthly | Архивных играют | Удержание | Переходы | Pass / платный вход | Призы | **Чистый эффект** | С поправкой на риск запрета | Юр. риск | PR-риск |")
    Lm.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for k, r in th["rows"].items():
        Lm.append(f"| {k} {r['name']} | {r['players_share']*100:.0f}% | {r['archive_players_share']*100:.0f}% | {sp(r['retention_bn']*1e3)} | "
                  f"{sp(r['upgrades_bn']*1e3)} | {sp((r['pass_bn']+r['paid_entry_bn'])*1e3)} | −{sp(r['prizes_bn']*1e3)} | "
                  f"**{sp(r['net_bn']*1e3)}** | {sp(r['risk_adj_net_bn']*1e3)} | {r['legal_risk']} | {r['pr_risk']} |")
    Lm.append("\n## Портфель (архивная когорта, с учётом P(запуска) и перекрытия)\n")
    p = port
    Lm.append(f"- ΔARPU когорты: M12 **{fr([x*100 for x in p['arpu_uplift_m12']], '{:.1f}%')}**, M24 **{fr([x*100 for x in p['arpu_uplift_m24']], '{:.1f}%')}**, M36 {fr([x*100 for x in p['arpu_uplift_m36']], '{:.1f}%')}")
    Lm.append(f"- Из них инициативы 1–3 на M24: {fr([x*100 for x in p['arpu_uplift_m24_i1_3']], '{:.1f}%')}")
    Lm.append(f"- План (всё запущено): M12 {sp(plan['arpu_uplift_m12']*100, '{:.1f}')}%, M24 {sp(plan['arpu_uplift_m24']*100, '{:.1f}')}%, M36 {sp(plan['arpu_uplift_m36']*100, '{:.1f}')}%")
    Lm.append(f"- Доп. выручка архивной когорты Y1 / Y2 / Y3: {fr(p['archive_rev_y1_bn'])} / {fr(p['archive_rev_y2_bn'])} / {fr(p['archive_rev_y3_bn'])} млрд; run-rate M24 ≈ ${fr(p['archive_run_rate_musd'])} млн/год")
    Lm.append(f"- Вклад портфеля (вкл. всю Loyalty) 24м: {fr(p['contrib_24_bn'])} млрд; 36м: **{fr(p['contrib_36_bn'])} млрд**; P(36м > 0) = {p['p_contrib36_pos']*100:.0f}%")
    Lm.append("- P(ΔARPU ≥ X) на M24: " + ", ".join(f"≥{float(t)*100:.0f}% — **{v*100:.0f}%**" for t, v in p["p_uplift_m24_ge"].items()))
    Lm.append("\n## Чувствительность Loyalty (вклад за 36 мес., млрд сум)\n")
    Lm.append(f"База (план): {sp(torn['base_bn'], '{:.1f}')}\n")
    Lm.append("| Параметр | При минимуме | При максимуме | Размах |")
    Lm.append("|---|---|---|---|")
    for r in torn["rows"][:10]:
        Lm.append(f"| {r['param']} | {sp(r['low'], '{:.1f}')} | {sp(r['high'], '{:.1f}')} | {sp(r['swing'], '{:.1f}')} |")
    Lm.append("\n## Размеры выборок (α 5%, мощность 80%)\n")
    Lm.append("| Тест | N на группу |")
    Lm.append("|---|---|")
    for t, v in ab.items():
        Lm.append(f"| {t} | {sp(v)} |")
    with open(os.path.join(OUT_DIR, "results_v2.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(Lm) + "\n")
    print("\n".join(Lm))


if __name__ == "__main__":
    main()
