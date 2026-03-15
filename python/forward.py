"""
FE5116 Project - Forward Curve
Equivalent to makeFwdCurve.m and getFwdSpot.m
"""
import numpy as np
from .curves import get_rate_integral


def make_fwd_curve(dom_curve, for_curve, spot, tau):
    """Pack forward curve data into a dict.

    Args:
        dom_curve: domestic rate curve (from make_depo_curve)
        for_curve: foreign rate curve (from make_depo_curve)
        spot: spot exchange rate
        tau: lag between spot and settlement (in years)

    Returns:
        dict containing forward curve data
    """
    return {
        'domCurve': dom_curve,
        'forCurve': for_curve,
        'spot': spot,
        'tau': tau,
    }


def get_fwd_spot(curve, T):
    """Compute the forward spot rate G_0(T).

    G_0(T) = S_0 * exp( int_tau^{T+tau} [r(u) - y(u)] du )

    Args:
        curve: dict from make_fwd_curve
        T: forward date (scalar or array)

    Returns:
        Forward spot price(s)
    """
    T = np.asarray(T, dtype=float)
    tau = curve['tau']

    dom_int_tau = get_rate_integral(curve['domCurve'], tau)
    dom_int_T_tau = get_rate_integral(curve['domCurve'], T + tau)

    for_int_tau = get_rate_integral(curve['forCurve'], tau)
    for_int_T_tau = get_rate_integral(curve['forCurve'], T + tau)

    dom_integral = dom_int_T_tau - dom_int_tau
    for_integral = for_int_T_tau - for_int_tau

    return curve['spot'] * np.exp(dom_integral - for_integral)
