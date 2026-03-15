"""
FE5116 Project - Main entry point
Equivalent to project.m — runs the same computations and prints results.
"""
import sys
import os
import numpy as np

# Add parent to path so we can import the python package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.market import get_market
from python.curves import make_depo_curve
from python.forward import make_fwd_curve, get_fwd_spot
from python.smile import make_smile, get_smile_vol
from python.vol_surface import make_vol_surface, get_vol
from python.pdf import get_pdf
from python.european import get_european


def main():
    print("=" * 60)
    print("FE5116 Numerical Project — Python Port")
    print("=" * 60)

    # Load market data
    mkt = get_market()
    spot = mkt['spot']
    lag = mkt['lag']
    days = mkt['days']
    domdfs = mkt['domdf']
    fordfs = mkt['fordf']
    vols = mkt['vols']
    cps = mkt['cps']
    deltas = mkt['deltas']

    tau = lag / 365.0
    Ts = days / 365.0

    # Construct market objects
    dom_curve = make_depo_curve(Ts, domdfs)
    for_curve = make_depo_curve(Ts, fordfs)
    fwd_curve = make_fwd_curve(dom_curve, for_curve, spot, tau)
    vol_surface = make_vol_surface(fwd_curve, Ts, cps, deltas, vols)

    # Compute a discount factor
    from python.curves import get_rate_integral
    dom_rate = np.exp(-get_rate_integral(dom_curve, 0.8))
    print(f"\ndomRate = exp(-getRateIntegral(domCurve, 0.8)) = {dom_rate:.6f}")

    # Compute forward spot G_0(0.8)
    fwd = get_fwd_spot(fwd_curve, 0.8)
    print(f"fwd = getFwdSpot(fwdCurve, 0.8) = {fwd:.6f}")

    # Build and use a smile
    smile = make_smile(fwd_curve, Ts[-1], cps, deltas, vols[-1, :])
    atmfvol = get_smile_vol(smile, np.array([get_fwd_spot(fwd_curve, Ts[-1])]))
    print(f"atmfvol = getSmileVol(smile, getFwdSpot(fwdCurve, Ts(end))) = {atmfvol[0]:.6f}")

    # Get some vol
    vol_vals, f = get_vol(vol_surface, 0.8, np.array([fwd, fwd]))
    print(f"[vol, f] = getVol(volSurface, 0.8, [fwd, fwd]) = [{vol_vals[0]:.6f}, {vol_vals[1]:.6f}], f = {f:.6f}")

    # Get pdf
    pdf_vals = get_pdf(vol_surface, 0.8, np.array([fwd, fwd]))
    print(f"pdf = getPdf(volSurface, 0.8, [fwd, fwd]) = [{pdf_vals[0]:.6f}, {pdf_vals[1]:.6f}]")

    # ATM European call
    payoff_call = lambda x: np.maximum(x - fwd, 0.0)
    u_call = get_european(vol_surface, 0.8, payoff_call)
    print(f"European call (ATM) = {u_call:.6f}")

    # ATM European put with subintervals hint
    payoff_put = lambda x: np.maximum(fwd - x, 0.0)
    u_put = get_european(vol_surface, 0.8, payoff_put, [0, fwd])
    print(f"European put  (ATM) = {u_put:.6f}")

    # ATM European digital call spread with subintervals hint
    payoff_digi = lambda x: ((x > 0.95 * fwd) & (x < 1.05 * fwd)).astype(float)
    u_digi = get_european(vol_surface, 0.8, payoff_digi, [0.95 * fwd, 1.05 * fwd])
    print(f"European digital call spread = {u_digi:.6f}")

    print("\n" + "=" * 60)
    print("All computations completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
