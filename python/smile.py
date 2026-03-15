"""
FE5116 Project - Volatility Smile
Equivalent to makeSmile.m and getSmileVol.m
"""
import numpy as np
from scipy.interpolate import CubicSpline

from .forward import get_fwd_spot
from .delta import get_strike_from_delta
from .black import get_black_call


def make_smile(fwd_curve, T, cps, deltas, vols):
    """Build a smile interpolation structure for a single tenor.

    Args:
        fwd_curve: forward curve dict
        T: time to expiry
        cps: array of +1 (call) / -1 (put)
        deltas: array of delta absolute values
        vols: array of implied volatilities

    Returns:
        dict containing smile data for get_smile_vol
    """
    cps = np.asarray(cps, dtype=float)
    deltas = np.asarray(deltas, dtype=float)
    vols = np.asarray(vols, dtype=float)

    assert len(cps) == len(vols) == len(deltas), \
        'Input vectors must have the same length!'

    # Compute forward spot
    fwd = get_fwd_spot(fwd_curve, T)

    # Resolve deltas to strikes
    Ks = get_strike_from_delta(fwd, T, cps, vols, deltas)

    # Sort by strike (ascending)
    sort_idx = np.argsort(Ks)
    Ks = Ks[sort_idx]
    vols = vols[sort_idx]

    # --- Arbitrage checks ---
    # C(K=0) = fwd (limit of Black formula)
    C_K0 = fwd
    C_Ks = get_black_call(fwd, T, Ks, vols)
    C_all = np.concatenate(([C_K0], C_Ks))
    K_all = np.concatenate(([0.0], Ks))

    dC = np.diff(C_all)
    assert np.all(dC <= 1e-10), 'Arbitrage Violation: Call prices must decrease.'

    dK = np.diff(K_all)
    slopes = dC / dK
    assert np.all(slopes >= -1 - 1e-10) and np.all(slopes <= 1e-10), \
        'Arbitrage Violation: Slopes out of bounds.'
    assert np.all(np.diff(slopes) >= -1e-6), \
        'Arbitrage Violation: Call prices are not convex.'

    # --- Build cubic spline ---
    cs = CubicSpline(Ks, vols, bc_type='not-a-knot')

    # --- Compute tanh wing parameters ---
    # First derivatives at boundaries
    d1_K1 = cs(Ks[0], 1)  # 1st derivative at K1
    d1_KN = cs(Ks[-1], 1)  # 1st derivative at KN

    # Wing strike boundaries
    KL = Ks[0] * (Ks[0] / Ks[1])
    KR = Ks[-1] * (Ks[-1] / Ks[-2])

    # bL, bR from the 50% derivative reduction condition
    C_tanh = np.arctanh(np.sqrt(0.5))
    bL = C_tanh / (Ks[0] - KL)
    bR = C_tanh / (KR - Ks[-1])

    # aL, aR from derivative continuity
    aL = -d1_K1 / bL
    aR = d1_KN / bR

    return {
        'Ks': Ks,
        'vols': vols,
        'cs': cs,
        'aL': aL,
        'bL': bL,
        'aR': aR,
        'bR': bR,
        'fwd': fwd,
        'T': T,
    }


def get_smile_vol(smile, Ks):
    """Evaluate the smile at given strikes.

    Args:
        smile: dict from make_smile
        Ks: scalar or array of strikes

    Returns:
        Array of implied volatilities
    """
    Ks = np.atleast_1d(np.asarray(Ks, dtype=float))
    vols = np.zeros_like(Ks)

    K1 = smile['Ks'][0]
    KN = smile['Ks'][-1]
    vol_K1 = smile['vols'][0]
    vol_KN = smile['vols'][-1]

    # Left wing: K < K1
    idx_L = Ks < K1
    vols[idx_L] = vol_K1 + smile['aL'] * np.tanh(smile['bL'] * (K1 - Ks[idx_L]))

    # Right wing: K > KN
    idx_R = Ks > KN
    vols[idx_R] = vol_KN + smile['aR'] * np.tanh(smile['bR'] * (Ks[idx_R] - KN))

    # Interior: K1 <= K <= KN
    idx_mid = ~idx_L & ~idx_R
    if np.any(idx_mid):
        vols[idx_mid] = smile['cs'](Ks[idx_mid])

    return vols
