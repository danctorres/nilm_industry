"""Self-check of validation.py and corrupt_states.py: python3 src/validation/test_validation.py"""

import contextlib
import io
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from corrupt_states import corrupt
from corrupt_states import main as corrupt_main

from validation import baselines, errors, main, metrics

# metrics, hand-computed: estimates 2, 2, 2 against true 1, 2, 3
m = metrics([1, 2, 3], [2, 2, 2], False).iloc[0]
assert np.allclose(m[["MAE", "MSE", "RMSE", "R2", "NDE", "SAE"]], [2 / 3, 2 / 3, np.sqrt(2 / 3), 0, 2 / 14, 0])
assert np.isclose(metrics([1000, 3000], [2000, 2000], True).iloc[0]["MAE"], 1.0)  # W shown in kW
assert np.isnan(metrics([0, 0], [0, 0], False).iloc[0]["R2"])  # a machine never on: no variance

ts = ["24-Oct-2017 10:00:00", "24-Oct-2017 10:00:01", "24-Oct-2017 10:00:02"]
truth = pd.DataFrame({"Time": ts, "Eq2_P_kW": [1.0, 2.0, 3.0], "Eq3_P_kW": [0.0, 1.0, 1.0]})
est = pd.DataFrame({"Timestamp": ts, "Aggregate": [1.0, 3.0, 4.0], "E0": [1.0, 2.0, 3.0], "E1": [0.0, 1.0, 1.0]})
per_machine, aggregate, pooled = errors(truth, est, False, "exact")
assert list(per_machine["machine"]) == ["Eq2_P_kW", "Eq3_P_kW"] and np.allclose(per_machine["MAE"], 0)
assert np.allclose(aggregate["MAE"], 0) and pooled["MAE"] == 0
# one miss of 1: MAE over all 6 samples, MAE_on over the 5 where a machine draws power
pooled = errors(truth, est.assign(E1=[0.0, 0.0, 1.0]), False, "one miss")[2]
assert np.isclose(pooled["MAE"], 1 / 6) and np.isclose(pooled["MAE_on"], 1 / 5), pooled
try:
    errors(truth, est.assign(Timestamp=ts[::-1]), False, "shuffled")
    raise AssertionError("timestamps that differ must be rejected")
except SystemExit:
    pass

# end to end: every results/<method>/<DATASET>/<N>.csv, at any depth, is paired with the metered power of N machines.
# Estimates use ", " separators. hart_inspired estimates the whole recording: only its test rows are scored (the extra
# row of 99s is left out), and NaN is scored as 0.
with tempfile.TemporaryDirectory() as name:
    d = Path(name)
    (d / "data/HIPE/2").mkdir(parents=True)
    truth.to_csv(d / "data/HIPE/2/equipment_validation.csv", index=False)
    for split in ["training", "validation"]:
        agg_split = pd.DataFrame({"Time": ts, "active_power": [1.0, 3.0, 4.0]})
        agg_split.to_csv(d / f"data/HIPE/2/aggregate_{split}.csv", index=False)
        states_split = pd.DataFrame({"Time": ts, "Eq2_State": 1, "Eq3_State": [0, 1, 1]})
        states_split.to_csv(d / f"data/HIPE/2/states_{split}.csv", index=False)
    rows = "".join(
        f"{t}, {a}, {e0}, {e1}\n"
        for t, a, e0, e1 in zip(ts, [1.0, 3.0, 4.0], [1.5, 2.0, 3.0], [0.0, 1.0, 1.0], strict=True)
    )
    for method in ["polynomial", "neural_network/plain"]:
        (d / "results" / method / "HIPE").mkdir(parents=True)
        (d / "results" / method / "HIPE/2.csv").write_text("Timestamp, Aggregate_Active_Power, E0, E1\n" + rows)
    (d / "results/polynomial/HIPE/coef_2.csv").write_text("Coef 0, Coef 1, Coef 2, Coef 3\n1, 2, 3, 4\n")
    (d / "results/hart_inspired/HIPE").mkdir(parents=True)
    (d / "results/hart_inspired/HIPE/2.csv").write_text(
        f"timestamp,active_power,E0,E1\n24-Oct-2017 09:59:59,99,99,99\n{ts[0]},1,1,0\n{ts[1]},3,2,NaN\n{ts[2]},4,3,1\n"
    )
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        main(["--data-root", str(d / "data"), "--results-root", str(d / "results"), "--plots", str(d / "plots")])
    text = printed.getvalue()
    for label in ["polynomial HIPE, 2 machines", "neural_network/plain HIPE, 2 machines"]:
        assert f"{label}, per machine" in text, text
    assert "hart_inspired HIPE, 2 machines, per machine" in text and "coef" not in text, text
    hart = text.split("hart_inspired HIPE, 2 machines, per machine")[1].split("\n\n")[0]
    assert "NaN" not in hart and "0.333333" in hart, text  # Eq3: 0, 0 (from NaN), 1 against 0, 1, 1
    assert "hart_inspired HIPE, 2 machines: an estimate for 80% of the ON samples" in text, text  # 4 of 5
    assert "Summary over all machines" in text and "baseline/proportional" in text.split("Summary")[1], text

    # baselines from the total and the states: zero, equal split, proportional to the fitted means (1, 2.5)
    base = dict(baselines(d / "data/HIPE/2"))
    assert (base["baseline/zero"].iloc[:, 2:] == 0).all().all()
    assert np.allclose(base["baseline/equal"].iloc[:, 2:], [[1, 0], [1.5, 1.5], [2, 2]])
    assert np.allclose(base["baseline/proportional"].iloc[:, 2:], [[1, 0], [3 / 3.5, 7.5 / 3.5], [4 / 3.5, 10 / 3.5]])
    # the fit puts Eq3 at 0 W: it gets nothing beside Eq2, but the whole total when ON alone, and no machine ON gets 0
    z = d / "zero"
    z.mkdir()
    for split, power, s2, s3 in (
        ("training", [1, 1, 1], 1, [0, 1, 1]),
        ("validation", [3, 2, 0], [1, 0, 0], [1, 1, 0]),
    ):
        pd.DataFrame({"Time": ts, "active_power": power}).to_csv(z / f"aggregate_{split}.csv", index=False)
        pd.DataFrame({"Time": ts, "Eq2_State": s2, "Eq3_State": s3}).to_csv(z / f"states_{split}.csv", index=False)
    assert np.allclose(dict(baselines(z))["baseline/proportional"].iloc[:, 2:], [[3, 0], [0, 2], [0, 0]])
    assert (d / "plots/neural_network_plain_HIPE_2.png").stat().st_size > 0
    assert (d / "plots/polynomial_HIPE_2.png").stat().st_size > 0

    # corrupt_states: a 1 s lag reads each state from one sample earlier (the first keeps its own); other files linked
    states_split.to_csv(d / "data/HIPE/2/states.csv", index=False)
    corrupt_main(
        ["--dataset", "hipe", "--machines", "2", "--lag", "1", "--data-root", str(d / "data"), "--out", str(d / "lag")]
    )
    lagged = pd.read_csv(d / "lag/HIPE/2/states_validation.csv")
    assert lagged.iloc[:, 1:].to_numpy().tolist() == [[1, 0], [1, 0], [1, 1]] and list(lagged.Time) == ts
    assert (d / "lag/HIPE/2/aggregate_training.csv").is_symlink()

# --flip 0.1 flips about 10% of the entries
many = pd.DataFrame(
    {"Time": pd.date_range("2017-10-23", periods=20000, freq="s").strftime("%d-%b-%Y %H:%M:%S"), "s": 0}
)
assert 0.09 < corrupt(many, 0, 0.1, np.random.default_rng(0)).s.mean() < 0.11

print("ok")
