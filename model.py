import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot

# t0: what time to assign to first element in time series
# t_spec: time where speculation terms are activated (relative to t0)
# P_1:  time series of S&P500 index
# P_2:  time series of bonds index inversed
# a:    parameter for k_c(t)
# b:    parameter for k_c(t)
# k_1:  mu_equity * gamma_0 (-0.095 or -0.085)
# k_2:  mu_bonds * gamma_0 (-67.9 or -48.2)
# k_sd: (0.098 or 0.093)
# k_sp: (1.29 or 1.27)

def run(a, b, k_sp, k_sd, speculation_start, P_assets, k, start, end, magic_price=None, noise_level=0):

    # Calendar and integer times
    ctimes = filter_dates(P_assets.index, start, end)
    itimes = np.arange(len(ctimes))

    P_assets = P_assets.loc[ctimes]
    P_assets.index = itimes

    integer_speculation_start = ctimes.get_loc(speculation_start)    

    if magic_price is not None:
        magic_time = integer_speculation_start + 1

    P = pd.Series(index=itimes)

    # Equilibrium prices for the first time steps
    for it in itimes[:2]:
        P[it] = a + b * (it ** 2)
        
    for it in itimes[1:-1]:

        # Eqn. 28 in SI
        k_c = (a + b * it ** 2) * k_sd + b * (2 * it  + 1)
        
        # Add noise to equilibrium price
        noise = 2 * (np.random.rand() - .5) * noise_level
        #P[it+1] *= (1 + noise)
        k_c *= (1 + noise)

        # This term is always included (SI Eqn. 29)
        P[it+1] = k_c + (1 - k_sd) * P[it]

        # integer_speculation_start == 40
        # när i >= 41 så är P(i+1) == P(42) påverkad av spekulation
        # magic_time == 41
        if it > integer_speculation_start:
            if magic_price is not None:
                P[magic_time] = magic_price
            
            P[it+1] += k_sp * (P[it] - P[it-1]) # auto-speculation
            for asset_name in P_assets.columns:
                P_asset = P_assets[asset_name] # alternative assets
                P[it+1] += k[asset_name] * (P_asset[it] - P_asset[it-1])

    P.index = ctimes

    return P

def filter_dates(dates, start=None, end=None):
    if start is not None:
        dates = dates[dates >= start]

    if end is not None:
        dates = dates[dates <= end]

    return dates


def load_assets(column='Adj Close', start=None, end=None):
    sp500 = pd.read_csv(
        'data/gspc-monthly.csv',
        index_col='Date',
        parse_dates=True)[column]
    bonds = pd.read_csv(
        'data/tnx-monthly.csv',
        index_col='Date',
        parse_dates=True)[column]
    assets = pd.DataFrame({'sp500': sp500, 'bonds': 1/bonds})

    return assets


if __name__ == '__main__':
    start = pd.datetime(2004, 1, 1)
    end = pd.datetime(2012, 3, 31)
    P_assets = load_assets()

    paper_params = dict(
        a=113,
        k_sd=0.093,
        b=0.011,
        k_sp=1.27,
        k={'sp500': -.085, 'bonds': -48.2},
        speculation_start=pd.datetime(2007, 5, 1),
        P_assets=P_assets,
        start=start,
        end=end
        )

    lagi_params = paper_params.copy()
    lagi_params.update(
        k_sd=0.09256,
        k_sp=1.2725,
        k={'sp500': -0.085033, 'bonds': -48.2},
        magic_price=140.45,
        #noise_level=1e-3
    )
    P = run(**lagi_params)

    print(P)
