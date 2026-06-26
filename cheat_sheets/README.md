# Pandas Cheat Sheets

A complete, beginner-friendly set of pandas cheat sheets — go from "never
opened pandas" to comfortable with every concept covered here. Based on
*Pandas for Everyone* by Daniel Y. Chen, rewritten with modern,
non-deprecated pandas syntax and runnable, self-contained examples.

| # | Sheet | Covers |
|---|---------|----------|
| [00](00_quick_reference.md) | **Quick reference** | One-page condensed summary of every topic below — start here if you just need a reminder |
| [01](01_dataframe_basics.md) | **DataFrame basics** | Loading data, `.head`/`.shape`/`.info`, subsetting rows & columns, `.loc`/`.iloc`, groupby & aggregation, your first plot |
| [02](02_series_and_dataframe.md) | **Series & DataFrame structures** | Creating Series/DataFrames by hand, attributes vs. methods, boolean subsetting, vectorized ops & index alignment, modifying data, exporting/importing |
| [03](03_plotting.md) | **Plotting** | matplotlib fundamentals (Figure/Axes), seaborn statistical plots & facets, pandas' built-in `.plot.*` |
| [04](04_combining_data.md) | **Combining data** | `pd.concat` (rows/columns, mismatched labels), `pd.merge` (one-to-one/many-to-one/many-to-many, join types) |
| [05](05_missing_data.md) | **Missing data** | What `NaN` is, where it comes from, finding/counting it, `fillna`/`ffill`/`bfill`/`interpolate`/`dropna`, calculations with missing values |
| [06](06_tidy_data_reshaping.md) | **Tidy data & reshaping** | Hadley Wickham's tidy data rules, `melt`, `pivot_table`, splitting compound columns, normalizing tables, combining many files |

## How to use these

Every code block is self-contained — copy it into a Python file or
notebook and run it as-is (each sheet builds its own small example data
inline, so you don't need any external CSV files to follow along).

Read them in order (00 → 06) if you're starting from zero, or jump
straight to the sheet that matches what you're stuck on. Each sheet also
calls out anywhere the source material used outdated/removed pandas
syntax (like `.ix` or `inplace=True`) and shows the modern replacement.
