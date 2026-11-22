"""Helpers shared by hipe.py and imdeld.py, ported from the MATLAB originals.
Each one reproduces the MATLAB function named in its docstring, including its edge behaviour."""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

REPO = Path(__file__).resolve().parents[2]
TIME_FORMAT = "%d-%b-%Y %H:%M:%S"  # MATLAB's default datetime display, used in every processed file
VALIDATION_SHARE = 0.3  # share of the time blocks held out for validation
TRAINING_PER_BIN = 490  # training rows drawn from every aggregate bin, as floor(700 * 0.7) before the block split
_CLOCK = np.array([f"{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}" for s in range(86400)])


def read_equipment_csv(folder: Path, usecols: list[str] | None = None) -> list[pd.DataFrame]:
    """One table per machine CSV in folder, in alphabetical file order: machine k is the k-th file."""
    files = sorted(Path(folder).glob("*.csv"))
    if not files:
        raise SystemExit(f"no csv files in {folder}")
    return [pd.read_csv(f, usecols=usecols) for f in files]


def movmean(x, k: int) -> np.ndarray:
    """MATLAB movmean(x, k) of data without NaN: mean over k samples centred on each one (k // 2 before,
    k - k // 2 - 1 after), the window shrinking at both ends."""
    return pd.Series(x, dtype=float).rolling(k, center=True, min_periods=1).mean().to_numpy()


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


def split_train_validation(t, agg, block: float, gap: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Time-block split. The recording (t in seconds) is cut into blocks of `block` seconds, and VALIDATION_SHARE of
    them, drawn at random, are validation: every row in them is scored, so validation follows the recording's own
    distribution. Rows within `gap` seconds of a block edge belong to neither side, so every training row is at least
    2 * gap away from every validation row. Training is draw_training from the other blocks. Returns 0-based row
    indices, training shuffled and validation in time order."""
    t, agg = np.asarray(t, dtype=float), np.asarray(agg, dtype=float)
    block_of = np.floor(t / block)
    usable = (t - block_of * block >= gap) & ((block_of + 1) * block - t > gap)
    blocks = np.unique(block_of[usable])
    chosen = rng.choice(blocks, max(1, round(VALIDATION_SHARE * len(blocks))), replace=False)
    in_validation = np.isin(block_of, chosen)
    return draw_training(np.flatnonzero(usable & ~in_validation), agg, rng), np.flatnonzero(usable & in_validation)


def draw_training(candidates: np.ndarray, agg, rng: np.random.Generator) -> np.ndarray:
    """The same number of rows (at most TRAINING_PER_BIN) from every aggregate bin of the candidate rows (adaptive
    binning, MATLAB split_train_validation): six bins of one standard deviation around the mean, those with more than
    100 rows. The two outer bins are open-ended (MATLAB's stopped at 3 standard deviations), so training sees the peaks
    that validation scores. Returns the rows shuffled."""
    a = np.asarray(agg, dtype=float)[candidates]
    edges = a.mean() + np.arange(-2, 3) * a.std(ddof=1)  # inner edges; MATLAB std divides by n - 1
    bin_of = np.searchsorted(edges, a, side="right")  # [a, b) bins, the first and last open-ended
    counts = np.bincount(bin_of, minlength=len(edges) + 1)
    bins = np.flatnonzero(counts > 100)
    if bins.size == 0:
        raise ValueError("draw_training: no aggregate bin of the training rows has more than 100 rows")
    n = min(TRAINING_PER_BIN, counts[bins].min())
    training = np.concatenate([rng.choice(candidates[bin_of == b], n, replace=False) for b in bins])
    return rng.permutation(training)


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
