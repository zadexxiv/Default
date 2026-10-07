# v2 — 4 инициативы роста ARPU архивной базы + Ucell Club (Loyalty)

**Текущая версия.** v1 (портфель из 13 идей) лежит в корне репозитория как справочный материал.

> 🟨 **Ваш этап:** анализ внутренних данных — [docs/12_data_request_for_analysts.md](docs/12_data_request_for_analysts.md).
> ❓ Мои допущения, которые стоит проверить, — [docs/16_open_questions.md](docs/16_open_questions.md).

## Главное

| | |
|---|---|
| Инициативы | I1 Sunset / Migration (+10–15%) · I2 More-for-More · I3 бустер + роуминг-промо · I4 Loyalty (кэшбэк, Daily Drops, Weekly Wins, Monthly Grand) |
| ΔARPU архивной когорты к M24 | **+9,1%** (P10–P90: +4,3…+12,1%); план +10,8% |
| Вклад портфеля за 36 мес. | **89,6 млрд сум** |
| Бюджет MVP Loyalty | **≈ 3,5 млрд сум (~$290 тыс.)** |
| Loyalty при масштабе | ~1,5 млн участников, ~2,6 млрд сум/мес.; окупаемость ~2,5 года |
| Порог участия | **O5:** играют все, кто платит вовремя; шансы растут с АП; Club+ Pass вместо платного входа |

## Документы

| # | Документ |
|---|---|
| 00 | [Executive Summary](docs/00_executive_summary.md) |
| 01 | [Discovery: гипотезы, исследования, гайды](docs/01_discovery.md) |
| 02 | [Бенчмарки: Verizon, T-Mobile, Turkcell, Safaricom, Tele2, Beeline UZ, Mobiuz + право РУз](docs/02_benchmarks.md) |
| 03 | [Инициативы I1–I3](docs/03_initiatives_1_3.md) |
| 04 | [Loyalty: механика, призы, бюджет по компонентам](docs/04_loyalty_program_design.md) |
| 05 | [Порог участия: 5 вариантов и решение win-win](docs/05_threshold_win_win.md) |
| 06 | [Партнёры: вовлечение, система, офлайн, брать ли деньги](docs/06_partners.md) |
| 07 | [Бюджет и unit-экономика](docs/07_budget_unit_economics.md) |
| 08 | [Шансы на успех](docs/08_success_probability.md) |
| 09 | [CJM](docs/09_cjm.md) |
| 10 | [Roadmap и Gantt](docs/10_roadmap_gantt.md) |
| 11 | [Data-Driven: дизайн MVP и экспериментов](docs/11_data_driven_mvp.md) |
| 12 | [🟨 Запрос данных и ваш анализ](docs/12_data_request_for_analysts.md) |
| 13 | [Риски и юридические вопросы](docs/13_risks_legal.md) |
| 14 | [Кросс-функциональная команда и RACI](docs/14_raci_cross_department.md) |
| 15 | [Питч и Q&A](docs/15_pitch_qa.md) |
| 16 | [Открытые вопросы](docs/16_open_questions.md) |

## Модель

| Файл | Что это |
|---|---|
| `model/assumptions_v2.py` | Все допущения, каталог призов, таблица сундука, варианты порога |
| `model/model_v2.py` | Монте-Карло 20 000 × 36 мес.: инициативы, Loyalty, портфель, пороги, чувствительность |
| `model/output/results_v2.md` | Результаты последнего прогона |
| `model/Ucell_v2_ARPU_Loyalty_Model.xlsx` | Excel с живыми формулами: Inputs · Initiatives · Monthly_I · Loyalty_Inputs · Prizes · Daily_Drops · Loyalty_Monthly · MVP_Budget · Thresholds · Portfolio · AB_Calculator · MC_Results |
| `prototype/loyalty_mvp_prototype.html` | Кликабельный прототип экрана программы (для юзабилити-тестов на Discovery) |

```bash
python v2/model/model_v2.py && python v2/model/build_excel_v2.py
```

Excel повторяет детерминированный прогон Python один в один (проверено по всем инициативам, компонентам Loyalty,
портфелю и порогам).
