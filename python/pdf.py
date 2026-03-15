"""
FE5116 Project - Probability Density Function
Equivalent to getPdf.m
"""
import numpy as np

from .vol_surface import get_vol
from .black import get_black_call


def get_pdf(vol_surf, T, Ks):
    """Compute the risk-neutral PDF of S(T) via finite differences of call prices.

    phi(K) = d²C/dK²

    Args:
        vol_surf: volatility surface dict
        T: time to expiry
        Ks: array of strike prices

    Returns:
        Array of PDF values at Ks
    """
    Ks = np.atleast_1d(np.asarray(Ks, dtype=float))
    dK = 1e-4

    # Prevent strikes from hitting 0
    Ks_safe = np.maximum(Ks, 1e-8)
    K_up = Ks_safe + dK
    K_down = np.maximum(Ks_safe - dK, 1e-8)

    # Get vols at the three points
    vols_mid, fwd = get_vol(vol_surf, T, Ks_safe)
    vols_up, _ = get_vol(vol_surf, T, K_up)
    vols_down, _ = get_vol(vol_surf, T, K_down)

    # Get call prices
    C = get_black_call(fwd, T, Ks_safe, vols_mid)
    C_up = get_black_call(fwd, T, K_up, vols_up)
    C_down = get_black_call(fwd, T, K_down, vols_down)

    # Second derivative via central finite differences
    pdf = (C_up - 2 * C + C_down) / (dK**2)

    # Floor at zero (probability can't be negative)
    pdf = np.maximum(pdf, 0.0)

    return pdf
