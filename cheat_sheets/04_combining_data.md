# 4. Combining Data: concat & merge

> Real datasets are rarely handed to you as one tidy file. They're split
> across tables (to avoid storing redundant info — "each type of
> observational unit forms a table") or across files (timeseries chunked by
> date, files too big to be one). This sheet covers the two tools for
> putting the pieces back together: `pd.concat` (stacking) and `pd.merge`
> (database-style joins).

```python
import pandas as pd
```

## 4.1 Setup data used throughout this sheet

```python
df1 = pd.DataFrame({'A': ['a0', 'a1', 'a2', 'a3'],
                     'B': ['b0', 'b1', 'b2', 'b3'],
                     'C': ['c0', 'c1', 'c2', 'c3'],
                     'D': ['d0', 'd1', 'd2', 'd3']})

df2 = pd.DataFrame({'A': ['a4', 'a5', 'a6', 'a7'],
                     'B': ['b4', 'b5', 'b6', 'b7'],
                     'C': ['c4', 'c5', 'c6', 'c7'],
                     'D': ['d4', 'd5', 'd6', 'd7']})

df3 = pd.DataFrame({'A': ['a8', 'a9', 'a10', 'a11'],
                     'B': ['b8', 'b9', 'b10', 'b11'],
                     'C': ['c8', 'c9', 'c10', 'c11']})
```

## 4.2 Concatenation = stacking dataframes

`pd.concat` takes a **list** of dataframes and glues them together. Think of
it as "blind stacking" — it does not try to match anything up beyond the
labels that already exist.

### 4.2.1 Adding rows (the default, `axis=0`)

```python
row_concat = pd.concat([df1, df2, df3])
#       A    B    C    D
#  0   a0   b0   c0   d0
#  1   a1   b1   c1   d1
#  2   a2   b2   c2   d2
#  3   a3   b3   c3   d3
#  0   a4   b4   c4   d4
#  ...
```

Notice the **row index is just stacked too** — labels `0,1,2,3` repeat for
every dataframe that gets concatenated. Subsetting still works (e.g.
`row_concat.iloc[3]` gives one specific row by position), but `.loc[0]` will
now return *multiple* rows (one from each original dataframe) since label
`0` appears three times.

### 4.2.2 Appending a single row

Trying to concat a plain `Series` onto a DataFrame does **not** do what you
want:

```python
new_row_series = pd.Series(['n1', 'n2', 'n3', 'n4'])
pd.concat([df1, new_row_series])
#        A     B     C     D    0
#  0    a0    b0    c0    d0  NaN
#  1    a1    b1    c1    d1  NaN
#  ...
#  0   NaN   NaN   NaN   NaN   n1
#  1   NaN   NaN   NaN   NaN   n2
```

A bare `Series` has no column labels of its own (just `0, 1, 2, 3` as its
*index*), so pandas can't line it up with `df1`'s columns — it gets added
as a brand new column called `0`, full of `NaN` for every existing row.

**Fix**: wrap the new row in a single-row DataFrame with matching column
names first.

```python
new_row_df = pd.DataFrame([['n1', 'n2', 'n3', 'n4']], columns=['A', 'B', 'C', 'D'])
pd.concat([df1, new_row_df])
#       A    B    C    D
#  0   a0   b0   c0   d0
#  1   a1   b1   c1   d1
#  2   a2   b2   c2   d2
#  3   a3   b3   c3   d3
#  0   n1   n2   n3   n4   <- matched on column names correctly
```

> The book also shows `df1.append(df2)` / `df1.append(data_dict, ignore_index=True)`.
> **`DataFrame.append` has been removed from modern pandas** — it's a
> deprecated alias for exactly what `pd.concat` already does, just with a
> worse API (no way to concat more than two things at once). Always use
> `pd.concat([...])` instead, even for appending just one row or dict:
>
> ```python
> pd.concat([df1, pd.DataFrame([data_dict])], ignore_index=True)
> ```

### 4.2.3 Resetting the index: `ignore_index=True`

If you don't care about preserving the original row labels (you just want
`0, 1, 2, ...` all the way down), pass `ignore_index=True`:

```python
pd.concat([df1, df2, df3], ignore_index=True)
#        A     B     C     D
#   0   a0    b0    c0    d0
#   1   a1    b1    c1    d1
#   ...
#   10  a10   b10   c10   d10
#   11  a11   b11   c11   d11    <- continuous 0..11, no repeats
```

### 4.2.4 Adding columns (`axis=1`)

Same function, just tell it to glue side-by-side instead of top-to-bottom:

```python
col_concat = pd.concat([df1, df2, df3], axis=1)   # rows matched by index label
```

If multiple input frames share a column name (here, all three have `A`,
`B`, `C`, `D`), selecting that name afterwards returns **all** of the
matching columns:

```python
col_concat['A']     # DataFrame with 3 columns, all named 'A' -- one per input frame
```

Adding one new column directly doesn't need `concat` at all — just assign:

```python
col_concat['new_col'] = ['n1', 'n2', 'n3', 'n4']
```

`ignore_index=True` works for columns too — it renumbers the *column*
labels `0, 1, 2, ...` instead of preserving (possibly duplicated) names.

## 4.3 Concatenation with mismatched labels

Real files don't always share every column or every row index. `concat`
handles this by **aligning on labels** and filling anything that doesn't
match with `NaN`.

### 4.3.1 Rows with different columns

```python
df1.columns = ['A', 'B', 'C', 'D']
df2.columns = ['E', 'F', 'G', 'H']
df3.columns = ['A', 'C', 'F', 'H']

pd.concat([df1, df2, df3])
#        A     B    C     D     E     F     G     H
#   0   a0    b0   c0    d0   NaN   NaN   NaN   NaN
#   ...
#   0  NaN   NaN  NaN   NaN    a4    b4    c4    d4
#   ...
#   0   a8   NaN   b8   NaN   NaN    c8   NaN    d8
#   ...
```

Every column that appears *anywhere* in the inputs shows up in the result
(this is the default `join='outer'`); anywhere a given frame didn't have
that column, you get `NaN`.

Use `join='inner'` to keep **only** the columns common to every input
frame instead of padding with `NaN`:

```python
pd.concat([df1, df2, df3], join='inner')   # no columns in common across all 3 -> empty DataFrame
pd.concat([df1, df3], join='inner')         # df1 & df3 share 'A' and 'C' -> only those 2 columns kept
```

### 4.3.2 Columns with different row indices

Same idea, just transposed — concatenating along `axis=1` aligns by **row
index** instead of column name:

```python
df1.index = [0, 1, 2, 3]
df2.index = [4, 5, 6, 7]
df3.index = [0, 2, 5, 7]

pd.concat([df1, df2, df3], axis=1)    # outer join on the row index -> NaN where a label is missing
pd.concat([df1, df3], axis=1, join='inner')   # keep only rows 0 and 2 (the labels both frames have)
```

### 4.3.3 `concat` cheat table

| Call                                              | Behavior                                  |
|----------------------------------------------------|---------------------------------------------|
| `pd.concat([a, b])`                                | stack rows, default `axis=0`, `join='outer'` |
| `pd.concat([a, b], axis=1)`                        | stack side-by-side as new columns          |
| `pd.concat([a, b], ignore_index=True)`              | stack rows, discard old index, renumber 0..n |
| `pd.concat([a, b], join='inner')`                   | keep only labels common to **all** inputs  |
| `pd.concat([a, b], join='outer')` *(default)*       | keep every label, fill gaps with `NaN`     |

## 4.4 Merging: database-style joins

Concatenation only lines things up by **position/label that already
matches**. A **merge** instead matches rows based on the *values* in one or
more shared columns — exactly like a SQL `JOIN`. Use this whenever you have
two or more tables that describe **different aspects of the same entity**
(e.g. a `site` table with lat/long, and a `visited` table recording who
went to each site and when).

```python
person  = pd.DataFrame({'ident': ['dyer', 'pb', 'lake', 'roe', 'danforth'],
                         'personal': ['William', 'Frank', 'Anderson', 'Valentina', 'Frank'],
                         'family': ['Dyer', 'Pabodie', 'Lake', 'Roerich', 'Danforth']})

site = pd.DataFrame({'name': ['DR-1', 'DR-3', 'MSK-4'],
                      'lat':  [-49.85, -47.15, -48.87],
                      'long': [-128.57, -126.72, -123.40]})

visited = pd.DataFrame({'ident': [619, 622, 734, 735, 751, 752, 837, 844],
                         'site':  ['DR-1', 'DR-1', 'DR-3', 'DR-3', 'DR-3', 'DR-3', 'MSK-4', 'DR-1'],
                         'dated': ['1927-02-08', '1927-02-10', '1939-01-07', '1930-01-12',
                                   '1930-02-26', None, '1932-01-14', '1932-03-22']})

survey = pd.DataFrame({'taken':   [619, 619, 622, 622, 734, 734, 734, 735],
                        'person':  ['dyer', 'dyer', 'dyer', 'dyer', 'pb', 'lake', 'pb', 'pb'],
                        'quant':   ['rad', 'sal', 'rad', 'sal', 'rad', 'sal', 'temp', 'rad'],
                        'reading': [9.82, 0.13, 7.80, 0.09, 8.41, 0.05, -21.50, 7.22]})
```

`merge` is a **DataFrame method**: `left.merge(right, ...)`. The dataframe
you call it on is the "left" table; the argument is the "right" table.

```python
left.merge(right, on='shared_col')                       # same column name on both sides
left.merge(right, left_on='name', right_on='site')        # different column names
```

### 4.4.1 `how=`: which rows survive (maps directly to SQL joins)

| pandas `how=` | SQL equivalent | Keeps...                                  |
|-----------------|------------------|----------------------------------------------|
| `'left'`        | LEFT OUTER       | every row from the left table               |
| `'right'`       | RIGHT OUTER      | every row from the right table              |
| `'outer'`       | FULL OUTER       | every row from both                         |
| `'inner'` *(default)* | INNER       | only keys present in **both** tables        |

### 4.4.2 One-to-one

The simplest case: both sides have at most one matching row per key.

```python
visited_subset = visited.loc[[0, 2, 6], :]   # one row per site, no repeats

o2o_merge = site.merge(visited_subset, left_on='name', right_on='site')
#     name    lat    long  ident   site       dated
# 0   DR-1  -49.85 -128.57   619   DR-1  1927-02-08
# 1   DR-3  -47.15 -126.72   734   DR-3  1939-01-07
# 2  MSK-4  -48.87 -123.40   837  MSK-4  1932-01-14
```

> The book uses `visited.ix[[0, 2, 6], ]` to build this subset. **`.ix` was
> removed from pandas years ago** — use `.loc` (label-based) as shown
> above, since the default index here is already the row label you want.

### 4.4.3 Many-to-one

Merge against the *full* `visited` table (which has repeated `site`
values) instead of the subset, and the single-observation side (`site`)
gets duplicated to match every repeat on the other side:

```python
m2o_merge = site.merge(visited, left_on='name', right_on='site')
#     name    lat    long  ident   site       dated
# 0   DR-1  -49.85 -128.57   619   DR-1  1927-02-08
# 1   DR-1  -49.85 -128.57   622   DR-1  1927-02-10
# 2   DR-1  -49.85 -128.57   844   DR-1  1932-03-22
# 3   DR-3  -47.15 -126.72   734   DR-3  1939-01-07
# ...
```

`DR-1`'s lat/long got copied onto every `visited` row that points at it.
This is completely normal — and exactly why splitting data into separate
tables in the first place avoids redundantly storing `lat`/`long` once
*per visit* instead of once *per site*.

### 4.4.4 Many-to-many

Merge on **multiple columns at once** by passing a list to `on=` /
`left_on=`/`right_on=`:

```python
ps = person.merge(survey, left_on='ident', right_on='person')
vs = visited.merge(survey, left_on='ident', right_on='taken')

ps_vs = ps.merge(
    vs,
    left_on=['ident', 'taken', 'quant', 'reading'],
    right_on=['person', 'ident', 'quant', 'reading'],
)
```

### 4.4.5 Colliding column names: `_x` / `_y` suffixes

Both `ps` and `vs` have columns like `ident`, `taken`, `person` that aren't
part of the merge key but exist on both sides. Pandas automatically
disambiguates them:

```python
ps_vs.iloc[0]
# ident_x          dyer      <- from the LEFT frame (ps)
# personal      William
# family           Dyer
# taken_x           619
# person_x         dyer
# quant             rad
# reading          9.82
# ident_y           619      <- from the RIGHT frame (vs)
# site             DR-1
# dated      1927-02-08
# taken_y           619
# person_y         dyer
```

`_x` = came from the left frame, `_y` = came from the right frame. Pick
your own labels instead with `suffixes=('_left', '_right')` if `_x`/`_y`
isn't descriptive enough:

```python
ps.merge(vs, left_on='ident', right_on='taken', suffixes=('_person', '_visit'))
```

## 4.5 `concat` vs. `merge`: which one do I want?

| Question to ask yourself                                          | Use      |
|---------------------------------------------------------------------|----------|
| "I have more rows/columns of the **same shape of data** to stick on" | `concat` |
| "I have **two different tables** that share a key and I need to combine their info" | `merge`  |
| "I just want to glue dataframes together by their existing index, nothing fancier" | `concat(axis=1)` or `.join()` (a thin wrapper around `merge` for index-based joins) |

## 4.6 Key takeaways

- `pd.concat([...])` always takes a **list**, can stack rows *or* columns,
  and aligns purely by existing label (row index for `axis=1`, column name
  for `axis=0`) — anything unmatched becomes `NaN` unless you use
  `join='inner'`.
- `DataFrame.append()` is gone from modern pandas — `pd.concat` replaces it
  completely, and handles more than two inputs at once.
- `merge` matches on **values**, not position — exactly like a SQL join.
  Specify the join column(s) with `on=`/`left_on=`/`right_on=`, and the
  rows to keep with `how=`.
- Splitting data into many small linked tables avoids storing redundant
  information; merging is the (necessary, expected) cost of putting it
  back together for analysis. Watch for the row-count explosion in
  many-to-one/many-to-many merges — it's not a bug, it's the data
  legitimately repeating to match every key on the other side.
