"""
FE5116 Project - Comprehensive Visualization Suite
Generates 7 publication-quality plots covering:
1. Yield Curves (domestic & foreign)
2. Forward Spot Curve
3. Volatility Smiles (all tenors)
4. 3D Volatility Surface
5. Risk-Neutral PDFs
6. European Option Prices (call & put vs strike)
7. Moneyness Smiles
"""
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.market import get_market
from python.curves import make_depo_curve, get_rate_integral
from python.forward import make_fwd_curve, get_fwd_spot
from python.delta import get_strike_from_delta
from python.smile import make_smile, get_smile_vol
from python.vol_surface import make_vol_surface, get_vol
from python.pdf import get_pdf
from python.black import get_black_call


def setup_style():
    """Set up a premium dark plotting style."""
    plt.style.use('dark_background')
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'figure.facecolor': '#1a1a2e',
        'axes.facecolor': '#16213e',
        'axes.edgecolor': '#e94560',
        'grid.color': '#333366',
        'grid.alpha': 0.3,
        'text.color': '#e0e0e0',
        'axes.labelcolor': '#e0e0e0',
        'xtick.color': '#bbbbbb',
        'ytick.color': '#bbbbbb',
    })


def build_market():
    """Load market data and construct all curve objects."""
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

    dom_curve = make_depo_curve(Ts, domdfs)
    for_curve = make_depo_curve(Ts, fordfs)
    fwd_curve = make_fwd_curve(dom_curve, for_curve, spot, tau)
    vol_surface = make_vol_surface(fwd_curve, Ts, cps, deltas, vols)

    return {
        'spot': spot, 'tau': tau, 'Ts': Ts, 'domdfs': domdfs, 'fordfs': fordfs,
        'vols': vols, 'cps': cps, 'deltas': deltas,
        'dom_curve': dom_curve, 'for_curve': for_curve,
        'fwd_curve': fwd_curve, 'vol_surface': vol_surface,
    }


def plot_yield_curves(ctx, save_dir):
    """Plot 1: Domestic and Foreign Zero-Coupon Yield Curves."""
    fig, ax = plt.subplots(figsize=(10, 5))

    dom_yields = -np.log(ctx['domdfs']) / ctx['Ts'] * 100
    for_yields = -np.log(ctx['fordfs']) / ctx['Ts'] * 100

    ax.plot(ctx['Ts'], dom_yields, '-o', color='#00d2ff', linewidth=2, markersize=6, label='Domestic Rate')
    ax.plot(ctx['Ts'], for_yields, '-s', color='#e94560', linewidth=2, markersize=6, label='Foreign Rate')

    ax.fill_between(ctx['Ts'], dom_yields, for_yields, alpha=0.15, color='#7b68ee')

    ax.set_title('Zero-Coupon Yield Curves', fontweight='bold')
    ax.set_xlabel('Time to Maturity (Years)')
    ax.set_ylabel('Annualized Rate (%)')
    ax.legend(framealpha=0.3)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(os.path.join(save_dir, '1_yield_curves.png'), dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("  [1/7] Yield curves ✓")


def plot_forward_curve(ctx, save_dir):
    """Plot 2: Forward Exchange Rate Curve G_0(T)."""
    fig, ax = plt.subplots(figsize=(10, 5))

    T_dense = np.linspace(0, max(ctx['Ts']), 200)
    fwd_dense = np.array([get_fwd_spot(ctx['fwd_curve'], t) for t in T_dense])

    ax.plot(T_dense, fwd_dense, '-', color='#00d2ff', linewidth=2.5, label='Forward Curve')
    ax.plot(0, ctx['spot'], 'o', color='#e94560', markersize=10, zorder=5, label=f"Spot = {ctx['spot']:.4f}")

    # Mark tenor points
    fwd_tenors = np.array([get_fwd_spot(ctx['fwd_curve'], t) for t in ctx['Ts']])
    ax.scatter(ctx['Ts'], fwd_tenors, color='#ffd700', s=40, zorder=5, label='Tenor Points')

    ax.set_title('Forward Exchange Rate Curve $G_0(T)$', fontweight='bold')
    ax.set_xlabel('Time to Maturity (Years)')
    ax.set_ylabel('Forward Rate')
    ax.legend(framealpha=0.3)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(os.path.join(save_dir, '2_forward_curve.png'), dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("  [2/7] Forward curve ✓")


def plot_all_smiles(ctx, save_dir):
    """Plot 3: Volatility Smiles for all tenors."""
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = cm.plasma(np.linspace(0.15, 0.95, len(ctx['Ts'])))

    for i, T in enumerate(ctx['Ts']):
        fwd_i = get_fwd_spot(ctx['fwd_curve'], T)
        sm = ctx['vol_surface']['smiles'][i]

        K_range = np.linspace(sm['Ks'][0] * 0.6, sm['Ks'][-1] * 1.4, 300)
        vol_range = get_smile_vol(sm, K_range)

        days_label = int(ctx['Ts'][i] * 365)
        ax.plot(K_range, vol_range * 100, '-', color=colors[i], linewidth=1.5,
                label=f'{days_label}D', alpha=0.9)
        ax.scatter(sm['Ks'], sm['vols'] * 100, color=colors[i], s=20, zorder=5)

    ax.set_title('Implied Volatility Smiles (All Tenors)', fontweight='bold')
    ax.set_xlabel('Strike Price (K)')
    ax.set_ylabel('Implied Volatility (%)')
    ax.legend(ncol=2, framealpha=0.3, fontsize=9)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(os.path.join(save_dir, '3_all_smiles.png'), dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("  [3/7] All smiles ✓")


def plot_3d_surface(ctx, save_dir):
    """Plot 4: 3D Implied Volatility Surface."""
    T_grid = np.linspace(0.05, max(ctx['Ts']), 30)
    K_grid = np.linspace(1.0, 2.2, 40)

    V_grid = np.zeros((len(T_grid), len(K_grid)))
    for i, T in enumerate(T_grid):
        vols, _ = get_vol(ctx['vol_surface'], T, K_grid)
        V_grid[i, :] = vols * 100

    K_mesh, T_mesh = np.meshgrid(K_grid, T_grid)

    fig = plt.figure(figsize=(13, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#16213e')

    surf = ax.plot_surface(K_mesh, T_mesh, V_grid, cmap='plasma',
                           edgecolor='none', alpha=0.92)
    fig.colorbar(surf, shrink=0.5, aspect=10, pad=0.1, label='Vol (%)')

    # Plot market points
    for i, T in enumerate(ctx['Ts']):
        fwd_i = get_fwd_spot(ctx['fwd_curve'], T)
        K_mkt = get_strike_from_delta(fwd_i, T, ctx['cps'], ctx['vols'][i, :], ctx['deltas'])
        ax.scatter(K_mkt, [T] * len(K_mkt), ctx['vols'][i, :] * 100,
                   color='white', s=15, zorder=10)

    ax.set_xlabel('Strike (K)')
    ax.set_ylabel('Maturity (Years)')
    ax.set_zlabel('Implied Vol (%)')
    ax.set_title('3D Implied Volatility Surface $\\sigma(T, K)$', fontweight='bold')
    ax.view_init(elev=25, azim=-45)
    fig.tight_layout()
    fig.savefig(os.path.join(save_dir, '4_vol_surface_3d.png'), dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("  [4/7] 3D surface ✓")


def plot_pdfs(ctx, save_dir):
    """Plot 5: Risk-Neutral Probability Density Functions."""
    fig, ax = plt.subplots(figsize=(11, 6))

    tenor_indices = [0, 2, 4, 7, 9]  # 7D, 21D, 59D, 365D, 730D
    colors = cm.viridis(np.linspace(0.2, 0.9, len(tenor_indices)))

    for j, idx in enumerate(tenor_indices):
        T = ctx['Ts'][idx]
        fwd = get_fwd_spot(ctx['fwd_curve'], T)
        K_range = np.linspace(fwd * 0.5, fwd * 1.6, 400)
        pdf_vals = get_pdf(ctx['vol_surface'], T, K_range)

        days_label = int(T * 365)
        ax.plot(K_range, pdf_vals, '-', color=colors[j], linewidth=2,
                label=f'{days_label}D (fwd={fwd:.4f})')
        ax.axvline(fwd, color=colors[j], linestyle=':', alpha=0.4)

    ax.set_title('Risk-Neutral Probability Density Functions $\\phi_{S_T}(x)$', fontweight='bold')
    ax.set_xlabel('Spot Price $S_T$')
    ax.set_ylabel('Probability Density')
    ax.legend(framealpha=0.3, fontsize=9)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(os.path.join(save_dir, '5_risk_neutral_pdfs.png'), dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("  [5/7] PDFs ✓")


def plot_option_prices(ctx, save_dir):
    """Plot 6: European Call and Put prices vs Strike for several tenors."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    tenor_indices = [4, 7, 9]  # 59D, 365D, 730D
    colors = ['#00d2ff', '#e94560', '#ffd700']

    for j, idx in enumerate(tenor_indices):
        T = ctx['Ts'][idx]
        fwd = get_fwd_spot(ctx['fwd_curve'], T)
        K_range = np.linspace(fwd * 0.7, fwd * 1.3, 100)

        vols, _ = get_vol(ctx['vol_surface'], T, K_range)
        calls = get_black_call(fwd, T, K_range, vols)
        puts = calls - fwd + K_range  # Put-Call parity

        days_label = int(T * 365)
        ax1.plot(K_range, calls, '-', color=colors[j], linewidth=2, label=f'{days_label}D')
        ax2.plot(K_range, puts, '-', color=colors[j], linewidth=2, label=f'{days_label}D')

        ax1.axvline(fwd, color=colors[j], linestyle=':', alpha=0.3)
        ax2.axvline(fwd, color=colors[j], linestyle=':', alpha=0.3)

    ax1.set_title('Undiscounted Call Prices', fontweight='bold')
    ax1.set_xlabel('Strike (K)')
    ax1.set_ylabel('Price')
    ax1.legend(framealpha=0.3)
    ax1.grid(True)

    ax2.set_title('Undiscounted Put Prices', fontweight='bold')
    ax2.set_xlabel('Strike (K)')
    ax2.set_ylabel('Price')
    ax2.legend(framealpha=0.3)
    ax2.grid(True)

    fig.suptitle('European Vanilla Option Prices by Tenor', y=1.02, fontweight='bold', fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(save_dir, '6_option_prices.png'), dpi=150, facecolor=fig.get_facecolor(),
                bbox_inches='tight')
    plt.close(fig)
    print("  [6/7] Option prices ✓")


def plot_moneyness_smiles(ctx, save_dir):
    """Plot 7: Vol vs Moneyness (K/F) for each tenor."""
    fig, ax = plt.subplots(figsize=(11, 6))
    colors = cm.plasma(np.linspace(0.15, 0.95, len(ctx['Ts'])))

    for i, T in enumerate(ctx['Ts']):
        fwd_i = get_fwd_spot(ctx['fwd_curve'], T)
        sm = ctx['vol_surface']['smiles'][i]

        K_range = np.linspace(sm['Ks'][0] * 0.6, sm['Ks'][-1] * 1.4, 300)
        vol_range = get_smile_vol(sm, K_range)
        moneyness = K_range / fwd_i

        days_label = int(T * 365)
        ax.plot(moneyness, vol_range * 100, '-', color=colors[i], linewidth=1.5,
                label=f'{days_label}D', alpha=0.9)

    ax.axvline(1.0, color='white', linestyle='--', alpha=0.5, linewidth=1, label='ATM')
    ax.set_title('Implied Volatility vs Moneyness (K / Forward)', fontweight='bold')
    ax.set_xlabel('Moneyness (K / F)')
    ax.set_ylabel('Implied Volatility (%)')
    ax.legend(ncol=2, framealpha=0.3, fontsize=9)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(os.path.join(save_dir, '7_moneyness_smiles.png'), dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("  [7/7] Moneyness smiles ✓")


def main():
    setup_style()
    
    # Output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(os.path.dirname(script_dir), 'plots')
    os.makedirs(save_dir, exist_ok=True)

    print("=" * 60)
    print("FE5116 Visualization Suite")
    print("=" * 60)
    print(f"Output directory: {save_dir}\n")
    print("Building market objects...")
    ctx = build_market()
    print("Market built successfully!\n")

    print("Generating plots:")
    plot_yield_curves(ctx, save_dir)
    plot_forward_curve(ctx, save_dir)
    plot_all_smiles(ctx, save_dir)
    plot_3d_surface(ctx, save_dir)
    plot_pdfs(ctx, save_dir)
    plot_option_prices(ctx, save_dir)
    plot_moneyness_smiles(ctx, save_dir)

    print(f"\n✅ All 7 plots saved to: {save_dir}")
    print("=" * 60)


if __name__ == '__main__':
    main()
