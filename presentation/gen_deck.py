import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deck")
S = os.path.join(ROOT, "project", "slides")
os.makedirs(S, exist_ok=True)

INK = "#14213D"; PAPER = "#F7F5F0"; CARD = "#FDFCF9"; LINE = "#E2DED3"
BODY = "#3D4A5C"; MUTED = "#5F6B7A"; ORANGE_T = "#A94A12"; ORANGE = "#C2571A"
BLUE = "#2B5FA6"; SOFT = "#B8C4D9"; ORANGE_L = "#F2A76B"
H = "font-family:'Rubik', Arial, sans-serif"
T = "font-family:'IBM Plex Sans', Arial, sans-serif"

LIGHT = f"background:{PAPER};color:{BODY};{T};padding:128px 128px 160px;display:flex;flex-direction:column;gap:32px"
DARK = f"background:{INK};color:{PAPER};{T};padding:128px 128px 160px;display:flex;flex-direction:column;gap:32px"

slides = []
outline = []


def head(eyebrow, title, dark=False):
    ec = ORANGE_L if dark else ORANGE_T
    tc = PAPER if dark else INK
    return (f'<div style="display:flex;flex-direction:column;gap:16px">'
            f'<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;font-weight:600;color:{ec}">{eyebrow}</p>'
            f'<h2 style="{H};font-size:64px;font-weight:600;line-height:1.1;color:{tc}">{title}</h2></div>')


def foot(n, text="Инициатива «Архивная база» · сценарий P50 с поправкой на риск", dark=False):
    c = SOFT if dark else MUTED
    return (f'<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:{c}">'
            f'{text} · {n}</p>')


def add(sid, body, notes, dark=False, section=None):
    style = DARK if dark else LIGHT
    html = f'<section id="{sid}" data-transition="fade" style="{style}">\n{body}\n<aside>{notes}</aside>\n</section>\n'
    slides.append((sid, html, section))
    outline.append((sid, body, notes))


def card(inner, pad=32, border=None):
    border = border or f"1px solid {LINE}"
    return (f'<div style="flex:1;display:flex;flex-direction:column;gap:12px;background:{CARD};padding:{pad}px;'
            f'border:{border};border-radius:16px">{inner}</div>')


def stat(num, label, color=INK, lc=BODY):
    return (f'<p style="{H};font-size:64px;font-weight:600;line-height:1.1;color:{color}">{num}</p>'
            f'<p style="font-size:24px;line-height:1.4;color:{lc}">{label}</p>')


def table(headers, rows, widths, size=26):
    th = "".join(f'<th style="width:{w}%;text-align:left">{h}</th>' for h, w in zip(headers, widths))
    trs = []
    for i, r in enumerate(rows):
        bg = f' style="background:{CARD}"' if i % 2 == 0 else ""
        trs.append(f"<tr{bg}>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    return (f'<table style="font-size:{size}px;color:{BODY};{T};width:1664px">'
            f'<tr style="background:#E9E5DA">{th}</tr>' + "".join(trs) + "</table>")


# 1 COVER -------------------------------------------------------------------
stats = "".join(
    f'<div style="flex:1;display:flex;flex-direction:column;gap:8px;border-top:2px solid {ORANGE_L};padding:24px 0 0 0">'
    f'<p style="{H};font-size:64px;font-weight:600;line-height:1.1;color:{PAPER}">{n}</p>'
    f'<p style="font-size:24px;line-height:1.4;color:{SOFT}">{l}</p></div>'
    for n, l in [("+11,5%", "ARPU архивной когорты к мес. 24 (P50 с поправкой на риск)"),
                 ("≈ $5,1 млн", "доп. выручки в год на выходе (run-rate)"),
                 ("61%", "вероятность выйти на ARPU ≥ +10% (75% с опцией A8)")])
add("cover", f"""<div style="display:flex;flex-direction:column;gap:32px">
<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;font-weight:600;color:{ORANGE_L}">Продуктовая инициатива · тарифные планы</p>
<h1 style="{H};font-size:96px;font-weight:600;line-height:1.1;color:{PAPER}">Рост ARPU архивной базы Ucell</h1>
<p style="font-size:28px;line-height:1.4;color:{SOFT};width:1300px">Портфель инициатив EASY / HARD, бизнес-кейс и шансы на успех — только для абонентов архивных тарифов</p>
</div>
<div style="flex:1"></div>
<div style="display:flex;gap:48px">{stats}</div>
{foot("", "Защита перед руководством · ноябрь 2026 · [ФИО, продакт-менеджер тарифных планов]", True).replace(" · </p>", "</p>")}""",
    "Цель встречи — утвердить программу роста ARPU архивной базы. Три цифры: +11,5% ARPU когорты за 24 месяца с учётом всех рисков, около 5 млн долларов дополнительной выручки в год на выходе и 61% вероятность выйти на +10%. Все цифры — из модели Монте-Карло на 20 000 сценариев; размеры базы — гипотезы до получения данных.",
    dark=True, section="s1")

# 2 PROBLEM -----------------------------------------------------------------
cards = "".join(card(stat(n, l)) for n, l in [
    ("3,52 млн", "активных абонентов на архивных тарифах"),
    ("18 500 сум", "ARPU когорты (~$1,5) — ниже актуальной линейки 27–90 тыс. сум"),
    ("781 млрд сум", "выручка когорты в год (~$65 млн), не индексировалась")])
ctx = "".join(f'<p style="flex:1;font-size:28px;line-height:1.4;color:{BODY};border-left:4px solid {ORANGE};padding:0 0 0 20px">{t}</p>' for t in [
    "Инфляция 7,3% (2025) и ~6,5% (2026) обесценивает фиксированную абонплату",
    "Рынок перешёл к more-for-more: Ucell 02/2026, Beeline Oila 105 → 155 тыс.",
    "Архивные тарифы дороги в поддержке: каталог, биллинг, контакт-центр"])
add("problem", f"""{head("Проблема", "3,5 млн абонентов платят по ценам прошлых лет")}
<div style="display:flex;gap:32px">{cards}</div>
<div style="display:flex;gap:32px">{ctx}</div>
{foot(2, "Размер и ARPU когорты — гипотезы (11 млн × 40% на архиве × 80% активны) до данных D1–D3")}""",
    "Архивная база — это около трети абонентов Ucell, но заметно меньшая доля выручки: они живут по старым ценам. Пока рынок перешёл к more-for-more, а инфляция съедает 6–7% в год, эти абоненты платят меньше, чем за сопоставимый пакет в актуальной линейке. Важно: цифры базы — рабочие гипотезы, они заменяются фактом одной выгрузкой, и модель пересчитывается автоматически.",
    section=None)

# 3 METRIC ------------------------------------------------------------------
wrong = card(f'<p style="font-size:24px;letter-spacing:2px;text-transform:uppercase;font-weight:600;color:{MUTED}">Так считать нельзя</p>'
             f'<h3 style="{H};font-size:40px;font-weight:600;line-height:1.2;color:{INK}">ARPU текущего архива</h3>'
             f'<p style="font-size:28px;line-height:1.4;color:{BODY}">Успешная миграция уводит лучших абонентов на новые тарифы — ARPU «архива» падает, хотя выручка растёт</p>')
right = card(f'<p style="font-size:24px;letter-spacing:2px;text-transform:uppercase;font-weight:600;color:{BLUE}">Предлагаем утвердить</p>'
             f'<h3 style="{H};font-size:40px;font-weight:600;line-height:1.2;color:{INK}">ARPU когорты T0</h3>'
             f'<p style="font-size:28px;line-height:1.4;color:{BODY}">Все, кто был на архивных тарифах 01.11.2026, остаются в расчёте, даже после перехода — видим реальный эффект</p>',
             border=f"2px solid {BLUE}")
add("metric", f"""{head("Метрика", "Договоримся о метрике: ARPU когорты, а не архива")}
<div style="display:flex;gap:32px">{wrong}{right}</div>
<p style="font-size:28px;line-height:1.4;color:{BODY}">Рядом всегда показываем <b>выручку когорты</b> и <b>отток</b>: ARPU может расти и от ухода низкодоходных абонентов — это не наша цель.</p>
{foot(3)}""",
    "Это первое решение, о котором прошу: зафиксировать когортную метрику. Иначе через полгода отчёт покажет падение ARPU архива именно потому, что программа работает — лучшие абоненты перешли на новые тарифы. Рядом всегда выручка и отток, чтобы рост ARPU не был просто эффектом ухода дешёвых абонентов.")

# 4 MARKET ------------------------------------------------------------------
rows = [
    ["Ucell, 03.02.2026: +5 000 сум на 8 тарифах с +ГБ, пенсионеры исключены", "Первая волна пройдена — это естественный эксперимент для калибровки"],
    ["Beeline Oila Max: 105 → 125 → 155 тыс. сум (03/2026)", "Конкуренты повышают; публичная критика «платим за ненужные ГБ»"],
    ["Правила связи с 01/2026: уведомление ≥ 15 дней, смена тарифа бесплатна, номер хранится 1 год", "Даунгрейд заложен в модель; «спящих» монетизируем только добровольно"],
    ["Комитет по конкуренции, 11/2025: запрос обоснований повышения цен", "Только точечно, с досье обоснования и независимо от конкурентов"],
    ["Переводы трудовых мигрантов — $18,9 млрд (2025)", "Отдельный сегмент с пакетами «Musofir»"],
]
add("market", f"""{head("Контекст рынка", "Рынок уже перешёл к more-for-more, регулятор наблюдает")}
{table(["Факт", "Что это значит для нас"], rows, [52, 48], 24)}
{foot(4, "Источники: ucell.uz, kun.uz 28.01.2026 и 08.03.2026, gazeta.uz 18.11.2025, ЦБ РУз")}""",
    "Ключевой вывод: лёгкая ценовая волна уже частично пройдена, а регулятор смотрит на повышения. Поэтому следующий шаг должен быть точечным, ценностным и доказуемым данными: не всем плюс пять тысяч, а только тем, кто объективно недоплачивает, с подарком до и бесплатной альтернативой после.",
    section="s2")

# 5 BENCHMARKS --------------------------------------------------------------
rows = [
    ["Россия: МТС, Билайн, МегаФон, T2", "Индексация архивных тарифов +10% (2022), +15–20% (T2, 2026)", "Повторяют ежегодно, выручка растёт"],
    ["США: AT&T 2022, T-Mobile 2024", "Legacy-планы +$5–6 на линию", "ARPU ↑; отток T-Mobile 0,86% → 0,93% — «в рамках ожиданий»"],
    ["Индия: Jio, Airtel, 07/2024", "Повышение тарифов на 10–25%", "ARPU +12–18% за год; Jio −11 млн абонентов за квартал"],
    ["Казахстан: Beeline, Kcell, 2025", "Точечно ~5% тарифов", "Выручка Beeline +18% (9 мес. 2024)"],
    ["VEON / Beeline UZ", "Связь + контент (multiplay)", "ARPU ×3,7, отток ÷2,2"],
]
add("benchmarks", f"""{head("Доказательства", "Каждая механика уже сработала в других странах")}
{table(["Где", "Что сделали", "Результат"], rows, [28, 36, 36], 24)}
{foot(5, "Детали и ссылки на источники — docs/02_market_benchmarks.md")}""",
    "Мы не изобретаем: индексация архива — ежегодная практика в России, AT&T и T-Mobile подняли цены legacy-планов с контролируемым оттоком, Индия показала рост ARPU на 12–18% за год, но и цену жёсткого подхода — потерю абонентов. Поэтому у нас только мягкие механики. Кейсы вендоров по персонализации мы сознательно занизили в модели.")

# 6 PORTFOLIO ---------------------------------------------------------------
def plist(title, color, items):
    rows = "".join(
        f'<div style="display:flex;gap:16px;align-items:center;border-top:1px solid {LINE};padding:10px 0 10px 0">'
        f'<p style="font-size:24px;font-weight:600;color:{color};width:64px">{c}</p>'
        f'<p style="flex:1;font-size:24px;line-height:1.3;color:{BODY}">{n}</p>'
        f'<p style="font-size:24px;font-weight:600;color:{INK};width:120px;text-align:right">{p}</p></div>'
        for c, n, p in items)
    return (f'<div style="flex:1;display:flex;flex-direction:column;gap:8px">'
            f'<h3 style="{H};font-size:40px;font-weight:600;color:{color}">{title}</h3>{rows}</div>')

easy = plist("EASY — настройка, 4–6 недель", BLUE, [
    ("A2", "Точечная индексация недооценённых тарифов", "80%"),
    ("A1", "«Ucell 30 — Upgrade»: переход с подарком", "92%"),
    ("A4", "Бустер-пакет при исчерпании (opt-in)", "90%"),
    ("A6", "Реактивация спящих SIM", "92%"),
    ("A7", "«Musofir» для трудовых мигрантов", "90%"),
    ("A5", "Контент-надстройка к тарифу", "85%"),
    ("A3", "Суточные микропакеты — только пилот", "70%"),
    ("A8", "Опция: индексация, волна 2", "65%")])
hard = plist("HARD — разработка, 6–12 мес.", ORANGE_T, [
    ("B1", "AI Next-Best-Offer в реальном времени", "64%"),
    ("B3", "Вывод устаревших тарифов с ценовой защитой", "60%"),
    ("B2", "Семейный аккаунт — после пилота", "33%"),
    ("B5", "Персональный «Mobil avans» — условно", "34%"),
    ("B4", "Смартфон в рассрочку — не делаем", "0%")])
add("portfolio", f"""{head("Портфель", "13 идей проверены, 11 рекомендуем, 1 отклонена")}
<div style="display:flex;gap:64px">{easy}{hard}</div>
{foot(6, "% — шанс успеха: окупится за 24 мес. и поднимет ARPU × вероятность запуска")}""",
    "Разделение по сложности для биллинга: EASY — это настройка существующих тарифов, пакетов и CRM-кампаний, запуск за 4–6 недель. HARD — новая функциональность биллинга, интеграции и ML-платформа. Идею со смартфонами в рассрочку модель отклонила — отрицательная экономика, мы её не прячем, это показатель честности отбора.",
    section="s3")

# 7 A1 → A2 -----------------------------------------------------------------
def step(num, title, text, color):
    return (f'<div style="flex:1;display:flex;flex-direction:column;gap:12px;background:{CARD};padding:32px;border-top:6px solid {color};border-radius:12px">'
            f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;color:{color}">{num}</p>'
            f'<h3 style="{H};font-size:40px;font-weight:600;line-height:1.2;color:{INK}">{title}</h3>'
            f'<p style="font-size:24px;line-height:1.4;color:{BODY}">{text}</p></div>')
steps = (step("ШАГ 1 · A1 · ДЕКАБРЬ", "Подарок к 30-летию за переход", "+50% ГБ на 3 мес. за переход на актуальный тариф. ~132 тыс. переходов, ARPU +1,4%, шанс 92%", BLUE)
         + step("ШАГ 2 · A2 · ЧЕРЕЗ 2–4 НЕД.", "Точечная индексация", "Только недооценённые тарифы: +4 000…6 000 сум с +ГБ. ~775 тыс. абонентов, ARPU +4,4%, вклад 39,6 млрд, шанс 80%", ORANGE_T)
         + step("ВСЕГДА", "Бесплатный выбор", "Right-size на тариф дешевле, пенсионеры исключены, уведомление ≥ 15 дней, пилот 10% с контрольной группой", BLUE))
add("carrot", f"""{head("Главный рычаг", "Сначала подарок, потом индексация — и всегда выбор")}
<div style="display:flex;gap:24px">{steps}</div>
<p style="font-size:28px;line-height:1.4;color:{INK};background:#EFE9DC;padding:24px 32px;border-radius:12px"><b>A2 остаётся прибыльной, пока доп. отток ниже 13,3% группы</b> — в 5 раз выше худших мировых кейсов (заложено 2,5%).</p>
{foot(7)}""",
    "Последовательность пряник, потом кнут. Сначала лояльным абонентам — подарок к 30-летию Ucell за добровольный переход. Через 2–4 недели тем, кто остался на недооценённых тарифах, — индексация с добавлением гигабайт и обязательной бесплатной альтернативой, включая тариф дешевле. Самое важное: даже если отток окажется в 5 раз хуже худших мировых кейсов, инициатива всё равно прибыльна.")

# 8 HARD --------------------------------------------------------------------
b3 = card(f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;color:{ORANGE_T}">B3 · СТАРТ ОКТЯБРЬ 2027</p>'
          f'<h3 style="{H};font-size:40px;font-weight:600;line-height:1.2;color:{INK}">Вывод устаревших тарифов</h3>'
          f'<p style="font-size:28px;line-height:1.4;color:{BODY}">Перевод на ближайший по ценности тариф, цена сохраняется 3 месяца, смена бесплатна</p>'
          f'<p style="{H};font-size:64px;font-weight:600;color:{INK}">+7,9% ARPU</p>'
          f'<p style="font-size:24px;line-height:1.4;color:{MUTED}">35 млрд сум/год на выходе · шанс 60% · бюджет ~6 млрд</p>')
b1 = card(f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;color:{ORANGE_T}">B1 · СТАРТ ИЮНЬ 2027</p>'
          f'<h3 style="{H};font-size:40px;font-weight:600;line-height:1.2;color:{INK}">AI Next-Best-Offer</h3>'
          f'<p style="font-size:28px;line-height:1.4;color:{BODY}">Лучшее предложение каждому абоненту в момент события: исчерпание, пополнение, роуминг, риск оттока</p>'
          f'<p style="{H};font-size:64px;font-weight:600;color:{INK}">+3,2% ARPU</p>'
          f'<p style="font-size:24px;line-height:1.4;color:{MUTED}">25 млрд сум/год · +31 тыс. удержанных · шанс 64%</p>')
add("hard", f"""{head("HARD-инициативы", "Во втором году рост дают вывод старых тарифов и AI")}
<div style="display:flex;gap:32px">{b3}{b1}</div>
<p style="font-size:28px;line-height:1.4;color:{BODY}">B2 семейный аккаунт и B5 персональный аванс — только после дешёвого пилота. B4 смартфоны в рассрочку — отрицательная экономика, не делаем.</p>
{foot(8)}""",
    "HARD-инициативы окупаются во втором году. Вывод устаревших тарифов даёт самый большой вклад, но и самый сложный: массовая миграция, поэтому стартует только после гейта в августе 2027. AI Next-Best-Offer — единственная крупная инициатива, которая растит долю рынка за счёт удержания; начинаем с MVP на трёх офферах и платим за платформу поэтапно.")

# 9 CHANCE CHART ------------------------------------------------------------
data = [("A1", "Переход с подарком", 92, "EASY"), ("A6", "Реактивация", 92, "EASY"), ("A4", "Бустер", 90, "EASY"),
        ("A7", "Musofir", 90, "EASY"), ("A5", "Контент", 85, "EASY"), ("A2", "Индексация", 80, "EASY"),
        ("A3", "Микропакеты", 70, "EASY"), ("A8", "Опция: волна 2", 65, "EASY"), ("B1", "AI NBO", 64, "HARD"),
        ("B3", "Вывод тарифов", 60, "HARD"), ("B5", "Mobil avans", 34, "HARD"), ("B2", "Семейный", 33, "HARD"),
        ("B4", "Смартфоны", 0, "HARD")]
rows = ""
for c, n, v, g in data:
    col = BLUE if g == "EASY" else ORANGE
    w = max(int(v * 9), 4)
    rows += (f'<div style="display:flex;gap:16px;align-items:center">'
             f'<p style="font-size:24px;color:{BODY};width:380px"><b>{c}</b> {n}</p>'
             f'<p style="font-size:24px;font-weight:600;color:{col};width:80px">{g}</p>'
             f'<div style="width:{w}px;height:30px;background:{col};border-radius:4px"></div>'
             f'<p style="font-size:24px;font-weight:600;color:{INK}">{v}%</p></div>')
add("chance", f"""{head("Шансы на успех", "Шанс на успех: 20 000 сценариев Монте-Карло")}
<div style="display:flex;flex-direction:column;gap:10px">{rows}</div>
{foot(9, "Шанс = P(вклад за 24 мес. > 0 и ARPU вырос) × P(запуск как задумано) · методика: docs/05")}""",
    "Как тестировали: для каждой инициативы задали диапазоны параметров по мировым кейсам — конверсия, отток, даунгрейд, затраты — и прогнали 20 000 сценариев на 24 месяца. Затем умножили на вероятность, что инициатива вообще запустится как задумано. У EASY экономика устойчива, риск — в исполнении и регуляторе. У HARD наоборот, поэтому B2 и B5 идут через пилот, а B4 отклонена.",
    section="s4")

# 10 EFFECT -----------------------------------------------------------------
eff = "".join(card(stat(n, l), pad=28) for n, l in [
    ("+11,5%", "ARPU когорты к мес. 24 · диапазон +6,1…+16,9%"),
    ("36,7 / 64,6", "млрд сум доп. выручки в 1-й / 2-й год"),
    ("≈ $5,1 млн", "run-rate доп. выручки в год на выходе"),
    ("61%", "вероятность ARPU ≥ +10% · 75% с опцией A8")])
add("effect", f"""{head("Эффект портфеля", "С учётом всех рисков: +11,5% ARPU и $5 млн в год")}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">{eff}</div>
<p style="font-size:28px;line-height:1.4;color:{BODY}">Если всё запустится по плану: <b>+15,8% ARPU</b>, ~$7,0 млн в год. Доля рынка — нейтрально (±0,08 п.п.). Вклад за 24 мес. — 53 млрд сум, окупается в 99% сценариев.</p>
{foot(10)}""",
    "Коммитим +10% как цель, держим +15% как stretch. Медианный сценарий с учётом того, что часть инициатив может не запуститься: +11,5% ARPU когорты и около 5 млн долларов в год на выходе. Если всё запустится по плану — почти +16%. Доля рынка нейтральна: потери от индексации компенсируются удержанием от AI и контента.")

# 11 ARPU CONTRIBUTIONS -----------------------------------------------------
contrib = [("B3", "Вывод устаревших тарифов", 1197), ("A2", "Индексация", 674), ("B1", "AI NBO", 439),
           ("A1", "Переход с подарком", 213), ("B2", "Семейный аккаунт", 130), ("A5", "Контент", 65),
           ("B5", "Mobil avans", 64), ("A4", "Бустер", 58), ("A7", "Musofir", 40), ("A3", "Микропакеты", 39),
           ("A6", "Реактивация", 9)]
rows = ""
for c, n, v in contrib:
    col = BLUE if c.startswith("A") else ORANGE
    w = max(int(v * 0.85), 4)
    rows += (f'<div style="display:flex;gap:16px;align-items:center">'
             f'<p style="font-size:24px;color:{BODY};width:420px"><b>{c}</b> {n}</p>'
             f'<div style="width:{w}px;height:30px;background:{col};border-radius:4px"></div>'
             f'<p style="font-size:24px;font-weight:600;color:{INK}">+{format(v, ",").replace(",", " ")} сум</p></div>')
add("bridge", f"""{head("Откуда рост", "ARPU когорты: 18 500 → ~21 400 сум по плану")}
<div style="display:flex;flex-direction:column;gap:12px">{rows}</div>
<p style="font-size:28px;line-height:1.4;color:{BODY}">80% прироста дают четыре инициативы: B3, A2, B1, A1. Синий — EASY, оранжевый — HARD.</p>
{foot(11, "План на мес. 24 после 20% перекрытия эффектов; сумма +2 926 сум = +15,8%")}""",
    "Мост ARPU показывает, где деньги: вывод устаревших тарифов, индексация, AI и переход с подарком дают 80% прироста. Остальные инициативы маленькие по деньгам, но нужны для удержания и для позитивной части коммуникации.")

# 12 UNIT ECONOMICS ---------------------------------------------------------
rows = [
    ["A1 переход с подарком", "LTV/CAC 17,3", "1,2 мес."],
    ["A2 индексация", "+2 873 сум/мес на абонента; безубыточна до оттока 13,3%", "5 дней"],
    ["A4 бустер", "LTV/CAC 10,1", "2,1 мес."],
    ["B3 вывод тарифов", "+3 761 сум/мес на абонента; до оттока 21%", "1,9 мес."],
    ["B1 AI NBO", "+429 сум/мес маржи на абонента", "~6 мес."],
    ["B4 смартфоны", "LTV/CAC 0,4", "нет"],
]
inv = (f'<div style="width:520px;display:flex;flex-direction:column;gap:12px;background:{INK};padding:32px;border-radius:16px">'
       f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;color:{ORANGE_L}">ИНВЕСТИЦИИ</p>'
       f'<p style="{H};font-size:64px;font-weight:600;color:{PAPER}">≈ $2 млн</p>'
       f'<p style="font-size:28px;line-height:1.4;color:{SOFT}">24 млрд сум разово, из них EASY — 1,8 млрд. Волна 1 даёт ~30 млрд выручки в первый год и финансирует HARD.</p></div>')
tbl = table(["Инициатива", "Ключевая юнит-метрика", "Окупаемость"], rows, [30, 52, 18], 24).replace("width:1664px", "width:1112px")
add("unit", f"""{head("Unit-экономика", "Первая волна окупается за недели и финансирует вторую")}
<div style="display:flex;gap:32px;align-items:start">{tbl}{inv}</div>
{foot(12, "Модальные значения параметров · детали: docs/04_unit_economics.md и Excel-модель")}""",
    "Юнит-экономика: переход с подарком окупается за месяц с LTV/CAC 17, индексация — за дни. Общие инвестиции около 2 млн долларов, но EASY стоит всего 1,8 млрд сум, а за первый год приносит около 30 млрд — этого достаточно, чтобы профинансировать HARD из эффекта первой волны.")

# 13 CJM --------------------------------------------------------------------
stages = [("Триггер", "«Опять повышают?»", "Подарок до индексации; сумма «было → стало» в SMS"),
          ("Сравнение", "Непонятно, что выгоднее", "Калькулятор в app: «вы тратите 7 ГБ из 6»"),
          ("Решение", "Переход только через колл-центр", "Переход в 1 клик, остатки сохраняются"),
          ("30 дней", "Страх скрытых списаний", "Автопродление только по согласию, SMS-чек"),
          ("Удержание", "Лояльных «наказывают» ценой", "Подарки за стаж, персональные офферы")]
cols = "".join(
    f'<div style="flex:1;display:flex;flex-direction:column;gap:12px">'
    f'<p style="font-size:24px;font-weight:600;color:{PAPER};background:{INK};padding:12px 16px;border-radius:8px">{s}</p>'
    f'<p style="font-size:24px;line-height:1.4;color:{ORANGE_T}"><b>Боль:</b> {p}</p>'
    f'<p style="font-size:24px;line-height:1.4;color:{BLUE}"><b>Решение:</b> {r}</p></div>'
    for s, p, r in stages)
add("cjm", f"""{head("Путь абонента", "CJM: превращаем «опять повышают» в «меня ценят»")}
<p style="font-size:28px;line-height:1.4;color:{BODY}">Персона: <b>Дильноза, 34, Ташкент</b> — 9 лет на старом пакете, интернет заканчивается к 20-му числу.</p>
<div style="display:flex;gap:20px">{cols}</div>
{foot(13, "Полная CJM, персоны, SMS на узбекском и русском, скрипты КЦ — docs/06_cjm.md")}""",
    "Главная эмоциональная точка — момент уведомления. Поэтому подарок идёт раньше индексации, в SMS всегда сумма было-стало, а в приложении — персональное сравнение по фактическому расходу. Автопродление — только по согласию.",
    section="s5")

# 14 ROADMAP ----------------------------------------------------------------
PX = 80
bars = [("Discovery и данные (ваш этап)", 0, 1.5, ORANGE), ("Волна 1: A1 A2 A4 A6", 2, 6, BLUE),
        ("Волна 2: A5 A7", 3, 7, BLUE), ("B1 AI NBO · запуск июн 2027", 2, 9, ORANGE),
        ("B2 / B5 · пилот → разработка", 3, 10, ORANGE), ("B3 вывод тарифов · окт 2027", 4, 13, ORANGE),
        ("A8 опция: волна 2 индексации", 14, 15, BLUE)]
rws = ""
for lab, a, b, col in bars:
    rws += (f'<div style="display:flex;gap:24px;align-items:center">'
            f'<p style="font-size:24px;color:{BODY};width:440px">{lab}</p>'
            f'<div style="position:relative;width:1200px;height:36px;background:#EEEAE0;border-radius:4px">'
            f'<div style="position:absolute;left:{int(a*PX)}px;top:0px;width:{int((b-a)*PX)}px;height:36px;background:{col};border-radius:4px"></div>'
            f'</div></div>')
q = "".join(f'<p style="font-size:24px;font-weight:600;color:{INK};width:240px">{t}</p>' for t in ["IV кв. 2026", "I кв. 2027", "II кв. 2027", "III кв. 2027", "IV кв. 2027"])
gates = [("G0", 1.5), ("G1", 3.65), ("G2", 6), ("G3", 10.5), ("G4", 12.5), ("G5", 14)]
g = "".join(f'<p style="position:absolute;left:{int(x*PX)-30}px;top:0px;width:60px;font-size:24px;font-weight:600;color:{PAPER};background:{INK};border-radius:8px;text-align:center">{n}</p>' for n, x in gates)
add("roadmap", f"""{head("Roadmap", "Пилоты в декабре 2026, HARD — в середине 2027")}
<div style="display:flex;flex-direction:column;gap:14px">
<div style="display:flex;gap:24px"><p style="font-size:24px;width:440px;color:{MUTED}">Квартал</p><div style="display:flex;width:1200px">{q}</div></div>
{rws}
<div style="display:flex;gap:24px;align-items:center"><p style="font-size:24px;color:{BODY};width:440px">Гейты решений</p><div style="position:relative;width:1200px;height:40px">{g}</div></div>
</div>
{foot(14, "G0 защита 16.11.2026 · G1 пилоты 20.01.2027 · G3 go B3 15.08.2027 · G4 решение A8 15.10.2027")}""",
    "Пилоты стартуют в декабре на 10% целевых групп, разбор пилотов 20 января, масштабирование в первом квартале. AI-платформа строится параллельно и запускается в июне. Вывод устаревших тарифов — только после гейта в августе. По второй волне индексации руководство решает в октябре 2027 по фактическим результатам.")

# 15 RISKS ------------------------------------------------------------------
rows = [
    ["Регулятор / Комитет по конкуренции", "Точечно, more-for-more, досье обоснования, пенсионеры исключены, решение независимо", "Предписание → пауза ценовых механик"],
    ["Отток выше модели", "Пилот 10% с контрольной группой, retention-офферы, AI-модель оттока", "Тест − контроль > 1,5 п.п. за 45 дней"],
    ["Негатив в СМИ", "Подарок до индексации, right-size альтернатива, нарратив «30 лет Ucell»", "Жалобы > 2× нормы"],
    ["Нагрузка на колл-центр", "Волны по 10–25% базы, самообслуживание в app и USSD, скрипты", "Ожидание > 5 мин"],
    ["AI не даёт эффекта", "MVP на 3 офферах, оплата платформы поэтапно", "Uplift MVP < +1,5%"],
]
add("risks", f"""{head("Риски", "Каждая ценовая механика имеет стоп-кран")}
{table(["Риск", "Митигация", "Стоп-критерий"], rows, [26, 50, 24], 24)}
{foot(15, "Реестр рисков, этика и pre-mortem — docs/10_risks_regulatory.md")}""",
    "Главный риск — не экономика, а регулятор и репутация. Поэтому точечность, добавление ценности, исключение пенсионеров, уведомление за 15 дней и бесплатная смена тарифа. У каждой ценовой механики есть заранее утверждённый стоп-критерий.")

# 16 DATA -------------------------------------------------------------------
dd = [("D1–D2", "Реестр тарифов, профиль и выручка абонентов когорты", "Размер и ARPU когорты, сегменты"),
      ("D3", "Потребление vs пакет, дата исчерпания", "Кто недоплачивает (value-gap)"),
      ("D4", "Отток, MNP, реактивации", "Базовый отток"),
      ("D7", "Результаты повышения 03.02.2026 vs контроль", "Эластичность оттока и даунгрейда")]
rws = "".join(
    f'<div style="display:flex;gap:24px;border-top:1px solid {LINE};padding:12px 0 12px 0">'
    f'<p style="font-size:24px;font-weight:600;color:{ORANGE_T};width:120px">{c}</p>'
    f'<p style="font-size:24px;line-height:1.4;color:{BODY};flex:1">{d}</p>'
    f'<p style="font-size:24px;line-height:1.4;color:{INK};width:520px">{w}</p></div>' for c, d, w in dd)
add("data", f"""{head("До запуска", "Данные и пилоты с контрольной группой")}
<div style="display:flex;flex-direction:column">{rws}</div>
<p style="font-size:28px;line-height:1.4;color:{BODY}">Каждая инициатива стартует как A/B-тест с постоянной контрольной группой 5–10%. Для MDE 3% ARPU нужно ~25 тыс. абонентов на группу — архивная база это позволяет.</p>
{foot(16, "Полный запрос D1–D16 и SQL-шаблоны — docs/09_data_request_for_analysts.md")}""",
    "Прежде чем масштабировать, заменяем гипотезы фактом: размер когорты, сегменты, кто недоплачивает и, главное, как абоненты отреагировали на наше собственное повышение в феврале 2026. После этого модель пересчитывается одной командой. Все инициативы идут через A/B-тест с контрольной группой, чтобы доказать инкрементальный эффект.")

# 17 ASK --------------------------------------------------------------------
asks = [("1", "Утвердить волны 1–2 и старт пилотов в декабре 2026"),
        ("2", "Утвердить когортную метрику ARPU и цель +10% (stretch +15%)"),
        ("3", "Бюджет: EASY 1,8 млрд сум + RFP для AI-платформы и анализ каталога тарифов"),
        ("4", "Решения по выводу тарифов и второй волне индексации — на гейтах в августе и октябре 2027")]
rws = "".join(
    f'<div style="display:flex;gap:32px;align-items:start;border-top:1px solid #33415E;padding:20px 0 0 0">'
    f'<p style="{H};font-size:40px;font-weight:600;color:{ORANGE_L};width:48px">{n}</p>'
    f'<p style="font-size:28px;line-height:1.4;color:{PAPER};flex:1">{t}</p></div>' for n, t in asks)
add("ask", f"""{head("Решение", "Что нужно от руководства сегодня", True)}
<div style="display:flex;flex-direction:column;gap:20px">{rws}</div>
{foot(17, "Инициатива «Архивная база» · материалы: README и docs/00–12", True)}""",
    "Прошу четыре решения: утвердить первые две волны, зафиксировать когортную метрику и цель +10%, выделить бюджет на EASY и RFP для AI-платформы, а решения по выводу тарифов и второй волне индексации принять на гейтах по фактическим данным. Спасибо, готов ответить на вопросы.",
    dark=True, section="s6")

# WRITE ---------------------------------------------------------------------
for sid, html, _ in slides:
    with open(os.path.join(S, f"{sid}.html"), "w", encoding="utf-8") as f:
        f.write(html)
sections = {
    "s1": {"description": "Проблема и метрика: архивная база недоплачивает, считаем ARPU по когорте", "start": "cover"},
    "s2": {"description": "Рынок и доказательства: механики уже сработали в других странах", "start": "market"},
    "s3": {"description": "Портфель инициатив EASY / HARD и главный рычаг", "start": "portfolio"},
    "s4": {"description": "Эффект, шансы и экономика", "start": "chance"},
    "s5": {"description": "Исполнение: CJM, roadmap, риски, данные", "start": "cjm"},
    "s6": {"description": "Решение руководства", "start": "ask"},
}
deck = {
    "v": 4,
    "createdOnFiles": {"v": 1, "at": "2026-09-30T10:40:00Z"},
    "lists": "css",
    "title": "Ucell — рост ARPU архивной базы",
    "order": [s[0] for s in slides],
    "sections": sections,
    "faces": {
        "rubik": {"family": "Rubik", "href": "https://fonts.googleapis.com/css2?family=Rubik:wght@400..700&display=swap"},
        "ibm-plex-sans": {"family": "IBM Plex Sans", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"},
    },
    "designSystems": [],
}
with open(os.path.join(ROOT, "project", "deck.json"), "w", encoding="utf-8") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)

# markdown outline with speaker notes for the repo
import re
md = ["# Презентация для руководства — структура и спикерские заметки", ""]
for i, (sid, body, notes) in enumerate(outline, 1):
    title = re.search(r"<h[12][^>]*>(.*?)</h[12]>", body)
    md.append(f"## {i}. {re.sub('<[^>]+>', '', title.group(1)) if title else sid}")
    md.append("")
    md.append(f"**Спикер:** {notes}")
    md.append("")
with open(os.path.join(os.path.dirname(__file__), "deck_outline.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print("slides:", len(slides))
for sid, html, _ in slides:
    print(sid, html.count("<"), "tags")
