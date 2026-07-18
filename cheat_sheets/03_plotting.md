# 3. Plotting with pandas, matplotlib & seaborn

> Visualizing data is part of the *analysis*, not just the final report —
> looking at a plot is often the fastest way to catch bad data (see
> Anscombe's quartet below).

## 3.0 The three layers

| Library      | Role                                                              |
|---------------|--------------------------------------------------------------------|
| **matplotlib**| The foundation. Total control, more code to write.                 |
| **seaborn**   | Built on matplotlib. Higher-level, statistical, prettier defaults.  |
| **pandas `.plot`** | Built on matplotlib too. Quickest one-liners straight from a DataFrame/Series. |

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
```

## 3.1 Why visualize: Anscombe's quartet

Four tiny datasets with **identical** mean, variance, correlation, and
regression line — but wildly different shapes once plotted. Summary
statistics alone can lie to you.

```python
anscombe = sns.load_dataset('anscombe')   # columns: dataset, x, y (datasets 'I'..'IV')
```

## 3.2 matplotlib fundamentals

### Figure vs. Axes (the most confusing terms in Python plotting)

- A **Figure** is the whole window/page.
- An **Axes** is one individual plot inside that figure (it has both an
  x-axis and a y-axis — confusingly, "axes" is the plot, "axis" is one of
  its rulers).

```python
fig = plt.figure()                  # blank canvas
ax = fig.add_subplot(1, 1, 1)       # 1 row, 1 column, 1st position -> one Axes
ax.plot(dataset_1['x'], dataset_1['y'])
ax.set_title('Dataset 1')
ax.set_xlabel('x')
ax.set_ylabel('y')
plt.show()
```

`add_subplot(nrows, ncols, position)` — position counts left-to-right, then
top-to-bottom, starting at 1.

### A 2x2 grid of subplots

```python
fig = plt.figure()
ax1 = fig.add_subplot(2, 2, 1)
ax2 = fig.add_subplot(2, 2, 2)
ax3 = fig.add_subplot(2, 2, 3)
ax4 = fig.add_subplot(2, 2, 4)

for ax, label in zip([ax1, ax2, ax3, ax4], ['I', 'II', 'III', 'IV']):
    data = anscombe[anscombe['dataset'] == label]
    ax.plot(data['x'], data['y'], 'o')      # 'o' = draw points, not a line
    ax.set_title(f'dataset {label}')

fig.suptitle('Anscombe Data')
fig.tight_layout()
plt.show()
```

The simpler, modern way to get a grid of Axes:

```python
fig, axes = plt.subplots(2, 2, figsize=(8, 8))
axes[0, 0].plot(...)   # axes is a 2-D numpy array of Axes objects
```

### Basic plot types (matplotlib)

```python
fig, ax = plt.subplots()
ax.hist(tips['total_bill'], bins=10)                 # histogram
ax.set_title('Histogram of Total Bill')

fig, ax = plt.subplots()
ax.scatter(tips['total_bill'], tips['tip'])           # scatter plot
ax.set_title('Scatterplot of Total Bill vs Tip')

fig, ax = plt.subplots()
ax.boxplot(
    [tips[tips['sex'] == 'Female']['tip'],
     tips[tips['sex'] == 'Male']['tip']],
    labels=['Female', 'Male'],
)
ax.set_title('Boxplot of Tips by Sex')
```

### Adding more variables with color, size, transparency

```python
tips['sex_color'] = tips['sex'].map({'Female': 0, 'Male': 1})

fig, ax = plt.subplots()
ax.scatter(
    x=tips['total_bill'],
    y=tips['tip'],
    s=tips['size'] * 10,     # bubble SIZE encodes a 3rd variable
    c=tips['sex_color'],     # bubble COLOR encodes a 4th variable
    alpha=0.5,                # transparency helps with overlapping points
)
```

**Rules of thumb for multivariate plots:** color is much easier for humans
to compare than size; if you must use size, make sure you're scaling *area*
(not radius) correctly, or differences will look exaggerated/misleading.

## 3.3 seaborn: statistical graphics with one line each

```python
tips = sns.load_dataset('tips')
```

### Univariate (one variable)

```python
sns.histplot(tips['total_bill'])                 # histogram
sns.histplot(tips['total_bill'], kde=True)        # histogram + density curve
sns.kdeplot(tips['total_bill'])                   # density curve only
sns.rugplot(tips['total_bill'])                   # tick mark per observation (combine with the above)
sns.countplot(x='day', data=tips)                 # bar chart of category frequencies
```

> Older seaborn versions used a single all-purpose `sns.distplot(...)`. It
> was removed in modern seaborn — use `histplot`/`kdeplot`/`rugplot`
> (combine them on the same Axes if you want the old all-in-one look).

### Bivariate (two variables)

```python
sns.scatterplot(x='total_bill', y='tip', data=tips)          # plain scatter
sns.regplot(x='total_bill', y='tip', data=tips)               # scatter + fitted regression line
sns.regplot(x='total_bill', y='tip', data=tips, fit_reg=False)  # scatter only, via regplot

sns.jointplot(x='total_bill', y='tip', data=tips)              # scatter + a histogram on each axis
sns.jointplot(x='total_bill', y='tip', data=tips, kind='hex')   # hexbin instead of scatter (better for dense data)
sns.jointplot(x='total_bill', y='tip', data=tips, kind='kde')   # 2D density instead of scatter

sns.barplot(x='time', y='total_bill', data=tips)               # bar = mean by default per category
sns.barplot(x='time', y='total_bill', data=tips, estimator='std')  # change the summary stat

sns.boxplot(x='time', y='total_bill', data=tips)               # min/quartiles/median/max + outliers
sns.violinplot(x='time', y='total_bill', data=tips)             # like a boxplot but shows the full density shape
```

`regplot` draws onto an existing Axes (axes-level); `lmplot` is the
figure-level version (it creates its own Figure and supports faceting — see
below).

### Pairwise relationships (lots of numeric columns at once)

```python
sns.pairplot(tips)                  # scatter for every pair, histogram on the diagonal
sns.pairplot(tips, hue='sex')        # color by a categorical column too

# manual control over the upper/lower/diagonal panels
grid = sns.PairGrid(tips)
grid.map_upper(sns.scatterplot)
grid.map_lower(sns.kdeplot)
grid.map_diag(sns.histplot)
```

### Multivariate: color, shape, and facets

```python
# hue = color by a category
sns.violinplot(x='time', y='total_bill', hue='sex', data=tips, split=True)
sns.lmplot(x='total_bill', y='tip', data=tips, hue='sex', fit_reg=False)

# pass extra styling straight through to the underlying matplotlib call
sns.lmplot(
    x='total_bill', y='tip', data=tips,
    fit_reg=False, hue='sex', markers=['o', 'x'],
    scatter_kws={'s': tips['size'] * 10},
)
```

**Facets** = automatically repeat a plot once per category, instead of you
manually subsetting and building a grid (your data must be "tidy"/"long" —
see `06_tidy_data_reshaping.md`):

```python
# figure-level facets via col=/row=/col_wrap=
sns.lmplot(x='x', y='y', data=anscombe, fit_reg=False, col='dataset', col_wrap=2)
sns.lmplot(x='total_bill', y='tip', data=tips, fit_reg=False, hue='sex', col='day')

# manual FacetGrid -- needed when the plot function doesn't support col=/row= itself
facet = sns.FacetGrid(tips, col='time')
facet.map(sns.histplot, 'total_bill')

facet = sns.FacetGrid(tips, col='day', hue='sex')
facet.map(plt.scatter, 'total_bill', 'tip')
facet.add_legend()

# facet on BOTH rows and columns at once
facet = sns.FacetGrid(tips, col='time', row='smoker', hue='sex')
facet.map(plt.scatter, 'total_bill', 'tip')

# combine faceting + an arbitrary plot kind without overlapping hues
sns.catplot(x='day', y='total_bill', hue='sex', data=tips, row='smoker', col='time', kind='violin')
```

### Styles & themes

```python
sns.set_style('whitegrid')   # one of: darkgrid, whitegrid, dark, white, ticks
sns.violinplot(x='time', y='total_bill', hue='sex', data=tips, split=True)

# preview every style at once
styles = ['darkgrid', 'whitegrid', 'dark', 'white', 'ticks']
fig, axes = plt.subplots(2, 3, figsize=(12, 6))
for ax, style in zip(axes.flat, styles):
    with sns.axes_style(style):
        sns.violinplot(x='time', y='total_bill', data=tips, ax=ax)
        ax.set_title(style)
fig.tight_layout()
```

## 3.4 pandas' own `.plot` methods

Every Series/DataFrame has a `.plot` accessor — fastest path from data to a
picture with zero extra imports beyond matplotlib for `plt.show()`.

```python
tips['total_bill'].plot.hist()                          # histogram, one Series
tips[['total_bill', 'tip']].plot.hist(alpha=0.5, bins=20)  # overlay two columns

tips['tip'].plot.kde()                                    # density plot

tips.plot.scatter(x='total_bill', y='tip')                 # scatter
tips.plot.hexbin(x='total_bill', y='tip', gridsize=10)      # hexbin

tips.plot.box()                                            # box plot of all numeric columns

df.groupby('year')['lifeExp'].mean().plot()                 # quick line plot (Ch. 1 example)
df.groupby('continent')['country'].nunique().plot.bar()      # quick bar plot
```

| `.plot.___`  | Plot type            |
|---------------|------------------------|
| `line` *(default)* | line chart        |
| `bar` / `barh`     | vertical / horizontal bar chart |
| `hist`             | histogram          |
| `box`              | box plot           |
| `kde` / `density`  | kernel density plot |
| `area`             | stacked area chart |
| `scatter`          | scatter plot        |
| `hexbin`           | hexbin plot         |
| `pie`              | pie chart            |

## 3.5 Picking the right tool

- Quick look while exploring data you already have in a DataFrame →
  **pandas `.plot`**.
- A polished statistical chart (with proper legends, regression lines, facets) →
  **seaborn**.
- You need pixel-level control over every element (custom annotations,
  combining wildly different plot types, publication figures) →
  **matplotlib** directly.
