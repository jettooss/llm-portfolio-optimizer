# Оптимизатор портфеля Return/Risk

Проект сравнивает LLM-модели как генераторы портфельных гипотез. Модель не считает доходность сама: она предлагает кандидаты в JSON, а Python проверяет каждый портфель на исторических ценах, считает риск/доходность и оставляет лучший вариант по score.

Основной сценарий сейчас находится в ноутбуке:

```text
default_feature_selection_2026.ipynb
```

## Постановка задачи

Нужно выбрать портфель из доступных инструментов так, чтобы на обучающем окне получить высокий ожидаемый годовой доход и не превысить ограничение по rolling risk.

Формально на каждом walk-forward шаге решается задача:

- вход: матрица исторических цен, список доступных тикеров, лимит риска `MAX_SIGMA_ANN`, ограничения на число активов и веса;
- решение: набор тикеров и long-only веса портфеля;
- ограничение: `sigma_q_0.9 <= MAX_SIGMA_ANN`, где `sigma_q_0.9` - 90-й перцентиль rolling annualized volatility;
- критерий: максимизировать `score`, который поощряет доходность и штрафует превышение риска и концентрацию;
- проверка: выбранный на train-окне портфель тестируется на следующем невидимом test-окне.

LLM здесь не является финансовым оракулом. Она генерирует кандидатов, а Python-оценщик строго проверяет их по данным и метрикам.

## Что делает проект

На каждом walk-forward шаге:

1. Берется train-окно с историческими ценами.
2. LLM предлагает несколько портфелей: тикеры и веса.
3. Python оценивает портфели на train-окне.
4. Лучший портфель проверяется на следующем test-окне.
5. Результаты сохраняются в CSV, JSON и графики.

Целевая функция:

```text
score = mu_ann - 20 * risk_violation - 0.02 * concentration
```

Где:

- `mu_ann` - ожидаемая годовая доходность на train-окне;
- `sigma_q_0.9` - 90-й перцентиль rolling annualized volatility;
- `risk_violation = max(0, sigma_q_0.9 - MAX_SIGMA_ANN)`;
- `concentration = sum(weight ** 2)`, штраф за слишком концентрированный портфель.

## Данные

Ноутбук ожидает данные в папке:

```text
data/
```

Основной файл:

```text
data/raw_dataset.parquet
```

Он используется для расчета доходности, rolling risk и test-проверки. В текущем walk-forward сценарии веса портфеля проверяются именно на этих ценовых рядах.

## LLM-модели

Настройки находятся в:

```text
llm_config.py
.env
```

По умолчанию используется OpenAI-compatible endpoint RouterAI:

```text
OPENAI_BASE_URL=https://routerai.ru/api/v1
```

Текущий дефолтный набор моделей:

```text
openai/gpt-oss-20b
openai/gpt-oss-120b
deepseek/deepseek-v4-pro
google/gemini-3.1-pro-preview
qwen/qwen3.5-35b-a3b
mistralai/mistral-small-2603
```

Если задан `RETURN_RISK_MODELS` в `.env`, он переопределяет дефолтный список.

Пример `.env`:

```text
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=https://routerai.ru/api/v1
OPENAI_TIMEOUT=180
RETURN_RISK_MODELS=openai/gpt-oss-20b,deepseek/deepseek-v4-pro
```

## Основной модуль

Вся тяжелая логика вынесена сюда:

```text
trading_optimizer/src/trading_optimizer/portfolio_return_optimizer.py
```

Главные функции:

- `run_multi_model_walk_forward_llm(...)` - запуск walk-forward эксперимента по нескольким моделям;
- `run_walk_forward_llm_optimizer(...)` - запуск walk-forward для одной модели;
- `optimize_return_under_risk(...)` - внутренний LLM-as-Optimizer цикл;
- `plot_walk_forward_comparison(...)` - построение сравнительных графиков;
- `portfolio_metrics_rolling(...)` - расчет rolling return/risk для портфеля.

## Результаты

Основная папка результатов:

```text
experiments_walk_forward_llm/
```

Главные файлы:

```text
all_models_walk_forward_results.csv
all_models_walk_forward_equity_curve.csv
all_models_walk_forward_summary.csv
all_models_walk_forward_epoch_scores.csv
compare_asset_frequency.csv
compare_train_score_by_epoch.csv
```

По каждой модели создается отдельная папка, например:

```text
experiments_walk_forward_llm/openai_gpt-oss-20b/
experiments_walk_forward_llm/deepseek_deepseek-v4-pro/
experiments_walk_forward_llm/qwen_qwen3.5-35b-a3b/
```

Внутри сохраняются:

- `walk_forward_results.csv`;
- `walk_forward_equity_curve.csv`;
- `walk_forward_summary.json`;
- `walk_forward_epoch_scores.csv`;
- `histories/step_XXX_history.csv`;
- `prompts/step_XXX_last_llm_prompt.json`.

## Аналитика выбора активов

Дополнительно создаются файлы:

```text
model_asset_analysis.md
model_final_asset_weights.csv
asset_consensus_summary.csv
model_asset_history_frequency.csv
model_final_asset_weights.png
asset_consensus_summary.png
```

Они показывают:

- какие активы выбрала каждая модель;
- какие тикеры стали консенсусом между моделями;
- какие активы чаще встречались в кандидатах;
- какие выбранные активы помогали или тянули портфель вниз на test-окне.

## Графики эксперимента

Ниже показаны графики, которые сохраняет ноутбук в `experiments_walk_forward_llm/`.

### Кривая капитала по моделям

![Кривая капитала](../experiments_walk_forward_llm/compare_equity_curve.png)

### Просадка по моделям

![Просадка](../experiments_walk_forward_llm/compare_drawdown.png)

### Доходность на test-окне

![Test return](../experiments_walk_forward_llm/compare_test_return.png)

### Лучший train score по эпохам

![Best train score](../experiments_walk_forward_llm/compare_best_train_score_by_epoch.png)

### Средний train score по эпохам

![Mean train score](../experiments_walk_forward_llm/compare_mean_train_score_by_epoch.png)

### Частота выбора активов

![Частота выбора активов](../experiments_walk_forward_llm/compare_asset_frequency.png)

### Финальные веса активов по моделям

![Финальные веса](../experiments_walk_forward_llm/model_final_asset_weights.png)

### Консенсус активов между моделями

![Консенсус активов](../experiments_walk_forward_llm/asset_consensus_summary.png)

## Как восстановить результаты в ноутбуке

Если kernel перезапущен и переменные потерялись, их можно восстановить из CSV:

```python
walk_forward_results_all = pd.read_csv(WF_OUT_DIR / "all_models_walk_forward_results.csv")
walk_forward_equity_curve_all = pd.read_csv(WF_OUT_DIR / "all_models_walk_forward_equity_curve.csv")
walk_forward_summary_all = pd.read_csv(WF_OUT_DIR / "all_models_walk_forward_summary.csv")
walk_forward_epoch_scores_all = pd.read_csv(WF_OUT_DIR / "all_models_walk_forward_epoch_scores.csv")
```

Частоту выбранных активов можно открыть так:

```python
asset_frequency = pd.read_csv(WF_OUT_DIR / "compare_asset_frequency.csv")
display(asset_frequency.sort_values(["model", "selected_count"], ascending=[True, False]))
```

А сохраненную картинку:

```python
from IPython.display import Image, display

display(Image(filename=str(WF_OUT_DIR / "compare_asset_frequency.png")))
```

## Важное замечание

Это исследовательский backtest. Историческая оптимизация и хорошие результаты на test-окне не гарантируют будущую доходность. LLM здесь используется только как генератор идей, а все расчеты риска и доходности выполняются обычным Python-кодом по заданным правилам.
