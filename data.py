import pandas as pd

def filter_dates(dates, start=None, end=None):
    if start is not None:
        dates = dates[dates >= start]

    if end is not None:
        dates = dates[dates <= end]

    return dates


def load_assets(column='Adj Close', start=None, end=None):
    """
    Load price data for alternative assets.

    Args:
        column: Which column in the price data to use.
        start: Filter out only data at this time or later.
        end: Filter out only data at this time or earlier.
    """

    # S&P500 index, monthly data
    equity = pd.read_csv(
        'data/gspc-monthly.csv',
        index_col='Date',
        parse_dates=True)[column]

    # 10-year US treasury bonds, monthly data
    bonds = pd.read_csv(
        'data/tnx-monthly.csv',
        index_col='Date',
        parse_dates=True)[column]

    assets = pd.DataFrame({'equity': equity, 'bonds': 1/bonds})

    dates = filter_dates(assets.index, start, end)
    assets = assets.loc[dates]

    return assets