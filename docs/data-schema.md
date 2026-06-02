# Data Schema & Column Mapping

Source: [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) (split: `train`, ~51.7k rows).

## Source columns → canonical fields

| Source column | Canonical field | Transformation |
|---------------|-----------------|----------------|
| `name` | `name` | Trim; required |
| `address` | `location` | City extracted from address; Bangalore aliases normalized |
| `location` | `attributes.area` | Neighborhood / area (e.g. BTM, Koramangala) |
| `cuisines` | `cuisines` | Split on `,` / `;`; lowercase tokens |
| `approx_cost(for two people)` | `cost_for_two`, `cost_bucket` | Parse numeric; derive bucket from thresholds |
| `rate` | `rating` | Parse `4.1/5` style; drop `NEW`, `-`, null |
| `rest_type`, `online_order`, `book_table`, `dish_liked`, `listed_in(type)`, `listed_in(city)` | `attributes.*` | Optional metadata |
| (row index) | `id` | `r{index}` stable id |

## Canonical `RestaurantRecord`

```text
id: string
name: string
location: string          # city (e.g. Bangalore)
cuisines: list[string]
rating: float             # 0–5
cost_for_two: float?      # INR-style numeric when parseable
cost_bucket: low|medium|high?
attributes: dict
```

## Row dropping rules

- Missing or empty `name`
- Unparseable `rate` (`NEW`, `-`, null, out of range)
- No valid city from `address`

## Budget thresholds (calibrated)

Profiling on `approx_cost(for two people)`:

| Statistic | Value (INR) |
|-----------|-------------|
| p25 | 300 |
| p50 | 400 |
| p75 | 550 |
| max | 950 |

**v1 config** (`config/settings.py`):

| Tier | Rule |
|------|------|
| low | `cost_for_two <= 400` |
| medium | `400 < cost_for_two <= 550` |
| high | `cost_for_two > 550` |

Override via `BUDGET_LOW_MAX` and `BUDGET_MEDIUM_MAX` environment variables.

## City normalization

- Tokens `bengaluru`, `banglore`, `bengalore`, `btm bangalore` → **Bangalore**
- If address contains any Bangalore token, city is **Bangalore**
- Tails like `Karnataka`, `India`, `Delivery Only` are not used as city

## Cache

Normalized records: `data/cache/restaurants.parquet`

Refresh: `REFRESH_DATASET=true` or `load_restaurants(refresh=True)`.

## Exploration

```bash
source .venv/bin/activate
python scripts/explore_dataset.py
python scripts/load_restaurants_demo.py
```
