"""Draws the two figures in docs/methods.md from its made-up example: 3,000 W total, Oven and Pump on. Also the
README's two examples from HIPE group 9: the per-phase readings once hipe.py has run, the estimates once
allocation.py has too, with and without --phases.

uv run docs/figures.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure

DOCS = Path(__file__).resolve().parent
REPO = DOCS.parent
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


# README example: HIPE group 9 (machines 2 to 10 in file order), a busy December morning
GROUP, START, END = 9, "2017-12-05 08:00", "2017-12-05 11:30"
OVENS = {"HighTemperatureOven": 1, "SolderingOven": 4}  # column in the group
TRUTH = REPO / "data" / "processed" / "HIPE" / str(GROUP) / "equipment_validation.csv"
ESTIMATE = REPO / "results" / "allocation_phases" / "HIPE" / f"{GROUP}.csv"  # Gaussian allocation, per-phase readings


def hipe_example() -> None:
    """Metered power and Gaussian allocation's estimate from the per-phase readings, one panel per oven."""
    truth = pd.read_csv(TRUTH)
    time = pd.to_datetime(truth.timestamp, format="%d-%b-%Y %H:%M:%S")
    rows = ((time >= START) & (time < END)).to_numpy()
    time, truth = time[rows], 1000 * truth.iloc[rows, 1:].to_numpy()
    est = 1000 * pd.read_csv(ESTIMATE, skipinitialspace=True).iloc[rows, 2:].to_numpy()
    fig = Figure(figsize=(10, 5), facecolor=SURFACE, layout="constrained")
    axes = fig.subplots(len(OVENS), 1, sharex=True)
    for ax, (name, j) in zip(axes, OVENS.items(), strict=True):
        style(ax)
        ax.fill_between(time, truth[:, j], color=BLUE, alpha=0.25, linewidth=0, label="Metered")
        ax.plot(time, est[:, j], color=ORANGE, linewidth=1, label="Estimated from the per-phase readings")
        off = np.abs(est[:, j] - truth[:, j]).mean()
        ax.set_title(f"{name}: off by {off:,.0f} W on average", loc="left", color=INK, fontsize=11)
        ax.set_ylabel("W", color=INK)
        ax.yaxis.set_major_formatter("{x:,.0f}")
    fig.legend(*axes[0].get_legend_handles_labels(), loc="outside upper right", ncols=2, frameon=False, labelcolor=INK)
    axes[-1].xaxis.set_major_formatter(DateFormatter("%H:%M"))
    axes[-1].set_xlabel("5 December 2017 (UTC)", color=INK)
    fig.suptitle(
        "The per-phase readings tell the two ovens apart", x=0.01, ha="left", color=INK, fontsize=13, fontweight="bold"
    )
    fig.savefig(DOCS / "allocation_example.png", dpi=100)


# README per-phase readings: group 9's meter while the HighTemperatureOven heats, then the SolderingOven
READINGS = REPO / "data" / "processed" / "HIPE" / str(GROUP) / "phases_validation.csv"
HEATING = {"HighTemperatureOven heats": ("08:40", "09:23"), "SolderingOven heats": ("09:17", "09:44")}  # own meters
AQUA = "#1baf7a"  # L3


def phases_example() -> None:
    """The total, then active and reactive power on each phase: each oven moves its own phases."""
    raw = pd.read_csv(READINGS)
    time = pd.to_datetime(raw.timestamp, format="%d-%b-%Y %H:%M:%S")
    rows = ((time >= "2017-12-05 08:30") & (time < "2017-12-05 09:50")).to_numpy()
    r = raw.iloc[rows, 1:].set_axis(time[rows]).rolling("10s").mean()  # 10 s means, to calm the 1 s jitter
    fig = Figure(figsize=(10, 7.5), facecolor=SURFACE, layout="constrained")
    axes = fig.subplots(3, 1, sharex=True)
    panels = (
        ("Total active power (kW): one reading", [r.iloc[:, :3].sum(axis=1)], [INK]),
        ("Active power on each phase (kW)", [r[f"P{k}_kW"] for k in (1, 2, 3)], [BLUE, ORANGE, AQUA]),
        ("Reactive power on each phase (kvar)", [r[f"Q{k}_kvar"] for k in (1, 2, 3)], [BLUE, ORANGE, AQUA]),
    )
    for ax, (title, lines, colors) in zip(axes, panels, strict=True):
        style(ax)
        for k, (y, color) in enumerate(zip(lines, colors, strict=True), 1):
            ax.plot(y.index, y, color=color, linewidth=1.4, label=f"L{k}")
        ax.set_title(title, loc="left", color=INK, fontsize=11)
        ax.axhline(0, color=MUTED, linewidth=0.8)
    top = axes[0].get_ylim()[1]
    for i, (label, span) in enumerate(HEATING.items()):  # one level each, as they overlap
        (a, b), y = (pd.Timestamp(f"2017-12-05 {t}") for t in span), top * (1 + 0.2 * i)
        axes[0].plot([a, b], [y, y], color=MUTED, linewidth=1)
        axes[0].text(a + (b - a) / 2, y, label, ha="center", va="bottom", color=INK, fontsize=10)
    axes[0].set_ylim(0, top * 1.4)
    axes[1].legend(loc="upper right", ncols=3, frameon=False, labelcolor=INK)
    axes[-1].xaxis.set_major_formatter(DateFormatter("%H:%M"))
    axes[-1].set_xlabel("5 December 2017 (UTC)", color=INK)
    fig.suptitle(
        "Each oven heats on its own phases, with its own reactive power",
        x=0.01,
        ha="left",
        color=INK,
        fontsize=13,
        fontweight="bold",
    )
    fig.savefig(DOCS / "phases_example.png", dpi=100)


if __name__ == "__main__":
    bell_curves()
    method_splits()
    print("saved", DOCS / "allocation_idea.png", DOCS / "methods_example.png")
    if READINGS.exists():
        phases_example()
        print("saved", DOCS / "phases_example.png")
    if all(f.exists() for f in (TRUTH, ESTIMATE)):
        hipe_example()
        print("saved", DOCS / "allocation_example.png")
    else:
        print("skipped allocation_example.png: run hipe.py, then allocation.py --dataset hipe --machines 9 --phases")
