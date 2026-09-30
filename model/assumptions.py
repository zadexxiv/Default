"""
Допущения модели роста ARPU архивной базы Ucell.

ВАЖНО: все значения с пометкой HYPOTHESIS — рабочие гипотезы для первичной оценки.
Их нужно заменить фактическими данными (см. docs/09_data_request_for_analysts.md),
после чего перезапустить `python model/arpu_model.py` и `python model/build_excel.py`.

Денежные значения — в сумах (UZS) БЕЗ НДС (12%), т.е. в той же базе, что и выручка/ARPU
в отчётности. Цены «на витрине» указаны с НДС и переводятся в net через VAT.

Распределения параметров задаются тройками (min, mode, max) для треугольного
распределения. Диапазоны откалиброваны по международным и локальным бенчмаркам
(docs/02_market_benchmarks.md).
"""

VAT = 0.12                      # НДС Узбекистана
FX_UZS_PER_USD = 12_100         # курс ЦБ РУз, 2026 (≈11 950–12 205)
HORIZON_MONTHS = 24             # горизонт оценки
N_SIMS = 20_000                 # число прогонов Монте-Карло
SEED = 42

BASE = {
    "total_subs": 11_000_000,          # Ucell, начало 2026 (>10,9 млн по открытым данным)
    "archive_share": 0.40,             # HYPOTHESIS: доля абонентов на архивных ТП
    "archive_active_ratio": 0.80,      # HYPOTHESIS: доля активных (доход за 30 дн.) среди архивных
    "monthly_churn": 0.015,            # HYPOTHESIS: месячный отток архивной базы
    "market_total_subs": 36_500_000,   # HYPOTHESIS: рынок РУз (35,6 млн на конец 2024 + рост)
    "ucell_market_share": 0.304,       # Opensignal, сен-2025
}

# Сегменты архивной базы (HYPOTHESIS — проверить кластеризацией на данных)
# share — доля активной архивной базы; arpu — net ARPU, сум/мес
SEGMENTS = {
    "S1": {"name": "Спящие / почти нулевые (2-я SIM, ARPU<5k)", "share": 0.20, "arpu": 3_000},
    "S2": {"name": "PAYG / голосовые, много кнопочных 2G/3G", "share": 0.20, "arpu": 10_000},
    "S3": {"name": "Недооценённые старые пакеты (платят мало, потребляют много)", "share": 0.30, "arpu": 21_000},
    "S4": {"name": "Старые пакеты mid/high + докупка пакетов", "share": 0.20, "arpu": 40_000},
    "S5": {"name": "Социально защищённые (жен. 55+, муж. 60+)", "share": 0.10, "arpu": 16_000},
}

# ---------------------------------------------------------------------------
# Инициативы. Типы механики:
#   adoption — абоненты добровольно принимают оффер (миграция/допродажа)
#   reprice  — изменение условий ТП для всей целевой группы (stay / downgrade / churn)
#   relative — относительный прирост выручки всей базы (платформенные эффекты)
# Общие поля:
#   group: EASY / HARD; complexity: 1..5 (биллинг/интеграции)
#   launch: месяц старта эффекта (1 = первый месяц программы); ramp: мес. до полного охвата
#   one_time: разовые затраты (UZS, тройка); opex_m: ежемесячные затраты (UZS)
#   margin: маржинальность инкрементальной выручки (после прямых затрат сети/партнёров)
#   optional: True — опция вне базового портфеля (входит в Stretch)
#   not_recommended: True — оценена, но не входит ни в один портфель
#   exec_prob: вероятность запуска «как задумано» (биллинг, интеграции, регуляторика) —
#              экспертная оценка, обоснование в docs/05_success_probability.md
# ---------------------------------------------------------------------------
M = 1_000_000
B = 1_000_000_000

INITIATIVES = {
    # ============================ EASY ============================
    "A1": {
        "name": "«Ucell 30 — Upgrade»: мягкая миграция с подарком",
        "group": "EASY", "complexity": 1, "type": "adoption",
        "segment_arpu": 21_000,
        "eligible_share": (0.40, 0.46, 0.52),   # S3 + ½ S4 + смартфонная часть S2
        "reach": (0.75, 0.85, 0.92),
        "takeup": (0.06, 0.12, 0.20),           # бенчмарк: 10% базы за <3 мес (Ближний Восток)
        "cannibal": (0.10, 0.20, 0.35),         # сами бы перешли (органическая миграция)
        "delta": (3_000, 6_500, 11_000),        # прирост net ARPU на мигранта
        "churn_incr": (0.000, 0.002, 0.006),
        "churn_red": (0.00, 0.10, 0.20),
        "cost_per_contact": 150,
        "cost_per_adopter_once": (1_000, 2_000, 4_000),  # подарочные ГБ (себестоимость)
        "var_cost_m": 0,
        "one_time": (300 * M, 400 * M, 600 * M),
        "opex_m": 30 * M,
        "margin": 0.85, "launch": 2, "ramp": 4, "exec_prob": 0.92,
    },
    "A2": {
        "name": "Точечная индексация недооценённых архивных ТП (more-for-more)",
        "group": "EASY", "complexity": 1, "type": "reprice",
        "segment_arpu": 21_000,
        "eligible_share": (0.18, 0.22, 0.26),   # S3 без соцгруппы и без ТП февральской волны 2026
        "price_up_gross": (4_000, 5_000, 6_000),  # +15–20% к абонплате, с НДС
        "downgrade": (0.04, 0.08, 0.15),        # бесплатная смена ТП с 2026 → часть уйдёт вниз
        "downgrade_delta": (-6_000, -3_000, 0),
        "churn_incr": (0.010, 0.025, 0.050),    # AT&T/T-Mobile/Индия: +0,5–3 п.п.
        "data_cost_m": (200, 400, 800),         # себестоимость добавленных ГБ
        "cost_per_contact": 100,
        "one_time": (200 * M, 300 * M, 500 * M),
        "opex_m": 20 * M,
        "margin": 1.0, "launch": 2, "ramp": 1, "exec_prob": 0.80,
    },
    "A3": {
        "name": "PAYG → суточные/недельные микропакеты",
        "group": "EASY", "complexity": 2, "type": "adoption",
        "segment_arpu": 10_000,
        "eligible_share": (0.18, 0.20, 0.22),
        "reach": (0.70, 0.80, 0.88),
        "takeup": (0.08, 0.15, 0.25),
        "cannibal": (0.10, 0.20, 0.30),
        "delta": (-1_500, 2_500, 5_500),        # часть «тяжёлых» PAYG заплатит меньше
        "churn_incr": (0.0, 0.0, 0.002),
        "churn_red": (0.00, 0.05, 0.15),
        "cost_per_contact": 150,
        "cost_per_adopter_once": (0, 500, 1_000),
        "var_cost_m": 300,
        "one_time": (150 * M, 250 * M, 400 * M),
        "opex_m": 15 * M,
        "margin": 0.85, "launch": 2, "ramp": 3, "exec_prob": 0.90,
    },
    "A4": {
        "name": "Smart add-on: пакет-«бустер» в момент исчерпания (opt-in автопродление)",
        "group": "EASY", "complexity": 2, "type": "adoption",
        "segment_arpu": 28_000,
        "eligible_share": (0.10, 0.15, 0.20),   # исчерпывают пакет ежемесячно (S3+S4)
        "reach": (0.85, 0.90, 0.95),
        "takeup": (0.08, 0.12, 0.18),
        "cannibal": (0.30, 0.45, 0.60),         # часть и так докупает вручную
        "delta": (5_000, 7_500, 12_000),        # цена бустера net × частота
        "churn_incr": (0.0, 0.0, 0.002),
        "churn_red": (0.00, 0.05, 0.10),
        "cost_per_contact": 50,
        "cost_per_adopter_once": (0, 0, 0),
        "var_cost_m": 500,
        "one_time": (250 * M, 350 * M, 550 * M),
        "opex_m": 10 * M,
        "margin": 0.85, "launch": 2, "ramp": 2, "exec_prob": 0.90,
    },
    "A5": {
        "name": "Контент-надстройка (Yandex Plus / OVVA / Ucell TV) для архивных ТП",
        "group": "EASY", "complexity": 2, "type": "adoption",
        "segment_arpu": 28_000,
        "eligible_share": (0.30, 0.35, 0.40),   # смартфонные S3+S4
        "reach": (0.70, 0.80, 0.88),
        "takeup": (0.010, 0.025, 0.050),
        "cannibal": (0.10, 0.20, 0.30),
        "delta": (9_000, 12_000, 16_000),       # цена подписки net
        "churn_incr": (0.0, 0.0, 0.0),
        "churn_red": (0.15, 0.25, 0.40),        # VEON: отток multiplay в 2,2× ниже
        "cost_per_contact": 150,
        "cost_per_adopter_once": (0, 0, 0),
        "var_cost_m": 0,
        "one_time": (100 * M, 200 * M, 350 * M),
        "opex_m": 10 * M,
        "margin": 0.30, "launch": 3, "ramp": 4, "exec_prob": 0.85,  # маржа = доля оператора
    },
    "A6": {
        "name": "Реактивация спящих архивных SIM (win-back оффер)",
        "group": "EASY", "complexity": 1, "type": "adoption",
        "segment_arpu": 3_000,
        "eligible_share": (0.18, 0.20, 0.22),
        "reach": (0.60, 0.70, 0.80),
        "takeup": (0.03, 0.06, 0.10),
        "cannibal": (0.10, 0.20, 0.30),
        "delta": (4_000, 7_000, 11_000),
        "adopter_decay_6m": (0.50, 0.65, 0.80),  # доля реактивированных, активных через 6 мес.
        "churn_incr": (0.0, 0.0, 0.0),
        "churn_red": (0.0, 0.0, 0.0),
        "cost_per_contact": 150,
        "cost_per_adopter_once": (1_500, 3_000, 5_000),
        "var_cost_m": 0,
        "one_time": (100 * M, 150 * M, 250 * M),
        "opex_m": 10 * M,
        "margin": 0.85, "launch": 2, "ramp": 3, "exec_prob": 0.92,
    },
    "A7": {
        "name": "«Musofir»: пакеты роуминга/OTP для трудовых мигрантов на архивных ТП",
        "group": "EASY", "complexity": 2, "type": "adoption",
        "segment_arpu": 15_000,
        "eligible_share": (0.04, 0.06, 0.08),   # роуминг/междунар. звонки за 12 мес.
        "reach": (0.70, 0.80, 0.88),
        "takeup": (0.10, 0.18, 0.28),
        "cannibal": (0.15, 0.25, 0.35),
        "delta": (3_000, 7_000, 12_000),
        "churn_incr": (0.0, 0.0, 0.0),
        "churn_red": (0.10, 0.20, 0.35),
        "cost_per_contact": 150,
        "cost_per_adopter_once": (0, 0, 0),
        "var_cost_m": 0,
        "one_time": (100 * M, 150 * M, 250 * M),
        "opex_m": 10 * M,
        "margin": 0.60, "launch": 3, "ramp": 3, "exec_prob": 0.90,
    },
    "A8": {
        "name": "ОПЦИЯ: ежегодная индексация архивных пакетов на инфляцию (волна 2)",
        "group": "EASY", "complexity": 1, "type": "reprice", "optional": True,
        "segment_arpu": 28_000,
        "eligible_share": (0.30, 0.38, 0.45),   # S3+S4 без соцгруппы, оставшиеся на архиве
        "price_up_gross": (1_500, 2_000, 2_500),  # ≈ инфляция 6,5% к абонплате
        "downgrade": (0.02, 0.04, 0.07),
        "downgrade_delta": (-4_000, -2_000, 0),
        "churn_incr": (0.005, 0.010, 0.020),
        "data_cost_m": (0, 100, 300),
        "cost_per_contact": 100,
        "one_time": (100 * M, 150 * M, 250 * M),
        "opex_m": 10 * M,
        "margin": 1.0, "launch": 14, "ramp": 1, "exec_prob": 0.65,
    },
    # ============================ HARD ============================
    "B1": {
        "name": "AI Next-Best-Offer: персональные офферы в реальном времени (RTD/CVM)",
        "group": "HARD", "complexity": 4, "type": "relative",
        "rel_uplift": (0.01, 0.03, 0.06),       # поверх rule-based кампаний A1–A7
        "churn_red_base": (0.02, 0.05, 0.10),
        "one_time": (6 * B, 9 * B, 14 * B),
        "opex_m": 150 * M,
        "margin": 0.85, "launch": 8, "ramp": 4, "exec_prob": 0.65,
    },
    "B2": {
        "name": "«Ucell Oila»: семейный/групповой аккаунт с общим пакетом",
        "group": "HARD", "complexity": 4, "type": "adoption",
        "segment_arpu": 28_000,
        "eligible_share": (0.15, 0.20, 0.25),   # плательщики с домохозяйством (S3+S4)
        "reach": (0.70, 0.80, 0.88),
        "takeup": (0.02, 0.04, 0.07),
        "cannibal": (0.05, 0.10, 0.20),
        "delta": (12_000, 22_000, 35_000),      # прирост ARPA группы, net
        "new_lines": (0.20, 0.40, 0.70),        # новые линии извне на группу (доля рынка)
        "new_line_arpu": 12_000,
        "churn_incr": (0.0, 0.0, 0.0),
        "churn_red": (0.20, 0.30, 0.45),
        "cost_per_contact": 150,
        "cost_per_adopter_once": (5_000, 10_000, 20_000),
        "var_cost_m": 1_500,
        "one_time": (3 * B, 5 * B, 8 * B),
        "opex_m": 50 * M,
        "margin": 0.85, "launch": 9, "ramp": 4, "exec_prob": 0.65,
    },
    "B3": {
        "name": "Sunset-программа: вывод устаревших семейств ТП с ценовой защитой",
        "group": "HARD", "complexity": 5, "type": "reprice",
        "segment_arpu": 15_000,
        "eligible_share": (0.15, 0.25, 0.35),
        "price_up_gross": (3_500, 6_500, 10_000),  # разница до ближайшего актуального ТП
        "downgrade": (0.05, 0.10, 0.18),
        "downgrade_delta": (-5_000, -2_000, 0),
        "churn_incr": (0.02, 0.04, 0.07),
        "data_cost_m": (200, 500, 900),
        "cost_per_contact": 200,
        "opex_savings_m": (40 * M, 80 * M, 160 * M),  # упрощение каталога/биллинга
        "one_time": (4 * B, 6 * B, 10 * B),
        "opex_m": 30 * M,
        "margin": 1.0, "launch": 12, "ramp": 1, "exec_prob": 0.60,
    },
    "B4": {
        "name": "Апгрейд 2G/3G → 4G-смартфон в рассрочку (BNPL-партнёр)",
        "group": "HARD", "complexity": 4, "type": "adoption", "not_recommended": True,
        "segment_arpu": 10_000,
        "eligible_share": (0.06, 0.08, 0.10),   # кнопочные в S2
        "reach": (0.60, 0.70, 0.80),
        "takeup": (0.02, 0.05, 0.09),
        "cannibal": (0.20, 0.35, 0.50),
        "delta": (6_000, 10_000, 16_000),
        "churn_incr": (0.0, 0.0, 0.0),
        "churn_red": (0.10, 0.20, 0.30),
        "cost_per_contact": 200,
        "cost_per_adopter_once": (0, 50_000, 120_000),  # со-финансирование скидки
        "var_cost_m": 800,
        "one_time": (1.5 * B, 2.5 * B, 4 * B),
        "opex_m": 40 * M,
        "margin": 0.85, "launch": 7, "ramp": 6, "exec_prob": 0.60,
    },
    "B5": {
        "name": "Персональные лимиты «Mobil avans» на ML-скоринге",
        "group": "HARD", "complexity": 3, "type": "adoption",
        "segment_arpu": 14_000,
        "eligible_share": (0.25, 0.30, 0.40),   # регулярно уходят в ноль
        "reach": (0.85, 0.90, 0.95),
        "takeup": (0.10, 0.18, 0.28),
        "cannibal": (0.35, 0.50, 0.65),         # часть уже пользуется авансом
        "delta": (1_500, 3_000, 5_000),
        "churn_incr": (0.0, 0.0, 0.0),
        "churn_red": (0.05, 0.10, 0.20),
        "cost_per_contact": 50,
        "cost_per_adopter_once": (0, 0, 0),
        "var_cost_m": 0,
        "one_time": (1.5 * B, 2.5 * B, 4 * B),
        "opex_m": 40 * M,
        "margin": 0.70, "launch": 6, "ramp": 3, "exec_prob": 0.70,  # маржа учитывает невозврат
    },
}

# Перекрытие эффектов в портфеле (одни и те же абоненты в нескольких инициативах)
PORTFOLIO_OVERLAP_HAIRCUT = (0.10, 0.20, 0.30)
