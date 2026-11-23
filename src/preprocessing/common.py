"""Helpers shared by hipe.py and imdeld.py."""

from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
TIME_FORMAT = "%d-%b-%Y %H:%M:%S"  # "01-Dec-2017 00:05:00", used in every processed file
VALIDATION_SHARE = 0.3  # share of the time blocks held out as test rows
TRAINING_ROWS = 19_600  # drawn at random, chosen on October (docs/notes.md)
_CLOCK = np.array([f"{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}" for s in range(86400)])


def read_equipment_csv(folder: Path, usecols: list[str] | None = None) -> list[pd.DataFrame]:
    """Read each machine CSV in folder into one table. Machine k is the k-th file in alphabetical order."""
    files = sorted(Path(folder).glob("*.csv"))
    if not files:
        raise SystemExit(f"no csv files in {folder}")
    return [pd.read_csv(f, usecols=usecols) for f in files]


def seconds(t: pd.Series) -> np.ndarray:
    """Seconds since 1970 for timestamps that carry no time zone."""
    return (pd.to_datetime(t) - pd.Timestamp(0)).dt.total_seconds().to_numpy()


def split_train_validation(t, block: float, gap: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Split the rows into training and test by time blocks of `block` seconds (t is in seconds).

    - Test: VALIDATION_SHARE of the blocks, picked at random. Every row in them is scored, so the test rows follow
      the recording's own distribution.
    - Rows within `gap` seconds of a block edge go to neither side, so training and test rows are
      at least 2 * gap apart.
    - Training: draw_training on the other blocks' rows.

    Returns 0-based row indices: training shuffled, test in time order."""
    t = np.asarray(t, dtype=float)
    block_of = np.floor(t / block)
    usable = (t - block_of * block >= gap) & ((block_of + 1) * block - t > gap)
    blocks = np.unique(block_of[usable])
    chosen = rng.choice(blocks, max(1, round(VALIDATION_SHARE * len(blocks))), replace=False)
    in_validation = np.isin(block_of, chosen)
    return draw_training(np.flatnonzero(usable & ~in_validation), rng), np.flatnonzero(usable & in_validation)


def draw_training(candidates: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Draw TRAINING_ROWS of the candidates at random (all of them if fewer), shuffled. At random, so training sees
    each power range as often as the test rows do."""
    return rng.choice(candidates, min(TRAINING_ROWS, len(candidates)), replace=False)


def time_strings(t) -> np.ndarray:
    """Format timestamps as TIME_FORMAT ("21-Feb-2018 00:00:00"), dropping fractions of a second like strftime.

    Joins one string per day with one per second of the day, because per-row strftime takes about a minute on a
    month of 1 Hz data."""
    day, second = np.divmod(pd.to_datetime(t).to_numpy().astype("datetime64[s]").astype(np.int64), 86400)
    days, inverse = np.unique(day, return_inverse=True)
    return np.char.add(pd.to_datetime(days, unit="D").strftime("%d-%b-%Y ").to_numpy(str)[inverse], _CLOCK[second])


def write_csv(df: pd.DataFrame, path: Path) -> None:
    """Write df to path: no index, timestamps in TIME_FORMAT, 15 significant digits, NaN as "NaN"."""
    path.parent.mkdir(parents=True, exist_ok=True)
    times = {c: time_strings(df[c]) for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])}
    df.assign(**times).to_csv(path, index=False, float_format="%.15g", na_rep="NaN")
