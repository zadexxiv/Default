"""Генератор слайдов v2 (Slides artifact): python v2/presentation/gen_deck_v2.py → v2/presentation/deck/project/*"""
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deck")
S = os.path.join(ROOT, "project", "slides")
os.makedirs(S, exist_ok=True)

INK = "#14213D"; PAPER = "#F7F5F0"; CARD = "#FDFCF9"; LINE = "#E2DED3"
BODY = "#3D4A5C"; MUTED = "#5F6B7A"; ORANGE_T = "#A94A12"; ORANGE = "#C2571A"
BLUE = "#2B5FA6"; SOFT = "#B8C4D9"; ORANGE_L = "#F2A76B"; GREEN = "#2E7D5B"
H = "font-family:'Rubik', Arial, sans-serif"
T = "font-family:'IBM Plex Sans', Arial, sans-serif"
LIGHT = f"background:{PAPER};color:{BODY};{T};padding:128px 128px 160px;display:flex;flex-direction:column;gap:32px"
DARK = f"background:{INK};color:{PAPER};{T};padding:128px 128px 160px;display:flex;flex-direction:column;gap:32px"
slides, outline = [], []


def head(eyebrow, title, dark=False):
    return (f'<div style="display:flex;flex-direction:column;gap:16px">'
            f'<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;font-weight:600;color:{ORANGE_L if dark else ORANGE_T}">{eyebrow}</p>'
            f'<h2 style="{H};font-size:64px;font-weight:600;line-height:1.1;color:{PAPER if dark else INK}">{title}</h2></div>')


def foot(n, text="Ucell · рост ARPU архивной базы v2 · P50 с поправкой на риск", dark=False):
    return (f'<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:{SOFT if dark else MUTED}">'
            f'{text}{" · " + str(n) if n else ""}</p>')


def add(sid, body, notes, dark=False):
    html = f'<section id="{sid}" data-transition="fade" style="{DARK if dark else LIGHT}">\n{body}\n<aside>{notes}</aside>\n</section>\n'
    slides.append((sid, html))
    outline.append((sid, body, notes))


def card(inner, pad=28, border=None, flex="1"):
    return (f'<div style="flex:{flex};display:flex;flex-direction:column;gap:12px;background:{CARD};padding:{pad}px;'
            f'border:{border or "1px solid " + LINE};border-radius:16px">{inner}</div>')


def stat(num, label, color=INK):
    return (f'<p style="{H};font-size:64px;font-weight:600;line-height:1.1;color:{color}">{num}</p>'
            f'<p style="font-size:24px;line-height:1.4;color:{BODY}">{label}</p>')


def eyebrow(t, c=ORANGE_T):
    return f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;color:{c}">{t}</p>'


def h3(t):
    return f'<h3 style="{H};font-size:40px;font-weight:600;line-height:1.2;color:{INK}">{t}</h3>'


def p(t, size=24, color=BODY):
    return f'<p style="font-size:{size}px;line-height:1.4;color:{color}">{t}</p>'


def table(headers, rows, widths, size=24, width=1664):
    th = "".join(f'<th style="width:{w}%;text-align:left">{h}</th>' for h, w in zip(headers, widths))
    trs = "".join((f'<tr style="background:{CARD}">' if i % 2 == 0 else "<tr>") + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
                  for i, r in enumerate(rows))
    return f'<table style="font-size:{size}px;color:{BODY};{T};width:{width}px"><tr style="background:#E9E5DA">{th}</tr>{trs}</table>'


# 1 cover
st = "".join(f'<div style="flex:1;display:flex;flex-direction:column;gap:8px;border-top:2px solid {ORANGE_L};padding:24px 0 0 0">'
             f'<p style="{H};font-size:64px;font-weight:600;line-height:1.1;color:{PAPER}">{n}</p>'
             f'<p style="font-size:24px;line-height:1.4;color:{SOFT}">{l}</p></div>'
             for n, l in [("+9,1%", "ARPU архивной когорты к M24 (P50 с учётом рисков)"),
                          ("89,6 млрд", "сум — вклад портфеля за 36 мес."),
                          ("≈ $290 тыс.", "бюджет MVP программы лояльности")])
add("cover", f"""<div style="display:flex;flex-direction:column;gap:28px">
<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;font-weight:600;color:{ORANGE_L}">Продуктовая инициатива · v2</p>
<h1 style="{H};font-size:96px;font-weight:600;line-height:1.1;color:{PAPER}">Рост ARPU архивной базы: 4 инициативы и Ucell Club</h1>
<p style="font-size:28px;line-height:1.4;color:{SOFT};width:1400px">Sunset / Migration · More-for-More · бустер и роуминг-промо · программа лояльности с MVP</p>
</div>
<div style="flex:1"></div>
<div style="display:flex;gap:48px">{st}</div>
{foot("", "Защита перед руководством · ноябрь 2026 · [ФИО, продакт-менеджер тарифных планов]", True)}""",
    "Сегодня четыре инициативы вместо широкого портфеля. Три цифры: +9% ARPU архивной когорты за 2 года с учётом всех рисков, около 90 млрд сум вклада за 3 года, и программа лояльности, которую мы сначала проверяем MVP примерно за 290 тысяч долларов. Размеры базы — гипотезы до данных.",
    dark=True)

# 2 problem + metric
cards = "".join(card(stat(n, l)) for n, l in [("3,52 млн", "активных абонентов на архивных тарифах"),
                                              ("18 500 сум", "ARPU когорты — по ценам прошлых лет"),
                                              ("781 млрд", "сум выручки в год (~$65 млн)")])
add("problem", f"""{head("Проблема и метрика", "Архив платит по старым ценам — меряем по когорте")}
<div style="display:flex;gap:28px">{cards}</div>
{p("<b>Метрика:</b> ARPU когорты всех, кто был на архиве 01.11.2026; мигрировавшие остаются в когорте, иначе успешная миграция «снижает» ARPU архива. Рядом всегда — выручка и отток.", 28)}
{foot(2, "Размер и ARPU когорты — гипотезы до данных D1–D3")}""",
    "Архивная база — около трети абонентов, но платит заметно меньше актуальной линейки. Прошу сразу зафиксировать когортную метрику: иначе через полгода отчёт покажет падение ARPU архива именно потому, что миграция работает.")

# 3 portfolio overview
rows = [["I1 Sunset / Migration → ТП дороже на 10–15%", "апр 2027, 2 волны", "35,6", "+6,2%", "65%"],
        ["I2 More-for-More: + АП и + трафик", "дек 2026, пилот 10%", "36,8", "+4,5%", "80%"],
        ["I3 Бустер при исчерпании + роуминг −50%", "дек 2026", "5,0", "+0,7%", "90%"],
        ["I4 Ucell Club: кэшбэк, Daily Drops, Weekly, Monthly", "MVP мар 2027 → сен 2027", "+12,4 (36 мес.)", "+0,9% (M24)", "54%"]]
add("four", f"""{head("Инициативы", "Четыре инициативы: три быстрые и одна стратегическая")}
{table(["Инициатива", "Старт", "Вклад 24м, млрд", "ΔARPU когорты", "Шанс успеха"], rows, [42, 20, 14, 12, 12], 24)}
{p("Шанс успеха = P(окупится и поднимет ARPU) × P(запуск как задумано), 20 000 сценариев Монте-Карло.", 24, MUTED)}
{foot(3)}""",
    "I2 и I3 — быстрые и надёжные, запускаем в декабре. I1 — самый большой вклад в ARPU, но сложное исполнение, поэтому две волны. Loyalty — стратегическая ставка на удержание с окупаемостью около 2,5 лет, поэтому через MVP.")

# 4 I1
steps = "".join(card(eyebrow(a, c) + h3(b) + p(t)) for a, b, t, c in [
    ("T−60 ДНЕЙ", "Выберите сами", "mapped-ТП или крупнее + 500 монет и 3 сундука Ucell Club", BLUE),
    ("T−15 ДНЕЙ", "Уведомление", "сумма «было → стало», что добавлено, бесплатная смена ТП", ORANGE_T),
    ("T0", "Перевод", "остатки сохраняются; соцгруппа — по той же цене", BLUE),
    ("T+30", "Right-size", "тем, кому новый ТП велик, — предложение дешевле", BLUE)])
add("i1", f"""{head("I1 Sunset / Migration", "Закрываем неэффективные линейки: +10–15% за больше ценности")}
<div style="display:flex;gap:20px">{steps}</div>
<div style="display:flex;gap:28px">{card(stat("+6,2%", "ARPU когорты через 12 мес. после старта"))}{card(stat("35,6 млрд", "вклад за 24 мес. (P10–P90: 25,6–47,6)"))}{card(stat("15,7%", "доп. отток, до которого I1 в плюсе (заложено 3%)"))}</div>
{foot(4, "~30% когорты (~1,06 млн); волны апрель и июль 2027; P(запуска) 65%")}""",
    "Перевод на актуальные тарифы дороже на 10–15%, но с большим объёмом. Сначала даём выбрать самим с подарком программы лояльности, потом уведомляем за 15 дней, переводим, а через месяц предлагаем right-size. Запас прочности большой: инициатива прибыльна, пока доп. отток ниже 16%.")

# 5 I2 + I3
c2 = card(eyebrow("I2 · ДЕКАБРЬ 2026") + h3("More-for-More") + p("+4 000…6 000 сум к АП и больше трафика для ~775 тыс. абонентов недооценённых линеек; рядом всегда бесплатный right-size") +
          f'<p style="{H};font-size:64px;font-weight:600;color:{INK}">+4,5% ARPU</p>' + p("вклад 36,8 млрд за 24 мес. · шанс 80% · пилот 10% с holdout", 24, MUTED))
c3 = card(eyebrow("I3 · ДЕКАБРЬ 2026", BLUE) + h3("Бустер + роуминг-промо") + p("«+5 ГБ» в момент исчерпания (автопродление только по согласию) и «Musofir» −50% на первый месяц для выезжающих") +
          f'<p style="{H};font-size:64px;font-weight:600;color:{INK}">LTV/CAC 7–10</p>' + p("вклад 5,0 млрд · окупаемость 2–3 мес. · шанс 90%", 24, MUTED))
add("i23", f"""{head("I2 и I3", "Быстрые деньги в декабре: More-for-More и пакеты по потребности")}
<div style="display:flex;gap:28px">{c2}{c3}</div>
{foot(5, "Стоп-критерий I2: отток тест − контроль > 1,5 п.п. за 45 дней или жалобы > 2× нормы")}""",
    "More-for-More — доказанная механика: Ucell сам сделал это в феврале 2026, конкуренты тоже. Отличие — бесплатная альтернатива right-size, чтобы не было критики «платим за ненужные гигабайты». I3 монетизирует моменты, когда абоненту действительно нужен трафик.")

# 6 loyalty architecture
cols = "".join(card(eyebrow(a, c) + h3(b) + p(t)) for a, b, t, c in [
    ("СЛОЙ 1", "Кэшбэк 3–5%", "Ucell Coins за оплату вовремя: 3% / 4% / 5% по полосам АП; тратить на пакеты, номера, до 30% счёта, мерч", BLUE),
    ("СЛОЙ 2", "Daily Drops", "Сундук каждый день, 3–4 тапа, пустых не бывает; серия 7 дней = +1 шанс", ORANGE_T),
    ("СЛОЙ 3", "Weekly Wins", "1 354 приза в неделю: iPhone, планшеты, AirPods, концерты + массовый уровень", BLUE),
    ("СЛОЙ 4", "Monthly Grand", "Авто, путешествия, умра; шансы в приложении, розыгрыш — эфир с нотариусом", ORANGE_T)])
add("loyalty", f"""{head("I4 Ucell Club", "Программа лояльности по модели Verizon — в 4 слоя")}
<div style="display:flex;gap:20px">{cols}</div>
{p("Verizon: 3% от счёта в «Verizon Dollars» + Verizon Shine с Daily Drops и еженедельными розыгрышами. T-Mobile Tuesdays: −27% оттока участников, 90+ млн погашений.", 24, MUTED)}
{foot(6)}""",
    "Четыре слоя: кэшбэк платит за оплату вовремя, сундук создаёт ежедневную привычку, Weekly Wins даёт эмоцию, Monthly Grand — большой повод и охват в соцсетях. Это повторяет Verizon, но с поправкой на их ошибку: у них лучшие дропы заканчивались за секунды, у нас каждый сундук гарантированно с призом.")

# 7 daily drops
rows = [["30–100 Ucell Coins", "50%", "23 сум"], ["300 МБ – 1 ГБ", "25%", "150 сум"], ["Безлимит мессенджеров / 30 мин", "7%", "40 сум"],
        ["Купон партнёра −10…30%", "14%", "5 сум"], ["Жетон +1 шанс", "2%", "0"], ["Слот инвентаря (кино, мерч, JBL, смартфон)", "2%", "недельный лимит"]]
inv = card(eyebrow("ИНВЕНТАРЬ В НЕДЕЛЮ") + f'<p style="{H};font-size:64px;font-weight:600;color:{INK}">89,8 млн</p>' +
           p("1 000 билетов в кино (50% партнёр), 100 худи, 60 кепок, 40 power bank, 20 JBL, 2 Galaxy A") +
           p("Вероятность = остаток / ожидаемые открытия → перерасход невозможен", 24, MUTED), flex="0 0 560px")
add("drops", f"""{head("Daily Drops", "Сундук: в среднем 52,5 сум за открытие, без пустых призов")}
<div style="display:flex;gap:28px;align-items:start">{table(["Приз", "Вероятность", "Себестоимость"], rows, [56, 20, 24], 24, 1076)}{inv}</div>
{foot(7, "Партнёр даёт скидку из маржи и только при покупке — в минус не уходит ни он, ни Ucell")}""",
    "Ключевой принцип — никто не уходит в минус. Цифровая часть контролируется таблицей вероятностей и стоит около 52 сум за открытие. Физические призы — фиксированный недельный лимит, вероятность пересчитывается по остатку, поэтому перерасход невозможен. Партнёр платит скидкой и только при покупке.")

# 8 weekly + monthly
w = card(eyebrow("WEEKLY WINS · 46 МЛН/НЕД.") + h3("1 354 приза каждую неделю") +
         p("1 iPhone 17 · 2 планшета · 5 AirPods · 10 пар на концерт · 30 пар в кино · Premium-пул для АП ≥ 80 тыс. · 1 000 × 5 ГБ · 300 ваучеров партнёров") +
         p("Шанс выиграть за неделю — 1 к ~1 100 вместо 1 к 27 500 без массового уровня", 24, MUTED))
m = card(eyebrow("MONTHLY GRAND · ~93 МЛН/МЕС.", BLUE) + h3("Авто, путешествия, умра") +
         p("4 × Chevrolet Onix (176,9 млн) · 4 × Турция на двоих · 2 × умра на двоих · 5 × iPhone · 10 × год связи бесплатно") +
         p("Гибрид: шансы копятся в приложении, розыгрыш — прямой эфир Instagram / Telegram с нотариусом (как MobiDRIVE у Mobiuz)", 24, MUTED))
add("wins", f"""{head("Розыгрыши", "Weekly Wins и Monthly Grand: много выигравших и большие призы")}
<div style="display:flex;gap:28px">{w}{m}</div>
{foot(8, "Цены — ориентиры 10/2026: Chevrolet (kursiv.media), кино 80–100 тыс. (Premier Cinema), мерч 100–180 тыс. (OLX)")}""",
    "Главная причина негатива в розыгрышах — никто не выигрывает. Поэтому в Weekly Wins есть массовый уровень: тысяча пакетов по 5 ГБ и ваучеры партнёров. Monthly Grand — гибрид: шансы в приложении привязаны к поведению, а сам розыгрыш — эфир в соцсетях с нотариусом ради охвата и доверия.")

# 9 threshold
rows = [["O1 Открыто всем", "100%", "100%", "1 226", "низкий"],
        ["O2 Только АП ≥ 60 тыс.", "30%", "3%", "1 309", "низкий / PR средний"],
        ["O3 Только АП ≥ 80 тыс.", "30%", "3%", "992", "PR высокий"],
        ["O4 Порог + платный вход 4 999 / 9 999", "33%", "7%", "1 507 → 904 с риском", "ВЫСОКИЙ: лотерея, лицензия"],
        ["<b>O5 Играют все, шансы растут с АП + Club+ Pass</b>", "100%", "100%", "<b>2 031</b>", "низкий"]]
add("threshold", f"""{head("Порог участия", "Не стена, а лестница: играют все, кто платит вовремя")}
{table(["Вариант", "Играют", "Архивных", "Эффект, млн сум/мес.", "Риск"], rows, [40, 11, 12, 19, 18], 24)}
{p("Шансы в неделю: 1 (до 30 тыс.) · 2 (30–59) · 3 (60–79 / Club+ Pass) · 5 (≥ 80 тыс.) + бонусы за серию, стаж и переход на старший ТП.", 24)}
{foot(9, "97% архивных участников — ниже 60 тыс. сум (гипотеза L2); MVP проверяет O2 против O5 двумя ветками")}""",
    "Жёсткий порог 60 или 80 тысяч исключает 97% архивных абонентов — ровно тех, чей ARPU мы растим. Платный вход — юридически лотерея: с 2025 года для неё нужна лицензия, и риск запрета высокий. Лестница шансов даёт больше всего: никто не исключён, а каждый шаг вверх по тарифу даёт больше шансов и кэшбэка.")

# 10 pass + negativity
pc = card(eyebrow("CLUB+ PASS · 9 999 СУМ/МЕС.") + h3("Законная версия «заплати и участвуй»") +
          p("+5 ГБ, кэшбэк ×1,5, второй сундук в день, скидка на номер. Шансы как у 60–79 тыс. — бонус к продукту, а не товар. Бесплатный путь всегда есть: оплата вовремя.") +
          p("Спрос 2–5% участников < 60 тыс. → ~210 млн сум/мес.", 24, MUTED))
nc = card(eyebrow("НЕЙТРАЛИЗУЕМ НЕГАТИВ", BLUE) + h3("Никто не уходит ни с чем") +
          p("Опоздал с оплатой → вернётся со следующего месяца · архив → бонус стажа · пенсионеры — уровень «Ehtirom», стаж ×2 · без смартфона → USSD-сундук · не выигрывал → ежемесячный «второй шанс» · публикуем победителей по регионам"))
add("pass", f"""{head("Win-win", "Club+ Pass и защита тех, кто выигрывает реже")}
<div style="display:flex;gap:28px">{pc}{nc}</div>
{foot(10, "Club+ Pass — только после заключения юристов, что он не считается платой за участие в лотерее")}""",
    "Club+ Pass закрывает вашу идею платного участия законно: абонент платит за гигабайты и повышенный кэшбэк, а дополнительные шансы — бонус. Для тех, кто выигрывает реже или не может участвовать, — гарантированный сундук, бонус стажа, USSD-версия и второй шанс.")

# 11 partners
ph = "".join(card(eyebrow(a, c) + h3(b) + p(t)) for a, b, t, c in [
    ("СТАРТ · MVP + 6 МЕС.", "Бартер", "Партнёр финансирует призы и скидки, мы даём охват бесплатно. Призы — это уже оплата", BLUE),
    ("ПОСЛЕ ДАННЫХ", "CPA", "Платят за погашённый купон или нового клиента: 5–15% чека или фикс", ORANGE_T),
    ("ЗРЕЛОСТЬ · 2028", "Размещения", "Featured Drop, брендированный сундук, баннер: от 50 млн сум/мес.", BLUE)])
add("partners", f"""{head("Партнёры", "Сначала натурой, потом деньгами — когда докажем трафик")}
<div style="display:flex;gap:20px">{ph}</div>
{p("<b>Для офлайн-партнёров без IT:</b> абонент показывает одноразовый код (живёт 24–72 ч), кассир вводит его в Telegram-бот Ucell Partner — подключение за 1–3 дня. Онлайн — API промокодов; платёжные — скидка при оплате по QR.", 26)}
{foot(11, "T-Mobile Tuesdays и Tele2 «Больше» — партнёры дают подарки за видимость; Verizon — до 20× ценности монет")}""",
    "Брать ли деньги с партнёров? На старте нет: у нас ещё нет статистики, и партнёры нужнее нам. Их оплата — бесплатные призы и скидки. Через 6 месяцев масштаба переводим на оплату за результат, а затем на платные размещения. Для офлайн-партнёров — Telegram-бот, никакой интеграции.")

# 12 loyalty budget
bud = [["Разработка MVP (web-view, кошелёк, антифрод)", "1,80"], ["Операционные + маркетинг", "0,61"], ["Кэшбэк", "0,25"],
       ["Daily Drops (цифровые + инвентарь)", "0,56"], ["Weekly Wins + Monthly Grand", "0,26"], ["<b>Итого MVP (150 тыс., 3 мес.)</b>", "<b>≈ 3,5 млрд (~$290 тыс.)</b>"]]
sc = card(eyebrow("ПРИ МАСШТАБЕ") + f'<p style="{H};font-size:64px;font-weight:600;color:{INK}">2,6 млрд/мес.</p>' +
          p("~1,5 млн участников · 1 765 сум на участника (4% его ARPU) · помесячно в плюсе с июня 2028 · окупаемость к маю–июню 2029") +
          p("36 мес.: +12,4 млрд (P50), P(> 0) = 84%", 24, MUTED), flex="0 0 600px")
add("budget", f"""{head("Бюджет Loyalty", "MVP за ~$290 тыс. до решения о масштабе")}
<div style="display:flex;gap:28px;align-items:start">{table(["Статья MVP", "млрд сум"], bud, [68, 32], 24, 1036)}{sc}</div>
{foot(12, "Главные рычаги окупаемости: переходы на старшие ТП, снижение оттока, оплата вовремя — гипотезы H1–H3 MVP")}""",
    "Программа лояльности — инвестиция в удержание с окупаемостью около 2,5 лет. Поэтому сначала MVP за 3,5 млрд сум, из них сам тест — 1,7 млрд. При масштабе — 2,6 млрд в месяц, из которых основное — призы и кэшбэк, и они масштабируются вместе с программой.")

# 13 portfolio effect
eff = "".join(card(stat(n, l), pad=24) for n, l in [("+9,1%", "ARPU когорты к M24 (P10–P90: +4,3…+12,1%); план +10,8%"),
                                                      ("30 / 44", "млрд сум доп. выручки когорты в Y1 / Y2"),
                                                      ("89,6 млрд", "сум — вклад портфеля за 36 мес. (вкл. всю Loyalty)"),
                                                      ("54% / 83%", "вероятность ARPU ≥ +8% / ≥ +5% к M24")])
add("effect", f"""{head("Эффект", "С учётом рисков: +9% ARPU и ~90 млрд вклада за 3 года")}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">{eff}</div>
{foot(13, "Мост ARPU (план, M24): I1 +5,1 п.п. · I2 +4,2 · I3 +0,6 · Loyalty +0,8")}""",
    "Предлагаю коммитить +8% как цель и +10% как stretch. Почти весь рост ARPU дают I1 и I2. Loyalty добавляет меньше процента ARPU архива, но его ценность — удержание всей базы и стимул к переходу на актуальные тарифы.")

# 14 roadmap
PX = 1200 / 30
bars = [("Discovery + 🟨 данные", 0.4, 1.75, ORANGE), ("I2 пилот → масштаб", 2, 5, BLUE), ("I3 бустер + роуминг", 2, 6, BLUE),
        ("Loyalty: разработка MVP", 2, 5, ORANGE), ("Loyalty: MVP 150 тыс.", 5, 8, ORANGE), ("I1 подготовка → волны", 2, 10, BLUE),
        ("Loyalty: масштаб и набор", 11, 15, ORANGE)]
rws = "".join(f'<div style="display:flex;gap:24px;align-items:center"><p style="font-size:24px;color:{BODY};width:440px">{lab}</p>'
              f'<div style="position:relative;width:1200px;height:36px;background:#EEEAE0;border-radius:4px">'
              f'<div style="position:absolute;left:{int(a*PX*2)}px;top:0px;width:{int((b-a)*PX*2)}px;height:36px;background:{c};border-radius:4px"></div></div></div>'
              for lab, a, b, c in bars)
q = "".join(f'<p style="font-size:24px;font-weight:600;color:{INK};width:240px">{t}</p>' for t in ["окт–дек 26", "янв–мар 27", "апр–июн 27", "июл–сен 27", "окт–дек 27"])
g = "".join(f'<p style="position:absolute;left:{int(x*PX*2)-30}px;top:0px;width:60px;font-size:24px;font-weight:600;color:{PAPER};background:{INK};border-radius:8px;text-align:center">{n}</p>'
            for n, x in [("G0", 1.75), ("G1", 3.85), ("G2", 7.7), ("G3", 8.6), ("G4", 14.0)])
add("roadmap", f"""{head("Roadmap", "Декабрь — I2 и I3, март — MVP, сентябрь — масштаб")}
<div style="display:flex;flex-direction:column;gap:14px">
<div style="display:flex;gap:24px"><p style="font-size:24px;width:440px;color:{MUTED}">Период</p><div style="display:flex;width:1200px">{q}</div></div>
{rws}
<div style="display:flex;gap:24px;align-items:center"><p style="font-size:24px;color:{BODY};width:440px">Гейты</p><div style="position:relative;width:1200px;height:40px">{g}</div></div>
</div>
{foot(14, "G0 23.11.2026 · G1 I2 27.01.2027 · G2 I1-волна 31.05 · G3 MVP 15.06.2027 · G4 итоги года 30.11.2027")}""",
    "В декабре стартуют I2 и I3. Параллельно делаем MVP программы лояльности к марту, а I1 — к апрелю, первой волной. 15 июня решаем, масштабировать ли Loyalty, и в сентябре запускаем её на всё приложение.")

# 15 MVP design
arms = "".join(card(eyebrow(a, c) + h3(b) + p(t)) for a, b, t, c in [
    ("ВЕТКА A · 75 ТЫС.", "O5 «лестница»", "Все, кто платит вовремя, играют; шансы 1/2/3/5; Club+ Pass; бонус за переход", BLUE),
    ("ВЕТКА B · 75 ТЫС.", "O2 «порог 60 тыс.»", "Кэшбэк и сундук всем; розыгрыши только при АП ≥ 60 тыс.", ORANGE_T),
    ("HOLDOUT · 80 ТЫС.", "Контроль", "Обычное приложение — для честного инкрементального эффекта", BLUE)])
add("mvp", f"""{head("MVP", "MVP отвечает на 4 вопроса до того, как мы потратим миллионы")}
<div style="display:flex;gap:20px">{arms}</div>
{p("<b>Масштабируем, если:</b> оплата вовремя +2 п.п., переходы на ТП ≥ 60 тыс. +0,3 п.п./мес., DAU сундука ≥ 25%, стоимость ≤ 1 900 сум на участника. Иначе урезаем призы и делаем MVP-2 или оставляем только кэшбэк.", 26)}
{foot(15, "Март–май 2027 · ≥ 40 тыс. архивных в выборке · отток досматриваем ещё 3 мес., участникам программу не отключаем")}""",
    "MVP — это эксперимент с тремя группами. Он одновременно отвечает, работает ли программа вообще и какая схема порога лучше: лестница или жёсткий порог. Решение о масштабе принимаем по заранее заданным критериям.")

# 16 risks
rows = [["Повышения I1 / I2 под вниманием регулятора", "Точечно, more-for-more, 15+ дней, соцгруппа исключена, пилот 10%"],
        ["Платный шанс = лотерея (лицензия НАПП с 2025)", "Не продаём шансы; Club+ Pass с ценностью; заключение Legal"],
        ["Loyalty не окупается", "MVP до масштаба, недельные лимиты призов, ≥ 25% призов от партнёров"],
        ["«Никто не выигрывает», недоверие к розыгрышам", "Пустых сундуков нет, 1 354 приза в неделю, нотариус, эфир, победители по регионам"],
        ["Архивные мало пользуются приложением", "USSD-сундук, SMS, офисы, welcome-пакет при I1 / I2"]]
add("risks", f"""{head("Риски", "Главные риски — регулятор и доверие, а не экономика")}
{table(["Риск", "Что делаем"], rows, [42, 58], 24)}
{foot(16, "Налоги на крупные призы — отдельное заключение; в бюджете резерв 10%")}""",
    "Ключевые риски — регуляторный и доверие к розыгрышам. На каждый есть конкретная мера. Платных шансов мы не продаём, ценовые изменения делаем точечно и с бесплатной альтернативой.")

# 17 ask
asks = [("1", "Запустить I2 (пилот 10%) и I3 в декабре 2026"),
        ("2", "Утвердить MVP Ucell Club: 3,5 млрд сум, март–май 2027, схема O5 против O2"),
        ("3", "Начать подготовку I1: mapping линеек, биллинг, Legal; волны в апреле и июле 2027"),
        ("4", "Утвердить когортную метрику ARPU и цель +8% (stretch +10%); масштаб Loyalty — на G3 15.06.2027")]
rws = "".join(f'<div style="display:flex;gap:32px;align-items:start;border-top:1px solid #33415E;padding:20px 0 0 0">'
              f'<p style="{H};font-size:40px;font-weight:600;color:{ORANGE_L};width:48px">{n}</p>'
              f'<p style="font-size:28px;line-height:1.4;color:{PAPER};flex:1">{t}</p></div>' for n, t in asks)
add("ask", f"""{head("Решение", "Что нужно от руководства сегодня", True)}
<div style="display:flex;flex-direction:column;gap:20px">{rws}</div>
{foot(17, "До защиты: данные D1–D4, D7, L1–L3 (v2/docs/12) — модель пересчитается одной командой", True)}""",
    "Прошу четыре решения: быстрые I2 и I3 в декабре, MVP программы лояльности, подготовку I1 и утверждение метрики и цели. Решение о масштабе программы лояльности — по данным MVP в июне 2027.",
    dark=True)

for sid, html in slides:
    with open(os.path.join(S, f"{sid}.html"), "w", encoding="utf-8") as f:
        f.write(html)
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-07T12:00:00Z"}, "lists": "css",
        "title": "Ucell — рост ARPU архивной базы v2", "order": [s[0] for s in slides],
        "sections": {"s1": {"description": "Проблема, метрика и четыре инициативы", "start": "cover"},
                     "s2": {"description": "Инициативы 1–3", "start": "i1"},
                     "s3": {"description": "Ucell Club: механика, призы, порог, партнёры", "start": "loyalty"},
                     "s4": {"description": "Бюджет, эффект, план, MVP, риски", "start": "budget"},
                     "s5": {"description": "Решение руководства", "start": "ask"}},
        "faces": {"rubik": {"family": "Rubik", "href": "https://fonts.googleapis.com/css2?family=Rubik:wght@400..700&display=swap"},
                  "ibm-plex-sans": {"family": "IBM Plex Sans", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(ROOT, "project", "deck.json"), "w", encoding="utf-8") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
md = ["# Презентация v2 — структура и текст спикера", ""]
for i, (sid, body, notes) in enumerate(outline, 1):
    t = re.search(r"<h[12][^>]*>(.*?)</h[12]>", body)
    md += [f"## {i}. {re.sub('<[^>]+>', '', t.group(1)) if t else sid}", "", f"**Спикер:** {notes}", ""]
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "deck_outline_v2.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(len(slides), "slides")
