"""
Шаблон «Карточка инициативы» для руководителя и передачи финансистам.
    python v2/templates/build_initiative_template.py → v2/templates/Initiative_Brief_Template.xlsx
Листы: Как заполнять · Портфель · I1…I4 (примеры) · Пустой шаблон.
"""
import os

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Initiative_Brief_Template.xlsx")
F = "Arial"
BLUE = Font(name=F, color="0000FF")
BLACK = Font(name=F, color="000000")
GREEN = Font(name=F, color="008000")
BOLD = Font(name=F, bold=True)
TITLE = Font(name=F, bold=True, size=14)
HFILL = PatternFill("solid", start_color="1F3864")
HFONT = Font(name=F, bold=True, color="FFFFFF")
SEC = PatternFill("solid", start_color="D9E1F2")
YEL = PatternFill("solid", start_color="FFF2CC")
thin = Side(style="thin", color="BFBFBF")
BRD = Border(left=thin, right=thin, top=thin, bottom=thin)
NUM = '#,##0;(#,##0);"-"'
NUM1 = '#,##0.0;(#,##0.0);"-"'
PCT = '0.0%;(0.0%);"-"'
PCT2 = '0.00%;(0.00%);"-"'
MULT = '0.0"x";(0.0"x");"-"'
WRAP = Alignment(wrap_text=True, vertical="top")

# --------------------------------------------------------------------------- примеры (v2)
BRIEF_KEYS = [
    ("name", "Название"), ("owner", "Владелец (PM)"), ("date", "Дата / версия"),
    ("status", "Статус"), ("problem", "Проблема (1–2 предложения, с цифрой)"),
    ("goal", "Цель и метрика успеха"), ("segment", "Целевой сегмент"),
    ("mechanics", "Что делаем (механика)"), ("why", "Почему сработает (бенчмарки, данные)"),
    ("hypothesis", "Гипотеза: «Если…, то…, потому что…»"), ("timeline", "Срок запуска и ключевые этапы"),
    ("risks", "Ключевые риски и как снижаем"), ("ask", "Какое решение нужно от руководителя"),
]
DRIVERS = [
    ("size", "Размер целевой группы", "абон.", NUM),
    ("reach", "Охват коммуникацией", "%", PCT),
    ("conv", "Принимают предложение / остаются на новом условии", "%", PCT),
    ("cannibal", "Каннибализация (сделали бы и без нас)", "%", PCT),
    ("delta", "Прирост платежа на принявшего, с НДС", "сум/мес", NUM),
    ("dg", "Доля даунгрейда (уходят на ТП дешевле)", "%", PCT),
    ("dg_loss", "Потеря платежа при даунгрейде, с НДС", "сум/мес", NUM),
    ("churn", "Доп. отток из-за инициативы", "%", PCT),
    ("arpu_out", "Платёж уходящих, с НДС", "сум/мес", NUM),
    ("start", "Месяц старта эффекта (1 = первый месяц программы)", "мес.", NUM),
    ("ramp", "Месяцев до полного эффекта", "мес.", NUM),
    ("capex", "Разовые затраты (CAPEX / внедрение)", "сум", NUM),
    ("opex", "Постоянные затраты в месяц (OPEX)", "сум/мес", NUM),
    ("var", "Переменные затраты на принявшего", "сум/мес", NUM),
    ("margin", "Маржинальность доп. выручки", "%", PCT),
    ("base_subs", "База для ΔARPU: абонентов", "абон.", NUM),
    ("base_arpu", "База для ΔARPU: ARPU без НДС", "сум/мес", NUM),
]

EX = {
    "I1": {
        "brief": {
            "name": "I1 Sunset / Migration старых неэффективных линеек → ТП дороже на 10–15%",
            "owner": "[ФИО, PM тарифных планов]", "date": "09.10.2026 · v0.3", "status": "Discovery",
            "problem": "~30% архивной базы (~1,06 млн) на старых линейках с низкой абонплатой (~20 тыс.) и дорогим сопровождением; ARPU когорты 18 500 сум.",
            "goal": "ARPU архивной когорты +5% за 12 мес. после старта; доп. отток ≤ 5%; −30% тарифных кодов.",
            "segment": "Абоненты неэффективных архивных линеек (без соцгруппы ж 55+, м 60+); список — из анализа D3.",
            "mechanics": "T−60: «выберите сами» + бонус Loyalty; T−15: уведомление (было → стало); T0: перевод на ближайший ТП +10–15%; T+30: right-size. Две волны: апр и июл 2027.",
            "why": "T-Mobile (grandfathered → новые планы), Airtel, Telenor (ARPU +4%), РФ (индексация архива). Ucell 02/2026 — естественный эксперимент.",
            "hypothesis": "Если перевести неэффективные линейки на ТП +10–15% с большим объёмом и бесплатной сменой, то ARPU когорты вырастет на ~5–6%, потому что ≥85% останутся на новом ТП.",
            "timeline": "Mapping и биллинг: дек 2026 – мар 2027; волна 1 — апр 2027; разбор — май; волна 2 — июл 2027.",
            "risks": "Регулятор (15 дней, социсключение, досье); отток (волны, контроль 5%); нагрузка на КЦ (скрипты, самообслуживание).",
            "ask": "Согласовать направление и передать в финансы для бизнес-кейса; выделить ресурс биллинга на mapping.",
        },
        "drivers": {
            "size": (1_056_000, 880_000, 1_408_000), "reach": (1, 1, 1), "conv": (0.89, 0.81, 0.945),
            "cannibal": (0, 0, 0), "delta": (4_000, 2_700, 6_500), "dg": (0.08, 0.14, 0.04),
            "dg_loss": (2_240, 4_480, 0), "churn": (0.03, 0.05, 0.015), "arpu_out": (17_920, 17_920, 17_920),
            "start": (6, 6, 6), "ramp": (4, 4, 4), "capex": (5_000_000_000, 8_000_000_000, 3_000_000_000),
            "opex": (0, 30_000_000, -30_000_000), "var": (300, 600, 100), "margin": (1, 1, 1),
            "base_subs": (3_520_000,) * 3, "base_arpu": (18_500,) * 3,
        },
        "src": {
            "size": "Гипотеза: 30% когорты; факт — D1/D3", "conv": "1 − даунгрейд − отток", "delta": "+12,5% к ~20 тыс. + апсейл 12% × 10 тыс.",
            "dg": "Бенчмарки; калибровка D7", "churn": "AT&T/T-Mobile/Индия; D7", "capex": "Оценка биллинга (запросить)",
            "opex": "OPEX 30 млн − экономия сопровождения ~60 млн", "base_subs": "Архивная когорта T0",
        },
    },
    "I2": {
        "brief": {
            "name": "I2 More-for-More для когорты недооценённых линеек",
            "owner": "[ФИО, PM тарифных планов]", "date": "09.10.2026 · v0.3", "status": "Готово к финансам",
            "problem": "~22% архивной базы (~775 тыс.) используют пакет полностью, но платят ниже актуальной линейки на 4–6 тыс. сум.",
            "goal": "ARPU когорты +4% за 12 мес.; даунгрейд ≤ 12%; доп. отток ≤ 3%; жалобы ≤ 2× нормы.",
            "segment": "Недооценённые архивные линейки (использование пакета ≥ 60%), без соцгруппы и без ТП волны 02/2026.",
            "mechanics": "+4 000…6 000 сум к абонплате + больше ГБ; бесплатный right-size рядом; уведомление ≥ 15 дней; пилот 10% с holdout → масштаб.",
            "why": "РФ (+10–20% на архиве), AT&T, T-Mobile, Индия, Казахстан; Ucell 02/2026 (+5 000 с +ГБ).",
            "hypothesis": "Если поднять абонплату на 4–6 тыс. с добавлением ГБ и дать бесплатную альтернативу, то ≥ 85% останутся, потому что ценность пакета растёт и цена ниже актуальной линейки.",
            "timeline": "Пилот 10% — дек 2026; разбор — 27.01.2027; масштаб — фев 2027.",
            "risks": "Комитет по конкуренции (точечность, досье); негатив «ненужные ГБ» (right-size); отток (стоп-критерий 1,5 п.п.).",
            "ask": "Утвердить пилот 10% в декабре и передать драйверы в финансы.",
        },
        "drivers": {
            "size": (774_400, 634_000, 915_000), "reach": (1, 1, 1), "conv": (0.895, 0.81, 0.95),
            "cannibal": (0, 0, 0), "delta": (5_000, 4_000, 6_000), "dg": (0.08, 0.15, 0.04),
            "dg_loss": (3_360, 6_720, 0), "churn": (0.025, 0.05, 0.01), "arpu_out": (23_520, 23_520, 23_520),
            "start": (2, 2, 2), "ramp": (3, 3, 3), "capex": (300_000_000, 500_000_000, 200_000_000),
            "opex": (20_000_000, 20_000_000, 20_000_000), "var": (400, 800, 200), "margin": (1, 1, 1),
            "base_subs": (3_520_000,) * 3, "base_arpu": (18_500,) * 3,
        },
        "src": {"size": "Гипотеза: 22% когорты; факт — D3", "delta": "Решение по прайсу", "dg": "Бенчмарки; D7",
                "churn": "Бенчмарки; D7", "capex": "Маркетинг + КЦ + юр."},
    },
    "I3": {
        "brief": {
            "name": "I3 Бустер при исчерпании трафика + роуминг-пакет по акции",
            "owner": "[ФИО, PM тарифных планов]", "date": "09.10.2026 · v0.3", "status": "Готово к финансам",
            "problem": "~15% архивной базы исчерпывают пакет до конца месяца; ~6% выезжают за рубеж (мигранты) и теряют связь / номер.",
            "goal": "+57 тыс. платящих за бустер / роуминг-пакет; LTV/CAC ≥ 5.",
            "segment": "Исчерпывающие пакет (D3/D5) + абоненты с роумингом / международными звонками (D9).",
            "mechanics": "Триггер «осталось 20% / 0%» → +5 ГБ в 1 клик (автопродление только по согласию); «Musofir» −50% первый месяц.",
            "why": "Flytxt (+8% ARPU на контекстных офферах), бустеры Jio/Airtel; переводы мигрантов $18,9 млрд (2025).",
            "hypothesis": "Если предложить пакет в момент исчерпания / выезда, то ≥ 10% купят, потому что потребность возникает прямо сейчас.",
            "timeline": "Запуск A/B — дек 2026; масштаб — фев 2027.",
            "risks": "Навязчивость (лимит 2 касания/мес., opt-in); каннибализация (holdout).",
            "ask": "Утвердить запуск A/B в декабре.",
        },
        "drivers": {
            "size": (739_000, 600_000, 900_000), "reach": (0.88, 0.80, 0.93), "conv": (0.14, 0.09, 0.20),
            "cannibal": (0.38, 0.50, 0.25), "delta": (8_150, 6_000, 12_000), "dg": (0, 0, 0),
            "dg_loss": (0, 0, 0), "churn": (0, 0, 0), "arpu_out": (0, 0, 0),
            "start": (2, 2, 2), "ramp": (3, 3, 3), "capex": (500_000_000, 800_000_000, 350_000_000),
            "opex": (20_000_000, 20_000_000, 20_000_000), "var": (280, 500, 150), "margin": (0.74, 0.65, 0.80),
            "base_subs": (3_520_000,) * 3, "base_arpu": (18_500,) * 3,
        },
        "src": {"size": "Исчерпывающие 528 тыс. + роуминг 211 тыс.", "conv": "A/B в декабре", "cannibal": "Доля докупающих сами (D5)",
                "margin": "Бустер 85%, роуминг 60% (оптовые затраты)"},
    },
    "I4": {
        "brief": {
            "name": "I4 Ucell Club — программа лояльности (MVP → масштаб)",
            "owner": "[ФИО, PM тарифных планов]", "date": "09.10.2026 · v0.3", "status": "Discovery",
            "problem": "Нет программы, поощряющей оплату вовремя и стаж; у конкурентов есть (Beeline BEEP, Mobiuz Bonus, розыгрыши авто).",
            "goal": "Оплата вовремя +2 п.п., отток участников −10%, переходы на ТП ≥ 60 тыс. +0,3 п.п./мес.; стоимость ≤ 1 900 сум на участника.",
            "segment": "Пользователи приложения (~1,5 млн при масштабе), из них ~20% архивные; MVP — 150 тыс.",
            "mechanics": "Кэшбэк 3–5% за оплату вовремя; сундук каждый день; Weekly Wins (1 354 приза); Monthly Grand (авто, путешествия, умра) в прямом эфире.",
            "why": "Verizon Dollars 3% + Shine; T-Mobile Tuesdays (−27% оттока участников); Simon-Kucher: +43% CLTV у участников.",
            "hypothesis": "Если давать кэшбэк за оплату вовремя и ежедневный гарантированный приз, то оплаты вовремя и удержание вырастут, потому что появится привычка и потеря при уходе.",
            "timeline": "Разработка MVP — дек–фев; MVP — мар–май 2027; решение — 15.06.2027; масштаб — сен 2027.",
            "risks": "Не окупается (MVP + стоп-правила); «никто не выигрывает» (массовые призы); юр. риск розыгрышей (без платы за шанс).",
            "ask": "Утвердить бюджет MVP 3,5 млрд сум; масштаб — по итогам MVP.",
        },
        "drivers": {
            "size": (1_485_000, 1_000_000, 2_000_000), "reach": (1, 1, 1), "conv": (1, 1, 1),
            "cannibal": (0, 0, 0), "delta": (3_000, 1_500, 4_500), "dg": (0, 0, 0), "dg_loss": (0, 0, 0),
            "churn": (0, 0, 0), "arpu_out": (0, 0, 0), "start": (11, 11, 11), "ramp": (6, 6, 6),
            "capex": (6_500_000_000, 8_000_000_000, 5_000_000_000),
            "opex": (1_082_000_000, 1_250_000_000, 950_000_000), "var": (1_037, 1_250, 850), "margin": (0.85, 0.85, 0.85),
            "base_subs": (1_485_000,) * 3, "base_arpu": (43_929,) * 3,
        },
        "src": {"size": "Участники при масштабе (MAU × вступление)",
                "delta": "Упрощённо: эффект на участника в стационаре (удержание + оплата вовремя + переходы + допродажи + Pass); полная модель — v2/model",
                "opex": "Призы (инвентарь + Weekly + Grand) + команда + маркетинг", "var": "Кэшбэк + цифровые призы сундука",
                "capex": "MVP 1,8 + масштаб 3,0 + маркетинг запуска 1,75 млрд", "base_subs": "ΔARPU — по участникам программы"},
    },
}

FIN_ASKS = [
    "Ставка дисконтирования (WACC) и горизонт для NPV / IRR",
    "Амортизация CAPEX, налог на прибыль, НДС в расчётах",
    "Аллокация общих затрат (сеть, IT, КЦ) — что считаем инкрементальным",
    "Учёт по МСФО (IFRS 15 — бонусы / кэшбэк / лояльность)",
    "Сценарии (пессимист / база / оптимист) и анализ чувствительности",
    "Валютный риск (закупка призов и оборудования в USD)",
]
CHECKLIST = [
    "Проблема и цель подтверждены данными, а не только гипотезой",
    "Размер целевой группы взят из выгрузки аналитиков",
    "У каждого драйвера указан источник и уровень уверенности",
    "Заполнены пессимистичный и оптимистичный сценарии",
    "CAPEX / OPEX оценены владельцами (IT, биллинг, маркетинг)",
    "Юридическая проверка пройдена или запрошена",
    "Определены KPI, контрольная группа и стоп-критерии",
    "Таймлайн согласован с IT / биллингом",
    "Руководитель видел одностраничник и согласен с направлением",
    "Сформирован список вопросов к финансам",
]
KPI_EX = {
    "I1": [("ΔARPU мигрантов vs контроль", "≥ +2 000 сум", "< +500 сум"), ("Доп. отток волны", "≤ 4%", "> 6%"), ("Закрыто тарифных кодов", "−30%", "—")],
    "I2": [("ΔARPU vs holdout", "≥ +3%", "< +1%"), ("Отток тест − контроль", "≤ 1,5 п.п.", "> 1,5 п.п. за 45 дней"), ("Жалобы", "≤ 2× нормы", "> 2× нормы")],
    "I3": [("Конверсия vs holdout", "+6 п.п.", "< +2 п.п."), ("Отписки от предложений", "≤ 2%", "> 5%"), ("LTV/CAC", "≥ 5", "< 2")],
    "I4": [("Оплата вовремя vs holdout", "+2 п.п.", "< +0,5 п.п."), ("DAU сундука / участники", "≥ 25%", "< 15%"), ("Стоимость на участника", "≤ 1 900 сум/мес", "> 2 500 сум/мес")],
}


def cell(ws, r, c, v=None, font=BLACK, fmt=None, fill=None, align=None, border=True):
    x = ws.cell(row=r, column=c, value=v)
    x.font = font
    if fmt:
        x.number_format = fmt
    if fill:
        x.fill = fill
    if align:
        x.alignment = align
    if border:
        x.border = BRD
    return x


def header(ws, r, labels):
    for j, h in enumerate(labels, 1):
        x = cell(ws, r, j, h, HFONT, fill=HFILL)
        x.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def section(ws, r, text):
    ws.cell(row=r, column=1, value=text).font = BOLD
    for c in range(1, 9):
        ws.cell(row=r, column=c).fill = SEC


GLOBAL = {}


def initiative_sheet(wb, title, data):
    ws = wb.create_sheet(title)
    ws["A1"] = f"Карточка инициативы · {title}"
    ws["A1"].font = TITLE
    ws["A2"] = "Синее — ввод, чёрное — формулы. Блок 1 — для руководителя, блоки 2–4 — для передачи финансам."
    ws["A2"].font = Font(name=F, italic=True, color="595959")
    rows = {}
    r = 4
    section(ws, r, "1. ОДНОСТРАНИЧНИК ДЛЯ РУКОВОДИТЕЛЯ")
    r += 1
    for k, label in BRIEF_KEYS:
        rows[k] = r
        cell(ws, r, 1, label, BOLD, align=WRAP)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=8)
        v = data["brief"].get(k, "") if data else ""
        x = cell(ws, r, 2, v, BLUE, align=WRAP, fill=None if v else YEL)
        for c in range(3, 9):
            ws.cell(row=r, column=c).border = BRD
        ws.row_dimensions[r].height = 46 if k not in ("name", "owner", "date", "status") else 20
        if k == "status":
            dv = DataValidation(type="list", formula1='"Идея,Discovery,Готово к финансам,В расчёте у финансов,Утверждено,Отклонено"', allow_blank=True)
            ws.add_data_validation(dv)
            dv.add(x)
        r += 1
    r += 1
    section(ws, r, "2. ДРАЙВЕРЫ ДЛЯ ФИНАНСОВ (каждое число — с источником и уверенностью)")
    r += 1
    header(ws, r, ["Параметр", "База", "Пессимист", "Оптимист", "Ед.", "Источник / как получено", "Уверенность", "Кто даёт данные"])
    r += 1
    conf_dv = DataValidation(type="list", formula1='"Высокая,Средняя,Низкая"', allow_blank=True)
    ws.add_data_validation(conf_dv)
    for k, label, unit, fmt in DRIVERS:
        rows[k] = r
        cell(ws, r, 1, label, align=WRAP)
        vals = data["drivers"].get(k, (None, None, None)) if data else (None, None, None)
        for j, v in enumerate(vals[:3], 2):
            cell(ws, r, j, v, BLUE, fmt, None if v is not None else YEL)
        cell(ws, r, 5, unit)
        cell(ws, r, 6, (data or {}).get("src", {}).get(k, ""), BLUE, align=WRAP)
        conf = ""
        if data:
            conf = "Средняя" if k in (data.get("src") or {}) else ("Высокая" if k in ("reach", "margin", "start", "base_subs", "base_arpu") else "Низкая")
        c = cell(ws, r, 7, conf, BLUE)
        conf_dv.add(c)
        owner = {"size": "Аналитика", "conv": "Аналитика / пилот", "cannibal": "Аналитика", "delta": "Продукт / прайсинг",
                 "dg": "Аналитика (D7)", "churn": "Аналитика (D7)", "capex": "IT / биллинг / маркетинг", "opex": "Владельцы затрат",
                 "var": "Сеть / финансы", "margin": "Финансы"}.get(k, "Продукт")
        cell(ws, r, 8, owner, BLUE)
        ws.row_dimensions[r].height = 30
        r += 1
    r += 1
    section(ws, r, "3. БЫСТРЫЙ РАСЧЁТ (sanity-check до финмодели; финансы уточнят NPV, налоги, амортизацию)")
    r += 1
    header(ws, r, ["Показатель", "База", "Пессимист", "Оптимист", "Ед.", "Как считается", "", ""])
    r += 1
    V = GLOBAL["VAT"]
    FX = GLOBAL["FX"]

    def v(col, key):
        rr = rows[key]
        return f"{col}{rr}" if col == "B" else f'IF({col}{rr}="",$B{rr},{col}{rr})'

    calc = [
        ("adopters", "Принявших, абон.", "абон.", NUM, "Размер × охват × принятие × (1 − каннибализация)",
         lambda c: f"={v(c,'size')}*{v(c,'reach')}*{v(c,'conv')}*(1-{v(c,'cannibal')})"),
        ("down", "Даунгрейд, абон.", "абон.", NUM, "Размер × доля даунгрейда", lambda c: f"={v(c,'size')}*{v(c,'dg')}"),
        ("lost", "Ушедших, абон.", "абон.", NUM, "Размер × доп. отток", lambda c: f"={v(c,'size')}*{v(c,'churn')}"),
        ("monthly", "Доп. выручка в месяц при полном эффекте, без НДС", "сум/мес", NUM,
         "(Принявшие × прирост − даунгрейд × потеря − ушедшие × платёж) / (1 + НДС)",
         lambda c: f"=({c}{{adopters}}*{v(c,'delta')}-{c}{{down}}*{v(c,'dg_loss')}-{c}{{lost}}*{v(c,'arpu_out')})/(1+{V})"),
        ("t1", "Месяцев эффекта в 1-й год", "мес.", NUM1, "12 − месяц старта + 1", lambda c: f"=MAX(0,12-{v(c,'start')}+1)"),
        ("eff1", "Эффективных месяцев в 1-й год (с набором)", "мес.", NUM1, "Учитывает линейный набор эффекта",
         lambda c: f"=IF({c}{{t1}}>={v(c,'ramp')},({v(c,'ramp')}+1)/2+({c}{{t1}}-{v(c,'ramp')}),{c}{{t1}}*({c}{{t1}}+1)/(2*MAX(1,{v(c,'ramp')})))"),
        ("t24", "Месяцев эффекта за 24 мес.", "мес.", NUM1, "24 − месяц старта + 1", lambda c: f"=MAX(0,24-{v(c,'start')}+1)"),
        ("eff24", "Эффективных месяцев за 24 мес.", "мес.", NUM1, "",
         lambda c: f"=IF({c}{{t24}}>={v(c,'ramp')},({v(c,'ramp')}+1)/2+({c}{{t24}}-{v(c,'ramp')}),{c}{{t24}}*({c}{{t24}}+1)/(2*MAX(1,{v(c,'ramp')})))"),
        ("rev1", "Доп. выручка за 1-й год", "сум", NUM, "Месячная × эффективные месяцы", lambda c: f"={c}{{monthly}}*{c}{{eff1}}"),
        ("rev24", "Доп. выручка за 24 мес.", "сум", NUM, "", lambda c: f"={c}{{monthly}}*{c}{{eff24}}"),
        ("cost24", "Затраты за 24 мес.", "сум", NUM, "CAPEX + OPEX × месяцы + перем. × принявшие × эфф. месяцы",
         lambda c: f"={v(c,'capex')}+{v(c,'opex')}*{c}{{t24}}+{v(c,'var')}*{c}{{adopters}}*{c}{{eff24}}"),
        ("contrib24", "Вклад за 24 мес. (маржа − затраты)", "сум", NUM, "Выручка × маржа − затраты",
         lambda c: f"={c}{{rev24}}*{v(c,'margin')}-{c}{{cost24}}"),
        ("payback", "Окупаемость CAPEX после старта", "мес.", NUM1, "CAPEX / месячный вклад при полном эффекте",
         lambda c: f'=IF({c}{{monthly}}*{v(c,"margin")}-{v(c,"opex")}-{v(c,"var")}*{c}{{adopters}}>0,{v(c,"capex")}/({c}{{monthly}}*{v(c,"margin")}-{v(c,"opex")}-{v(c,"var")}*{c}{{adopters}}),"не окупается")'),
        ("roi", "ROI за 24 мес.", "x", MULT, "Вклад / затраты", lambda c: f"=IF({c}{{cost24}}>0,{c}{{contrib24}}/{c}{{cost24}},0)"),
        ("arpu_upl", "ΔARPU базы при полном эффекте", "%", PCT2, "Месячная выручка / (база × ARPU базы)",
         lambda c: f"=IF({v(c,'base_subs')}*{v(c,'base_arpu')}>0,{c}{{monthly}}/({v(c,'base_subs')}*{v(c,'base_arpu')}),0)"),
        ("usd", "Run-rate доп. выручки в год, USD", "$", '"$"#,##0', "Месячная × 12 / курс", lambda c: f"={c}{{monthly}}*12/{FX}"),
    ]
    start = r
    for i, (k, *_rest) in enumerate(calc):
        rows[k] = start + i
    for k, label, unit, fmt, how, fn in calc:
        rr = rows[k]
        cell(ws, rr, 1, label, BOLD if k in ("monthly", "rev1", "contrib24", "arpu_upl") else BLACK, align=WRAP)
        for j, c in enumerate("BCD", 2):
            f = fn(c)
            for kk in ("adopters", "down", "lost", "monthly", "t1", "eff1", "t24", "eff24", "rev24", "cost24", "contrib24"):
                f = f.replace("{" + kk + "}", str(rows[kk]))
            cell(ws, rr, j, f, BLACK, fmt)
        cell(ws, rr, 5, unit)
        cell(ws, rr, 6, how, align=WRAP)
        ws.merge_cells(start_row=rr, start_column=6, end_row=rr, end_column=8)
    r = start + len(calc) + 1
    section(ws, r, "4. ЧТО НУЖНО ОТ ФИНАНСОВ")
    r += 1
    header(ws, r, ["Вопрос / задача", "Статус", "", "", "", "Комментарий", "", ""])
    r += 1
    st_dv = DataValidation(type="list", formula1='"Не начато,Запрошено,Получено"', allow_blank=True)
    ws.add_data_validation(st_dv)
    for q in FIN_ASKS:
        cell(ws, r, 1, q, align=WRAP)
        c = cell(ws, r, 2, "Не начато" if data else "", BLUE)
        st_dv.add(c)
        ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=8)
        cell(ws, r, 6, "", BLUE)
        ws.row_dimensions[r].height = 28
        r += 1
    r += 1
    section(ws, r, "5. KPI, КРИТЕРИИ УСПЕХА И СТОП-КРИТЕРИИ")
    r += 1
    header(ws, r, ["KPI", "Цель", "Стоп-критерий", "", "", "", "", ""])
    r += 1
    kp = KPI_EX.get(title, [("", "", "")] * 3) if data else [("", "", "")] * 3
    for a, b, c in kp:
        cell(ws, r, 1, a, BLUE, align=WRAP)
        cell(ws, r, 2, b, BLUE)
        cell(ws, r, 3, c, BLUE)
        r += 1
    r += 1
    section(ws, r, "6. ГОТОВНОСТЬ К ПЕРЕДАЧЕ ФИНАНСАМ (Definition of Ready)")
    r += 1
    header(ws, r, ["Пункт", "Да / Нет", "", "", "", "", "", ""])
    r += 1
    yn = DataValidation(type="list", formula1='"Да,Нет"', allow_blank=True)
    ws.add_data_validation(yn)
    c0 = r
    ready_ex = {"I1": 5, "I2": 8, "I3": 7, "I4": 4}
    for i, q in enumerate(CHECKLIST):
        cell(ws, r, 1, q, align=WRAP)
        val = ("Да" if i < ready_ex.get(title, 0) else "Нет") if data else ""
        c = cell(ws, r, 2, val, BLUE)
        yn.add(c)
        r += 1
    cell(ws, r, 1, "Готовность", BOLD)
    cell(ws, r, 2, f'=COUNTIF(B{c0}:B{r-1},"Да")/{len(CHECKLIST)}', BOLD, PCT)
    cell(ws, r, 3, f'=IF(B{r}>=0.8,"Можно передавать финансам","Доработать до 80%")', BOLD)
    rows["ready"] = r
    ws.column_dimensions["A"].width = 46
    for col, w in zip("BCDEFGH", (18, 16, 16, 10, 44, 13, 22)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A4"
    return rows


def build():
    wb = Workbook()
    ws = wb.active
    ws.title = "Как заполнять"
    lines = [
        ("Карточка инициативы: от идеи к бизнес-кейсу", TITLE), ("", None),
        ("Путь инициативы", BOLD),
        ("1. Идея → 2. Карточка (этот файл) → 3. Ревью у руководителя (15–20 мин) → 4. Передача финансам → 5. Бизнес-кейс (NPV / IRR) → 6. Инвест-комитет / SteerCo", None),
        ("", None), ("Что заполняете вы (PM)", BOLD),
        ("Блок 1 — одностраничник: проблема с цифрой, цель, сегмент, механика, доказательства, гипотеза, сроки, риски, какое решение нужно.", None),
        ("Блок 2 — драйверы: каждое число в трёх сценариях, с источником, уверенностью и владельцем данных. Финансы считают по вашим драйверам, поэтому драйвер без источника = вопрос на ревью.", None),
        ("Блок 3 — быстрый расчёт: проверка порядка цифр до финмодели (без дисконтирования, налогов и амортизации — это делают финансы).", None),
        ("Блоки 4–6 — вопросы к финансам, KPI и стоп-критерии, чек-лист готовности (≥ 80% → можно передавать).", None),
        ("", None), ("Что делают финансы (не делайте за них)", BOLD),
        ("NPV / IRR / дисконтирование, налоги, амортизация CAPEX, аллокация общих затрат, учёт по МСФО, итоговый P&L и влияние на EBITDA.", None),
        ("", None), ("Легенда", BOLD),
        ("Синий текст — ввод; чёрный — формулы; жёлтая заливка — не заполнено; списки выбора — Статус, Уверенность, Да / Нет.", None),
        ("Лист «Портфель» собирает все карточки в одну таблицу и приоритизирует. Новую инициативу — копируйте лист «Пустой шаблон» и добавьте строку в «Портфель».", None),
        ("", None), ("Примеры I1–I4 заполнены по v2 (гипотезы до данных). Числа — ориентиры; замените фактом из выгрузок аналитиков.", Font(name=F, italic=True, color="595959")),
    ]
    for i, (t, f) in enumerate(lines, 1):
        c = ws.cell(row=i, column=1, value=t)
        c.font = f or BLACK
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width = 150

    wp = wb.create_sheet("Портфель")
    wp["A1"] = "Портфель инициатив — сводка для руководителя"
    wp["A1"].font = TITLE
    glob = [("Курс, сум за 1 USD", 12_100, NUM, "FX"), ("НДС", 0.12, PCT, "VAT")]
    wp["A3"] = "Общие допущения"
    wp["A3"].font = BOLD
    for i, (lab, val, fmt, key) in enumerate(glob, 4):
        cell(wp, i, 1, lab)
        cell(wp, i, 2, val, BLUE, fmt)
        GLOBAL[key] = f"'Портфель'!$B${i}"

    sheets = {}
    for k in ("I1", "I2", "I3", "I4"):
        sheets[k] = initiative_sheet(wb, k, EX[k])
    tmpl_rows = initiative_sheet(wb, "Пустой шаблон", None)

    r0 = 8
    heads = ["ID", "Инициатива", "Статус", "Старт, мес.", "Выручка 1-й год", "Вклад 24м: база", "Вклад 24м: пессимист",
             "Вклад 24м: оптимист", "CAPEX", "Окупаемость, мес.", "ΔARPU базы", "Уверенность", "Сложность (1–5)",
             "Приоритет", "Готовность к финансам"]
    for j, h in enumerate(heads, 1):
        cell(wp, r0, j, h, HFONT, fill=HFILL).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    wp.row_dimensions[r0].height = 45
    cx = {"I1": 4, "I2": 1, "I3": 2, "I4": 4}
    conf = {"I1": "Средняя", "I2": "Высокая", "I3": "Высокая", "I4": "Низкая"}
    yes = DataValidation(type="list", formula1='"Высокая,Средняя,Низкая"', allow_blank=True)
    wp.add_data_validation(yes)
    for i, k in enumerate(("I1", "I2", "I3", "I4"), r0 + 1):
        R = sheets[k]
        s = f"'{k}'!"
        vals = [
            (k, None, BLACK), (f"={s}B{R['name']}", None, GREEN), (f"={s}B{R['status']}", None, GREEN),
            (f"={s}B{R['start']}", NUM, GREEN), (f"={s}B{R['rev1']}", NUM, GREEN), (f"={s}B{R['contrib24']}", NUM, GREEN),
            (f"={s}C{R['contrib24']}", NUM, GREEN), (f"={s}D{R['contrib24']}", NUM, GREEN), (f"={s}B{R['capex']}", NUM, GREEN),
            (f"={s}B{R['payback']}", NUM1, GREEN), (f"={s}B{R['arpu_upl']}", PCT2, GREEN),
            (conf[k], None, BLUE), (cx[k], NUM, BLUE),
            (f'=F{i}/1000000000*IF(L{i}="Высокая",1,IF(L{i}="Средняя",0.7,0.4))/MAX(1,M{i})', NUM1, BLACK),
            (f"={s}B{R['ready']}", PCT, GREEN),
        ]
        for j, (v, fmt, font) in enumerate(vals, 1):
            c = cell(wp, i, j, v, font, fmt)
            if j == 2:
                c.alignment = WRAP
            if j == 12:
                yes.add(c)
        wp.row_dimensions[i].height = 32
    last = r0 + 4
    t = last + 1
    cell(wp, t, 2, "Итого (база)", BOLD)
    for col, fmt in (("E", NUM), ("F", NUM), ("G", NUM), ("H", NUM), ("I", NUM)):
        cell(wp, t, " ABCDEFGHI".index(col), f"=SUM({col}{r0+1}:{col}{last})", BOLD, fmt)
    wp.cell(row=t + 2, column=1, value="Приоритет = вклад 24м (млрд) × уверенность (1 / 0,7 / 0,4) / сложность. Это ориентир для разговора, не решение.").font = Font(name=F, italic=True, color="595959")
    ch = BarChart()
    ch.type = "bar"
    ch.title = "Вклад за 24 мес., сум: пессимист / база / оптимист"
    ch.y_axis.number_format = '#,##0'
    data = Reference(wp, min_col=6, max_col=8, min_row=r0, max_row=last)
    ch.add_data(data, titles_from_data=True)
    ch.set_categories(Reference(wp, min_col=1, min_row=r0 + 1, max_row=last))
    ch.height, ch.width = 9, 22
    wp.add_chart(ch, f"A{t + 4}")
    for col, w in zip("ABCDEFGHIJKLMNO", (8, 46, 16, 10, 18, 18, 18, 18, 18, 12, 12, 12, 12, 11, 13)):
        wp.column_dimensions[col].width = w
    wp.freeze_panes = f"C{r0+1}"

    for sh in wb.worksheets:
        for row in sh.iter_rows():
            for c in row:
                f = c.font
                if f is None or f.name != F:
                    c.font = Font(name=F, bold=bool(f and f.bold), italic=bool(f and f.italic),
                                  color=f.color if f else None, size=f.size if f and f.size else 11)
    wb.calculation.fullCalcOnLoad = True
    wb.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    build()
