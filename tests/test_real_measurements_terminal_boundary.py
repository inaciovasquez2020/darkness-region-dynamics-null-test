import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_boundary():
    files = sorted((ROOT / "artifacts" / "darkness").glob("real_measurements_terminal_boundary_*.json"))
    assert files
    return json.loads(files[-1].read_text(encoding="utf-8"))

def test_boundary_status():
    data = load_boundary()
    assert data["status"] == "STOPPED_AT_REAL_MEASUREMENTS_BOUNDARY"
    assert data["minimal_missing_object"] == "ConcreteTrialDatasetWithRealMeasurements"

def test_no_empirical_claims():
    data = load_boundary()
    not_proven = set(data["not_proven"])
    assert "real_null_result" in not_proven
    assert "real_anomaly" in not_proven
    assert "new_physics_detected" in not_proven
    assert "DarknessFieldD_exists" in not_proven
    assert "darkness_is_a_medium" in not_proven
