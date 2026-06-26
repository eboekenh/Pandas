# 1. Pandas DataFrame Basics

> Goal of this sheet: go from "never opened pandas" to comfortably loading a
> dataset and looking at the parts you care about. Every example below is
> self-contained — copy it into a Python file or notebook and run it.

## 1.1 What pandas actually is

Pandas adds two new data types to Python:

| Type        | Think of it as...                              |
|-------------|-------------------------------------------------|
| `Series`    | one column of data (a labeled 1‑D array)        |
| `DataFrame` | a whole spreadsheet/table (a dict of `Series`)  |

Every column in a `DataFrame` is a `Series`, and every column must be a
single dtype, but different columns can hold different dtypes (numbers,
text, dates, ...). Rows can mix types because each row is just one element
from several different `Series`.

```python
import pandas as pd
```

By convention pandas is **always** imported as `pd`.

## 1.2 Loading your first dataset

```python
import pandas as pd

# comma-separated file (the default)
df = pd.read_csv('data.csv')

# tab-separated file -- use sep='\t'
df = pd.read_csv('data.tsv', sep='\t')
```

If you don't have a file handy, build a small DataFrame by hand so you can
follow along with every example on this page:

```python
df = pd.DataFrame({
    'country':   ['Afghanistan', 'Afghanistan', 'Brazil', 'Brazil', 'China', 'China'],
    'continent': ['Asia', 'Asia', 'Americas', 'Americas', 'Asia', 'Asia'],
    'year':      [1952, 1957, 1952, 1957, 1952, 1957],
    'lifeExp':   [28.801, 30.332, 50.917, 51.516, 44.0, 50.5],
    'pop':       [8425333, 9240934, 56602560, 65551171, 556263527, 637408000],
    'gdpPercap': [779.45, 820.85, 2108.94, 2487.37, 400.4, 575.99],
})
```

## 1.3 First look at a dataset

```python
df.head()        # first 5 rows
df.head(n=10)    # first 10 rows
df.tail()        # last 5 rows
df.tail(n=1)     # just the very last row

df.shape         # (rows, columns) tuple -- NOTE: no parentheses, it's an attribute!
df.shape[0]      # number of rows
df.shape[1]      # number of columns

df.columns       # Index of column names
df.dtypes        # dtype of every column
df.info()        # dtypes + non-null counts + memory usage, all at once
df.describe()    # summary stats (count, mean, std, min, quartiles, max) for numeric columns
type(df)         # <class 'pandas.core.frame.DataFrame'>
```

`df.shape` is an **attribute**, not a method — leave off the parentheses.
`df.shape()` raises `TypeError: 'tuple' object is not callable`.

### Pandas dtypes vs. Python types

| Pandas dtype    | Plain Python equivalent | Meaning                              |
|-----------------|--------------------------|---------------------------------------|
| `object`        | `str`                    | text (or any mixed Python object)     |
| `int64`         | `int`                    | whole numbers                         |
| `float64`       | `float`                  | numbers with decimals (and `NaN`)     |
| `bool`          | `bool`                   | `True` / `False`                      |
| `datetime64[ns]`| `datetime.datetime`      | dates/timestamps                      |
| `category`      | —                        | a fixed, repeated set of string labels|

## 1.4 Subsetting columns

### By name

```python
country_df = df['country']          # single column -> a Series
country_df = df.country             # same thing, "dot notation" (only works for valid identifier names)

subset = df[['country', 'continent', 'year']]   # multiple columns -> a DataFrame
#            ^ outer brackets = "subset the DataFrame"
#                ^ inner brackets = "a list of the columns I want"
```

That double square bracket (`df[[...]]`) trips up everyone at first: the
*outer* brackets are pandas' indexing syntax, the *inner* brackets are just
an ordinary Python `list`.

### By position

```python
df.iloc[:, 0]          # first column, by position, as a Series
df.iloc[:, [0, -1]]    # first and last column, as a DataFrame
df.iloc[:, 0:3]        # first three columns, by position
```

Don't use `df[[0]]` to mean "first column" — if your columns aren't
literally named `0`, pandas will try to match a column *named* `0` and
raise a `KeyError`. Use `.iloc` whenever you mean "the Nth column."

### Single column vs. multiple columns: what type comes back?

```python
type(df['country'])        # Series  (one set of brackets)
type(df[['country']])      # DataFrame (double brackets -- a 1-column DataFrame)
```

## 1.5 Subsetting rows

Every DataFrame has a **row label** (the bold numbers on the left when you
print it), separate from the **row position**. By default the label is just
the row number, but it doesn't have to be (e.g. dates in time series data).
Two tools, two jobs:

| Tool        | Subsets by...                  |
|-------------|---------------------------------|
| `.loc[]`    | row/column **label** (name)     |
| `.iloc[]`   | row/column **position** (0, 1, 2, ...) |

> Older pandas had a third option, `.ix[]`, that guessed between label and
> position. It was confusing and was **removed** from pandas years ago —
> always use `.loc` or `.iloc` explicitly.

```python
df.loc[0]                # row with label 0          -> Series
df.loc[[0, 99, 999]]      # rows with labels 0, 99, 999 -> DataFrame

df.iloc[0]                # row at position 0 (same as df.loc[0] if index is default)
df.iloc[-1]                # the LAST row -- this works with iloc but NOT with loc
df.iloc[[0, 99, 999]]     # rows at positions 0, 99, 999

df.iloc[0:3]              # first 3 rows by position (like list slicing)
```

`df.loc[-1]` will raise a `KeyError` unless you actually have a row labeled
`-1` — `.loc` always means "the label," never "count from the end." For
"give me the last row," use `.iloc[-1]` or `df.tail(1)`.

## 1.6 Subsetting rows AND columns at the same time

```python
df.loc[42, 'country']            # one cell, by row label + column name
df.iloc[42, 0]                   # one cell, by row position + column position

df.loc[[0, 99], ['country', 'lifeExp']]      # multiple rows x multiple columns, by label
df.iloc[[0, 99], [0, 3]]                     # multiple rows x multiple columns, by position
```

Prefer passing **actual column names** over numeric positions when you can
— it's more readable and survives the columns being reordered later.

### Cheat table: every way to subset a DataFrame

| Syntax                              | Result                              |
|--------------------------------------|--------------------------------------|
| `df['col']`                          | one column (Series)                 |
| `df[['col1', 'col2']]`               | multiple columns (DataFrame)        |
| `df.loc['label']`                    | row by label                        |
| `df.loc[['l1', 'l2']]`               | multiple rows by label              |
| `df.iloc[0]`                         | row by position                     |
| `df.iloc[[0, 1]]`                    | multiple rows by position           |
| `df[bool_series]`                    | rows where the boolean Series is `True` |
| `df[start:stop:step]`                | rows by Python slice notation       |
| `df.loc[row_sel, col_sel]`           | rows & columns simultaneously       |

## 1.7 Grouped & aggregated calculations

This is the "split‑apply‑combine" pattern: split the data into groups, apply
a calculation to each group, combine the results into one table.

```python
# average life expectancy per year
df.groupby('year')['lifeExp'].mean()

# what's actually happening, one step at a time:
grouped = df.groupby('year')             # a DataFrameGroupBy "recipe" -- nothing computed yet
grouped_col = grouped['lifeExp']         # a SeriesGroupBy -- still just a recipe
grouped_col.mean()                       # now we actually compute something

# group by MULTIPLE columns, summarize MULTIPLE columns at once
df.groupby(['year', 'continent'])[['lifeExp', 'gdpPercap']].mean()

# different aggregation per column
df.groupby('continent').agg({'lifeExp': 'mean', 'pop': 'sum'})

# multiple aggregations on the same column
df.groupby('continent')['lifeExp'].agg(['mean', 'min', 'max', 'count'])

# named aggregation -- cleanest way to get readable output columns
df.groupby('continent').agg(
    avg_life_exp=('lifeExp', 'mean'),
    total_pop=('pop', 'sum'),
)
```

### Counting things

```python
df['country'].nunique()                 # how many DISTINCT countries overall
df.groupby('continent')['country'].nunique()   # distinct countries PER continent

df['continent'].value_counts()           # frequency count of every value
df.groupby('continent')['country'].count()      # row count per continent (counts duplicates)
```

`nunique` = "how many different values," `value_counts` = "how often does
each value show up," plain `count` = "how many non-missing rows."

## 1.8 A first plot

Pandas Series and DataFrames have a built-in `.plot()` that's a thin wrapper
around matplotlib — great for a quick look without importing anything else.

```python
import matplotlib.pyplot as plt

yearly_life_exp = df.groupby('year')['lifeExp'].mean()
yearly_life_exp.plot()      # quick line plot, index on the x-axis
plt.show()
```

See `03_plotting.md` for the full plotting cheat sheet (matplotlib, seaborn,
and every pandas `.plot.*` method).

## 1.9 Common first mistakes

- Calling `df.shape()` instead of `df.shape` (it's an attribute).
- Using `df[0]` hoping for "the first column" — pandas looks for a column
  *named* `0`. Use `df.iloc[:, 0]`.
- Mixing up `.loc` (label) and `.iloc` (position) — when the default index
  is just row numbers they happen to behave the same, which hides the bug
  until you filter/sort/reindex the data and the index stops matching row
  position.
- Forgetting the double brackets for multi-column selection: `df['a', 'b']`
  is a `KeyError`; you want `df[['a', 'b']]`.
