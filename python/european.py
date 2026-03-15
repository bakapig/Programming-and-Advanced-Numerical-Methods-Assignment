"""
FE5116 Project - European Option Pricing
Equivalent to getEuropean.m
"""
import numpy as np
from scipy.integrate import quad

from .pdf import get_pdf


def get_european(vol_surface, T, payoff, ints=None):
    """Compute the forward price of a European payoff by numerical integration.

    V = integral_0^inf f(x) * phi(x) dx

    Args:
        vol_surface: volatility surface dict
        T: time to maturity
        payoff: callable, payoff function (must accept arrays)
        ints: optional, partition of integration domain (e.g., [0, K, inf])
              Defaults to [0, inf]

    Returns:
        Forward (undiscounted) price of the option
    """
    if ints is None:
        ints = [0.0, np.inf]

    def integrand(x):
        """Integrand: payoff(x) * pdf(x). Must return scalar for quad."""
        x_arr = np.atleast_1d(np.asarray(x, dtype=float))
        pdf_vals = get_pdf(vol_surface, T, x_arr)
        pay_vals = np.atleast_1d(payoff(x_arr))
        result = float(np.sum(pay_vals * pdf_vals))
        return result

    u = 0.0
    for i in range(len(ints) - 1):
        lower = ints[i]
        upper = ints[i + 1]
        if lower == upper:
            continue
        val, _ = quad(integrand, lower, upper, limit=200)
        u += val

    return u
