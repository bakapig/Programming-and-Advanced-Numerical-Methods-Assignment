"""
FE5116 Project - Delta to Strike Conversion
Equivalent to getStrikeFromDelta.m
"""
import numpy as np
from scipy.special import erfinv


def get_strike_from_delta(fwd, T, cp, sigma, delta):
    """Compute strike from delta, using the analytical inversion.

    Args:
        fwd: forward spot price
        T: time to expiry
        cp: 1 for call, -1 for put (scalar or array)
        sigma: implied volatility (scalar or array)
        delta: delta in absolute value (scalar or array)

    Returns:
        Strike(s)
    """
    cp = np.asarray(cp, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    delta = np.asarray(delta, dtype=float)

    # N_inv(delta) = sqrt(2) * erfinv(2*delta - 1)
    norm_inv_delta = np.sqrt(2) * erfinv(2 * delta - 1)

    # d1 = cp * N_inv(delta)
    d1 = cp * norm_inv_delta

    # K = fwd * exp(-sigma*sqrt(T) * (d1 - 0.5*sigma*sqrt(T)))
    exponent = -sigma * np.sqrt(T) * (d1 - 0.5 * sigma * np.sqrt(T))
    K = fwd * np.exp(exponent)

    return K
