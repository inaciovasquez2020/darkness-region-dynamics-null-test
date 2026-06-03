import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_dataset():
    artifacts = sorted((ROOT / "artifacts" / "darkness").glob("concrete_trial_dataset_synthetic_null_*.json"))
    assert artifacts
    return json.loads(artifacts[-1].read_text(encoding="utf-8"))

def test_synthetic_dataset_has_no_empirical_claim():
    data = load_dataset()
    assert data["synthetic"] is True
    assert data["actual_measurements_supplied"] is False
    assert data["null_result_proven"] is False
    assert data["anomaly_proven"] is False

def test_all_trials_are_schema_nulls():
    data = load_dataset()
    assert len(data["trials"]) >= data["N_min"]
    for trial in data["trials"]:
        assert trial["residual_norm"] <= data["tau"]
        assert trial["null_verdict"] is True

def test_forbidden_conclusions_present():
    data = load_dataset()
    forbidden = set(data["forbidden_conclusions"])
    assert "real_null_result" in forbidden
    assert "real_anomaly" in forbidden
    assert "new_physics_detected" in forbidden
    assert "darkness_is_a_medium" in forbidden
