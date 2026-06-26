# 6. Tidy Data by Reshaping

> Based on Hadley Wickham's *Tidy Data* paper. Tidy data is a goal to aim
> for when cleaning, not a strict requirement — but data in this shape is
> dramatically easier to analyze, visualize, and collect correctly.

```python
import pandas as pd
import glob
```

## 6.1 What "tidy" means

Hadley Wickham's three rules:

1. Each **row** is an observation.
2. Each **column** is a variable.
3. Each type of **observational unit forms a table** (don't mix two kinds
   of "thing" — e.g. song metadata and weekly chart rankings — in one
   table).

Data that breaks these rules isn't *wrong* — "wide" tables are often the
most convenient shape for data entry and for presenting in a report. It's
just not the shape most pandas functions (especially seaborn faceting,
`groupby`, and plotting) expect. Reshaping is how you convert between the
two.

| Problem                                       | Fix                          | Covered in |
|--------------------------------------------------|---------------------------------|--------------|
| Column headers are actually *values* of a variable | melt (unpivot/gather)        | §6.2         |
| One column holds 2+ variables crammed together     | split the column, then assign  | §6.3         |
| Variables are spread across both rows AND columns  | melt, then `pivot_table`       | §6.4         |
| One table mixes 2 different observational units    | normalize into 2 linked tables | §6.5         |
| The same observational unit is spread across files  | load + `pd.concat`            | §6.6         |

## 6.2 Columns contain values, not variables: `melt`

### 6.2.1 Keep one column fixed

```python
pew = pd.DataFrame({
    'religion': ['Agnostic', 'Atheist', 'Buddhist', 'Catholic'],
    '<$10k':    [27, 12, 27, 418],
    '$10-20k':  [34, 27, 21, 617],
    '$20-30k':  [60, 37, 30, 732],
})
```

Every income bracket is its own column — convenient to read as a table,
but `<$10k`/`$10-20k`/`$20-30k` are really three *values* of one variable
("income bracket"), not three different variables. This "one variable
spread across many columns" shape is called **wide** format; we want
**long** (tidy) format instead.

```python
pew_long = pd.melt(pew, id_vars='religion')
#    religion variable  value
# 0  Agnostic    <$10k     27
# 1   Atheist    <$10k     12
# 2  Buddhist    <$10k     27
# 3  Catholic    <$10k    418
# ...
```

`melt` parameters:

| Parameter      | Meaning                                                              |
|------------------|---------------------------------------------------------------------------|
| `id_vars`       | column(s) to leave alone — these identify the observation                |
| `value_vars`    | column(s) to melt down; defaults to "everything not in `id_vars`"         |
| `var_name`      | name for the new column holding the *old column names* (default: `'variable'`) |
| `value_name`    | name for the new column holding the *values* (default: `'value'`)        |

```python
pew_long = pd.melt(pew, id_vars='religion', var_name='income', value_name='count')
#    religion income  count
# 0  Agnostic  <$10k     27
# 1   Atheist  <$10k     12
```

### 6.2.2 Keep multiple columns fixed

Real datasets often have several identifying columns, not just one — e.g.
chart data where every week is its own column:

```python
billboard = pd.DataFrame({
    'year':   [2000, 2000],
    'artist': ['2Ge+her', '3 Doors Down'],
    'track':  ['The Hardest Part Of...', 'Kryptonite'],
    'time':   ['3:15', '3:53'],
    'date.entered': ['2000-09-02', '2000-04-08'],
    'wk1': [91, 81],
    'wk2': [87, 70],
})

billboard_long = pd.melt(
    billboard,
    id_vars=['year', 'artist', 'track', 'time', 'date.entered'],
    var_name='week',
    value_name='rating',
)
#    year         artist        track  time date.entered week  rating
# 0  2000        2Ge+her  The Hardest...  3:15   2000-09-02  wk1      91
# 1  2000  3 Doors Down       Kryptonite  3:53   2000-04-08  wk1      81
# 2  2000        2Ge+her  The Hardest...  3:15   2000-09-02  wk2      87
# ...
```

Pass a **list** to `id_vars` — every column not listed gets melted.
This shape is exactly what you need for, say, a faceted seaborn plot of
rating-over-time per song (the facet/x-axis variable must be a column).

## 6.3 Columns contain multiple variables: split them apart

Sometimes a single column name is itself encoding two variables, e.g.
`Cases_Guinea` = status (`Cases`) + country (`Guinea`):

```python
ebola = pd.DataFrame({
    'Date': ['1/5/2015', '1/4/2015'],
    'Day':  [289, 288],
    'Cases_Guinea':  [2776.0, 2775.0],
    'Cases_Liberia': [None, None],
    'Deaths_Guinea': [1786.0, 1781.0],
})

ebola_long = pd.melt(ebola, id_vars=['Date', 'Day'])
#        Date  Day      variable   value
# 0  1/5/2015  289  Cases_Guinea  2776.0
# 1  1/4/2015  288  Cases_Guinea  2775.0
# 2  1/5/2015  289 Cases_Liberia     NaN
# ...
```

`variable` now holds compound strings like `Cases_Guinea`. We need to
split each one into a `status` column and a `country` column.

### 6.3.1 Split, then assign each piece (most explicit)

```python
variable_split = ebola_long['variable'].str.split('_')   # Series of LISTS, e.g. ['Cases', 'Guinea']

ebola_long['status']  = variable_split.str.get(0)
ebola_long['country'] = variable_split.str.get(1)
```

`.str` unlocks Python string methods element-wise across a whole Series.
`.str.split('_')` returns a Series where every element is a Python
`list`; `.str.get(i)` pulls out one position from each of those lists.

### 6.3.2 Split straight into separate columns: `expand=True`

```python
variable_split = ebola_long['variable'].str.split('_', expand=True)
variable_split.columns = ['status', 'country']

ebola_parsed = pd.concat([ebola_long, variable_split], axis=1)
```

`expand=True` returns a full DataFrame (one column per split piece)
instead of a Series-of-lists — skip the `.str.get()` calls and just
`pd.concat` it onto the original (matched up by row index, see
`04_combining_data.md` §4.3.2).

### 6.3.3 Split and assign in one line: `zip(*...)`

```python
ebola_long['status'], ebola_long['country'] = zip(*ebola_long['variable'].str.split('_'))
```

`zip(*iterable_of_pairs)` "transposes" a list of `[status, country]`
pairs into one list of all statuses and one list of all countries —
Python's `*` unpacks the Series-of-lists into individual arguments for
`zip`. This is the terse one-liner version of §6.3.1/6.3.2; reach for the
explicit version above if this reads as too dense.

## 6.4 Variables in both rows AND columns

The weather dataset combines both problems at once: `d1`...`d31` are
values of a "day" variable (columns-that-should-be-rows, fix with `melt`),
while `tmax`/`tmin` are *separate variables* crammed as values inside one
`element` column (rows-that-should-be-columns, fix with `pivot_table`).

```python
weather = pd.DataFrame({
    'id': ['MX17004', 'MX17004', 'MX17004', 'MX17004'],
    'year': [2010, 2010, 2010, 2010],
    'month': [1, 1, 2, 2],
    'element': ['tmax', 'tmin', 'tmax', 'tmin'],
    'd1': [None, None, None, None],
    'd2': [None, None, 27.3, 14.4],
})
```

**Step 1 — melt the day columns down:**

```python
weather_melt = pd.melt(
    weather,
    id_vars=['id', 'year', 'month', 'element'],
    var_name='day',
    value_name='temp',
)
#         id  year  month element day  temp
# 0  MX17004  2010      1    tmax  d1   NaN
# 1  MX17004  2010      1    tmin  d1   NaN
# 2  MX17004  2010      2    tmax  d1   NaN
# ...
```

**Step 2 — pivot the `element` values back out into their own columns.**
This is the reverse of melt — also called "cast" or "spread" in other
tools. Unlike `melt` (a plain function), `pivot_table` is a **method**
called on the DataFrame:

```python
weather_tidy = weather_melt.pivot_table(
    index=['id', 'year', 'month', 'day'],
    columns='element',
    values='temp',
).reset_index()
#   id       year  month  day  tmax  tmin
# 0 MX17004  2010      1   d1   NaN   NaN
# 1 MX17004  2010      1  d10   NaN   NaN
```

`pivot_table` puts the result's row labels into a (possibly
multi-level) index — `.reset_index()` flattens that back into ordinary
columns, which is almost always what you want for further analysis.

> `pivot_table` defaults to averaging when multiple rows match the same
> `index`+`columns` combination (it has an `aggfunc=` parameter, default
> `'mean'`). If you know there's exactly one value per combination — as
> here — that default aggregation is harmless, but it's worth knowing
> it's happening.

## 6.5 One table, multiple observational units: normalize

A warning sign that a table secretly holds **two kinds of thing**: scan
down a column and see the same values repeating row after row. In the
billboard data, `year`/`artist`/`track`/`time` repeat identically across
every week's rating row for the same song — that's *song info* and
*weekly ranking* being forced into one table.

```python
billboard_long[billboard_long['track'] == 'Loser']
#   year        artist  track  time date.entered week  rating
# 3 2000  3 Doors Down  Loser  4:24   2000-10-21  wk1    76.0
# 320 2000 3 Doors Down Loser  4:24   2000-10-21  wk2    76.0
# ...   <- year/artist/track/time identical every time
```

Repeating the same values over and over (especially with manual data
entry) is exactly how you get inconsistent data. The fix mirrors
**reversing** a merge from Chapter 4: split into two tables linked by a
surrogate ID.

```python
# 1. pull out just the "song" columns, then de-duplicate
billboard_songs = billboard_long[['year', 'artist', 'track', 'time']].drop_duplicates()
billboard_songs.shape    # (317, 4) -- way fewer rows than the full long table

# 2. assign a surrogate key
billboard_songs['id'] = range(len(billboard_songs))

# 3. merge the new id back onto the full table, keyed by the song columns
billboard_ratings = billboard_long.merge(billboard_songs, on=['year', 'artist', 'track', 'time'])

# 4. keep only what belongs in the "ratings" table
billboard_ratings = billboard_ratings[['id', 'date.entered', 'week', 'rating']]
```

Now `billboard_songs` (one row per unique song) and `billboard_ratings`
(one row per song-per-week) are two clean, non-redundant tables linked by
`id` — exactly the kind of split-by-observational-unit structure that
Chapter 4's merges exist to put back together when you need both at once.

## 6.6 The same observational unit, split across multiple files

The opposite problem from §6.5: instead of one table holding two things,
many files each hold a slice of the *same* thing (common for large
datasets shared online, or data collected incrementally — e.g. one file
per day/month/year).

```python
csv_files = glob.glob('nyc-taxi/*.csv')
# ['nyc-taxi/fhv_tripdata_2015-03.csv', 'nyc-taxi/fhv_tripdata_2015-02.csv', ...]
```

`glob.glob(pattern)` returns every filename matching a shell-style
wildcard pattern — the standard way to grab "every file that matches this
naming convention" without hardcoding a list.

**Manually** (fine for a handful of files, tedious beyond that):

```python
taxi1 = pd.read_csv(csv_files[0])
taxi2 = pd.read_csv(csv_files[1])
# ...
taxi = pd.concat([taxi1, taxi2, ...])
```

**With a loop** (scales to any number of files):

```python
list_taxi_df = []
for csv_filename in csv_files:
    df = pd.read_csv(csv_filename)
    list_taxi_df.append(df)

taxi_loop_concat = pd.concat(list_taxi_df)
```

**With a list comprehension** (same result, more idiomatic Python):

```python
list_taxi_df_comp = [pd.read_csv(csv_filename) for csv_filename in csv_files]
taxi_loop_concat_comp = pd.concat(list_taxi_df_comp)
```

All three approaches produce identical results — verify with
`.equals()`, the exact-equality check from `02_series_and_dataframe.md`:

```python
taxi.equals(taxi_loop_concat)            # True
taxi_loop_concat_comp.equals(taxi_loop_concat)  # True
```

`pd.concat` always wants a **list** of dataframes — that's exactly what
both the loop and the list comprehension build before the final
`pd.concat(...)` call.

## 6.7 Key takeaways

- Tidy = one observation per row, one variable per column, one kind of
  thing per table. It's a destination, not a rule to follow at every
  intermediate step — wide formats are often better for display/entry.
- "Column headers are actually values" → `pd.melt` (wide → long).
- "Row values are actually column headers" → `.pivot_table()` +
  `.reset_index()` (long → wide) — the reverse of `melt`.
- "One column name encodes two variables" → `.str.split('_')`, then
  either `.str.get(i)`, `expand=True` + `concat`, or `zip(*...)` unpacking.
- "One table mixes two observational units" → subset the repeating
  columns, `.drop_duplicates()`, assign a surrogate `id`, merge the id
  back onto the rest, then re-subset into two clean tables.
- "One observational unit is spread across many files" → `glob.glob()` to
  find them, a loop or list comprehension to load each into a list of
  DataFrames, then a single `pd.concat()` to stack them all.
