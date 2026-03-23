# 🐼 Pandas Data Manipulation Exercises

Practice exercises demonstrating core Pandas operations: merging datasets, aggregation, groupby analysis, and value counts on a user-purchase dataset.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Pandas](https://img.shields.io/badge/Pandas-Exercises-green)

## Operations Covered

- DataFrame merging (inner join on user ID)
- `.nunique()` — Count unique values
- `.value_counts()` — Frequency distributions
- `.groupby().agg()` — Grouped aggregations (mean, sum, count)
- Revenue analysis by country, device, and gender
- Sorting and filtering techniques

## Dataset

Expects two CSV files:
- `users.csv` — User demographics (country, device, gender, age)
- `purchases.csv` — Purchase records (user ID, price)

## Usage

```bash
python Pandas_operations.py
```

## License

MIT
