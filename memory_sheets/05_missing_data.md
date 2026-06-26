# 5. Missing Data

> It is rare to get a dataset with zero missing values — and even data that
> starts complete can pick up missing values during your own munging
> (merges, reindexing, user input). Knowing how missing values behave is
> part of basic data validity checking, not an edge case.

```python
import numpy as np
import pandas as pd
```

## 5.1 What a `NaN` value actually is

Different tools represent "missing" differently — SQL has `NULL`, some
languages use `NA`, some datasets encode it as an empty string `''` or even
a sentinel number like `99`. **Pandas always displays missing numeric data
as `NaN`** ("Not a Number"), which it gets from numpy.

```python
from numpy import nan   # NaN, NAN, and nan are all the exact same object
```

### The single most important fact about `NaN`: it is never equal to anything

Missing means "we don't know the value" — so it can't be compared for
equality, not even to itself.

```python
nan == True     # False
nan == False    # False
nan == 0         # False
nan == ''        # False
nan == nan       # False  <- yes, really, even to itself
```

Because `==` never works, pandas gives you dedicated functions instead:

```python
pd.isnull(nan)    # True
pd.isnull(42)     # False
pd.notnull(nan)   # False
pd.notnull(42)    # True
```

> Modern pandas also exposes `pd.isna()` / `pd.notna()` (and the
> Series/DataFrame methods `.isna()` / `.notna()`) as exact aliases of
> `isnull`/`notnull`. Either name works identically — `isna`/`notna` is
> the more commonly seen spelling in current docs and code.

## 5.2 Where missing values come from

### 5.2.1 Loading data

`read_csv` already understands common missing-value spellings (`NA`,
`NaN`, empty cells, ...) and converts them to `NaN` automatically. Three
parameters give you control over exactly what counts as "missing":

| Parameter           | Default | What it does                                                  |
|------------------------|-----------|------------------------------------------------------------------|
| `na_values`           | none      | extra strings/values to *also* treat as missing, e.g. `na_values=[99]` for health data that codes 99 as missing |
| `keep_default_na`     | `True`    | whether pandas' built-in list of missing-value spellings (`NA`, `NaN`, empty string, ...) is still used alongside `na_values` |
| `na_filter`           | `True`    | master switch — set `False` to skip missing-value detection entirely (a performance optimization for data you know has no missing values) |

```python
pd.read_csv('survey_visited.csv')                                   # default: '' becomes NaN
pd.read_csv('survey_visited.csv', keep_default_na=False)             # '' stays as a literal empty string, not NaN
pd.read_csv('survey_visited.csv', na_values=[''], keep_default_na=False)  # back to NaN, but ONLY for '' (nothing else)
```

### 5.2.2 Merging data

Joins (see `04_combining_data.md`) routinely introduce `NaN` wherever a
key on one side has no match, or where the original data already had
missing fields:

```python
visited = pd.read_csv('survey_visited.csv')   # has one NaN 'dated' to begin with
survey  = pd.read_csv('survey_survey.csv')    # has NaN 'person' for two rows

vs = visited.merge(survey, left_on='ident', right_on='taken')
# every row where 'dated' or 'person' was already missing keeps that NaN,
# AND it gets duplicated across however many survey rows matched that visit
```

### 5.2.3 You create them yourself

`NaN` is a perfectly valid value to put in a Series or DataFrame directly:

```python
num_legs = pd.Series({'goat': 4, 'amoeba': np.nan})

scientists = pd.DataFrame({
    'Name': ['Rosaline Franklin', 'William Gosset'],
    'Born': ['1920-07-25', '1876-06-13'],
})
scientists['missing'] = np.nan      # assign an entire column of NaN at once
```

### 5.2.4 Reindexing

`reindex` (or `.loc[]`/slicing with new labels) keeps your existing values
but introduces `NaN` for every label that didn't already exist. This is
the standard way to "fill the gaps" in something like a yearly time series:

```python
life_exp = gapminder.groupby('year')['lifeExp'].mean()   # only has the years actually in the data: 1952, 1957, ...

y2000 = life_exp[life_exp.index > 2000]      # subset first
y2000.reindex(range(2000, 2010))             # then reindex onto every year 2000-2009
# year
# 2000          NaN
# 2001          NaN
# 2002    65.694923
# 2003          NaN
# ...
# 2007    67.007423
# 2008          NaN
# 2009          NaN
```

> The book reaches for `life_exp.ix[range(2000, 2010), ]` to do this in one
> step. **`.ix` was removed from pandas** — there's no direct one-step
> replacement that mixes label and position the way `.ix` did; the safe
> modern pattern is exactly the two-step subset-then-`reindex()` shown
> above.

## 5.3 Finding and counting missing data

```python
ebola = pd.read_csv('country_timeseries.csv')   # ebola case-count data, many sparse columns

ebola.shape            # (122, 18)
ebola.count()           # non-missing count per column (NOT total rows!)

num_missing = ebola.shape[0] - ebola.count()    # missing count per column
```

Total missing values across the *whole* DataFrame (or one column):

```python
np.count_nonzero(ebola.isnull())                      # 1214 total missing cells
np.count_nonzero(ebola['Cases_Guinea'].isnull())       # 29 missing in just this column
```

`value_counts` normally drops `NaN` — pass `dropna=False` to see how often
missing shows up as if it were just another value:

```python
ebola['Cases_Guinea'].value_counts(dropna=False).head()
# NaN      29
# 86.0      3
# 495.0     2
# ...
```

| Tool                                   | Tells you...                                  |
|-------------------------------------------|--------------------------------------------------|
| `.count()`                              | non-missing count, per column                   |
| `shape[0] - .count()`                   | missing count, per column                        |
| `np.count_nonzero(df.isnull())`         | total missing cells in the whole frame           |
| `np.count_nonzero(df['col'].isnull())`  | missing count in one specific column             |
| `.value_counts(dropna=False)`           | frequency table that includes `NaN` as a category |

## 5.4 Cleaning missing data

### 5.4.1 Recode with a fixed value: `fillna`

```python
ebola.fillna(0)             # every NaN becomes 0
```

> The book calls this with `inplace=True` to mutate the data without
> making a copy. **Avoid `inplace=True`** (see `02_series_and_dataframe.md`
> §2.6) — it doesn't reliably skip the internal copy anyway, and silently
> mutating data makes bugs harder to track down. Just reassign:
> `ebola = ebola.fillna(0)`.

### 5.4.2 Forward fill: carry the last known value forward

```python
ebola.ffill()      # modern method form
ebola.fillna(method='ffill')   # equivalent, older spelling
```

Each `NaN` is replaced by whatever the **most recent non-missing value
above it** was. If a column's very first values are missing, they stay
missing — there's nothing earlier to carry forward.

### 5.4.3 Backward fill: carry the next known value backward

```python
ebola.bfill()
ebola.fillna(method='bfill')   # equivalent, older spelling
```

Mirror image of forward fill: each `NaN` takes the **next non-missing
value below it**. If a column's last values are missing, they stay
missing.

> The book uses `ebola.fillna(method='ffill')` / `method='bfill')`.
> **`fillna(method=...)` is deprecated in modern pandas** — use the
> dedicated `.ffill()` / `.bfill()` methods shown above instead; they do
> exactly the same thing with a clearer name.

### 5.4.4 Interpolate: fill using surrounding values

```python
ebola.interpolate()   # default: linear interpolation between the nearest known values on each side
```

Where `ffill`/`bfill` just copy a neighboring value verbatim, `interpolate`
computes a value *between* the nearest known points (e.g. the midpoint, for
linear interpolation). The `method=` parameter supports other interpolation
strategies (`'time'`, `'polynomial'`, etc.) for fancier cases.

### 5.4.5 Drop missing data: `dropna`

Sometimes the right move is to throw away incomplete rows/columns rather
than guess a fill value — but be careful:

```python
ebola.dropna()           # default how='any': drop a row if ANY column is missing
ebola.dropna(how='all')   # only drop a row if ALL columns are missing
ebola.dropna(thresh=10)   # keep rows with at least 10 non-missing values
```

```python
ebola.shape              # (122, 18)
ebola.dropna().shape      # (1, 18)   <- only ONE complete row survives!
```

> **Be very careful with `dropna()`** on real-world sparse data. The ebola
> dataset above goes from 122 rows to just 1 row of "complete cases" —
> dropping anything with a single missing value among 18 columns is almost
> never what you actually want. Either the missingness is random (and
> dropping loses most of your sample for no reason) or it isn't (and
> dropping introduces bias, since the rows that remain aren't
> representative of the whole). `how=` and `thresh=` exist specifically
> to make dropping less all-or-nothing.

| `dropna` parameter | Meaning                                                  |
|------------------------|-------------------------------------------------------------|
| `how='any'` *(default)*| drop the row/column if **any** value is missing            |
| `how='all'`           | drop only if **every** value is missing                     |
| `thresh=N`            | keep only rows/columns with at least `N` non-missing values |
| `axis=1`              | apply the drop to **columns** instead of rows               |

## 5.5 Calculations with missing data

By default, any arithmetic that touches a `NaN` propagates the `NaN`:

```python
ebola['Cases_multiple'] = (
    ebola['Cases_Guinea'] + ebola['Cases_Liberia'] + ebola['Cases_SierraLeone']
)
# Cases_multiple is only non-missing for rows where ALL THREE inputs were non-missing
```

Aggregation methods (`.sum()`, `.mean()`, etc.) behave differently — they
have a `skipna` parameter that defaults to `True`, meaning they quietly
ignore `NaN` rather than propagate it:

```python
ebola['Cases_Guinea'].sum(skipna=True)    # 84729.0 -- NaNs ignored (this is the default)
ebola['Cases_Guinea'].sum(skipna=False)   # nan -- a single missing value poisons the whole sum
```

| Operation type                          | Behavior with `NaN`                                   |
|--------------------------------------------|------------------------------------------------------------|
| Element-wise arithmetic (`+`, `-`, `*`, `/`) | always propagates — any `NaN` input makes that output `NaN` |
| Aggregations (`.sum()`, `.mean()`, `.std()`, ...) | skip `NaN` by default (`skipna=True`); pass `skipna=False` to force propagation |

## 5.6 Key takeaways

- `NaN` is never `==` to anything, including itself — always test with
  `pd.isnull()`/`isna()` or `pd.notnull()`/`notna()`, never `== nan`.
- Missing values can enter your data four ways: they were already in the
  source file, they were introduced by a merge, you added them yourself
  (manual `NaN`), or you created them by reindexing onto labels that
  didn't exist before.
- Cleaning options, roughly from "least destructive" to "most destructive":
  `fillna(value)` → `.ffill()`/`.bfill()` → `.interpolate()` →
  `.dropna()`. Reach for `dropna()` last, and always check `.shape` before
  and after to make sure you didn't just throw away most of your dataset.
- Element-wise math propagates `NaN`; most aggregation methods quietly
  skip it instead (`skipna=True` by default) — know which behavior you're
  getting for the calculation you're writing.
