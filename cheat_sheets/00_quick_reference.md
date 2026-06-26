# 0. Pandas Quick Reference

> A one-page cheat sheet for the commands you'll reach for constantly.
> Each section links to the detailed sheet with full explanations,
> gotchas, and runnable examples.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
```

## Load & inspect — `01_dataframe_basics.md`

```python
df = pd.read_csv('data.csv')          # or sep='\t' for tab-separated
df.head()        df.tail()             # first / last 5 rows
df.shape          df.columns           df.dtypes   # all attributes, no ()
df.info()         df.describe()
```

## Subsetting — `01_dataframe_basics.md`

| Want                          | Syntax                              |
|----------------------------------|----------------------------------------|
| One column (Series)              | `df['col']`                            |
| Multiple columns (DataFrame)      | `df[['col1', 'col2']]`                 |
| Nth column by position            | `df.iloc[:, n]`                        |
| Row by label                      | `df.loc[label]`                        |
| Row by position                   | `df.iloc[pos]` (supports `-1` for last) |
| Rows + columns at once             | `df.loc[row_sel, col_sel]`              |
| Rows matching a condition          | `df[df['col'] > x]`                     |
| Rows matching multiple conditions  | `df[(cond1) & (cond2)]` or `df.query('cond1 and cond2')` |

`.loc` = **label**, `.iloc` = **position**. Never use `.ix` — removed
from pandas. Never use Python's `and`/`or`/`not` on a boolean Series —
use `&`/`|`/`~`.

## groupby / aggregation — `01_dataframe_basics.md`

```python
df.groupby('col')['target'].mean()
df.groupby(['col1', 'col2'])[['t1', 't2']].mean()
df.groupby('col').agg({'t1': 'mean', 't2': 'sum'})
df.groupby('col').agg(avg=('t1', 'mean'), total=('t2', 'sum'))   # named aggregation

df['col'].nunique()           # count of distinct values
df['col'].value_counts()       # frequency table
```

## Creating & modifying — `02_series_and_dataframe.md`

```python
pd.Series([1, 2, 3], index=['a', 'b', 'c'])
pd.DataFrame({'col1': [...], 'col2': [...]})

df['new_col'] = ...                      # add/replace a column
df.rename(columns={'old': 'new'})
df.drop(columns=['col'])
df['col'].apply(func)                     # element-wise
df.apply(lambda row: ..., axis=1)          # row-wise
```

Reassign instead of `inplace=True`: `df = df.fillna(0)`, not
`df.fillna(0, inplace=True)`.

## Export / import — `02_series_and_dataframe.md`

```python
df.to_csv('f.csv', index=False)      df = pd.read_csv('f.csv')
df.to_excel('f.xlsx', index=False)   df = pd.read_excel('f.xlsx')
df.to_pickle('f.pickle')              df = pd.read_pickle('f.pickle')
df.to_parquet('f.parquet')            df = pd.read_parquet('f.parquet')
```

## Plotting — `03_plotting.md`

```python
df['col'].plot.hist()             df.plot.scatter(x='a', y='b')
sns.histplot(df['col'])            sns.scatterplot(x='a', y='b', data=df)
sns.boxplot(x='cat', y='num', data=df, hue='cat2')
sns.lmplot(x='a', y='b', data=df, col='facet_col')   # faceted regression
```

Pick: pandas `.plot` for a quick look, **seaborn** for a polished
statistical chart, **matplotlib** (`fig, ax = plt.subplots()`) for full
control.

## Combining data — `04_combining_data.md`

```python
pd.concat([df1, df2])                       # stack rows (axis=0, default)
pd.concat([df1, df2], axis=1)                 # stack columns
pd.concat([df1, df2], ignore_index=True)       # renumber the index after stacking
pd.concat([df1, df2], join='inner')            # keep only shared labels

left.merge(right, on='key')                    # SQL-style join
left.merge(right, left_on='a', right_on='b', how='outer')
```

`how=`: `'inner'` (default, matches only) / `'left'` / `'right'` /
`'outer'` (everything). `DataFrame.append()` is gone — always use
`pd.concat`.

## Missing data — `05_missing_data.md`

```python
pd.isnull(x)       pd.notnull(x)        # NEVER use == to test for NaN
df.isnull().sum()                        # missing count per column

df.fillna(0)        df.ffill()      df.bfill()      df.interpolate()
df.dropna()          df.dropna(how='all')   df.dropna(thresh=N)

df['col'].sum(skipna=True)   # default: aggregations ignore NaN
```

## Tidy data & reshaping — `06_tidy_data_reshaping.md`

```python
pd.melt(df, id_vars=['id'], var_name='var', value_name='val')   # wide -> long
df.pivot_table(index='id', columns='var', values='val').reset_index()  # long -> wide

df['col'].str.split('_', expand=True)     # split a compound column

# normalize: split a table that mixes 2 observational units
sub = df[['a', 'b']].drop_duplicates()
sub['id'] = range(len(sub))
df.merge(sub, on=['a', 'b'])

import glob
files = glob.glob('data/*.csv')
pd.concat([pd.read_csv(f) for f in files])   # combine many files
```

## Deprecated / removed — don't use these even though you may see them in old tutorials

| Old / deprecated                 | Use instead                          |
|--------------------------------------|------------------------------------------|
| `.ix[...]`                          | `.loc[...]` (label) or `.iloc[...]` (position) |
| `df.append(other)`                  | `pd.concat([df, other])`                |
| `df.fillna(0, inplace=True)`        | `df = df.fillna(0)`                     |
| `df.fillna(method='ffill')`          | `df.ffill()`                            |
| `df.fillna(method='bfill')`          | `df.bfill()`                            |
| `sns.distplot(...)`                  | `sns.histplot(...)` / `sns.kdeplot(...)` / `sns.rugplot(...)` |
| `sns.factorplot(...)`                | `sns.catplot(...)`                      |
