"""Draws the two figures in docs/methods.md from its made-up example: 3,000 W total, Oven and Pump on.

uv run docs/figures.py
"""

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

DOCS = Path(__file__).resolve().parent
TOTAL = 3000
OVEN, PUMP = (2000, 800), (500, 50)  # typical power and spread (W), as in the example
SURFACE, INK, MUTED = "#fcfcfb", "#0b0b0b", "#52514e"
BLUE, ORANGE = "#2a78d6", "#eb6834"  # Oven, Pump

# Gaussian allocation, 1 level: the leftover is shared by variance
leftover = TOTAL - OVEN[0] - PUMP[0]
oven_share = OVEN[1] ** 2 / (OVEN[1] ** 2 + PUMP[1] ** 2)
ALLOCATION = (OVEN[0] + oven_share * leftover, PUMP[0] + (1 - oven_share) * leftover)
# best first, as in the table at the top of methods.md
SPLITS = {
    "Gaussian allocation": ALLOCATION,
    "Neural network": (2300 * TOTAL / 2900, 600 * TOTAL / 2900),
    "Proportional split": (TOTAL * 0.8, TOTAL * 0.2),
    "Equal split": (TOTAL / 2, TOTAL / 2),
}


def style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelcolor=INK)


def bell_curves() -> None:
    """One panel per machine on a shared power axis: the wide curve takes the leftover."""
    fig = Figure(figsize=(8, 4.2), facecolor=SURFACE, layout="constrained")
    axes = fig.subplots(2, 1, sharex=True)
    x = np.linspace(0, 4000, 2000)
    for ax, name, (mu, sd), est, color in zip(
        axes, ("Oven", "Pump"), (OVEN, PUMP), ALLOCATION, (BLUE, ORANGE), strict=True
    ):
        style(ax)
        y = np.exp(-0.5 * ((x - mu) / sd) ** 2)  # each curve scaled to height 1: only its width matters here
        ax.fill_between(x, y, color=color, alpha=0.18, linewidth=0)
        ax.plot(x, y, color=color, linewidth=2)
        ax.axvline(mu, color=MUTED, linewidth=1, linestyle="--")
        ax.plot([est], [np.exp(-0.5 * ((est - mu) / sd) ** 2)], "o", color=color, markersize=9, mec=SURFACE, mew=2)
        ax.annotate(
            f"typical {mu:,} W",
            (mu, 1.02),
            ha="right",
            va="bottom",
            color=MUTED,
            xytext=(-4, 0),
            textcoords="offset points",
        )
        ax.annotate(
            f"estimate {est:,.0f} W (+{est - mu:,.0f})",
            (est, 0.95 if name == "Oven" else 0.5),
            color=INK,
            xytext=(10, 0),
            textcoords="offset points",
            va="center",
        )
        ax.set_ylim(0, 1.25)
        ax.set_yticks([])
        ax.set_title(f"{name}: {mu:,} ± {sd} W while on", loc="left", color=INK, fontsize=11)
    axes[1].set_xlabel("Power (W)", color=INK)
    axes[1].xaxis.set_major_formatter("{x:,.0f}")
    fig.suptitle(
        f"Of the {leftover} W leftover, the wide Oven takes {oven_share:.1%}",
        x=0.01,
        ha="left",
        color=INK,
        fontsize=13,
        fontweight="bold",
    )
    fig.savefig(DOCS / "allocation_idea.png", dpi=120)


def method_splits() -> None:
    """One stacked bar per method: Oven, then Pump, against the total and the Pump's usual power."""
    fig = Figure(figsize=(8, 3.6), facecolor=SURFACE, layout="constrained")
    ax = fig.subplots()
    style(ax)
    names = list(SPLITS)[::-1]  # barh draws bottom up
    oven = np.array([SPLITS[n][0] for n in names])
    pump = np.array([SPLITS[n][1] for n in names])
    gap = {"edgecolor": SURFACE, "linewidth": 1.5, "height": 0.6}
    ax.barh(names, oven, color=BLUE, label="Oven", **gap)
    ax.barh(names, pump, left=oven, color=ORANGE, label="Pump", **gap)
    for i, (o, p) in enumerate(zip(oven, pump, strict=True)):
        ax.text(o / 2, i, f"{o:,.0f}", ha="center", va="center", color="white", fontsize=10)
        ax.text(o + p / 2, i, f"{p:,.0f}", ha="center", va="center", color=INK, fontsize=10)
    ax.axvline(TOTAL, color=INK, linewidth=1.5)
    ax.text(TOTAL, len(names) - 0.45, " total 3,000 W", color=INK, va="bottom", fontsize=9)
    ax.axvline(TOTAL - PUMP[0], color=MUTED, linewidth=1, linestyle="--")
    ax.text(
        TOTAL - PUMP[0], len(names) - 0.45, "Pump at its usual 500 W ", color=MUTED, va="bottom", ha="right", fontsize=9
    )
    ax.set_ylim(-0.6, len(names) - 0.1)
    ax.set_xlim(0, 3300)
    ax.xaxis.set_major_formatter("{x:,.0f}")
    ax.set_xlabel("Power (W)", color=INK)
    ax.tick_params(axis="y", length=0)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.08), ncols=2, frameon=False, labelcolor=INK)
    fig.suptitle(
        "Each method's split of the same 3,000 W", x=0.01, ha="left", color=INK, fontsize=13, fontweight="bold"
    )
    fig.savefig(DOCS / "methods_example.png", dpi=120)


if __name__ == "__main__":
    bell_curves()
    method_splits()
    print("saved", DOCS / "allocation_idea.png", DOCS / "methods_example.png")
