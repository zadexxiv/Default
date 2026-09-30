# 02. Международная и локальная практика: было ли это где-то и сработало ли?

> Требование задачи: перед тем как предложить идею — проверить, применялась ли она в других странах и
> улучшила ли метрики. Ниже — доказательная база по каждой механике и оценка силы доказательств
> (1 — слабая, 5 — сильная). Эти диапазоны использованы как входы Монте-Карло
> ([05_success_probability.md](05_success_probability.md)).

## Сводная таблица

| Механика | Где применялась | Результат по метрикам | Сработало? | Сила доказ. | Инициатива |
|---|---|---|---|---|---|
| Повышение цены на архивных/legacy-тарифах | Россия (МТС, Билайн, МегаФон, Tele2/T2 — 2020, 2022, 2026), США (AT&T 2022, T-Mobile 2024), Казахстан (Beeline, Kcell 2025), Узбекистан (Ucell 02/2026, Beeline 2025–26) | AT&T: ARPU ↑, отток ↑ «в рамках ожиданий»; T-Mobile: отток 0,86%→0,93%, ARPU ↑; РФ: +10% (2022), +15–20% (T2, 2026) — повторяют ежегодно | **Да**, выручка ↑ во всех кейсах; цена — умеренный рост оттока | 5 | A2, A8, B3 |
| Общий ценовой подъём + вывод дешёвых планов | Индия (Jio, Airtel, Vi, 07/2024; минимальная оплата 2018–19) | Airtel ARPU +18% г/г, Jio +11,9%; Jio −11 млн абонентов за квартал; в 2018–19 ARPU Airtel +20% кв/кв, база 340→286 млн | **Да по ARPU**, но с ощутимой потерей базы при жёстком варианте | 5 | A2, A3 (только добровольный вариант) |
| Миграция с legacy на новые ТП (tariff realignment) | Telenor Norway, T-Mobile US, ближневосточный оператор (кейс консультантов), TPG (Австралия), Airtel | Telenor: мобильный ARPU +4% (NOK 13) за счёт миграции; ближневост. оператор: 10% базы за <3 мес., ARPU мигрантов +55%; консалт-кейс: выручка +15% | **Да** | 4 | A1, B3 |
| More-for-more (+ГБ за + цену) | Ucell 02/2026, Beeline UZ Oila Max (105→125→155 тыс.), Kcell/Beeline KZ | Выручка ↑, но **негатив «платим за ГБ, которые не используем»** (kun.uz, 03/2026) | Да по выручке, риск репутации | 4 | A2 (с опцией right-size) |
| Персональные офферы / NBO на ML | Flytxt (несколько операторов), fonYou, Acxiom, Telefónica Argentina (Teradata), Beeline UZ (predictive AI) | ARPU +8,2% (Flytxt), +22% (fonYou), +2%/год и отток −15% (Acxiom); Telefónica — 75+ офферов на 9 млн B2C | **Да**, но кейсы вендоров (оптимистичны) | 3 | B1, A4, A6 |
| Контент/цифровые сервисы в пакете (multiplay) | VEON (все рынки), Beeline UZ, Ucell (Yandex Plus в BOR 90) | Multiplay ARPU в 3,6–3,7× выше, отток в 2,2× ниже; у Beeline UZ 51,3% MAU | **Да** (но корреляция ≠ причинность) | 4 | A5 |
| Семейные / групповые тарифы | T-Mobile/AT&T, Beeline RU («Интернет на всё», 2014), Beeline UZ Oila (12/2024), Beeline KZ | Отток ↓, ARPA ↑, но ARPU на линию ↓ | **Да по оттоку**, ARPU — неоднозначно | 3 | B2 |
| Airtime credit / мобильный аванс | MTN (XtraTime), Vodacom, Airtel Africa; Ucell «Mobil avans» | Vodacom: до 48% пополнений — через аванс; MTN Nigeria — основной драйвер финтех-выручки | Да по выручке; **регуляторный риск** (FCCPC Нигерия приостановил в 2025) | 3 | B5 |
| Апгрейд 2G/3G → 4G-смартфон | VEON, Airtel, Jazz | 4G/multiplay-клиенты генерируют кратно больше ARPU | Да, но **дорого** и медленно | 2 | B4 |
| Пакеты для трудовых мигрантов / роуминг | Операторы РФ/КЗ (тарифы «для гостей»), Flytxt — реактивация иностранных резидентов (+8% ARPU) | Рост ARPU в нише, удержание номера | Да, локально | 3 | A7 |
| Регулирование индексаций | Великобритания (Ofcom): с 17.01.2025 запрет индексации «на инфляцию +X%» в середине контракта — только суммы в фунтах и пенсах, раскрытые при продаже | Индексации продолжаются, но **прозрачно** | Урок: прозрачность и заранее объявленная сумма | — | A2, A8 |

## Детально по кейсам

### 1. Россия — архивные тарифы как постоянный источник роста ARPU

- Январь 2022: МТС подняла стоимость архивных тарифов (~+60 руб.), следом «Билайн», «МегаФон», Tele2 —
  ~+10%. Причины — инфляция и рост трафика ([Коммерсантъ](https://www.kommersant.ru/doc/5172549)).
- 2020: операторы подняли расценки на архивных ТП ([Ведомости](https://www.vedomosti.ru/technology/articles/2020/01/16/820805-operatori-podnyali)).
- 01.01.2026: T2 повышает цены на архивных тарифах на 70–150 руб. (~15–20%) ([Mobile Info](https://mbif.ru/news/t2-povyshaet-czeny-na-arhivnyh-tarifah-s-1-yanvarya-2026-goda/)).
- Экспертная логика (TelecomDaily): архивные ТП приносят меньше денег, повышение цены — способ
  «подтолкнуть» к переходу на пакетные предложения ([info24](https://info24.ru/news/oni-prinosyat-menshe-deneg-ekspert-obyasnil-podorozhanie-arhivnyh-tarifov-svyazi.html)).

**Вывод для Ucell:** практика устойчивая и повторяющаяся (раз в 1–2 года). Работает в связке
«кнут (индексация архива) + пряник (переход на новый ТП с бонусом)» — ровно A2 + A1.

### 2. США — legacy-планы AT&T и T-Mobile

- AT&T (06/2022): +$6/мес на одиночных и +$12 на семейных legacy-планах, первый рост за 3 года.
  ARPU вырос, отток вырос; CEO: реакция клиентов «tracking as we expected» — часть заплатила,
  часть мигрировала на новые планы ([Fierce](https://fierce-network.com/wireless/att-raises-prices-some-mobile-plans-6-month),
  [AT&T 10-K 2022](https://www.sec.gov/Archives/edgar/data/732717/000073271723000011/t-20221231.htm)).
- T-Mobile (06/2024): +$5 на линию на планах ONE, Simple Choice, Magenta — первый рост почти за 10 лет.
  Постоплатный отток телефонов 0,86% (2024) → 0,93% (2025); компания сообщила, что отток в рамках ожиданий,
  потому что повышение было **двухэтапным** ([Fierce](https://www.fierce-network.com/wireless/t-mobile-raising-prices-some-older-plans),
  [T-Mobile ARS 2024](https://www.sec.gov/Archives/edgar/data/1283699/000119312525085763/d924785dars.pdf)).

**Вывод:** на зрелом рынке повышение legacy-цены даёт +ARPU при росте оттока на единицы
десятых п.п. Поэтапность снижает всплеск оттока → в A2 закладываем пилот 10% → масштабирование.

### 3. Индия — самый масштабный «естественный эксперимент»

- 07/2024: Jio, Airtel, Vi подняли тарифы на 10–25%. ARPU Airtel +18% г/г, Jio +11,9%;
  Jio потерял ~11 млн абонентов за квартал, BSNL получил приток
  ([TelecomTalk/TRAI](https://telecomtalk.info/indian-telcos-see-major-uptick-in-arpu/996901/),
  [Medianama](https://www.medianama.com/2024/10/223-jio-subscriber-base-falls-after-tariff-hike-despite-uptick-in-5g-customers-in-q2fy25/)).
- 2018–19: минимальные ежемесячные пополнения (Airtel, Vodafone Idea): ARPU Airtel +20% кв/кв,
  Vodafone Idea +16,3%, но база Airtel сократилась с 340 до 286 млн
  ([Business Standard](https://www.business-standard.com/article/companies/bharti-airtel-likely-to-see-arpu-rise-benefit-only-from-march-quarter-119010400040_1.html),
  [TelecomTalk](https://telecomtalk.info/?p=185378)).
- Airtel выводит низкодоходные планы, чтобы поднять ARPU ([Outlook Business](https://www.outlookbusiness.com/corporate/bharti-airtel-scraps-select-plans-to-boost-arpu-growth)).

**Вывод:** жёсткие механики (обязательный минимум) дают сильный рост ARPU, но стоят доли рынка.
В Узбекистане с 2026 года номер хранится бесплатно до 1 года, а договор при нулевом балансе
расторгается только через 1 год — **принудительный минимум не применим**. Используем только
добровольные микропакеты (A3).

### 4. Казахстан — ближайший аналог по структуре рынка

- Beeline KZ повысил абонплату с 01.02.2025 (затронуто ~5% тарифов), Kcell — с 26.02.2025; Агентство по
  защите и развитию конкуренции начало разбирательство
  ([bes.media](https://bes.media/news/dohodi-beeline-rastut-bistree-chem-u-konkurentov-na-fone-povisheniya-tarifov-na-internet-i-svyaz-razbor-viruchki-mobilnih-operatorov/),
  [Digital Business](https://digitalbusiness.kz/2025-01-15/beeline-podnimaet-tseni-po-nekotorim-tarifam-s-15-fevralya/)).
- Выручка Beeline KZ за 9 мес. 2024: +18% (Kcell: +9%) — оператор, активнее управлявший ценой, рос быстрее.

**Вывод:** точечная работа с ценой (5% тарифов) — рабочая модель; антимонопольное внимание — норма,
к нему нужно готовить обоснование заранее.

### 5. Узбекистан — что уже сделано на рынке

- Ucell, 03.02.2026: +5 000 сум к абонплате «Yaxshi kayfiyat», «COSMO Start», «Ovoz», «Sof Start», «Doimiy Start»
  и др. с добавлением ГБ; **повышение не затронуло женщин 55+ и мужчин 60+** (ucell.uz).
- Beeline UZ: Oila Max 105 → 125 → 155 тыс. сум (+45 ГБ) с 11.03.2026 — вызвало публичную критику
  «платим за данные, которые не используем» ([kun.uz](https://kun.uz/en/news/2026/03/08/dear-customer-your-tariff-is-rising-again-why-were-paying-for-data-we-dont-even-use)).
- Beeline UZ: при снижении абонентов на 5,5% выручка +12% за 9 мес. 2025 за счёт multiplay и цифровых
  сервисов ([Frank.uz](https://frank.uz/en/news-en/beeline-uzbekistan-increased-its-revenue-by-12-to-2-864-trillion-soums-over-nine-months/),
  [UzDaily](https://www.uzdaily.uz/en/beeline-uzbekistan-increases-revenue-by-93-in-q3/)).
- Комитет по развитию конкуренции (11/2025) запросил обоснования повышения цен и предупредил о проверке
  при признаках согласованности ([Gazeta.uz](https://www.gazeta.uz/ru/2025/11/18/mobile-operator/)).
- Правила с 01/2026: смена ТП бесплатна, уведомление об изменениях ≥15 дней, хранение номера до 1 года
  ([kun.uz](https://kun.uz/ru/news/2026/01/28/smena-tarifnogo-plana-stala-besplatnoy-izmeneny-pravila-okazaniya-uslug-mobilnoy-svyazi),
  [anhor.uz](https://anhor.uz/news/free-7/)).

**Вывод:** Ucell уже провёл первую ценовую волну — **её результаты являются бесплатным естественным
экспериментом** для калибровки A2 (🟨 анализ D7 в [09](09_data_request_for_analysts.md)).

### 6. Миграция и упрощение портфеля

- Telenor Norway: выравнивание тарифов → базовый мобильный ARPU +4% (NOK 13) за счёт роста данных и
  миграции на новые ТП; отток — в основном низкодоходные подписки
  ([Telenor Q2 2014](https://www.telenor.com/wp-content/uploads/2014/01/Telenor-Q2-2014-report.pdf)).
- Ближневосточный оператор: обновление препейд-портфеля — 10% базы перешло менее чем за 3 месяца,
  ARPU перешедших +55%; программа миграции с legacy — выручка +15%
  ([Arthur D. Little](https://adlittle.com/en/node/21831), [Simon-Kucher](https://www.simon-kucher.com/index%2Ephp/insights/delivering-innovation-happy-customers-and-increase-revenue)) —
  *кейсы консультантов, возможен отбор успешных примеров*.
- T-Mobile переводит абонентов с grandfathered-планов на новые
  ([Fierce](https://www.fierce-network.com/wireless/report-t-mobile-to-move-customers-off-grandfathered-plans-to-new-rate-plans)).

### 7. Персонализация / Next-Best-Offer

- Flytxt: +8,2% ARPU (AI-decisioning), +8% при реактивации неактивных иностранных резидентов
  ([Cuspera/Flytxt](https://www.cuspera.com/vendors/flytxt-ai/customer-story)).
- fonYou: +22% ARPU на персональных пополнениях/бандлах ([fonYou](https://www.fonyou.com/downloads/fonyou_carrier_data_the_new_goldrush_wp.pdf)).
- Acxiom: ARPU +2% в год, отток −15% ([Acxiom](https://www.acxiom.com/wp-content/uploads/2020/07/telecommunications-case-study-v-5-19-20.pdf)).
- Telefónica Argentina: NBA-движок, 75+ офферов, 9 млн B2C, 1 500 признаков ([Teradata](https://teradata.com/customers/telefonica-argentina)).

**Поправка на оптимизм:** вендорские кейсы публикуют лучшие результаты. В модели используем
**+1…6% (мода 3%)** поверх rule-based кампаний, а не +8–22%.

### 8. Multiplay / контент

- VEON: multiplay ARPU в 3,6× выше; 22% базы дают 38,6% B2C-выручки
  ([Mobile World Live](https://mobileworldlive.com/operators/digital-push-begins-to-pay-off-for-veon)).
- Beeline UZ: multiplay 3,7 млн (51,3% MAU), ARPU в 3,7×, отток в 2,2× ниже ([UzDaily](https://www.uzdaily.uz/en/beeline-uzbekistan-increases-revenue-by-93-in-q3/)).

**Поправка на самоотбор:** активные клиенты сами выбирают контент. В модели эффект на отток
**−15…40%**, а не «в 2,2 раза».

### 9. Семейные тарифы

- Семейные планы снижают отток, но ARPU на линию примерно вдвое ниже одиночного
  ([RCR Wireless](https://www.rcrwireless.com/20050801/carriers/brady-bunch-plans-give-operators-lower-arpu-lower-churn)).
- Beeline UZ Oila (12/2024): 2–5 человек на одном счёте, Oila Max — до 3 человек, 100 тыс. сум,
  + Kinom и беспроцентные переводы в Beepul ([beeline.uz](https://beeline.uz/en/events/news/oila-beeline-uzbekistan-zapuskaet-lineyku-tarifov-dlya-vsey-semi)).
- У Ucell в открытых источниках — промо «1+1» (вторая SIM с BOR 50 на месяц), полноценного группового аккаунта не найдено
  ([ucell.uz](https://ucell.uz/en/news/1plus1_new_promotion)) — **проверить внутри**.

### 10. Airtime credit

- Vodacom: до 48% пополнений через аванс; MTN SA сократила долю с 42% до ~30% — минус 1,1 млн абонентов
  и −16,3% финтех-выручки за квартал ([TechCentral](https://techcentral.co.za/mtn-is-cutting-airtime-credit-while-its-rivals-lean-on-it/285226/)).
- MTN Nigeria приостановила XtraTime после новых правил FCCPC ([Techeconomy](https://techeconomy.ng/mtn-restore-xtratime-airtime-lending-fccpc-deon)).
- У Ucell уже есть «Mobil avans» 4 900–210 000 сум ([ucell.uz](https://ucell.uz/en/payment/mobilnyj-avans)) → инициатива B5 — это **персонализация лимитов**, а не новый продукт.

### 11. Регулирование и прозрачность (урок Великобритании)

Ofcom с 17.01.2025 запретил индексацию «на инфляцию + X%» в середине контракта: будущие повышения
должны быть указаны в фунтах и пенсах при продаже ([Telecoms.com](https://telecoms.com/operator-ecosystem/ofcom-bans-telcos-from-enacting-inflation-linked-mid-contract-price-rises)).
**Для Ucell:** если вводим ежегодную индексацию (A8), объявляем её **заранее, в сумах**, и только для
архивных ТП с бесплатной альтернативой.

## Что НЕ предлагаем, и почему

| Механика | Почему отклонена |
|---|---|
| Абонплата за «неактивный номер» | Правила 2026: номер хранится бесплатно до 1 года |
| Принудительный минимальный платёж (как в Индии 2018) | Противоречит правилам 2026; высокий риск оттока и регуляторного конфликта |
| Скрытые подписки / автопродление без согласия | Потребительский и репутационный риск; только явный opt-in |
| Повышение для соцгруппы (ж 55+, м 60+) | Ucell сам задал стандарт исключения в 02/2026; политический риск |
| Округление тарификации / скрытые платы | Неэтично и выявляется регулятором |

## Источники по рынку Узбекистана

- Opensignal, 09/2025: https://insights.opensignal.com/2025/09/01/uzbekistan-regional-position-operator-experience-september-2025/dt
- Итоги Ucell 2025: https://kun.uz/ru/news/2026/02/25/ucell-texnologik-yetakchilik-yili
- Ucell, новые тарифы (05/2025): https://ucell.uz/en/news/new_tariffs · BOR 90: https://ucell.uz/en/news/bor90 · BOR 70: https://ucell.uz/en/news/bor70_new · изменения ТП: https://ucell.uz/en/news/news_tarif · https://ucell.uz/en/news/news_tariff_update
- Ucell 30 лет: https://ucell.uz/en/news/ucell_30years_presents
- Mordor Intelligence (ARPU рынка < $3): https://www.mordorintelligence.com/industry-reports/uzbekistan-telecom-mno-market
- Продажа Mobiuz ($300 млн): https://kun.uz/en/news/2025/07/17/uzbekistan-expects-to-raise-300-million-from-mobiuz-sale
- Антимонопольное внимание к росту тарифов: https://podrobno.uz/cat/obchestvo/rost-tarifov-na-mobilnuyu-svyaz-v-uzbekistane-privlek-vnimanie-antimonopolnogo-komiteta/
- ЦБ РУз, инфляция и ставка: https://kun.uz/en/news/2025/12/11/central-bank-keeps-key-rate-unchanged-at-14-percent
- Переводы мигрантов $18,9 млрд: https://kun.uz/en/news/2026/03/17/remittances-to-uzbekistan-exceed-189-billion-tripling-in-five-years · ~1,3 млн в РФ: https://timesca.com/over-100000-uzbek-workers-recruited-to-work-in-russia-in-2025/
