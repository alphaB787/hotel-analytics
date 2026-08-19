import matplotlib.pyplot as plt
import pandas as pd


def print_value_counts(df, columns, normalize=False, dropna=False):
    """Print value_counts() for one or more columns in sequence.

    Iterates over `columns` and prints the value distribution for each,
    with a header separating them. Intended as a quick, scannable first
    look at several categorical columns at once — not for programmatic use.

    Args:
        df (pd.DataFrame): Source dataframe.
        columns (list[str]): Column names to summarize. Each must exist in `df`.
        normalize (bool): If True, show relative frequencies (proportions)
            instead of raw counts. Defaults to False.
        dropna (bool): If True, exclude NaN values from the counts.
            Defaults to False (NaNs are counted as their own category).

    Returns:
        None. Output is printed directly to stdout.

    Example:
        >>> print_value_counts(df, ['hotel', 'meal'], normalize=True)
        === hotel ===
        City Hotel      0.66
        Resort Hotel    0.34
        Name: hotel, dtype: float64
        ...
    """
    for col in columns:
        print(f"=== {col} ===")
        print(df[col].value_counts(normalize=normalize, dropna=dropna))
        print()


def plot_boxplot(df, numeric_col, by=None, ax=None, title=None):
    """Draw a boxplot of a numeric column, optionally grouped by category.

    Thin wrapper around `DataFrame.boxplot` that suppresses pandas' default
    auto-title (which duplicates the axis title when grouping) and applies
    consistent sizing and layout.

    Args:
        df (pd.DataFrame): Source dataframe.
        numeric_col (str): Name of the numeric column to plot.
        by (str, optional): Name of a categorical column to group the
            boxplot by (one box per category). If None, a single box is
            drawn for the whole column. Defaults to None.
        ax (matplotlib.axes.Axes, optional): Axes to draw on. If None, a
            new figure and axes are created with figsize=(6, 4).
            Defaults to None.
        title (str, optional): Plot title. If None, defaults to
            `numeric_col` (or "`numeric_col` by `by`" when grouping).
            Defaults to None.

    Returns:
        matplotlib.axes.Axes: The axes the boxplot was drawn on.

    Example:
        >>> plot_boxplot(df, 'adr', by='is_canceled')
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 4))
    if by:
        df.boxplot(column=numeric_col, by=by, ax=ax)
        plt.suptitle("")  # pandas adds an ugly auto-title, drop it
    else:
        df.boxplot(column=numeric_col, ax=ax)
    ax.set_title(title or (f"{numeric_col} by {by}" if by else numeric_col))
    plt.tight_layout()
    return ax


def plot_correlation_heatmap(df, columns, title="Correlation matrix", ax=None):
    """Draw an annotated correlation heatmap for a set of numeric columns.

    Computes the pairwise Pearson correlation matrix for `columns` and
    renders it as a heatmap (coolwarm colormap, fixed [-1, 1] scale) with
    each cell's coefficient printed at two decimal places.

    Args:
        df (pd.DataFrame): Source dataframe.
        columns (list[str]): Names of numeric columns to correlate.
            Non-numeric columns will raise an error from `.corr()`.
        title (str): Plot title. Defaults to "Correlation matrix".
        ax (matplotlib.axes.Axes, optional): Axes to draw on. If None, a
            new figure and axes are created, sized to scale with the
            number of columns. Defaults to None.

    Returns:
        pd.DataFrame: The underlying correlation matrix (not the axes) —
        useful for further inspection beyond the plot.

    Example:
        >>> corr = plot_correlation_heatmap(df, ['lead_time', 'adr', 'is_canceled'])
    """
    corr = df[columns].corr()
    if ax is None:
        size = max(6, len(columns) * 0.6)
        fig, ax = plt.subplots(figsize=(size, size * 0.85))
    im = ax.imshow(corr, vmin=-1, vmax=1, cmap="coolwarm")
    ax.set_xticks(range(len(columns)))
    ax.set_xticklabels(columns, rotation=45, ha="right")
    ax.set_yticks(range(len(columns)))
    ax.set_yticklabels(columns)
    for i in range(len(columns)):
        for j in range(len(columns)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
    ax.figure.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title(title)
    plt.tight_layout()
    return corr


def rate_by_category(df, cat_col, target_col="is_canceled", min_n=100, sort_by_rate=True):
    """Compute the rate of a binary outcome within each category of a column.

    Groups `df` by `cat_col` and, for each group, computes the count and
    the mean of `target_col` (interpreted as a 0/1 indicator) as a
    percentage. Categories with fewer than `min_n` rows are dropped to
    avoid reporting noisy rates from small groups. This is the shared
    aggregation logic behind `plot_rate_by_category`.

    Args:
        df (pd.DataFrame): Source dataframe.
        cat_col (str): Name of the categorical column to group by.
        target_col (str): Name of the binary (0/1) outcome column whose
            rate is computed. Defaults to "is_canceled".
        min_n (int): Minimum number of rows a category must have to be
            included in the output. Defaults to 100.
        sort_by_rate (bool): If True, sort results descending by rate.
            If False, keep `cat_col`'s natural/categorical order — use
            this for ordered buckets (e.g. lead-time ranges) where
            sorting by rate would obscure a trend such as monotonicity.
            Defaults to True.

    Returns:
        pd.DataFrame: Indexed by `cat_col`, with columns:
            - n (int): Row count for the category.
            - positives (int/float): Sum of `target_col` in the category.
            - rate_pct (float): 100 * positives / n, rounded to 1 decimal.

    Example:
        >>> rate_by_category(df, 'market_segment', target_col='cancelled', min_n=100)
    """
    g = df.groupby(cat_col, observed=True).agg(n=(target_col, "size"), positives=(target_col, "sum"))
    g["rate_pct"] = (100 * g["positives"] / g["n"]).round(1)
    g = g[g["n"] >= min_n]
    if sort_by_rate:
        g = g.sort_values("rate_pct", ascending=False)
    return g


def plot_rate_by_category(df, cat_col, target_col="is_canceled", min_n=100,
                           ax=None, title=None, color="#2E5EAA", sort_by_rate=True):
    """Bar chart of the outcome rate within each category of a column.

    Calls `rate_by_category` to compute per-category rates, then renders
    the result as a bar chart. Returns both the axes and the underlying
    summary table so callers can inspect the exact numbers alongside the
    plot.

    Args:
        df (pd.DataFrame): Source dataframe.
        cat_col (str): Name of the categorical column to group by.
        target_col (str): Name of the binary (0/1) outcome column whose
            rate is plotted. Defaults to "is_canceled".
        min_n (int): Minimum number of rows a category must have to be
            included. Categories below this threshold are dropped.
            Defaults to 100.
        ax (matplotlib.axes.Axes, optional): Axes to draw on. If None, a
            new figure and axes are created with figsize=(7, 4).
            Defaults to None.
        title (str, optional): Plot title. If None, defaults to
            "`target_col` rate by `cat_col`". Defaults to None.
        color (str): Bar color (any matplotlib-recognized color spec).
            Defaults to "#2E5EAA".
        sort_by_rate (bool): If True, sort bars descending by rate.
            If False, keep `cat_col`'s natural order — use this for
            ordered buckets (e.g. lead-time ranges) so a trend isn't
            hidden by sorting bars by height. Defaults to True.

    Returns:
        tuple[matplotlib.axes.Axes, pd.DataFrame]: The axes the bar chart
        was drawn on, and the summary table from `rate_by_category`
        (columns: n, positives, rate_pct).

    Example:
        >>> ax, table = plot_rate_by_category(df, 'lead_time_bucket',
        ...                                    target_col='cancelled', min_n=1,
        ...                                    sort_by_rate=False)
    """
    g = rate_by_category(df, cat_col, target_col, min_n, sort_by_rate=sort_by_rate)
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4))
    g["rate_pct"].plot(kind="bar", ax=ax, color=color)
    ax.set_ylabel(f"{target_col} rate (%)")
    ax.set_xlabel(cat_col)
    ax.set_title(title or f"{target_col} rate by {cat_col}")
    plt.xticks(rotation=40, ha="right")
    plt.tight_layout()
    return ax, g
