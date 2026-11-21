"""Helpers shared by hipe.py and imdeld.py, ported from the MATLAB originals.
Each one reproduces the MATLAB function named in its docstring, including its edge behaviour."""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

REPO = Path(__file__).resolve().parents[2]
TIME_FORMAT = "%d-%b-%Y %H:%M:%S"  # MATLAB's default datetime display, used in every processed file
_CLOCK = np.array([f"{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}" for s in range(86400)])


def read_equipment_csv(folder: Path, usecols: list[str] | None = None) -> list[pd.DataFrame]:
    """One table per machine CSV in folder, in alphabetical file order: machine k is the k-th file."""
    files = sorted(Path(folder).glob("*.csv"))
    if not files:
        raise SystemExit(f"no csv files in {folder}")
    return [pd.read_csv(f, usecols=usecols) for f in files]


def movmean(x, k: int) -> np.ndarray:
    """MATLAB movmean(x, k): mean over k samples centred on each one (k // 2 before, k - k // 2 - 1 after),
    the window shrinking at both ends."""
    x = np.asarray(x, dtype=float)
    if np.isnan(x).any():
        raise ValueError("movmean: NaN in the input; drop missing values first")
    n = len(x)
    c = np.concatenate([[0.0], np.cumsum(x)])
    i = np.arange(n)
    lo = np.maximum(i - k // 2, 0)
    hi = np.minimum(i + (k - k // 2 - 1) + 1, n)
    return (c[hi] - c[lo]) / (hi - lo)


def spline(x, y, xq) -> np.ndarray:
    """MATLAB spline(x, y, xq): not-a-knot cubic spline, extrapolating beyond the data."""
    return CubicSpline(np.asarray(x, dtype=float), np.asarray(y, dtype=float))(np.asarray(xq, dtype=float))


def matlab_round(x, decimals: int = 0):
    """MATLAB round: halves go away from zero (numpy rounds them to even)."""
    scale = 10.0**decimals
    return np.sign(x) * np.floor(np.abs(x) * scale + 0.5) / scale


def seconds(t: pd.Series) -> np.ndarray:
    """Seconds since 1970 of naive timestamps, as MATLAB posixtime."""
    return (pd.to_datetime(t) - pd.Timestamp(0)).dt.total_seconds().to_numpy()


def split_train_validation(agg, ratio: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Adaptive binning split (MATLAB split_train_validation). The aggregate is cut into six bins of one standard
    deviation around its mean; from every bin with more than 100 samples the same budget n_bin is drawn:
    floor(n_bin * ratio) for training and floor(n_bin * (1 - ratio)) for validation, without overlap.
    n_bin is the smallest kept bin, capped at 1000 * ratio. Returns shuffled 0-based row indices."""
    agg = np.asarray(agg, dtype=float)
    edges = agg.mean() + np.arange(-3, 4) * agg.std(ddof=1)  # MATLAB std divides by n - 1
    counts, _ = np.histogram(agg, edges)  # like histcounts: [a, b) bins, the last one [a, b]
    bin_of = np.searchsorted(edges, agg, side="right") - 1
    bin_of[agg == edges[-1]] = len(edges) - 2
    bins = np.flatnonzero(counts > 100)
    if bins.size == 0:
        raise ValueError("split_train_validation: no aggregate bin has more than 100 samples")
    n_bin = min(1000 * ratio, counts[bins].min())
    n_training, n_validation = int(np.floor(n_bin * ratio)), int(np.floor(n_bin * (1 - ratio)))

    training, validation = [], []
    for b in bins:
        samples = np.flatnonzero(bin_of == b)
        bin_training = rng.choice(samples, n_training, replace=False)
        training.append(bin_training)
        validation.append(rng.choice(np.setdiff1d(samples, bin_training), n_validation, replace=False))
    return rng.permutation(np.concatenate(training)), rng.permutation(np.concatenate(validation))


def time_strings(t) -> np.ndarray:
    """Timestamps in TIME_FORMAT ("21-Feb-2018 00:00:00"), fractions of a second dropped as strftime does. Joined from
    one string per day and one per second of the day: per-row strftime takes about a minute on a month of 1 Hz data."""
    day, second = np.divmod(pd.to_datetime(t).to_numpy().astype("datetime64[s]").astype(np.int64), 86400)
    days, inverse = np.unique(day, return_inverse=True)
    return np.char.add(pd.to_datetime(days, unit="D").strftime("%d-%b-%Y ").to_numpy(str)[inverse], _CLOCK[second])


def write_csv(df: pd.DataFrame, path: Path) -> None:
    """Write like MATLAB writetable: no index, timestamps in TIME_FORMAT, 15 significant digits, NaN as "NaN"."""
    path.parent.mkdir(parents=True, exist_ok=True)
    times = {c: time_strings(df[c]) for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])}
    df.assign(**times).to_csv(path, index=False, float_format="%.15g", na_rep="NaN")
