# 02. Бенчмарки: было ли это где-то и сработало ли

> Ценовые механики (I1, I2) подробно разобраны в v1: [docs/02_market_benchmarks.md](../../docs/02_market_benchmarks.md).
> Здесь — кратко по ним и подробно по программе лояльности.

## 1. I1 / I2 — Sunset, Migration, More-for-More

| Где | Что сделали | Результат |
|---|---|---|
| Россия (МТС, Билайн, МегаФон, T2) | Индексация архивных тарифов: +10% (2022), +15–20% (T2, 01.2026) | Повторяют ежегодно, выручка растёт |
| США: AT&T (2022), T-Mobile (2024) | Legacy-планы +$5–6 на линию; T-Mobile переводит абонентов с grandfathered-планов | ARPU ↑; отток T-Mobile 0,86% → 0,93% — «в рамках ожиданий» (повышение было двухэтапным) |
| Индия (07/2024) | Повышение тарифов на 10–25%; Airtel убирает дешёвые планы | ARPU +12–18% за год; у Jio −11 млн абонентов за квартал |
| Норвегия, Telenor | Перевод на новые тарифы | Мобильный ARPU +4% |
| Казахстан (2025) | Beeline, Kcell — точечно ~5% тарифов | Выручка Beeline +18% |
| **Узбекистан** | Ucell 03.02.2026: +5 000 сум с +ГБ, пенсионеры исключены. Beeline Oila Max 105 → 155 тыс. | Рынок принял; но критика «платим за ненужные ГБ», и Комитет по конкуренции запрашивал обоснования |

## 2. I3 — бустеры и роуминг-пакеты

- Контекстные предложения в момент исчерпания: +8% ARPU (Flytxt); бустеры Jio/Airtel; автопродление у операторов РФ.
- Трудовые мигранты: переводы в Узбекистан **$18,9 млрд** в 2025, ~1,3 млн граждан работают в РФ. Растут
  направления Казахстан, Корея, Турция, ЕС.

## 3. I4 — программы лояльности операторов

| Программа | Механика | Результаты / факты | Чему учимся |
|---|---|---|---|
| **Verizon Dollars + Verizon Shine** (США, 2026) | **3% от ежемесячного счёта** в «долларах Verizon». Траты: партнёры (до 20× ценности), устройства, перевод в другие программы. Shine: **Daily Drops** (билеты, мерч, подарочные карты; первыми пришли — первыми получили), еженедельные розыгрыши «Epic Wins» по понедельникам | Запуск с розыгрышем поездки на финал ЧМ-2026. **Критика:** хорошие дропы заканчиваются за секунды, приложение падало на раздаче $10-карт | Ваша вилка 3–5% совпадает с рынком. **Нельзя «first come, first served» для всего** — нужен гарантированный приз и инвентарь с динамической вероятностью |
| **T-Mobile Tuesdays** (США, с 2016) | Бесплатные подарки каждую неделю (кофе, пицца, кино) — без баллов и покупок; призы дают партнёры за видимость | 90+ млн погашений, 28 млн установок; отток участников программы −27%; удовлетворённость +13%, готовность рекомендовать +20% | Партнёры готовы финансировать призы за охват. Эффект на отток реальный, но с самоотбором — в модели берём −8…25% |
| **Turkcell** (Турция) | Ежедневная игра «Salla Kazan» (потряси и выиграй) в приложении; «Колесо удачи» | «Колесо удачи»: 502 тыс. участников, 242 тыс. подарков, трафик в офисы +11% | Ежедневная мини-игра — рабочий формат удержания в приложении |
| **Safaricom Bonga** (Кения) | Баллы за траты → минуты, данные, мерч, телефоны | После ввода срока сгорания (3 года) обязательства по неиспользованным баллам −34% за год | Срок жизни монет нужен для управления breakage и обязательствами |
| **Tele2 «Больше»** (Россия) | Скидки и кэшбэк от партнёров | Участников ×3 за год; популярны онлайн-кино, обучение, доставка | Партнёрские скидки работают без денег оператора |
| **МТС Cashback** (Россия) | Кэшбэк до 25% у партнёров | Партнёры финансируют кэшбэк | Модель «партнёр платит за результат» |
| Simon-Kucher, Global Telco Study 2025 | Опрос операторов | Участие в программе лояльности = **+43% CLTV**; 80% операторов имеют программу, но только половина клиентов в неё вступает | Вступление (enrollment) — отдельный KPI |

## 4. Узбекистан: конкуренты и сам Ucell

| Игрок | Что есть | Вывод |
|---|---|---|
| **Ucell** | Акция «+%» — **5% кэшбэка за пополнение в приложении** | Кэшбэк-привычка у абонентов уже есть. Новую программу нужно встроить, а не дублировать |
| **Beeline UZ** | Beepul: баллы **BEEP** → пакеты связи и бесплатные переводы; 5% кэшбэк за оплату по QR (до 50 тыс. сум/мес.); семейный тариф Oila | Конкурент строит экосистему: финтех + связь |
| **Beeline UZ — hambi fortuna** | Колесо в приложении: 3 бесплатные попытки + **платная «Fortuna Plus» 1 490 сум/попытка**; призы — смартфоны, ноутбуки, ГБ, лимиты P2P; организатор по правилам — ViaMobi. В 2020 году регулятор ставил под сомнение законность промо Beeline + ViaMobi без лицензии на лотереи | Спрос на платные «прокруты» есть, но это серая зона: см. разбор в [05](05_threshold_win_win.md) |
| **Mobiuz** | Mobiuz Bonus: баллы за регистрацию, привязку карты, пополнение (50 баллов за 1 000 сум) → МБ. **MobiDRIVE:** 3 автомобиля BYD Song Plus, участвуют тарифы с АП **от 35 тыс. сум** (вход через USSD), розыгрыши в прямом эфире Instagram | **Конкурент уже использует порог по АП и эфирные розыгрыши авто.** Нам нужно сделать лучше: лестница шансов вместо стены и розыгрыш, связанный с поведением |
| Рынок в целом | UzAuto предупреждала о фейковых «розыгрышах Chevrolet» | Доверие к розыгрышам — отдельная задача: нотариус, публичный seed, публикация победителей |

## 5. Правовая рамка Узбекистана (для проверки юристами)

| Норма | Значение для программы |
|---|---|
| С 2025 года лотереи, онлайн-игры и букмекерство разрешены **только по лицензии** Национального агентства перспективных проектов (5 лет, 18,75 млн сум; только юрлица-резиденты; участники 18+) | **Платный вход в розыгрыш = лотерея.** Без лицензии нельзя → вариант O4 отклоняем ([05](05_threshold_win_win.md)) |
| Не облагаются НДФЛ доходы участников программ, направленных на рост активности клиентов, с бонусами по правилам программы (по разъяснениям buxgalter.uz) | Кэшбэк и мелкие призы, вероятно, не облагаются. **Крупные призы (авто, путешествия) — отдельное заключение**; в бюджете заложен резерв 10% |
| Правила оказания услуг связи (01/2026): уведомление об изменении условий ≥ 15 дней, смена тарифа бесплатна | I1 / I2 — с уведомлением; бесплатный right-size заложен в модель |
| Закон о персональных данных (локализация) | Данные программы хранятся в РУз; партнёрам передаётся код, а не номер |

## Источники

- Verizon: https://www.verizon.com/loyalty/ · https://www.verizon.com/shop/consumer-guides/verizon-loyalty-program/ · https://www.verizon.com/support/shine-faqs/ · https://www.androidauthority.com/verizon-shine-rewards-gift-card-app-crash-3683722/
- T-Mobile Tuesdays: https://mmaglobal.com/case-study-hub/case_studies/view/50446
- Turkcell: https://ommasign.com/?p=3909
- Safaricom Bonga: https://www.businessdailyafrica.com/bd/markets/market-news/safaricom-bonga-points-drop-34pc-on-expiry-date--4299146
- Tele2 «Больше»: https://altapress.ru/story/chislo-polzovateley-programmi-loyalnosti-tele-viroslo-v-tri-raza-263393
- Simon-Kucher Telco Study 2025: https://www.simon-kucher.com/index%2Ephp/en/insights/turning-engagement-tangible-customer-value-insights-global-telecommunications-study-2025
- Ucell «+%»: https://ucell.uz/en/faq/ucell-mobile-application · Mobil avans: https://ucell.uz/en/payment/mobilnyj-avans
- Beeline UZ BEEP / Beepul: https://beeline.uz/en/products/services/beepul · кэшбэк QR: https://beeline.uz/en/events/news/poluchite-cashback-5-na-vash-nomer-za-oplatu-s-pomoshchyu-qr-kodov
- Mobiuz Bonus: https://mobi.uz/en/special-offers/discounts/mobiuz-app-bonuses/ · MobiDRIVE: https://www.spot.uz/ru/2024/12/12/mobiuz/
- Лицензирование лотерей: https://www.gazeta.uz/ru/2024/12/14/bookmakers/ · https://www.norma.uz/novoe_v_zakonodatelstve/opredelen_poryadok_licenzirovaniya_organizacii_igr_loterey_i_bukmekerskoy_deyatelnosti
- Налоги на маркетинговые акции: https://buxgalter.uz/ru/publish/doc/text203639_kak_oblagat_nalogami_marketingovye_akcii
- Цены Chevrolet: https://uz.kursiv.media/2026-04-07/skolko-stoyat-samye-populyarnye-avtomobili-v-uzbekistane-v-aprele-2026-goda/
- Билеты в кино: https://www.afisha.uz/ru/cinema/2026/01/21/premier-cinema · мерч (DTF-печать): https://www.olx.uz/moda-i-stil/tashkent/q-футболки-с-принтом-на-заказ/
- Фейковые розыгрыши: https://www.spot.uz/ru/2025/12/12/uzauto-fake/
- Beeline hambi fortuna: https://beeline.uz/ru/events/actions/rozygrysh-v-hambi-fortuna · проверка промо Beeline/ViaMobi (2020): https://kun.uz/ru/news/2020/01/30/vyigryshnuyu-lotereyu-beeline-proveryat-na-predmet-zakonnosti · https://podrobno.uz/cat/obchestvo/aktsiya-kompanii-beeline-vyzvala-somneniya-v-zakonnosti-u-agentstva-po-razvitiyu-rynka-kapitala/
- Переводы мигрантов: https://kun.uz/en/news/2026/03/17/remittances-to-uzbekistan-exceed-189-billion-tripling-in-five-years
