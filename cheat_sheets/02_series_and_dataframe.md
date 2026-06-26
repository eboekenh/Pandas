# 2. Series & DataFrame: Creating, Modifying, Exporting

## 2.1 Creating a Series by hand

A `Series` is a one-dimensional, labeled array — like a Python `list` where
every element also has a name (the *index*).

```python
import pandas as pd
import numpy as np

# from a plain list -- gets a default 0,1,2,... index
s = pd.Series(['banana', 42])
#  0    banana
#  1        42

# mixed types -> dtype becomes 'object' (generic Python objects)

# give it your own index labels
s = pd.Series(
    ['Wes McKinney', 'Creator of Pandas'],
    index=['Person', 'Who'],
)
#  Person           Wes McKinney
#  Who         Creator of Pandas

# from a dict -- keys become the index automatically
s = pd.Series({'goat': 4, 'amoeba': np.nan})
#  goat      4.0
#  amoeba    NaN

# from a single scalar, repeated for every given index label
s = pd.Series(5, index=['a', 'b', 'c'])
#  a    5
#  b    5
#  c    5
```

## 2.2 Creating a DataFrame by hand

The most common way: a dict where each key is a column name and each value
is the column's contents.

```python
scientists = pd.DataFrame({
    'Name':       ['Rosaline Franklin', 'William Gosset'],
    'Occupation': ['Chemist', 'Statistician'],
    'Born':       ['1920-07-25', '1876-06-13'],
    'Died':       ['1958-04-16', '1937-10-16'],
    'Age':        [37, 61],
})
```

Dict key order is preserved in modern Python/pandas, but if you want to be
explicit (or set the row index to something other than 0,1,2,...), pass
`columns=` and `index=`:

```python
scientists = pd.DataFrame(
    data={
        'Occupation': ['Chemist', 'Statistician'],
        'Born':       ['1920-07-25', '1876-06-13'],
        'Died':       ['1958-04-16', '1937-10-16'],
        'Age':        [37, 61],
    },
    index=['Rosaline Franklin', 'William Gosset'],   # use names as the row index
    columns=['Occupation', 'Born', 'Died', 'Age'],   # force this column order
)
```

You can also build a DataFrame from a list of rows:

```python
pd.DataFrame(
    [['n1', 'n2', 'n3', 'n4']],
    columns=['A', 'B', 'C', 'D'],
)
```

## 2.3 Series attributes & methods

When `.loc`/`.iloc` returns a single row, you get back a `Series` whose
index is the *column names* of the original row:

```python
first_row = scientists.loc['William Gosset']
type(first_row)     # Series
first_row.index     # Index(['Occupation', 'Born', 'Died', 'Age'])
first_row.values    # array(['Statistician', '1876-06-13', '1937-10-16', 61], dtype=object)
first_row.keys()    # same as .index, but it's a method, so it needs ()
```

**Attribute vs. method**: attributes (`.index`, `.values`, `.shape`,
`.dtype`) describe the object and need no parentheses. Methods (`.keys()`,
`.mean()`, `.sort_values()`) *do* something and are called with `()`.

### The most useful Series attributes

| Attribute        | What it gives you                          |
|-------------------|---------------------------------------------|
| `.index`          | the row labels                              |
| `.values`         | the underlying array (no labels)            |
| `.dtype`          | the data type of the values                 |
| `.shape`          | `(n,)` tuple                                |
| `.size`           | number of elements                          |
| `.T`              | transpose (mostly a no-op for 1-D Series)   |

### The most useful Series methods

| Method               | What it does                                   |
|------------------------|-------------------------------------------------|
| `.mean()`, `.median()`, `.mode()` | central tendency                  |
| `.min()`, `.max()`    | extremes                                        |
| `.std()`, `.var()`    | spread                                          |
| `.quantile(q)`        | value at quantile `q` (e.g. `0.5` = median)     |
| `.describe()`         | all of the above, in one call                   |
| `.sum()`, `.count()`  | total / number of non-missing values            |
| `.unique()`           | array of distinct values                        |
| `.nunique()`          | count of distinct values                        |
| `.value_counts()`     | frequency table                                 |
| `.sort_values()`      | sort by value                                   |
| `.sort_index()`       | sort by index label                             |
| `.drop_duplicates()`  | remove repeated values                          |
| `.isin([...])`        | boolean: is each value in this list?            |
| `.apply(func)`        | run `func` on every element                     |
| `.map(func_or_dict)`  | element-wise transform/lookup                   |
| `.astype(dtype)`      | convert/cast the dtype                          |
| `.replace(a, b)`      | swap values                                     |
| `.sample(n)`          | random sample of rows                           |
| `.to_frame()`         | convert the Series into a 1-column DataFrame    |
| `.corr(other)`, `.cov(other)` | correlation / covariance with another Series |
| `.equals(other)`      | exact equality check between two Series         |

## 2.4 Boolean subsetting

A comparison on a Series gives back a Series of `True`/`False` — pass that
boolean Series back into `[]` to filter:

```python
ages = pd.Series([37, 61, 90, 66, 56, 45, 41, 77])

ages > ages.mean()        #  Series of True/False
ages[ages > ages.mean()]  #  only the values above the mean

# you can build the boolean mask manually too
mask = [True, True, False, False, True, True, False, False]
ages[mask]
```

This same trick works on a whole DataFrame — the boolean Series filters
**rows**:

```python
scientists[scientists['Age'] > scientists['Age'].mean()]

# combine conditions with & / | (NOT the plain `and`/`or` keywords)
scientists[(scientists['Age'] > 40) & (scientists['Occupation'] == 'Chemist')]

# readable alternative for complex conditions
scientists.query('Age > 40 and Occupation == "Chemist"')
```

> Use `&` / `|` / `~` (with parentheses around each condition), never the
> Python keywords `and` / `or` / `not` — those don't work element-wise on a
> Series and will raise a `ValueError`.

## 2.5 Vectorized operations & broadcasting

Pandas operations work on the **whole Series at once** — no manual loops.

```python
ages + ages       # element-by-element: each value added to its pair
ages * 2          # scalar is "broadcast" across every element

# Series of DIFFERENT lengths -> aligned by index; anything that
# doesn't line up becomes NaN
pd.Series([1, 2, 3]) + pd.Series([10, 20])
#  0    11.0
#  1    22.0
#  2     NaN

# plain numpy arrays of different lengths instead raise an error --
# they don't have labels to align on
import numpy as np
ages.values + np.array([1, 100])   # ValueError: shapes don't match
```

Pandas always tries to line up by **index label** first, not position. If
you reorder/reindex a Series and then do arithmetic with the original, the
values still match up by label, not by position in the array.

## 2.6 Modifying Series & DataFrames

### Add or replace a column

```python
scientists['born_dt'] = pd.to_datetime(scientists['Born'], format='%Y-%m-%d')
scientists['died_dt'] = pd.to_datetime(scientists['Died'], format='%Y-%m-%d')

# datetime arithmetic -> a Timedelta
scientists['age_days'] = scientists['died_dt'] - scientists['born_dt']
scientists['age_years'] = scientists['age_days'].dt.days // 365
```

### Modify in place vs. assign to a new variable

Most pandas methods return a **new** object and leave the original alone:

```python
sorted_ages = ages.sort_values()   # `ages` itself is untouched
```

A few operations are "in place" by nature (they mutate the object directly
instead of returning a copy), so don't forget to capture the column you
actually want:

```python
# Modern, safe way to shuffle a column's values without mutating
# anything by surprise:
scientists['Age'] = scientists['Age'].sample(frac=1).reset_index(drop=True)
```

> Many older pandas tutorials use `inplace=True` (e.g.
> `df.fillna(0, inplace=True)`). It's now considered poor practice — it can
> silently fail to modify anything (it sometimes still makes a copy
> internally) and makes code harder to read. Prefer
> `df = df.fillna(0)`.

### Rename / drop / reorder columns

```python
df.rename(columns={'old_name': 'new_name'})
df.drop(columns=['col_to_remove'])
df[['col_b', 'col_a']]              # reorder by re-selecting
```

### Apply a function row-wise or column-wise

```python
df['col'].apply(lambda x: x * 2)             # element-wise on a Series
df.apply(lambda row: row['a'] + row['b'], axis=1)   # row-wise across a DataFrame
```

## 2.7 Exporting and importing data

### Pickle — fastest, Python-only, binary

```python
scientists.to_pickle('scientists.pickle')
scientists = pd.read_pickle('scientists.pickle')
```
Use this for intermediate results that only your own Python code needs to
read back. Anyone without Python can't open it.

### CSV — universal, human-readable, the default choice for sharing

```python
scientists.to_csv('scientists.csv')                  # writes the row index as a column too
scientists.to_csv('scientists.csv', index=False)      # don't write the row index
scientists.to_csv('scientists.tsv', sep='\t')         # tab-separated instead of comma

scientists = pd.read_csv('scientists.csv')
```

### Excel

```python
# a Series has no to_excel -- convert it to a 1-column DataFrame first
names_df = names.to_frame()
names_df.to_excel('names.xlsx')

scientists.to_excel('scientists.xlsx', sheet_name='scientists', index=False)
scientists = pd.read_excel('scientists.xlsx', sheet_name='scientists')
```

### Other formats worth knowing (modern additions, used constantly in practice)

| Method                  | Use for...                                      |
|--------------------------|--------------------------------------------------|
| `to_json` / `read_json`  | web APIs, config-like data                       |
| `to_sql` / `read_sql`    | reading/writing a SQL database table             |
| `to_parquet` / `read_parquet` | fast, compressed, columnar — great for big data |
| `to_dict()`              | convert to a plain Python dict                   |
| `to_numpy()`             | convert to a plain numpy array (drops labels)    |
| `to_clipboard()`         | copy straight to your OS clipboard                |
| `to_html()`              | render as an HTML `<table>`                      |
| `to_string()`            | full string representation (handy for printing)   |

## 2.8 Quick reference: dataframe vs series cheat table

| Concept                | Series                         | DataFrame                          |
|--------------------------|---------------------------------|--------------------------------------|
| Dimensions               | 1-D                              | 2-D                                  |
| Create from              | list, dict, scalar               | dict of lists, list of lists, list of dicts |
| Index                    | one (row labels)                 | two (row labels + column labels)     |
| `type(...)`              | `pandas.core.series.Series`      | `pandas.core.frame.DataFrame`        |
| Get a column             | n/a                              | `df['col']` or `df.col`              |
| Get a row                | `s.loc[label]`/`s.iloc[pos]` (gives a scalar) | `df.loc[label]`/`df.iloc[pos]` (gives a Series) |
