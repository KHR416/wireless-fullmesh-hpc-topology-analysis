#!/usr/bin/env python3
"""Plot relative bisection-width bandwidth thresholds for PPT figures.

The plotted y-value is the required per-link bandwidth ratio
`B_wireless / B_wired = W_wired / W_wireless(c)`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="figures/bisection_width")
    parser.add_argument("--n-min", type=int, default=64)
    parser.add_argument("--n-max", type=int, default=8192)
    parser.add_argument("--k", type=float, default=20)
    parser.add_argument("--r", type=float, default=16)
    parser.add_argument("--d", type=float, default=3)
    parser.add_argument("--dpi", type=int, default=220)
    return parser.parse_args()


def compute_curves(n: np.ndarray, c: float | np.ndarray, k: float, r: float, d: float) -> dict[str, np.ndarray]:
    c_arr = np.asarray(c, dtype=float)
    return {
        "Fat-tree": np.broadcast_to(1 / c_arr, n.shape),
        "Jellyfish": np.broadcast_to(r / (2 * (k - r) * c_arr), n.shape),
        "Hypercube": np.broadcast_to(1 / c_arr, n.shape),
        "Dragonfly": np.broadcast_to(1 / (2 * c_arr), n.shape) + 1 / (2 * c_arr * np.sqrt(n)),
        f"{int(d) if d.is_integer() else d}D Torus": 4 / (c_arr * np.power(n, 1 / d)),
    }


def plot_for_c(
    n: np.ndarray,
    c_value: int | str,
    c: float | np.ndarray,
    outdir: Path,
    k: float,
    r: float,
    d: float,
    dpi: int,
) -> None:
    curves = compute_curves(n, c, k, r, d)
    fig, ax = plt.subplots(figsize=(8.4, 5.0))

    styles = {
        "Fat-tree": ("#1f77b4", "-"),
        "Jellyfish": ("#d62728", "-"),
        "Hypercube": ("#2ca02c", "--"),
        "Dragonfly": ("#9467bd", "-."),
        f"{int(d) if d.is_integer() else d}D Torus": ("#ff7f0e", ":"),
    }

    for name, y in curves.items():
        color, linestyle = styles[name]
        ax.plot(n, y, label=name, color=color, linestyle=linestyle, linewidth=2.2)

    ax.set_xscale("log", base=2)
    ax.set_xlim(n.min(), n.max())
    ax.grid(True, which="both", linestyle=":", linewidth=0.8, alpha=0.65)
    ax.set_xlabel("Number of endpoints, N")
    ax.set_ylabel("Required relative bandwidth, $B_{wireless}/B_{wired}$")
    c_label = "N/2" if c_value == "n_over_2" else str(c_value)
    ax.set_title(f"Required wireless bandwidth vs N, c = {c_label}")
    ax.legend(loc="best", frameon=True)

    note = f"Jellyfish: k={k:g}, r={r:g}; Torus: d={d:g}; even N assumed"
    ax.text(
        0.01,
        0.01,
        note,
        transform=ax.transAxes,
        fontsize=8,
        color="#444444",
        va="bottom",
    )

    fig.tight_layout()
    stem = f"relative_bisection_width_c_{c_label.replace('/', '_over_')}"
    fig.savefig(outdir / f"{stem}.png", dpi=dpi)
    fig.savefig(outdir / f"{stem}.svg")
    plt.close(fig)


def plot_for_topology(
    n: np.ndarray,
    topology: str,
    outdir: Path,
    k: float,
    r: float,
    d: float,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    colors = {1: "#1f77b4", 2: "#d62728", 3: "#2ca02c", 4: "#9467bd"}

    for c_value in [1, 2, 3, 4]:
        y = compute_curves(n, float(c_value), k, r, d)[topology]
        ax.plot(n, y, label=f"c = {c_value}", color=colors[c_value], linewidth=2.2)

    ax.set_xscale("log", base=2)
    ax.set_xlim(n.min(), n.max())
    ax.grid(True, which="both", linestyle=":", linewidth=0.8, alpha=0.65)
    ax.set_xlabel("Number of endpoints, N")
    ax.set_ylabel("Required relative bandwidth, $B_{wireless}/B_{wired}$")
    ax.set_title(f"{topology}: Required wireless bandwidth vs N")
    ax.legend(loc="best", frameon=True)

    note = f"Jellyfish: k={k:g}, r={r:g}; Torus: d={d:g}; even N assumed"
    ax.text(
        0.01,
        0.01,
        note,
        transform=ax.transAxes,
        fontsize=8,
        color="#444444",
        va="bottom",
    )

    fig.tight_layout()
    stem_topology = "balanced_dragonfly" if topology == "Dragonfly" else topology.lower().replace(" ", "_").replace("-", "_")
    stem = "relative_bisection_width_" + stem_topology
    fig.savefig(outdir / f"{stem}.png", dpi=dpi)
    fig.savefig(outdir / f"{stem}.svg")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    n = np.unique(np.round(np.logspace(np.log2(args.n_min), np.log2(args.n_max), 220, base=2))).astype(float)

    topology_outdir = outdir / "by_topology"
    topology_outdir.mkdir(parents=True, exist_ok=True)
    for topology in compute_curves(n, 1.0, args.k, args.r, args.d):
        plot_for_topology(n, topology, topology_outdir, args.k, args.r, args.d, args.dpi)

    combined_outdir = outdir / "combined"
    combined_outdir.mkdir(parents=True, exist_ok=True)
    plot_for_c(n, "n_over_2", n / 2, combined_outdir, args.k, args.r, args.d, args.dpi)


if __name__ == "__main__":
    main()
