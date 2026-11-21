"""Self-check of the validation: python3 src/validation/test_validation.py"""

import contextlib
import io
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from validation import errors, main, metrics

# metrics: hand-computed errors -1, 0, 1 against true 1, 2, 3
m = metrics([1, 2, 3], [2, 2, 2], False).iloc[0]
assert np.allclose(m[["MAE", "MSE", "RMSE", "R2", "NDE", "SAE"]], [2 / 3, 2 / 3, np.sqrt(2 / 3), 0, 2 / 14, 0])
assert np.isclose(metrics([1000, 3000], [2000, 2000], True).iloc[0]["MAE"], 1.0)  # W shown in kW
assert np.isnan(metrics([0, 0], [0, 0], False).iloc[0]["R2"])  # a machine never on: no variance

ts = ["24-Oct-2017 10:00:00", "24-Oct-2017 10:00:01", "24-Oct-2017 10:00:02"]
truth = pd.DataFrame({"Time": ts, "Eq2_P_kW": [1.0, 2.0, 3.0], "Eq3_P_kW": [0.0, 1.0, 1.0]})
est = pd.DataFrame({"Timestamp": ts, "Aggregate": [1.0, 3.0, 4.0], "E0": [1.0, 2.0, 3.0], "E1": [0.0, 1.0, 1.0]})
per_machine, aggregate = errors(truth, est, False, "exact")
assert list(per_machine["machine"]) == ["Eq2_P_kW", "Eq3_P_kW"] and np.allclose(per_machine["MAE"], 0)
assert np.allclose(aggregate["MAE"], 0)
try:
    errors(truth, est.assign(Timestamp=ts[::-1]), False, "shuffled")
    raise AssertionError("timestamps that differ must be rejected")
except SystemExit:
    pass

# end to end: every results/<method>/<DATASET>/<N>.csv, at any depth, is paired with the ground truth for N machines;
# estimates written with ", " separators; the oracle-state baseline scored on the validation rows of its whole-recording
# estimates (the extra row of 99s is left out), NaN scored as 0
with tempfile.TemporaryDirectory() as name:
    d = Path(name)
    (d / "data/HIPE/2").mkdir(parents=True)
    truth.to_csv(d / "data/HIPE/2/equipment_validation.csv", index=False)
    rows = "".join(
        f"{t}, {a}, {e0}, {e1}\n"
        for t, a, e0, e1 in zip(ts, [1.0, 3.0, 4.0], [1.5, 2.0, 3.0], [0.0, 1.0, 1.0], strict=True)
    )
    for method in ["optimization", "deep_learning/plain"]:
        (d / "results" / method / "HIPE").mkdir(parents=True)
        (d / "results" / method / "HIPE/2.csv").write_text("Timestamp, Aggregate_Active_Power, E0, E1\n" + rows)
    (d / "results/optimization/HIPE/coef_2.csv").write_text("Coef 0, Coef 1, Coef 2, Coef 3\n1, 2, 3, 4\n")
    (d / "results/hart_inspired/HIPE").mkdir(parents=True)
    (d / "results/hart_inspired/HIPE/2.csv").write_text(
        f"timestamp,active_power,E0,E1\n24-Oct-2017 09:59:59,99,99,99\n{ts[0]},1,1,0\n{ts[1]},3,2,NaN\n{ts[2]},4,3,1\n"
    )
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        main(["--data-root", str(d / "data"), "--results-root", str(d / "results"), "--plots", str(d / "plots")])
    text = printed.getvalue()
    for label in ["optimization HIPE, 2 machines", "deep_learning/plain HIPE, 2 machines"]:
        assert f"{label}, per machine" in text, text
    assert "hart_inspired HIPE, 2 machines, per machine" in text and "coef" not in text, text
    hart = text.split("hart_inspired")[1]
    assert "NaN" not in hart and "0.333333" in hart, text  # Eq3: 0, 1 (from NaN), 1 against 0, 1, 1
    assert (d / "plots/deep_learning_plain_HIPE_2.png").stat().st_size > 0
    assert (d / "plots/optimization_HIPE_2.png").stat().st_size > 0

print("ok")
