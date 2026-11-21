"""Compares the per-machine estimates in results/ with the ground truth in data/processed (port of validation.m).

    python3 src/validation/validation.py [--data-root DIR] [--results-root DIR] [--plots DIR]

Every estimate file results/<method>/<DATASET>/<N>.csv is paired with the ground truth
data/processed/<DATASET>/<N>/equipment_validation.csv (equipment.csv for the oracle-state baseline, which runs on the
unsplit tables). Prints, per file, the errors per machine and of the reconstructed aggregate (the sum of the machine
estimates against the measured aggregate)."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.figure import Figure

REPO = Path(__file__).resolve().parents[2]
DATASETS = ("HIPE", "IMDELD")


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, skipinitialspace=True)  # the estimators write ", " separators


def metrics(true_vals, est_vals, w_to_kw: bool) -> pd.DataFrame:
    """calculate_error.m, one row per column: MAE, MSE, RMSE (kW), R2, NDE and SAE (unitless), no rounding.
    NDE = sum((est - true)^2) / sum(true^2), SAE = |sum(est) - sum(true)| / sum(true)."""
    t, e = np.asarray(true_vals, dtype=float), np.asarray(est_vals, dtype=float)
    if t.ndim == 1:
        t, e = t[:, None], e[:, None]
    if w_to_kw:
        t, e = t / 1000, e / 1000
    sq = ((e - t) ** 2).sum(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):  # a machine that is never on gives inf or nan, as in MATLAB
        return pd.DataFrame(
            {
                "MAE": np.abs(e - t).mean(axis=0),
                "MSE": sq / len(t),
                "RMSE": np.sqrt(sq / len(t)),
                "R2": 1 - sq / ((t - t.mean(axis=0)) ** 2).sum(axis=0),
                "NDE": sq / (t**2).sum(axis=0),
                "SAE": np.abs(e.sum(axis=0) - t.sum(axis=0)) / t.sum(axis=0),
            }
        )


def errors(truth: pd.DataFrame, est: pd.DataFrame, w_to_kw: bool, name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """calculate_all_errors.m for one pair. truth: timestamp, machine 1..M; est: timestamp, measured aggregate,
    estimate 1..M. Returns the per-machine errors and the aggregate-reconstruction errors."""
    if not truth.iloc[:, 0].astype(str).tolist() == est.iloc[:, 0].astype(str).tolist():
        raise SystemExit(f"{name}: the timestamps of the estimates and the ground truth differ")
    true_vals, est_vals = truth.iloc[:, 1:], est.iloc[:, 2:]
    if est_vals.shape[1] != true_vals.shape[1]:
        raise SystemExit(f"{name}: {est_vals.shape[1]} estimate columns for {true_vals.shape[1]} machines")
    per_machine = metrics(true_vals, est_vals, w_to_kw)
    per_machine.insert(0, "machine", list(true_vals.columns))
    aggregate = metrics(est.iloc[:, 1], est_vals.sum(axis=1), w_to_kw)
    return per_machine, aggregate


def plot(path: Path, title: str, truth: pd.DataFrame, est: pd.DataFrame, unit: str) -> None:
    """True against estimated power of every machine, one subplot each."""
    n = truth.shape[1] - 1
    cols = int(np.ceil(np.sqrt(n)))
    fig = Figure(figsize=(5 * cols, 3.5 * np.ceil(n / cols)))
    axes = fig.subplots(int(np.ceil(n / cols)), cols, squeeze=False)
    for i, ax in enumerate(axes.flat):
        if i >= n:
            ax.axis("off")
            continue
        ax.plot(truth.iloc[:, i + 1].to_numpy(), ".", markersize=2, label="True")
        ax.plot(est.iloc[:, i + 2].to_numpy(), ".", markersize=2, label="Estimated")
        ax.set(
            title=str(truth.columns[i + 1]).replace("_", " "), xlabel="Sample index", ylabel=f"Active power [{unit}]"
        )
        ax.legend()
    fig.suptitle(title)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=100)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-root", type=Path, default=REPO / "data" / "processed")
    p.add_argument("--results-root", type=Path, default=REPO / "results")
    p.add_argument("--plots", type=Path, help="also save true-against-estimated plots as PNG files in this folder")
    a = p.parse_args(argv)

    files = sorted(
        (f for f in a.results_root.rglob("*.csv") if f.stem.isdigit() and f.parent.name in DATASETS),
        key=lambda f: (f.parent, int(f.stem)),
    )
    if not files:
        print(f"no <method>/<DATASET>/<N>.csv in {a.results_root}")
    for est_path in files:
        dataset, n = est_path.parent.name, est_path.stem
        method = est_path.parent.parent.relative_to(a.results_root).as_posix()  # e.g. deep_learning/state
        oracle = method == "hart_inspired"
        truth_path = a.data_root / dataset / n / ("equipment.csv" if oracle else "equipment_validation.csv")
        w_to_kw = dataset == "IMDELD"  # IMDELD is in W, shown in kW
        truth, est = read_csv(truth_path), read_csv(est_path)
        if oracle:
            est = est.fillna(0)  # NaN means no estimate was possible, scored as 0
        label = f"{method} {dataset}, {n} machines"
        per_machine, aggregate = errors(truth, est, w_to_kw, f"{est_path} against {truth_path}")
        print(f"\n{label}, per machine (MAE, MSE, RMSE in kW):\n{per_machine.to_string(index=False)}")
        print(f"{label}, aggregate reconstruction:\n{aggregate.to_string(index=False)}")
        if a.plots:
            plot(a.plots / f"{method.replace('/', '_')}_{dataset}_{n}.png", label, truth, est, "W" if w_to_kw else "kW")


if __name__ == "__main__":
    main()
