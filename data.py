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

def load_price_index(**kwargs):
    d = pd.DataFrame.from_csv('data/food-price-index.csv')
    dates = d['period']
    dates.replace(
        '(?P<year>20\d{2})(?P<month>[A-Z]{3})',
        '\g<month> \g<year>',
        regex=True,
        inplace=True)

    dates = pd.to_datetime(dates)

    values = d['data']
    values.index = dates

    values.sort_index(inplace=True)

    values.dropna(inplace=True)

    dates = filter_dates(values.index, **kwargs)
    values = values[dates]

    return values
