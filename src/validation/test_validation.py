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

# end to end: estimates written with ", " separators are paired with the ground truth by machine count
with tempfile.TemporaryDirectory() as name:
    d = Path(name)
    (d / "data/HIPE/1_week/equipment_validation").mkdir(parents=True)
    truth.to_csv(d / "data/HIPE/1_week/equipment_validation/eq_validation_2.csv", index=False)
    out = d / "results/optimization/HIPE/1_week"
    out.mkdir(parents=True)
    (out / "estimated_active_power_2.csv").write_text(
        "Timestamp, Aggregate_Active_Power, Estimate_0, Estimate_1\n"
        + "".join(
            f"{t}, {a}, {e0}, {e1}\n"
            for t, a, e0, e1 in zip(ts, [1.0, 3.0, 4.0], [1.5, 2.0, 3.0], [0.0, 1.0, 1.0], strict=True)
        )
    )
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        main(["--data-root", str(d / "data"), "--results-root", str(d / "results"), "--plots", str(d / "plots")])
    text = printed.getvalue()
    assert "EMUPF HIPE, 2 machines" in text and "skipped EMUPF IMDELD" in text, text
    assert (d / "plots/EMUPF_HIPE_2_machines.png").stat().st_size > 0

print("ok")
