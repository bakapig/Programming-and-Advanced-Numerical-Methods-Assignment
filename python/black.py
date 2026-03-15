"""
FE5116 Project - Black Formula
Equivalent to getBlackCall.m
"""
import numpy as np
from scipy.special import erf


def get_black_call(f, T, Ks, Vs):
    """Compute undiscounted Black call option prices.

    Args:
        f: forward spot price
        T: time to expiry
        Ks: array of strikes
        Vs: array of implied volatilities

    Returns:
        Array of undiscounted call prices
    """
    Ks = np.asarray(Ks, dtype=float)
    Vs = np.asarray(Vs, dtype=float)

    u = np.zeros_like(Ks, dtype=float)

    # Handle K=0 edge case: C(0) = f
    zero_mask = (Ks == 0)
    nonzero_mask = ~zero_mask

    if np.any(nonzero_mask):
        K = Ks[nonzero_mask]
        V = Vs[nonzero_mask]

        d1 = (np.log(f) - np.log(K)) / (V * np.sqrt(T)) + 0.5 * V * np.sqrt(T)
        d2 = d1 - V * np.sqrt(T)

        N_d1 = 0.5 * (1 + erf(d1 / np.sqrt(2)))
        N_d2 = 0.5 * (1 + erf(d2 / np.sqrt(2)))

        u[nonzero_mask] = f * N_d1 - K * N_d2

    u[zero_mask] = f

    return u
