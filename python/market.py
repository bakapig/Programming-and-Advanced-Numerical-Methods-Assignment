"""
FE5116 Project - Market Data
Equivalent to getMarket.m
"""
import numpy as np


def get_market():
    """Returns the hard-coded market data.

    Returns:
        dict with keys: spot, lag, days, domdf, fordf, vols, cps, deltas
    """
    spot = 1.5123
    lag = 2  # spot rule settlement lag (calendar days)

    data = np.array([
        [7,   0.99962, 0.99923, 20.80, 20.20, 20.00, 20.40, 21.60],
        [14,  0.99922, 0.99845, 21.32, 20.71, 20.50, 20.91, 22.14],
        [21,  0.99882, 0.99766, 21.84, 21.21, 21.00, 21.42, 22.68],
        [28,  0.99841, 0.99685, 22.36, 21.72, 21.50, 21.93, 23.22],
        [59,  0.99655, 0.99322, 23.40, 22.73, 22.50, 22.95, 24.30],
        [90,  0.99466, 0.98959, 24.96, 24.24, 24.00, 24.48, 25.92],
        [181, 0.98866, 0.97818, 26.00, 25.25, 25.00, 25.50, 27.00],
        [365, 0.97579, 0.95432, 27.04, 26.26, 26.00, 26.52, 28.08],
        [546, 0.96138, 0.92864, 29.12, 28.28, 28.00, 28.56, 30.24],
        [730, 0.94457, 0.89984, 31.20, 30.30, 30.00, 30.60, 32.41],
    ])

    days = data[:, 0]
    domdf = data[:, 1]
    fordf = data[:, 2]
    vols = data[:, 3:] / 100.0
    cps = np.array([-1, -1, 1, 1, 1])
    deltas = np.array([0.1, 0.25, 0.5, 0.25, 0.1])

    return {
        'spot': spot,
        'lag': lag,
        'days': days,
        'domdf': domdf,
        'fordf': fordf,
        'vols': vols,
        'cps': cps,
        'deltas': deltas,
    }
