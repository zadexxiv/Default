"""
Генерирует Excel-модель с живыми формулами:
    python model/build_excel.py  →  model/Ucell_Archive_ARPU_Model.xlsx

Лист Monthly — помесячный движок (24 мес.) по той же логике, что и детерминированный
прогон model/arpu_model.py на модальных значениях (результаты совпадают). Меняете синие
ячейки на листах Inputs / Initiatives → пересчитываются все итоги.

Вероятности успеха считаются Монте-Карло в Python и вставлены на лист MC_Results
как значения (Excel их не пересчитывает).
"""
from __future__ import annotations

import json
import os
import sys

from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(__file__))
import assumptions as A  # noqa: E402

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "Ucell_Archive_ARPU_Model.xlsx")
H = A.HORIZON_MONTHS

FONT = "Arial"
BLUE = Font(name=FONT, color="0000FF")
BLACK = Font(name=FONT, color="000000")
GREEN = Font(name=FONT, color="008000")
BOLD = Font(name=FONT, bold=True)
TITLE = Font(name=FONT, bold=True, size=14)
HDR_FILL = PatternFill("solid", start_color="1F3864")
HDR_FONT = Font(name=FONT, bold=True, color="FFFFFF")
YELLOW = PatternFill("solid", start_color="FFFF00")
SEC_FILL = PatternFill("solid", start_color="D9E1F2")
thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

NUM = '#,##0;(#,##0);"-"'
NUM1 = '#,##0.0;(#,##0.0);"-"'
NUM3 = '0.000;(0.000);"-"'
PCT = '0.0%;(0.0%);"-"'
PCT2 = '0.00%;(0.00%);"-"'
MULT = '0.0"x";(0.0"x");"-"'


def mode(v):
    return v[1] if isinstance(v, (tuple, list)) else v


def style_header(ws, row, ncol, start=1):
    for c in range(start, ncol + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HDR_FILL
        cell.font = HDR_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER


def put(ws, row, col, value, font=BLACK, fmt=None, fill=None, border=True):
    c = ws.cell(row=row, column=col, value=value)
    c.font = font
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if border:
        c.border = BORDER
    return c


# ---------------------------------------------------------------------------
def sheet_readme(wb):
    ws = wb.active
    ws.title = "README"
    rows = [
        ("Ucell — модель роста ARPU архивной базы", TITLE),
        ("", None),
        ("Как пользоваться", BOLD),
        ("1. Замените ЖЁЛТЫЕ ячейки на листе Inputs фактом от аналитиков (docs/09_data_request_for_analysts.md).", None),
        ("2. Лист Initiatives: синие ячейки — параметры инициатив (модальные значения бенчмарков). После пилотов подставьте фактические конверсии/отток.", None),
        ("3. Лист Monthly — помесячный движок на 24 мес.; лист Portfolio — итоги портфеля, динамика ARPU, график.", None),
        ("4. Лист AB_Calculator — размер выборок для пилотов; лист MC_Results — вероятности из Монте-Карло (значения из Python).", None),
        ("5. После изменения допущений в коде: python model/arpu_model.py && python model/build_excel.py", None),
        ("", None),
        ("Легенда", BOLD),
        ("Синий текст — ввод · Чёрный — формула · Зелёный — ссылка на другой лист · Жёлтая заливка — ключевая гипотеза, заменить фактом", None),
        ("", None),
        ("Единицы и определения", BOLD),
        ("Деньги — сум (UZS) без НДС 12%, если не указано «с НДС». Курс — лист Inputs.", None),
        ("ARPU считается по КОГОРТЕ абонентов, бывших на архивных ТП на дату T0: мигрировавшие на актуальные ТП остаются в когорте.", None),
        ("Иначе миграция «выносит» лучших абонентов из архива и формально снижает ARPU архива — ловушка метрики.", None),
        ("ΔARPU когорты = (R0 + ΔR) / (S0 + ΔS) / ARPU0 − 1, где R0, S0 — выручка и абоненты когорты без инициатив (с естественным оттоком).", None),
        ("", None),
        ("Типы механик", BOLD),
        ("adoption — добровольное принятие оффера (миграция, допродажа); reprice — изменение условий ТП для целевой группы (stay/downgrade/churn); relative — относительный прирост выручки всей когорты (платформа).", None),
    ]
    for i, (t, f) in enumerate(rows, 1):
        ws.cell(row=i, column=1, value=t).font = f or BLACK
    ws.column_dimensions["A"].width = 150


# ---------------------------------------------------------------------------
def sheet_inputs(wb):
    wi = wb.create_sheet("Inputs")
    wi["A1"] = "Базовые допущения"
    wi["A1"].font = TITLE
    for j, h in enumerate(["Параметр", "", "Значение", "Ед.", "Источник / комментарий"], 1):
        wi.cell(row=3, column=j, value=h)
    style_header(wi, 3, 5)
    b = A.BASE
    inputs = [
        ("Абонентская база Ucell", b["total_subs"], "абон.", "Ucell: >10,9 млн на начало 2026 (итоги 2025, kun.uz 25.02.2026)", False),
        ("Доля абонентов на архивных ТП", b["archive_share"], "%", "HYPOTHESIS — заменить фактом (запрос D1)", True),
        ("Доля активных среди архивных (доход за 30 дн.)", b["archive_active_ratio"], "%", "HYPOTHESIS — запрос D1", True),
        ("Активная архивная когорта (N)", "=C4*C5*C6", "абон.", "Формула", False),
        ("ARPU архивной когорты (ARPU0, net)", "=SUMPRODUCT(C17:C21,D17:D21)", "сум/мес", "Средневзвешенный по сегментам (ниже)", False),
        ("Месячный отток архивной когорты (c)", b["monthly_churn"], "%", "HYPOTHESIS — запрос D4", True),
        ("НДС", A.VAT, "%", "НК РУз: 12%", False),
        ("Курс, сум за 1 USD", A.FX_UZS_PER_USD, "сум", "ЦБ РУз, 2026: 11 950–12 205", False),
        ("Рынок мобильной связи РУз, абонентов", b["market_total_subs"], "абон.", "HYPOTHESIS: 35,6 млн на конец 2024 + рост", True),
        ("Выручка когорты в месяц (R0 мес. 0)", "=C7*C8", "сум/мес", "Формула", False),
    ]
    for i, (name, val, unit, src, key) in enumerate(inputs, 4):
        wi.cell(row=i, column=1, value=name).font = BLACK
        is_f = isinstance(val, str) and val.startswith("=")
        put(wi, i, 3, val, BLACK if is_f else BLUE, PCT if unit == "%" else NUM, YELLOW if key else None)
        wi.cell(row=i, column=4, value=unit)
        wi.cell(row=i, column=5, value=src)

    wi["A15"] = "Сегменты архивной когорты (HYPOTHESIS — проверить кластеризацией, запрос D2)"
    wi["A15"].font = BOLD
    for j, h in enumerate(["Код", "Сегмент", "Доля когорты", "ARPU net, сум", "Абонентов", "Выручка/мес, сум"], 1):
        wi.cell(row=16, column=j, value=h)
    style_header(wi, 16, 6)
    for i, (k, s) in enumerate(A.SEGMENTS.items(), 17):
        put(wi, i, 1, k)
        put(wi, i, 2, s["name"])
        put(wi, i, 3, s["share"], BLUE, PCT, YELLOW)
        put(wi, i, 4, s["arpu"], BLUE, NUM, YELLOW)
        put(wi, i, 5, f"=$C$7*C{i}", fmt=NUM)
        put(wi, i, 6, f"=E{i}*D{i}", fmt=NUM)
    wi["A22"] = "Итого"
    wi["A22"].font = BOLD
    put(wi, 22, 3, "=SUM(C17:C21)", BOLD, PCT)
    put(wi, 22, 5, "=SUM(E17:E21)", BOLD, NUM)
    put(wi, 22, 6, "=SUM(F17:F21)", BOLD, NUM)
    wi["A23"] = "Проверка: сумма долей = 100%"
    wi["C23"] = '=IF(ABS(C22-1)<0.0001,"OK","ОШИБКА: доли ≠ 100%")'
    for col, w in zip("ABCDEF", (48, 58, 16, 14, 64, 22)):
        wi.column_dimensions[col].width = w


N = "Inputs!$C$7"
ARPU0 = "Inputs!$C$8"
CH = "Inputs!$C$9"
VAT = "Inputs!$C$10"
FX = "Inputs!$C$11"
MKT = "Inputs!$C$12"

PARAMS = [
    ("Название", "name", None),
    ("Группа (EASY/HARD)", "group", None),
    ("Тип механики", "type", None),
    ("Сложность биллинг/интеграции (1–5)", "complexity", NUM),
    ("Портфель: 1 = базовый, 2 = опция (Stretch), 0 = не рекомендуется", "portfolio", NUM),
    ("ARPU целевого сегмента, сум", "segment_arpu", NUM),
    ("Доля целевой группы от когорты", "eligible_share", PCT),
    ("Охват коммуникацией", "reach", PCT),
    ("Конверсия (take-up)", "takeup", PCT),
    ("Каннибализация (сделали бы и так)", "cannibal", PCT),
    ("ΔARPU на адоптера, сум/мес", "delta", NUM),
    ("Доп. отток от изменения/контакта", "churn_incr", PCT),
    ("Снижение оттока адоптеров (отн.)", "churn_red", PCT),
    ("Доля адоптеров, активных через 6 мес. (A6)", "adopter_decay_6m", PCT),
    ("Повышение абонплаты, сум с НДС", "price_up_gross", NUM),
    ("Доля даунгрейда", "downgrade", PCT),
    ("Δ выручки при даунгрейде, сум/мес", "downgrade_delta", NUM),
    ("Себестоимость доп. трафика, сум/мес", "data_cost_m", NUM),
    ("Отн. прирост выручки когорты", "rel_uplift", PCT),
    ("Снижение оттока всей когорты (отн.)", "churn_red_base", PCT),
    ("Новые линии на адоптера", "new_lines", NUM1),
    ("ARPU новой линии, сум", "new_line_arpu", NUM),
    ("Стоимость контакта, сум", "cost_per_contact", NUM),
    ("Разовая стоимость на адоптера, сум", "cost_per_adopter_once", NUM),
    ("Перем. затраты на адоптера, сум/мес", "var_cost_m", NUM),
    ("Разовые затраты (внедрение), сум", "one_time", NUM),
    ("OPEX, сум/мес", "opex_m", NUM),
    ("Экономия OPEX, сум/мес", "opex_savings_m", NUM),
    ("Маржинальность инкр. выручки", "margin", PCT),
    ("Месяц запуска (1 = старт программы)", "launch", NUM),
    ("Набор до полного эффекта, мес", "ramp", NUM),
    ("Вероятность запуска как задумано", "exec_prob", PCT),
]
DERIVED = [
    ("Целевая группа, абон.", "elig", NUM),
    ("Охвачено коммуникацией, абон.", "contacted", NUM),
    ("Адоптеры при полном наборе (инкр.), абон.", "a_final", NUM),
    ("reprice: остаются и платят больше, абон.", "stay", NUM),
    ("reprice: ушли на более дешёвый ТП, абон.", "down", NUM),
    ("Доп. отток всего, абон.", "lost_total", NUM),
    ("Повышение абонплаты net, сум", "up_net", NUM),
    ("Темп «засыпания» адоптеров, в мес.", "decay_m", PCT2),
    ("Месяцев подготовки (разовые затраты)", "build", NUM),
    ("Месяцев распределения доп. оттока", "K", NUM),
    ("Месяц оценки (12-й после запуска, ≤24)", "eval_m", NUM),
]
SUMMARY = [
    ("Выручка Y1 (мес. 1–12), сум", "rev1", NUM),
    ("Выручка Y2 (мес. 13–24), сум", "rev2", NUM),
    ("Run-rate выручки/год на мес. 24, сум", "runrate", NUM),
    ("Run-rate выручки/год, USD", "runrate_usd", NUM),
    ("Затраты за 24 мес., сум", "cost24", NUM),
    ("Вклад (маржа − затраты) за 24 мес., сум", "contrib24", NUM),
    ("ROI за 24 мес. (вклад / затраты)", "roi", MULT),
    ("ΔARPU когорты на месяц оценки", "upl_eval", PCT2),
    ("ΔARPU когорты на мес. 24", "upl24", PCT2),
    ("Δ абонентов к мес. 24 (вкл. новые линии)", "dsubs24", NUM),
    ("Δ доли рынка к мес. 24, п.п.", "dshare", NUM3),
    ("Ожидаемый вклад с учётом P(запуска), сум", "exp_contrib", NUM),
]
BLOCK = ["f", "target", "new", "R", "pool", "L", "rev", "rev_ext", "cost", "contrib", "dsubs", "dsubs_ext"]
BLOCK_LABEL = {
    "f": "Доля набора", "target": "Адоптеры (цель)", "new": "Новые адоптеры", "R": "Удержанные (эффект оттока)",
    "pool": "Пул адоптеров", "L": "Потерянные из-за инициативы", "rev": "Инкр. выручка когорты",
    "rev_ext": "Выручка новых линий", "cost": "Затраты", "contrib": "Вклад", "dsubs": "Δ абонентов когорты",
    "dsubs_ext": "Новые линии",
}
BLOCK_FMT = {"f": PCT}
MONTH_COL0 = 3  # колонка C = месяц 1


def mcol(m):
    return get_column_letter(MONTH_COL0 + m - 1)


def build():
    wb = Workbook()
    sheet_readme(wb)
    sheet_inputs(wb)
    keys = list(A.INITIATIVES)

    # ------------------------------------------------------------------ Initiatives
    wn = wb.create_sheet("Initiatives")
    wn["A1"] = "Инициативы: параметры (синие) → производные (чёрные) → итоги из листа Monthly (зелёные)"
    wn["A1"].font = TITLE
    wn.cell(row=3, column=1, value="Параметр")
    wn.cell(row=3, column=2, value="Ключ")
    for j, k in enumerate(keys, 3):
        wn.cell(row=3, column=j, value=k)
    style_header(wn, 3, 2 + len(keys))
    rowof = {}
    r = 4
    for label, key, fmt in PARAMS:
        rowof[key] = r
        wn.cell(row=r, column=1, value=label)
        wn.cell(row=r, column=2, value=key)
        for j, k in enumerate(keys, 3):
            p = A.INITIATIVES[k]
            if key == "portfolio":
                v = 0 if p.get("not_recommended") else (2 if p.get("optional") else 1)
            elif key == "adopter_decay_6m":
                v = mode(p.get(key, 1))
            elif key in ("name", "group", "type"):
                v = p.get(key, "")
            else:
                v = mode(p.get(key, 0))
            c = put(wn, r, j, v, BLUE, fmt)
            if key == "name":
                c.alignment = Alignment(wrap_text=True, vertical="top")
            if isinstance(p.get(key), (tuple, list)):
                lo, _, hi = p[key]
                c.comment = Comment(f"Диапазон Монте-Карло: {lo:,} … {hi:,}", "model")
        r += 1
    r += 1
    wn.cell(row=r, column=1, value="ПРОИЗВОДНЫЕ").font = BOLD
    for j in range(1, 3 + len(keys)):
        wn.cell(row=r, column=j).fill = SEC_FILL
    r += 1
    for label, key, fmt in DERIVED:
        rowof[key] = r
        wn.cell(row=r, column=1, value=label)
        wn.cell(row=r, column=2, value=key)
        r += 1
    r += 1
    wn.cell(row=r, column=1, value="ИТОГИ (из листа Monthly)").font = BOLD
    for j in range(1, 3 + len(keys)):
        wn.cell(row=r, column=j).fill = SEC_FILL
    r += 1
    for label, key, fmt in SUMMARY:
        rowof[key] = r
        wn.cell(row=r, column=1, value=label)
        wn.cell(row=r, column=2, value=key)
        r += 1

    # ------------------------------------------------------------------ Monthly
    wm = wb.create_sheet("Monthly")
    wm["A1"] = "Помесячный движок, 24 мес. (формулы; сум без НДС)"
    wm["A1"].font = TITLE
    wm.cell(row=3, column=1, value="Месяц")
    for m in range(1, H + 1):
        wm.cell(row=3, column=MONTH_COL0 + m - 1, value=m)
    style_header(wm, 3, MONTH_COL0 + H - 1)
    wm.cell(row=4, column=1, value="S0: абоненты когорты без инициатив")
    wm.cell(row=5, column=1, value="R0: выручка когорты без инициатив")
    for m in range(1, H + 1):
        col = mcol(m)
        put(wm, 4, MONTH_COL0 + m - 1, f"={N}*(1-{CH})^{col}$3", fmt=NUM)
        put(wm, 5, MONTH_COL0 + m - 1, f"={col}4*{ARPU0}", fmt=NUM)

    brow = {}  # (key, item) -> row
    r = 7
    for k in keys:
        jcol = get_column_letter(3 + keys.index(k))
        wm.cell(row=r, column=1, value=f"{k} — {A.INITIATIVES[k]['name']}").font = BOLD
        for c in range(1, MONTH_COL0 + H):
            wm.cell(row=r, column=c).fill = SEC_FILL
        r += 1
        for item in BLOCK:
            brow[(k, item)] = r
            wm.cell(row=r, column=1, value=BLOCK_LABEL[item])
            wm.cell(row=r, column=2, value=item)
            r += 1
        r += 1

        def P(key):
            return f"Initiatives!${jcol}${rowof[key]}"

        for m in range(1, H + 1):
            X = mcol(m)
            W = get_column_letter(MONTH_COL0 + m - 2)  # предыдущий месяц (для m=1 — колонка B, пустая)
            mm = f"{X}$3"

            def R_(item, col=X):
                return f"{col}{brow[(k, item)]}"

            fml = {
                "f": f"=IF({mm}<{P('launch')},0,MIN(({mm}-{P('launch')}+1)/{P('ramp')},1))",
                "target": f"={P('a_final')}*{R_('f')}",
                "new": f"=MAX({R_('target')}-N({R_('target', W)}),0)",
                "R": (f'=IF({P("type")}="adoption",N({R_("R", W)})*(1-{CH})+N({R_("pool", W)})*{CH}*{P("churn_red")},'
                      f'IF({P("type")}="relative",N({R_("R", W)})*(1-{CH})+{X}$4*{CH}*{P("churn_red_base")}*{R_("f")},0))'),
                "pool": f"=N({R_('pool', W)})*(1-{P('decay_m')})*(1-{CH}*(1-{P('churn_red')}))+{R_('new')}",
                "L": (f"=N({R_('L', W)})*(1-{CH})+IF(AND({mm}>={P('launch')},{mm}<{P('launch')}+{P('K')}),"
                      f"{P('lost_total')}/{P('K')},0)"),
                "rev": (f'=IF({P("type")}="adoption",{R_("pool")}*{P("delta")}+{R_("R")}*{P("segment_arpu")}-{R_("L")}*{P("segment_arpu")},'
                        f'IF({P("type")}="reprice",IF({mm}>={P("launch")},({P("stay")}*{P("up_net")}+{P("down")}*{P("downgrade_delta")})'
                        f'*(1-{CH})^({mm}-{P("launch")}),0)-{R_("L")}*{P("segment_arpu")},'
                        f'{X}$5*{P("rel_uplift")}*{R_("f")}+{R_("R")}*{ARPU0}))'),
                "rev_ext": f"={R_('pool')}*{P('new_lines')}*{P('new_line_arpu')}",
                "cost": (f"=IF({mm}<={P('build')},{P('one_time')}/{P('build')},0)+IF({mm}>={P('launch')},{P('opex_m')},0)"
                         f"+IF({mm}={P('launch')},{P('contacted')}*{P('cost_per_contact')},0)"
                         f"+{R_('new')}*{P('cost_per_adopter_once')}+{R_('pool')}*{P('var_cost_m')}"
                         f'+IF(AND({P("type")}="reprice",{mm}>={P("launch")}),{P("stay")}*{P("data_cost_m")}*(1-{CH})^({mm}-{P("launch")})'
                         f"-{P('opex_savings_m')},0)"),
                "contrib": f"=({R_('rev')}+{R_('rev_ext')})*{P('margin')}-{R_('cost')}",
                "dsubs": f"={R_('R')}-{R_('L')}",
                "dsubs_ext": f"={R_('pool')}*{P('new_lines')}",
            }
            for item in BLOCK:
                put(wm, brow[(k, item)], MONTH_COL0 + m - 1, fml[item], fmt=BLOCK_FMT.get(item, NUM))

    # портфель: итоговые строки
    first, last = mcol(1), mcol(H)
    wm.cell(row=r, column=1, value="ПОРТФЕЛЬ (детерминированный, все рекомендуемые инициативы запущены)").font = BOLD
    for c in range(1, MONTH_COL0 + H):
        wm.cell(row=r, column=c).fill = SEC_FILL
    r += 1
    prow = {}
    port_items = [
        ("core_rev", "Базовый: Σ выручка когорты до перекрытия", "rev", "core"),
        ("core_ext", "Базовый: Σ выручка новых линий", "rev_ext", "core"),
        ("core_dsubs", "Базовый: Σ Δ абонентов когорты", "dsubs", "core"),
        ("core_contrib", "Базовый: Σ вклад", "contrib", "core"),
        ("all_rev", "Stretch: Σ выручка когорты до перекрытия", "rev", "all"),
        ("all_dsubs", "Stretch: Σ Δ абонентов когорты", "dsubs", "all"),
        ("core_arpu", "Базовый: ARPU когорты после перекрытия, сум", None, None),
        ("core_upl", "Базовый: ΔARPU когорты", None, None),
        ("all_arpu", "Stretch: ARPU когорты после перекрытия, сум", None, None),
        ("all_upl", "Stretch: ΔARPU когорты", None, None),
    ]
    for key, label, _, _ in port_items:
        prow[key] = r
        wm.cell(row=r, column=1, value=label).font = BOLD
        r += 1
    HC = "Portfolio!$C$3"
    for m in range(1, H + 1):
        X = mcol(m)
        cidx = MONTH_COL0 + m - 1
        for key, _, item, scope in port_items:
            if item is None:
                continue
            terms = []
            for k in keys:
                jcol = get_column_letter(3 + keys.index(k))
                ref = f"{X}{brow[(k, item)]}"
                flag = f"Initiatives!${jcol}${rowof['portfolio']}"
                if scope == "core":
                    terms.append(f"{ref}*({flag}=1)")
                else:
                    terms.append(f"{ref}*({flag}>=1)")
            put(wm, prow[key], cidx, "=" + "+".join(terms), fmt=NUM)
        put(wm, prow["core_arpu"], cidx,
            f"=({X}$5+{X}{prow['core_rev']}*(1-{HC}))/({X}$4+{X}{prow['core_dsubs']}*(1-{HC}))", fmt=NUM)
        put(wm, prow["core_upl"], cidx, f"={X}{prow['core_arpu']}/{ARPU0}-1", fmt=PCT)
        put(wm, prow["all_arpu"], cidx,
            f"=({X}$5+{X}{prow['all_rev']}*(1-{HC}))/({X}$4+{X}{prow['all_dsubs']}*(1-{HC}))", fmt=NUM)
        put(wm, prow["all_upl"], cidx, f"={X}{prow['all_arpu']}/{ARPU0}-1", fmt=PCT)
    wm.column_dimensions["A"].width = 58
    wm.column_dimensions["B"].width = 10
    for m in range(1, H + 1):
        wm.column_dimensions[mcol(m)].width = 15
    wm.freeze_panes = "C4"

    # ------------------------------------------------------------------ Initiatives formulas
    for j, k in enumerate(keys, 3):
        jcol = get_column_letter(j)

        def P(key):
            return f"{jcol}${rowof[key]}"

        def row_rng(item, m1=1, m2=H):
            rr = brow[(k, item)]
            return f"Monthly!{mcol(m1)}{rr}:{mcol(m2)}{rr}"

        def at(item, month_expr):
            rr = brow[(k, item)]
            return f"INDEX(Monthly!${first}${rr}:${last}${rr},1,{month_expr})"

        der = {
            "elig": f"={N}*{P('eligible_share')}",
            "contacted": f'=IF({P("type")}="adoption",{P("elig")}*{P("reach")},IF({P("type")}="reprice",{P("elig")},0))',
            "a_final": f'=IF({P("type")}="adoption",{P("contacted")}*{P("takeup")}*(1-{P("cannibal")}),0)',
            "stay": f'=IF({P("type")}="reprice",{P("elig")}*(1-{P("downgrade")}-{P("churn_incr")}),0)',
            "down": f'=IF({P("type")}="reprice",{P("elig")}*{P("downgrade")},0)',
            "lost_total": f'=IF({P("type")}="relative",0,{P("contacted")}*{P("churn_incr")})',
            "up_net": f"={P('price_up_gross')}/(1+{VAT})",
            "decay_m": f"=1-{P('adopter_decay_6m')}^(1/6)",
            "build": f"=MAX({P('launch')}-1,1)",
            "K": f'=IF({P("type")}="reprice",2,3)',
            "eval_m": f"=MIN({P('launch')}+11,{H})",
        }
        for label, key, fmt in DERIVED:
            put(wn, rowof[key], j, der[key], BLACK, fmt)
        summ = {
            "rev1": f"=SUM({row_rng('rev', 1, 12)})+SUM({row_rng('rev_ext', 1, 12)})",
            "rev2": f"=SUM({row_rng('rev', 13, H)})+SUM({row_rng('rev_ext', 13, H)})",
            "runrate": f"=(Monthly!{last}{brow[(k, 'rev')]}+Monthly!{last}{brow[(k, 'rev_ext')]})*12",
            "runrate_usd": f"={P('runrate')}/{FX}",
            "cost24": f"=SUM({row_rng('cost')})",
            "contrib24": f"=SUM({row_rng('contrib')})",
            "roi": f"=IF({P('cost24')}>0,{P('contrib24')}/{P('cost24')},0)",
            "upl_eval": (f"=(INDEX(Monthly!${first}$5:${last}$5,1,{P('eval_m')})+{at('rev', P('eval_m'))})"
                         f"/(INDEX(Monthly!${first}$4:${last}$4,1,{P('eval_m')})+{at('dsubs', P('eval_m'))})/{ARPU0}-1"),
            "upl24": (f"=(Monthly!{last}$5+Monthly!{last}{brow[(k, 'rev')]})"
                      f"/(Monthly!{last}$4+Monthly!{last}{brow[(k, 'dsubs')]})/{ARPU0}-1"),
            "dsubs24": f"=Monthly!{last}{brow[(k, 'dsubs')]}+Monthly!{last}{brow[(k, 'dsubs_ext')]}",
            "dshare": f"=IF({MKT}>0,{P('dsubs24')}/{MKT}*100,0)",
            "exp_contrib": f"={P('contrib24')}*{P('exec_prob')}",
        }
        for label, key, fmt in SUMMARY:
            font = BLACK if key in ("runrate_usd", "roi", "dshare", "exp_contrib") else GREEN
            put(wn, rowof[key], j, summ[key], font, fmt)
    wn.column_dimensions["A"].width = 52
    wn.column_dimensions["B"].width = 20
    for j in range(3, 3 + len(keys)):
        wn.column_dimensions[get_column_letter(j)].width = 19
    wn.row_dimensions[rowof["name"]].height = 80
    wn.freeze_panes = "C4"

    # ------------------------------------------------------------------ Portfolio
    wp = wb.create_sheet("Portfolio")
    wp["A1"] = "Портфель: базовый кейс (детерминированный) — вероятностный прогноз см. MC_Results"
    wp["A1"].font = TITLE
    wp["A3"] = "Перекрытие эффектов (haircut)"
    put(wp, 3, 3, mode(A.PORTFOLIO_OVERLAP_HAIRCUT), BLUE, PCT, YELLOW)
    wp["D3"] = "Доля эффекта, «съедаемая» пересечением целевых групп (одни и те же абоненты в нескольких инициативах)"
    hdr = ["#", "Инициатива", "Группа", "Портфель (1/2/0)", "Выручка Y1", "Выручка Y2", "Run-rate/год", "Вклад 24 мес",
           "Затраты 24 мес", "ROI", "ΔARPU (мес. оценки)", "Δ доли, п.п.", "P(запуска)", "Ожид. вклад"]
    for j, h in enumerate(hdr, 1):
        wp.cell(row=5, column=j, value=h)
    style_header(wp, 5, len(hdr))
    src = ["key", "name", "group", "portfolio", "rev1", "rev2", "runrate", "contrib24", "cost24", "roi", "upl_eval",
           "dshare", "exec_prob", "exp_contrib"]
    fmts = [None, None, None, NUM, NUM, NUM, NUM, NUM, NUM, MULT, PCT2, NUM3, PCT, NUM]
    for i, k in enumerate(keys, 6):
        jcol = get_column_letter(3 + keys.index(k))
        for j, (s, f_) in enumerate(zip(src, fmts), 1):
            v = k if s == "key" else f"=Initiatives!{jcol}{rowof[s]}"
            c = put(wp, i, j, v, BLACK if s == "key" else GREEN, f_)
            if s == "name":
                c.alignment = Alignment(wrap_text=True)
    lastr = 5 + len(keys)
    s0 = lastr + 2
    wp.cell(row=s0, column=1, value="Итоги портфеля").font = BOLD
    lines = [
        ("Базовый: выручка Y1 после перекрытия, сум",
         f"=SUMIFS(E6:E{lastr},$D$6:$D${lastr},1)*(1-$C$3)", NUM),
        ("Базовый: выручка Y2 после перекрытия, сум",
         f"=SUMIFS(F6:F{lastr},$D$6:$D${lastr},1)*(1-$C$3)", NUM),
        ("Базовый: run-rate/год на мес. 24 после перекрытия, сум",
         f"=SUMIFS(G6:G{lastr},$D$6:$D${lastr},1)*(1-$C$3)", NUM),
        ("Базовый: run-rate/год, USD", f"=C{s0+3}/{FX}", '"$"#,##0'),
        ("Базовый: вклад 24 мес. = маржа × (1 − перекрытие) − затраты",
         f"=(SUMIFS(H6:H{lastr},$D$6:$D${lastr},1)+SUMIFS(I6:I{lastr},$D$6:$D${lastr},1))*(1-$C$3)"
         f"-SUMIFS(I6:I{lastr},$D$6:$D${lastr},1)", NUM),
        ("Базовый: ARPU когорты до, сум", f"={ARPU0}", NUM),
        ("Базовый: ARPU когорты на мес. 12, сум", f"=Monthly!{mcol(12)}{prow['core_arpu']}", NUM),
        ("Базовый: ARPU когорты на мес. 24, сум", f"=Monthly!{last}{prow['core_arpu']}", NUM),
        ("Базовый: ΔARPU когорты на мес. 12", f"=Monthly!{mcol(12)}{prow['core_upl']}", PCT),
        ("Базовый: ΔARPU когорты на мес. 24", f"=Monthly!{last}{prow['core_upl']}", PCT),
        ("Stretch (+опции): ΔARPU когорты на мес. 24", f"=Monthly!{last}{prow['all_upl']}", PCT),
        ("Базовый: прирост выручки когорты (run-rate), % к базе",
         f"=IF(Inputs!C13>0,C{s0+3}/(Inputs!C13*12),0)", PCT),
        ("Базовый: Δ доли рынка к мес. 24, п.п.",
         f"=SUMIFS(L6:L{lastr},$D$6:$D${lastr},1)*(1-$C$3)", NUM3),
    ]
    for i, (lab, f_, fm) in enumerate(lines, s0 + 1):
        wp.cell(row=i, column=1, value=lab)
        put(wp, i, 3, f_, BOLD, fm)
    # динамика ARPU
    t0 = s0 + len(lines) + 3
    wp.cell(row=t0, column=1, value="Динамика ΔARPU когорты по месяцам").font = BOLD
    wp.cell(row=t0 + 1, column=1, value="Месяц")
    wp.cell(row=t0 + 2, column=1, value="Базовый портфель")
    wp.cell(row=t0 + 3, column=1, value="Stretch (+A8)")
    for m in range(1, H + 1):
        put(wp, t0 + 1, 2 + m, m, BLACK, NUM)
        put(wp, t0 + 2, 2 + m, f"=Monthly!{mcol(m)}{prow['core_upl']}", GREEN, PCT)
        put(wp, t0 + 3, 2 + m, f"=Monthly!{mcol(m)}{prow['all_upl']}", GREEN, PCT)
    ch = LineChart()
    ch.title = "ΔARPU архивной когорты, базовый кейс"
    ch.y_axis.title = "ΔARPU"
    ch.x_axis.title = "Месяц"
    ch.y_axis.number_format = "0%"
    data = Reference(wp, min_col=1, max_col=2 + H, min_row=t0 + 2, max_row=t0 + 3)
    ch.add_data(data, from_rows=True, titles_from_data=True)
    ch.set_categories(Reference(wp, min_col=3, max_col=2 + H, min_row=t0 + 1))
    ch.height, ch.width = 8, 22
    wp.add_chart(ch, f"A{t0 + 5}")
    wp.column_dimensions["A"].width = 58
    wp.column_dimensions["B"].width = 50
    for col in range(3, 3 + H):
        wp.column_dimensions[get_column_letter(col)].width = 14

    # ------------------------------------------------------------------ AB calculator
    wa = wb.create_sheet("AB_Calculator")
    wa["A1"] = "Калькулятор размера выборки A/B (двусторонний тест)"
    wa["A1"].font = TITLE
    items = [
        ("Уровень значимости alpha", 0.05, PCT),
        ("Мощность (power)", 0.80, PCT),
        ("Коэф. вариации ARPU σ/μ (из данных, запрос D6)", 1.2, "0.00"),
        ("Минимальный детектируемый эффект (MDE), отн.", 0.03, PCT),
    ]
    for i, (lab, v, fm) in enumerate(items, 3):
        wa.cell(row=i, column=1, value=lab)
        put(wa, i, 2, v, BLUE, fm, YELLOW)
    wa["A8"] = "N на группу — ARPU (t-тест)"
    put(wa, 8, 2, "=ROUNDUP(2*(NORMSINV(1-B3/2)+NORMSINV(B4))^2*B5^2/B6^2,0)", BOLD, NUM)
    wa["A10"] = "Конверсия/отток в контроле p1"
    put(wa, 10, 2, 0.10, BLUE, PCT, YELLOW)
    wa["A11"] = "Конверсия/отток в тесте p2"
    put(wa, 11, 2, 0.11, BLUE, PCT, YELLOW)
    wa["A12"] = "N на группу — пропорции"
    put(wa, 12, 2, ("=ROUNDUP((NORMSINV(1-B3/2)*SQRT(2*((B10+B11)/2)*(1-(B10+B11)/2))"
                    "+NORMSINV(B4)*SQRT(B10*(1-B10)+B11*(1-B11)))^2/(B11-B10)^2,0)"), BOLD, NUM)
    wa["A14"] = ("Рекомендация: holdout 5–10% целевой группы на весь срок программы; стратификация по сегменту, "
                 "региону, тенуре, типу устройства; фиксировать гипотезу и MDE до старта (pre-registration).")
    wa.column_dimensions["A"].width = 64
    wa.column_dimensions["B"].width = 16

    # ------------------------------------------------------------------ MC results
    wr = wb.create_sheet("MC_Results")
    wr["A1"] = "Результаты Монте-Карло (20 000 прогонов) — значения из model/output/results.json"
    wr["A1"].font = TITLE
    wr["A2"] = ("Выход внешней модели (python model/arpu_model.py), не формулы. Млрд сум без НДС. "
                "Шанс успеха = P(вклад 24м > 0 и ΔARPU > 0) × P(запуска). Бизнес-кейс = ≥70% плана по вкладу и ΔARPU.")
    res_path = os.path.join(HERE, "output", "results.json")
    if os.path.exists(res_path):
        res = json.load(open(res_path, encoding="utf-8"))
        hdr = ["#", "Инициатива", "Группа", "Выручка Y1 P10", "Выручка Y1 P50", "Выручка Y1 P90",
               "Вклад 24м P10", "Вклад 24м P50", "Вклад 24м P90", "ΔARPU P50", "P(вклад>0)",
               "P(запуска)", "Шанс успеха", "Шанс ≥70% бизнес-кейса"]
        for j, h in enumerate(hdr, 1):
            wr.cell(row=4, column=j, value=h)
        style_header(wr, 4, len(hdr))
        for i, x in enumerate(res["initiatives"], 5):
            vals = [x["key"], x["name"], x["group"], *[round(v, 2) for v in x["rev_y1_bn"]],
                    *[round(v, 2) for v in x["contrib_24_bn"]], x["arpu_uplift_12m_after_launch"][1],
                    x["p_contrib_positive"], x["exec_prob"], x["success_chance"], x["business_case_chance"]]
            fm = [None, None, None, NUM1, NUM1, NUM1, NUM1, NUM1, NUM1, PCT2, PCT, PCT, PCT, PCT]
            for j, (v, f_) in enumerate(zip(vals, fm), 1):
                put(wr, i, j, v, BLUE, f_)
        r = 6 + len(res["initiatives"])
        wr.cell(row=r, column=1, value="Портфель (с учётом P(запуска) каждой инициативы и перекрытия)").font = BOLD
        hdr2 = ["Сценарий", "", "ΔARPU мес.12 P50", "ΔARPU мес.24 P10", "ΔARPU мес.24 P50", "ΔARPU мес.24 P90",
                "Выручка Y1 P50", "Выручка Y2 P50", "Вклад 24м P50", "P(ΔARPU≥10%)", "P(ΔARPU≥15%)", "P(ΔARPU≥20%)"]
        for j, h in enumerate(hdr2, 1):
            wr.cell(row=r + 1, column=j, value=h)
        style_header(wr, r + 1, len(hdr2))
        for i, (lab, key) in enumerate((("Базовый", "portfolio_all"), ("Только EASY", "portfolio_easy"),
                                        ("Только HARD", "portfolio_hard"), ("Stretch (+A8)", "portfolio_stretch")), r + 2):
            pr = res[key]
            vals = [lab, "", pr["arpu_uplift_m12"][1], *pr["arpu_uplift_m24"], round(pr["rev_y1_bn"][1], 1),
                    round(pr["rev_y2_bn"][1], 1), round(pr["contrib_24_bn"][1], 1),
                    pr["p_uplift_m24_ge"]["0.1"], pr["p_uplift_m24_ge"]["0.15"], pr["p_uplift_m24_ge"]["0.2"]]
            fm = [None, None, PCT, PCT, PCT, PCT, NUM1, NUM1, NUM1, PCT, PCT, PCT]
            for j, (v, f_) in enumerate(zip(vals, fm), 1):
                put(wr, i, j, v, BLUE, f_)
    wr.column_dimensions["A"].width = 14
    wr.column_dimensions["B"].width = 62
    for j in range(3, 15):
        wr.column_dimensions[get_column_letter(j)].width = 16

    # единый шрифт
    for sh in wb.worksheets:
        for row in sh.iter_rows():
            for c in row:
                f = c.font
                if f is None or f.name != FONT:
                    c.font = Font(name=FONT, bold=bool(f and f.bold), color=f.color if f else None,
                                  size=f.size if f and f.size else 11)
    wb.calculation.fullCalcOnLoad = True
    wb.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    build()
