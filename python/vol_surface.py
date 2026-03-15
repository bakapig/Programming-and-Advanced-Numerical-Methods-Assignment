"""
FE5116 Project - Volatility Surface
Equivalent to makeVolSurface.m and getVol.m
"""
import numpy as np

from .forward import get_fwd_spot
from .smile import make_smile, get_smile_vol


def make_vol_surface(fwd_curve, Ts, cps, deltas, vols):
    """Build the full volatility surface from market data.

    Args:
        fwd_curve: forward curve dict
        Ts: array of expiry times (years)
        cps: array of call/put flags
        deltas: array of delta values
        vols: matrix of volatilities (num_tenors x num_deltas)

    Returns:
        dict containing vol surface data for get_vol
    """
    Ts = np.asarray(Ts, dtype=float).ravel()
    num_tenors = len(Ts)

    smiles = []
    fwds = np.zeros(num_tenors)
    atm_vars = np.zeros(num_tenors)

    for i in range(num_tenors):
        T = Ts[i]
        vol_row = vols[i, :]

        fwd = get_fwd_spot(fwd_curve, T)
        fwds[i] = fwd

        sm = make_smile(fwd_curve, T, cps, deltas, vol_row)
        smiles.append(sm)

        # Calendar arbitrage check: ATM total variance must be increasing
        atm_vol = get_smile_vol(sm, np.array([fwd]))[0]
        atm_vars[i] = atm_vol**2 * T

        if i > 0:
            assert atm_vars[i] >= atm_vars[i - 1], \
                f'Calendar Arbitrage Violation at Tenor {i+1} (Variance decreased!)'

    return {
        'fwdCurve': fwd_curve,
        'Ts': Ts,
        'smiles': smiles,
        'fwds': fwds,
    }


def get_vol(vol_surf, T, Ks):
    """Get implied volatility from the surface at (T, Ks).

    Args:
        vol_surf: dict from make_vol_surface
        T: time to expiry (scalar)
        Ks: array of strikes

    Returns:
        (vols, fwd) - volatilities array and forward spot price
    """
    Ks = np.atleast_1d(np.asarray(Ks, dtype=float))

    fwd = get_fwd_spot(vol_surf['fwdCurve'], T)

    Ts = vol_surf['Ts']
    if T > Ts[-1]:
        raise ValueError('Time T exceeds the maximum tenor. Extrapolation beyond TN is not allowed.')

    vols = np.zeros_like(Ks)

    if T <= Ts[0]:
        # Map strikes along moneyness lines
        K1 = Ks * (vol_surf['fwds'][0] / fwd)
        vols = get_smile_vol(vol_surf['smiles'][0], K1)

    else:
        # Find bounding tenors
        idx_next = np.searchsorted(Ts, T, side='left')
        if idx_next < len(Ts) and Ts[idx_next] == T:
            # Exact tenor match
            Ki = Ks * (vol_surf['fwds'][idx_next] / fwd)
            vols = get_smile_vol(vol_surf['smiles'][idx_next], Ki)
        else:
            # Interpolate between tenors
            i = idx_next - 1
            Ti = Ts[i]
            Tip1 = Ts[i + 1]

            # Moneyness-equivalent strikes
            Ki = Ks * (vol_surf['fwds'][i] / fwd)
            Kip1 = Ks * (vol_surf['fwds'][i + 1] / fwd)

            # Get vols from adjacent smiles
            Vi = get_smile_vol(vol_surf['smiles'][i], Ki)
            Vip1 = get_smile_vol(vol_surf['smiles'][i + 1], Kip1)

            # Total variance interpolation
            Wi = Vi**2 * Ti
            Wip1 = Vip1**2 * Tip1

            W_interp = ((Tip1 - T) / (Tip1 - Ti)) * Wi + ((T - Ti) / (Tip1 - Ti)) * Wip1
            vols = np.sqrt(W_interp / T)

    return vols, fwd
