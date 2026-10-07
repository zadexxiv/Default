"""
v2: допущения для 4 инициатив роста ARPU архивной базы Ucell.

  I1  Sunset / Migration старых неэффективных линеек → актуальные ТП дороже на 10–15%
  I2  More-for-More: + абонплата, + трафик для когорты линеек
  I3  Пакеты для тех, кто исчерпывает трафик + промо роуминг-пакетов (I3a + I3b)
  I4  Loyalty program (кэшбэк, Daily Drops, Weekly Wins, Monthly Grand) — MVP → масштаб

HYPOTHESIS — рабочие гипотезы до получения данных (см. v2/docs/12_data_request_for_analysts.md).
Деньги — сумы (UZS); выручка/ARPU — без НДС 12%, цены «на витрине» — с НДС.
Тройки (min, mode, max) — треугольные распределения для Монте-Карло.
Месяц 1 программы = ноябрь 2026.
"""

VAT = 0.12
FX_UZS_PER_USD = 12_100
HORIZON_MONTHS = 36
N_SIMS = 20_000
SEED = 7

M = 1_000_000
B = 1_000_000_000

BASE = {
    "total_subs": 11_000_000,          # Ucell, начало 2026
    "archive_share": 0.40,             # HYPOTHESIS
    "archive_active_ratio": 0.80,      # HYPOTHESIS
    "archive_arpu": 18_500,            # HYPOTHESIS, net
    "monthly_churn": 0.015,            # HYPOTHESIS: архивная когорта
    "market_total_subs": 36_500_000,   # HYPOTHESIS
}

# ---------------------------------------------------------------------------
# Инициативы 1–3 (архивная когорта). Типы:
#   reprice  — изменение условий ТП целевой группы волнами: stay / upsell / downgrade / churn
#   adoption — добровольное принятие оффера
# ---------------------------------------------------------------------------
INITIATIVES = {
    "I1": {
        "name": "Sunset / Migration старых неэффективных линеек → ТП дороже на 10–15%",
        "short": "Sunset / Migration",
        "type": "reprice", "complexity": 4,
        "segment_arpu": 16_000,                  # ARPU мигрируемых линеек, net
        "eligible_share": (0.25, 0.30, 0.40),    # доля когорты на «неэффективных» линейках (без соцгруппы)
        "price_up_pct": (0.10, 0.125, 0.15),     # новый ТП дороже текущей абонплаты
        "base_fee_gross": 20_000,                # средняя абонплата мигрируемых линеек с НДС
        "upsell_share": (0.08, 0.12, 0.20),      # выбирают ТП крупнее, чем mapped
        "upsell_delta": (6_000, 10_000, 15_000), # доп. net ARPU у выбравших крупнее
        "downgrade": (0.04, 0.08, 0.14),         # уходят на ТП дешевле (смена бесплатна)
        "downgrade_delta": (-4_000, -2_000, 0),
        "churn_incr": (0.015, 0.030, 0.050),
        "data_cost_m": (100, 300, 600),
        "cost_per_contact": 200,
        "opex_savings_m": (30 * M, 60 * M, 120 * M),   # упрощение каталога/биллинга
        "one_time": (3 * B, 5 * B, 8 * B),
        "opex_m": 30 * M,
        "margin": 1.0,
        "waves": [(6, 0.5), (9, 0.5)],           # апрель и июль 2027
        "exec_prob": 0.65,
    },
    "I2": {
        "name": "More-for-More: + абонплата и + трафик для когорты недооценённых линеек",
        "short": "More-for-More",
        "type": "reprice", "complexity": 1,
        "segment_arpu": 21_000,
        "eligible_share": (0.18, 0.22, 0.26),
        "price_up_gross": (4_000, 5_000, 6_000),
        "upsell_share": (0.0, 0.0, 0.0),
        "upsell_delta": (0, 0, 0),
        "downgrade": (0.04, 0.08, 0.15),
        "downgrade_delta": (-6_000, -3_000, 0),
        "churn_incr": (0.010, 0.025, 0.050),
        "data_cost_m": (200, 400, 800),
        "cost_per_contact": 100,
        "opex_savings_m": (0, 0, 0),
        "one_time": (200 * M, 300 * M, 500 * M),
        "opex_m": 20 * M,
        "margin": 1.0,
        "waves": [(2, 0.1), (4, 0.9)],           # пилот 10% в декабре, масштаб в феврале
        "exec_prob": 0.80,
    },
    "I3a": {
        "name": "Пакет-бустер для исчерпывающих трафик (opt-in автопродление)",
        "short": "Бустер при исчерпании",
        "type": "adoption", "complexity": 2, "group": "I3",
        "segment_arpu": 28_000,
        "eligible_share": (0.10, 0.15, 0.20),
        "reach": (0.85, 0.90, 0.95),
        "takeup": (0.08, 0.12, 0.18),
        "cannibal": (0.30, 0.45, 0.60),
        "delta": (5_000, 7_500, 12_000),
        "churn_incr": (0.0, 0.0, 0.002),
        "churn_red": (0.00, 0.05, 0.10),
        "cost_per_contact": 50,
        "cost_per_adopter_once": (0, 0, 0),
        "var_cost_m": 500,
        "one_time": (250 * M, 350 * M, 550 * M),
        "opex_m": 10 * M,
        "margin": 0.85, "launch": 2, "ramp": 2, "exec_prob": 0.90,
    },
    "I3b": {
        "name": "Роуминг-пакет по акции (−50% первый месяц) для выезжающих",
        "short": "Роуминг-промо",
        "type": "adoption", "complexity": 2, "group": "I3",
        "segment_arpu": 15_000,
        "eligible_share": (0.04, 0.06, 0.08),
        "reach": (0.70, 0.80, 0.88),
        "takeup": (0.12, 0.20, 0.30),
        "cannibal": (0.15, 0.25, 0.35),
        "delta": (3_000, 7_000, 12_000),
        "churn_incr": (0.0, 0.0, 0.0),
        "churn_red": (0.10, 0.20, 0.35),
        "cost_per_contact": 150,
        "cost_per_adopter_once": (4_000, 6_000, 9_000),   # скидка 50% первого месяца
        "var_cost_m": 0,
        "one_time": (100 * M, 150 * M, 250 * M),
        "opex_m": 10 * M,
        "margin": 0.60, "launch": 2, "ramp": 3, "exec_prob": 0.90,
    },
}

PORTFOLIO_OVERLAP_HAIRCUT = (0.05, 0.10, 0.15)

# ---------------------------------------------------------------------------
# I4 Loyalty program
# ---------------------------------------------------------------------------
# Распределение участников по абонплате (HYPOTHESIS, запрос L2). fee — средняя АП с НДС.
# cb — ставка кэшбэка, entries — шансы в Weekly/Monthly на неделю (рекомендуемая схема O5).
BANDS = {
    "lt30":  {"name": "АП < 30 тыс.",    "member_share": 0.30, "archive_share": 0.80, "fee": 22_000, "cb": 0.03, "entries": 1},
    "30_59": {"name": "АП 30–59 тыс.",   "member_share": 0.40, "archive_share": 0.17, "fee": 45_000, "cb": 0.03, "entries": 2},
    "60_79": {"name": "АП 60–79 тыс.",   "member_share": 0.18, "archive_share": 0.02, "fee": 70_000, "cb": 0.04, "entries": 3},
    "ge80":  {"name": "АП ≥ 80 тыс.",    "member_share": 0.12, "archive_share": 0.01, "fee": 100_000, "cb": 0.05, "entries": 5},
}

LOYALTY = {
    "name": "Loyalty program: кэшбэк 3–5% + Daily Drops + Weekly Wins + Monthly Grand",
    "short": "Loyalty program",
    # охват
    "app_mau_share": (0.22, 0.27, 0.32),        # HYPOTHESIS: MAU приложения / база
    "enroll_of_mau": (0.35, 0.50, 0.60),        # вступили в программу при полном масштабе
    "archive_share_members": (0.15, 0.20, 0.25),
    "mvp_participants": 150_000,
    "mvp_start": 5, "mvp_months": 3,            # март–май 2027
    "scale_start": 11, "scale_ramp": 6,         # сентябрь 2027, набор 6 мес.
    # кэшбэк
    "ontime_share": (0.80, 0.85, 0.90),
    "breakage": (0.25, 0.30, 0.40),             # не потрачено (сгорает через 12 мес.)
    "redeem_cost_ratio": (0.45, 0.515, 0.60),   # 50% свои услуги ×0,15 + 30% оплата счёта ×1 + 20% мерч/партнёры ×0,7
    # Daily Drops
    "drops_dau_share": (0.20, 0.30, 0.40),      # ежедневно открывают сундук
    "drop_digital_cost": (35, 52.5, 70),        # ожидаемая себестоимость цифрового приза за открытие, сум
    "drops_inventory_week": (60 * M, 82 * M, 110 * M),   # физические/партнёрские призы, неделя
    # розыгрыши
    "weekly_wins_week": (35 * M, 45.5 * M, 60 * M),
    "monthly_grand": (70 * M, 88 * M, 120 * M),          # в среднем в месяц (авто, путешествия, умра)
    "mvp_prize_share": 0.30,                             # призовые фонды MVP = 30% от масштаба
    # затраты платформы
    "mvp_build": (1.0 * B, 1.8 * B, 3.0 * B),
    "scale_build": (2.0 * B, 3.0 * B, 5.0 * B),
    "opex_m": (180 * M, 250 * M, 350 * M),               # команда, лицензии, фулфилмент, КЦ
    "mvp_opex_m": (80 * M, 120 * M, 180 * M),
    "marketing_m": (100 * M, 150 * M, 250 * M),
    "launch_marketing": (1.0 * B, 1.5 * B, 2.5 * B),
    "mvp_marketing": (150 * M, 250 * M, 400 * M),
    # эффекты (участники всей базы Ucell)
    "member_churn_base": 0.012,
    "churn_reduction": (0.08, 0.15, 0.25),      # T-Mobile Tuesdays: −27% (с самоотбором) → берём консервативно
    "ontime_rev_uplift": (0.005, 0.015, 0.025),
    "upgrade_rate_m": (0.0015, 0.004, 0.008),   # доп. переходы на ТП ≥ 60 тыс. среди участников < 60 тыс. (гипотеза H1 MVP)
    "upgrade_delta": (12_000, 20_000, 28_000),
    "pass_adoption": (0.02, 0.03, 0.05),        # Club+ Pass среди участников < 60 тыс.
    "pass_price_gross": 9_999,
    "pass_value_cost": 0.25,                    # себестоимость ГБ/бонусов внутри Pass
    "engagement_upsell": (0.004, 0.008, 0.015), # доп. покупки пакетов через приложение
    "partner_cash_m": (0, 50 * M, 150 * M),     # платные размещения партнёров, с scale_start+6
    "margin": 0.85,
    # архивная когорта внутри программы
    "archive_member_arpu": 22_000,
    "archive_churn_base": 0.015,
    "archive_upgrade_rate_m": (0.002, 0.004, 0.008),     # переход на актуальный ТП ради бонусов/шансов
    "archive_upgrade_delta": (8_000, 12_000, 18_000),
    # исполнение
    "exec_mvp": 0.85,
    "exec_scale_given_mvp": 0.75,
}

# Каталог призов (цены — ориентиры октябрь 2026, уточнить у закупок; источники в docs/04)
PRIZES = {
    "car_onix":      {"name": "Chevrolet Onix 1LS MT", "price": 176_900_000, "src": "kursiv.media, 04/2026"},
    "car_cobalt":    {"name": "Chevrolet Cobalt", "price": 146_455_000, "src": "kursiv.media, 04/2026"},
    "trip_turkey2":  {"name": "Путешествие в Турцию на двоих (7 ночей)", "price": 32_000_000, "src": "оценка ~$2 600"},
    "umrah2":        {"name": "Умра на двоих", "price": 50_000_000, "src": "оценка ~$2 000/чел."},
    "domestic_trip2": {"name": "Самарканд–Бухара–Хива на двоих (Afrosiyob + отель)", "price": 7_000_000, "src": "оценка"},
    "iphone17":      {"name": "iPhone 17 256 ГБ", "price": 12_500_000, "src": "оценка, OLX/ритейл 11,3–13 млн"},
    "galaxy_a":      {"name": "Samsung Galaxy A (A36/A56)", "price": 4_500_000, "src": "оценка"},
    "tablet":        {"name": "Планшет Samsung Galaxy Tab A9+", "price": 3_000_000, "src": "оценка"},
    "airpods":       {"name": "AirPods 4", "price": 2_000_000, "src": "оценка (MSRP $129 + импорт)"},
    "jbl":           {"name": "Наушники JBL Tune", "price": 700_000, "src": "оценка"},
    "concert_pair":  {"name": "2 билета на концерт", "price": 1_200_000, "src": "оценка"},
    "cinema_pair":   {"name": "2 билета в кино", "price": 160_000, "src": "Premier Cinema 80–100 тыс./билет"},
    "hoodie":        {"name": "Худи с принтом (мерч)", "price": 160_000, "src": "OLX: DTF-печать 100–180 тыс."},
    "cap":           {"name": "Кепка / шоппер", "price": 60_000, "src": "оценка"},
    "powerbank":     {"name": "Power bank 10 000 мА·ч", "price": 180_000, "src": "оценка"},
    "free_year":     {"name": "Год связи бесплатно (АП 100 тыс./мес)", "price": 1_200_000, "src": "расчёт"},
    "data_5gb":      {"name": "5 ГБ интернета (себестоимость)", "price": 1_250, "src": "~250 сум/ГБ маржинально"},
    "partner_voucher": {"name": "Ваучер партнёра (номинал 100 тыс.)", "price": 100_000, "src": "100% финансирует партнёр"},
}

# Еженедельный фонд Weekly Wins (масштаб): (приз, кол-во в неделю, доля софинансирования партнёром)
WEEKLY_WINS = [
    ("iphone17", 1, 0.0),
    ("tablet", 2, 0.0),
    ("airpods", 5, 0.0),
    ("concert_pair", 10, 0.5),
    ("cinema_pair", 30, 0.5),
    ("galaxy_a", 1, 0.0),        # Premium-пул (АП ≥ 80 тыс.)
    ("jbl", 5, 0.0),             # Premium-пул
    ("data_5gb", 1000, 0.0),     # массовый уровень: чтобы выигрывали многие
    ("partner_voucher", 300, 1.0),
]
# Еженедельный инвентарь Daily Drops (масштаб)
DROPS_INVENTORY = [
    ("cinema_pair", 500, 0.5),   # 1 000 билетов
    ("hoodie", 100, 0.0),
    ("cap", 60, 0.0),
    ("powerbank", 40, 0.0),
    ("jbl", 20, 0.0),
    ("galaxy_a", 2, 0.0),
]
# Monthly Grand на 12 месяцев (масштаб)
MONTHLY_GRAND = ["car_onix", "trip_turkey2", "umrah2", "car_onix", "trip_turkey2", "iphone17_x5",
                 "car_onix", "trip_turkey2", "free_year_x10", "car_onix", "trip_turkey2", "umrah2"]
GRAND_OVERHEAD = 0.10   # логистика, нотариус/комиссия, оформление, резерв на налоги

# Daily Drops: цифровые призы на одно открытие (вероятность, себестоимость, комментарий)
DROP_TABLE = [
    ("30–100 Ucell Coins", 0.50, 23.0, "65 монет × 70% погашения × 0,515 себестоимости"),
    ("300 МБ – 1 ГБ интернета", 0.25, 150.0, "0,6 ГБ × ~250 сум/ГБ маржинальной себестоимости"),
    ("30 мин внутри сети / безлимит мессенджеров на сутки", 0.07, 40.0, ""),
    ("Купон партнёра (−10…30%)", 0.14, 5.0, "финансирует партнёр, наша стоимость — платформа"),
    ("Жетон серии: +1 шанс в Weekly Wins", 0.02, 0.0, "только шанс"),
    ("Слот инвентаря (кино, мерч, наушники, смартфон)", 0.02, 0.0, "лимит в неделю, бюджет — отдельной строкой"),
]

# Варианты порога участия (анализ win-win), стационарный режим масштаба
THRESHOLD_OPTIONS = {
    "O1": {"name": "Открыто всем (без порога)", "play_share_below": 1.0, "engagement_below": 1.00,
           "upgrade_rate": 0.0020, "pass_adoption": 0.0, "pass_price": 0, "paid_entry_share": 0.0,
           "paid_entry_price": 0, "legal_risk": "низкий", "pr_risk": "низкий"},
    "O2": {"name": "Weekly/Monthly только АП ≥ 60 тыс. и оплата вовремя", "play_share_below": 0.0, "engagement_below": 0.70,
           "upgrade_rate": 0.0036, "pass_adoption": 0.0, "pass_price": 0, "paid_entry_share": 0.0,
           "paid_entry_price": 0, "legal_risk": "низкий", "pr_risk": "средний"},
    "O3": {"name": "Weekly/Monthly только АП ≥ 80 тыс.", "play_share_below": 0.0, "engagement_below": 0.60,
           "upgrade_rate": 0.0024, "pass_adoption": 0.0, "pass_price": 0, "paid_entry_share": 0.0,
           "paid_entry_price": 0, "legal_risk": "низкий", "pr_risk": "высокий"},
    "O4": {"name": "Порог 60 тыс. + платный вход 4 999 / 9 999 сум для остальных", "play_share_below": 0.04, "engagement_below": 0.80,
           "upgrade_rate": 0.0028, "pass_adoption": 0.0, "pass_price": 0, "paid_entry_share": 0.04,
           "paid_entry_price": 7_500, "legal_risk": "ВЫСОКИЙ (платный шанс = лотерея, лицензия НАПП)", "pr_risk": "высокий"},
    "O5": {"name": "РЕКОМЕНДУЕМ: играют все, шансы растут с АП + Club+ Pass с реальной ценностью", "play_share_below": 1.0,
           "engagement_below": 1.00, "upgrade_rate": 0.0050, "pass_adoption": 0.03, "pass_price": 9_999,
           "paid_entry_share": 0.0, "paid_entry_price": 0, "legal_risk": "низкий–средний (Pass ≥ своей цены по ценности)",
           "pr_risk": "низкий"},
}
