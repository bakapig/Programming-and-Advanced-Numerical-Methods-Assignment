"""
FE5116 Project - Interest Rate Curves
Equivalent to makeDepoCurve.m and getRateIntegral.m
"""
import numpy as np


def make_depo_curve(ts, dfs):
    """Build a piecewise-constant rate curve from discount factors.

    Args:
        ts: array of size N, times to settlement in years
        dfs: array of size N, discount factors

    Returns:
        dict containing curve data needed by get_rate_integral
    """
    ts = np.asarray(ts, dtype=float).ravel()
    dfs = np.asarray(dfs, dtype=float).ravel()

    # Pad with origin (t=0, df=1)
    t_padded = np.concatenate(([0.0], ts))
    df_padded = np.concatenate(([1.0], dfs))

    # Bootstrap piecewise-constant local rates
    dt = np.diff(t_padded)
    local_rates = -np.diff(np.log(df_padded)) / dt

    # Cumulative integral at tenor nodes: int_0^T r(u) du = -ln(df)
    cum_int = -np.log(dfs)

    return {
        'ts': ts,
        'dfs': dfs,
        'rates': local_rates,
        'cumInt': cum_int,
        'tailRate': local_rates[-1],
    }


def get_rate_integral(curve, t):
    """Compute the integral of the rate from 0 to t.

    Args:
        curve: dict from make_depo_curve
        t: scalar or array of times

    Returns:
        Integral value(s), same shape as t
    """
    scalar_input = np.isscalar(t)
    t = np.atleast_1d(np.asarray(t, dtype=float))

    # Input validation
    if np.any(t < 0):
        raise ValueError('Time t must be non-negative.')

    max_T = curve['ts'][-1] + 30.0 / 365.0
    if np.any(t > max_T):
        raise ValueError(
            f'Extrapolation beyond {max_T:.4f} (last tenor + 30 days) not allowed.'
        )

    # Nodes for interpolation
    t_nodes = np.concatenate(([0.0], curve['ts']))
    int_nodes = np.concatenate(([0.0], curve['cumInt']))

    # Linear interpolation; handle extrapolation with constant tail rate
    result = np.zeros_like(t)
    for i, ti in enumerate(t.ravel()):
        if ti <= curve['ts'][-1]:
            result.ravel()[i] = np.interp(ti, t_nodes, int_nodes)
        else:
            result.ravel()[i] = int_nodes[-1] + curve['tailRate'] * (ti - curve['ts'][-1])

    if scalar_input:
        return float(result.ravel()[0])
    return result

