"""Compares the per-machine estimates in results/ with the ground truth in data/processed.

    python3 src/validation/validation.py [--data-root DIR] [--results-root DIR] [--plots DIR]

Every estimate file results/<method>/<DATASET>/<N>.csv is paired with the ground truth
data/processed/<DATASET>/<N>/equipment_validation.csv; the oracle-state baseline estimates the whole recording and is
scored on the same validation rows. Three baselines that see only the aggregate and the states are scored next to
them: zero, the aggregate split equally among the ON machines, and split in proportion to each machine's mean power
fitted to the training split. Prints, per file, the errors per machine and of the reconstructed aggregate (the sum of
the machine estimates against the measured aggregate), then one summary line per method over all machines. Negative
estimates are scored as 0 for every method."""

import argparse
from itertools import chain
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from scipy.optimize import nnls

REPO = Path(__file__).resolve().parents[2]
DATASETS = ("HIPE", "IMDELD")


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, skipinitialspace=True)  # the estimators write ", " separators


def metrics(true_vals, est_vals, w_to_kw: bool) -> pd.DataFrame:
    """One row per column: MAE, MSE, RMSE (kW), R2, NDE and SAE (unitless), no rounding.
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


def errors(
    truth: pd.DataFrame, est: pd.DataFrame, w_to_kw: bool, name: str
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """Errors of one pair. truth: timestamp, machine 1..M; est: timestamp, measured aggregate, estimate 1..M. Returns
    the per-machine errors, the aggregate-reconstruction errors and the errors over every machine's samples pooled."""
    if not truth.iloc[:, 0].astype(str).tolist() == est.iloc[:, 0].astype(str).tolist():
        raise SystemExit(f"{name}: the timestamps of the estimates and the ground truth differ")
    true_vals, est_vals = truth.iloc[:, 1:], est.iloc[:, 2:].clip(lower=0)  # every method scored without negatives
    if est_vals.shape[1] != true_vals.shape[1]:
        raise SystemExit(f"{name}: {est_vals.shape[1]} estimate columns for {true_vals.shape[1]} machines")
    per_machine = metrics(true_vals, est_vals, w_to_kw)
    per_machine.insert(0, "machine", list(true_vals.columns))
    aggregate = metrics(est.iloc[:, 1], est_vals.sum(axis=1), w_to_kw)
    pooled = metrics(true_vals.to_numpy().ravel(), est_vals.to_numpy().ravel(), w_to_kw).iloc[0]
    return per_machine, aggregate, pooled


def baselines(d: Path) -> list[tuple[str, pd.DataFrame]]:
    """Estimates in the estimators' layout from the aggregate and the states alone, the information every method
    gets: zero, the aggregate split equally among the ON machines, and split in proportion to each machine's mean
    power, fitted by non-negative least squares to the training aggregate and states."""
    a_tr = pd.read_csv(d / "aggregate_training.csv").iloc[:, 1].to_numpy()
    s_tr = pd.read_csv(d / "states_training.csv").iloc[:, 1:].to_numpy(float)
    val = pd.read_csv(d / "aggregate_validation.csv").iloc[:, :2]
    s = pd.read_csv(d / "states_validation.csv").iloc[:, 1:].to_numpy(float)
    w = s * nnls(s_tr, a_tr)[0]
    with np.errstate(divide="ignore", invalid="ignore"):  # no machine ON: 0 / 0, scored as 0
        shares = {
            "zero": 0 * s,
            "equal": s / s.sum(axis=1, keepdims=True),
            "proportional": w / w.sum(axis=1, keepdims=True),
        }
    a = val.iloc[:, 1].to_numpy()[:, None]
    return [(f"baseline/{k}", pd.concat([val, pd.DataFrame(np.nan_to_num(v) * a)], axis=1)) for k, v in shares.items()]


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
    summary = []
    for dataset, n in sorted({(f.parent.name, f.stem) for f in files}, key=lambda x: (x[0], int(x[1]))):
        d = a.data_root / dataset / n
        truth_path = d / "equipment_validation.csv"
        truth, w_to_kw = read_csv(truth_path), dataset == "IMDELD"  # IMDELD is in W, shown in kW
        found = [f for f in files if (f.parent.name, f.stem) == (dataset, n)]
        # method e.g. deep_learning/state; a generator, so one estimate file is in memory at a time
        results = ((f.parent.parent.relative_to(a.results_root).as_posix(), read_csv(f)) for f in found)
        for method, raw in chain(results, baselines(d)):
            label, est = f"{method} {dataset}, {n} machines", raw
            if method == "hart_inspired":  # whole recording: its validation rows, NaN (no estimate possible) as 0
                est = raw.set_index(raw.columns[0]).loc[truth.iloc[:, 0]].reset_index()
                covered = est.iloc[:, 2:].notna().to_numpy()[truth.iloc[:, 1:].to_numpy() > 0].mean()
                print(f"\n{label}: an estimate for {covered:.0%} of the ON samples")
                est = est.fillna(0)
            per_machine, aggregate, pooled = errors(truth, est, w_to_kw, f"{label} against {truth_path}")
            print(f"\n{label}, per machine (MAE, MSE, RMSE in kW):\n{per_machine.to_string(index=False)}")
            print(f"{label}, aggregate reconstruction:\n{aggregate.to_string(index=False)}")
            summary.append({"dataset": dataset, "machines": int(n), "method": method, **pooled[["MAE", "NDE"]]})
            if a.plots:
                plot(
                    a.plots / f"{method.replace('/', '_')}_{dataset}_{n}.png",
                    label,
                    truth,
                    est,
                    "W" if w_to_kw else "kW",
                )
    if summary:
        table = pd.DataFrame(summary).sort_values(["dataset", "machines", "MAE"])
        print(f"\nSummary over all machines (MAE in kW, NDE pooled):\n{table.to_string(index=False)}")


if __name__ == "__main__":
    main()
