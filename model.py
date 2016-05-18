import numpy as np
import pandas as pd
import data

def run_model(a, b, k_sp, k_sd, P_assets, k, speculation_start, t0=0,
        magic_price=None, noise_level=0):
    """
    Run the model from the article (doi: 10.1073/pnas.1413108112).

    Args:
        a, b, k_sp, k_sd: Parameter values as defined in the paper.
        P_assets: A pandas.DataFrame where each column is a Series of set of
            prices of alternative assets (stocks and bonds in the paper).
        k: A dict-like set of parameters for the speculation in alternative
            assets. (Called k_equity and k_bonds in the paper.)
            Keys should match the columns of P_assets.
        speculation_start: The first time where speculators act. This
            value must be an index in P_assets.
        t0: What integer to assign to the first time step (as defined by the 
            index of P_assets). This choice affects the equilibrium price
            function (a + b**t).
        magic_price: If not None, changes the logic for how prices are
            determined close to speculation_start. See implementation below.
        noise_level: Relative magnitude of white noise added to k_c
            (essentially a way of adding noise to the equilibrium price).
            For example, noise_level=0.01 multiplies the k_c(t) values by
            numbers uniformly and IID in the range [0.99, 1.01].

    Returns:
        A pandas Series with the same time index as P_assets.

    """

    # Reindex asset prices
    calendar_times = P_assets.index
    integer_times = np.arange(t0, len(calendar_times)+t0)
    P_assets.index = integer_times

    integer_speculation_start = calendar_times.get_loc(speculation_start)

    noise = pd.Series(
        data=(2 * (np.random.rand(len(integer_times)) - .5) * noise_level),
        index=integer_times)

    P = pd.Series(index=integer_times)

    # Equilibrium prices for the first time steps
    for t in integer_times[:2]:
        P[t] = a + b * (t ** 2)
        
    for t in integer_times[1:-1]:

        k_c = (a + b * t ** 2) * k_sd + b * (2 * t  + 1) # Eqn. 28 in SI
        
        k_c *= (1 + noise[t])

        # This term is always included (SI Eqn. 27 and 29)
        P[t+1] = k_c + (1 - k_sd) * P[t]

        if t >= integer_speculation_start:

            if magic_price is not None:
                # Only do this if magic_price is specified.
                # This changes how the price is calculated at two time steps:
                # 1. at time step integer_speculation_start and
                # 2. at time step (integer_speculation_start + 1).
                # P[integer_speculation_start] = magic price, but only AFTER
                # the normal calculation of P[integer_speculation_start]
                # has been used to evaluate the expression from SI Eqn. 27.
                P[integer_speculation_start] = magic_price
            
            P[t+1] += k_sp * (P[t] - P[t-1]) # auto-speculation
            for asset_name in P_assets.columns:
                P_asset = P_assets[asset_name] # alternative assets
                P[t+1] += k[asset_name] * (P_asset[t] - P_asset[t-1])

    P.index = calendar_times
    P_assets.index = calendar_times

    return P


if __name__ == '__main__':
    start = pd.datetime(2004, 1, 1)
    end = pd.datetime(2012, 1, 31)
    P_assets = data.load_assets(start=start, end=end)

    # The parameters reported in the paper
    reported_params = dict(
        a=113,
        k_sd=0.093,
        b=0.011,
        k_sp=1.27,
        k={'equity': -.085, 'bonds': -48.2},
        speculation_start=pd.datetime(2007, 6, 1),
        P_assets=P_assets
        )

    # The corrected parameters (reproducing the paper results)
    corrected_params = reported_params.copy()
    corrected_params.update(
        k_sd=0.09256,
        k_sp=1.2725,
        k={'equity': -0.085033, 'bonds': -48.2},
        magic_price=140.45
    )

    # Corrected parameters with 1% noise added to equilibrium price
    noisy_params = corrected_params.copy()
    noisy_params.update(noise_level=1e-2)

    P = run_model(**corrected_params)
