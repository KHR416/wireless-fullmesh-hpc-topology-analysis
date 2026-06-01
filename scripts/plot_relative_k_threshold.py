#!/usr/bin/env python3
"""Plot K-based bandwidth-threshold sensitivity to active-link budget c.

The plotted y-value is `K_wired / K_wireless(c)`, i.e. the required
`B_link / L` ratio for the selected traffic mode.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


MODE_LABELS = {
    0: "random permutation",
    1: "all-to-all",
    4: "longest matching",
}


# Reconstructed from Jyothi Table I using local k16 Jellyfish raw K as the baseline.
# Torus is intentionally absent because Jyothi Table I does not include a Torus row.
K_WIRED = {
    0: {
        "Fat-tree": 1.00904368,
        "Jellyfish": 1.3822516114,
        "Hypercube": 1.16109135,
        "Dragonfly": 1.05051122,
    },
    1: {
        "Fat-tree": 0.00099887,
        "Jellyfish": 0.0015367200,
        "Hypercube": 0.00110644,
        "Dragonfly": 0.00145988,
    },
    4: {
        "Fat-tree": 1.01958967,
        "Jellyfish": 1.1456063704,
        "Hypercube": 0.58425925,
        "Dragonfly": 0.82483659,
    },
}


TOPOLOGY_STYLES = {
    "Fat-tree":          ("#1f77b4", "-"),
    "Jellyfish":         ("#d62728", "-"),
    "Hypercube":         ("#2ca02c", "--"),
    "Dragonfly": ("#9467bd", "-."),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="figures/k_threshold")
    parser.add_argument("--n-min", type=int, default=64)
    parser.add_argument("--n-max", type=int, default=8192)
    parser.add_argument("--fixed-n", type=int, default=1024,
                        help="Fixed N for c-sweep plots")
    parser.add_argument("--c-max", type=float, default=16,
                        help="Maximum c for c-sweep plots")
    parser.add_argument("--dpi", type=int, default=220)
    return parser.parse_args()


def k_wireless(mode: int, n: np.ndarray, c: float) -> np.ndarray:
    if mode == 0:
        return np.full_like(n, c / 2, dtype=float)
    if mode == 1:
        return c / (n - 1)
    if mode == 4:
        return np.full_like(n, c, dtype=float)
    raise ValueError(f"unsupported mode: {mode}")


def k_wireless_scalar(mode: int, n_fixed: int, c: np.ndarray) -> np.ndarray:
    """K_wireless as a function of c with N fixed."""
    if mode == 0:
        return c / 2
    if mode == 1:
        return c / (n_fixed - 1)
    if mode == 4:
        return c
    raise ValueError(f"unsupported mode: {mode}")


def plot_topology(mode: int, topology: str, k_wired: float, n: np.ndarray, outdir: Path, dpi: int) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    colors = {1: "#1f77b4", 2: "#d62728", 3: "#2ca02c", 4: "#9467bd"}

    for c in [1, 2, 3, 4]:
        y = k_wired / k_wireless(mode, n, float(c))
        ax.plot(n, y, label=f"c = {c}", color=colors[c], linewidth=2.2)

    ax.set_xscale("log", base=2)
    ax.set_xlim(n.min(), n.max())
    ax.grid(True, which="both", linestyle=":", linewidth=0.8, alpha=0.65)
    ax.set_xlabel("Number of endpoints, N")
    ax.set_ylabel("Required relative bandwidth, $K_{wired}/K_{wireless}$")
    ax.set_title(f"{topology}: Required wireless bandwidth vs N ({MODE_LABELS[mode]})")
    ax.legend(loc="best", frameon=True)
    ax.text(
        0.01,
        0.01,
        "K_wired reconstructed from Jyothi Table I; c is per-endpoint active-link budget",
        transform=ax.transAxes,
        fontsize=8,
        color="#444444",
        va="bottom",
    )
    fig.tight_layout()
    stem_topology = "balanced_dragonfly" if topology == "Dragonfly" else topology.lower().replace(" ", "_").replace("-", "_")
    stem = f"k_threshold_mode_{mode}_" + stem_topology
    fig.savefig(outdir / f"{stem}.png", dpi=dpi)
    fig.savefig(outdir / f"{stem}.svg")
    plt.close(fig)


def plot_c_sweep(mode: int, topology_values: dict, n_fixed: int, c_max: float, outdir: Path, dpi: int) -> None:
    """One figure per mode: x=c (continuous), y=threshold, one line per topology."""
    c = np.linspace(1, c_max, 300)

    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    for topology, k_wired in topology_values.items():
        color, linestyle = TOPOLOGY_STYLES[topology]
        y = k_wired / k_wireless_scalar(mode, n_fixed, c)
        ax.plot(c, y, label=topology, color=color, linestyle=linestyle, linewidth=2.2)

    ax.set_xlim(1, c_max)
    ax.set_ylim(bottom=0)
    ax.grid(True, linestyle=":", linewidth=0.8, alpha=0.65)
    ax.set_xlabel("Active-link budget, $c$")
    ax.set_ylabel("Required relative bandwidth, $B_{wireless}/B_{wired}$")
    ax.set_title(f"Required wireless bandwidth vs c, N = {n_fixed} ({MODE_LABELS[mode]})")
    ax.legend(loc="best", frameon=True)
    ax.text(
        0.01,
        0.01,
        f"N = {n_fixed} (fixed); K_wired reconstructed from Jyothi Table I",
        transform=ax.transAxes,
        fontsize=8,
        color="#444444",
        va="bottom",
    )
    fig.tight_layout()
    stem = f"k_threshold_mode_{mode}_c_sweep_N{n_fixed}"
    fig.savefig(outdir / f"{stem}.png", dpi=dpi)
    fig.savefig(outdir / f"{stem}.svg")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    n = np.unique(np.round(np.logspace(np.log2(args.n_min), np.log2(args.n_max), 220, base=2))).astype(float)

    # existing N-sweep figures (per topology)
    for mode, topology_values in K_WIRED.items():
        mode_outdir = outdir / f"mode_{mode}"
        mode_outdir.mkdir(parents=True, exist_ok=True)
        for topology, k_wired in topology_values.items():
            plot_topology(mode, topology, k_wired, n, mode_outdir, args.dpi)

    # new c-sweep figures (all topologies per mode, N fixed)
    c_sweep_outdir = outdir / "c_sweep"
    c_sweep_outdir.mkdir(parents=True, exist_ok=True)
    for mode, topology_values in K_WIRED.items():
        plot_c_sweep(mode, topology_values, args.fixed_n, args.c_max, c_sweep_outdir, args.dpi)


if __name__ == "__main__":
    main()
