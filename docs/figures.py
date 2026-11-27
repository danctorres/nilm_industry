"""Draws the bell curves of the made-up example in docs/methods.md: 3,000 W total, Oven and Pump on. Also the README's
three examples from HIPE group 9: the per-phase readings and the ovens' learned levels once hipe.py has run (the levels
take about 30 s to learn), the estimates once allocation.py --phases has too.

uv run docs/figures.py
"""

import sys
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
    fig.savefig(DOCS / "allocation_idea.png", dpi=120)


# README example: HIPE group 9 (machines 2 to 10 in file order), a busy December morning
GROUP, START, END = 9, "2017-12-05 08:00", "2017-12-05 11:30"
OVENS = {"HighTemperatureOven": 1, "SolderingOven": 4}  # column in the group
TRUTH = REPO / "data" / "processed" / "HIPE" / str(GROUP) / "equipment_validation.csv"
ESTIMATE = REPO / "results" / "allocation_phases" / "HIPE" / f"{GROUP}.csv"  # Gaussian allocation, per-phase readings


def morning() -> tuple[np.ndarray, pd.Series, np.ndarray]:
    """The December morning's rows in the validation files, their times, and each machine's metered power (W)."""
    truth = pd.read_csv(TRUTH)
    time = pd.to_datetime(truth.timestamp, format="%d-%b-%Y %H:%M:%S")
    rows = ((time >= START) & (time < END)).to_numpy()
    return rows, time[rows], 1000 * truth.iloc[rows, 1:].to_numpy()


def hipe_example() -> None:
    """Metered power and Gaussian allocation's estimate from the per-phase readings, one panel per oven."""
    rows, time, truth = morning()
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
    fig.savefig(DOCS / "allocation_example.png", dpi=100)


def levels_example() -> None:
    """One row per oven: its metered power on the December morning, and beside it, on the same power axis, the levels
    Gaussian allocation learns from November's total and states alone, as in allocation.py without --phases."""
    sys.path.append(str(REPO / "src" / "allocation"))
    from allocation import fit_mixture  # noqa: PLC0415 (a script folder, put on the path just above)

    total = pd.read_csv(TRUTH.parent / "aggregate_training.csv", usecols=[1]).to_numpy()
    states = pd.read_csv(TRUTH.parent / "states_training.csv").iloc[:, 1:].to_numpy(float)
    scale = np.abs(total).max()  # allocation.py fits the total scaled to [0, 1]
    mu, cov, pi = fit_mixture(total / scale, states, 3, np.array([scale]), np.ones(1, bool))
    mean, sd = 1000 * scale * mu[..., 0], 1000 * scale * np.sqrt(cov[..., 0, 0])  # W, (machines, levels)
    _, time, truth = morning()
    fig = Figure(figsize=(10, 5), facecolor=SURFACE, layout="constrained")
    axes = fig.subplots(len(OVENS), 2, sharex="col", sharey="row", width_ratios=(3, 1))
    for (left, right), (name, j) in zip(axes, OVENS.items(), strict=True):
        style(left)
        style(right)
        left.fill_between(time, truth[:, j], color=BLUE, alpha=0.18, linewidth=0)
        left.plot(time, truth[:, j], color=BLUE, linewidth=1)
        left.set_title(name, loc="left", color=INK, fontsize=11)
        left.set_ylabel("W", color=INK)
        left.yaxis.set_major_formatter("{x:,.0f}")
        y = np.linspace(0, (mean[j] + 3 * sd[j]).max(), 2000)
        for m, s, w in zip(mean[j], sd[j], pi[j], strict=True):
            x = w * np.exp(-0.5 * ((y - m) / s) ** 2)  # peak height: the share of on time at this level
            right.fill_betweenx(y, x, color=ORANGE, alpha=0.18, linewidth=0)
            right.plot(x, y, color=ORANGE, linewidth=2)
    fig.legend(
        [axes[0, 0].lines[0], axes[0, 1].lines[0]],
        ["Metered", "Levels learned from November's total and states"],
        loc="outside upper right",
        ncols=2,
        frameon=False,
        labelcolor=INK,
    )
    axes[-1, 0].xaxis.set_major_formatter(DateFormatter("%H:%M"))
    axes[-1, 0].set_xlabel("5 December 2017 (UTC)", color=INK)
    axes[-1, 1].set_xlim(0, 1.1 * pi[list(OVENS.values())].max())
    axes[-1, 1].xaxis.set_major_formatter("{x:.0%}")
    axes[-1, 1].set_xlabel("Share of on time", color=INK)
    fig.savefig(DOCS / "levels_example.png", dpi=100)


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
    fig.savefig(DOCS / "phases_example.png", dpi=100)


if __name__ == "__main__":
    bell_curves()
    print("saved", DOCS / "allocation_idea.png")
    if READINGS.exists():  # hipe.py makes every file but the estimates
        phases_example()
        print("saved", DOCS / "phases_example.png")
        levels_example()
        print("saved", DOCS / "levels_example.png")
    if all(f.exists() for f in (TRUTH, ESTIMATE)):
        hipe_example()
        print("saved", DOCS / "allocation_example.png")
    else:
        print("skipped allocation_example.png: run hipe.py, then allocation.py --dataset hipe --machines 9 --phases")
