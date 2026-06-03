import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_latest(pattern):
    files = sorted((ROOT / "artifacts" / "darkness").glob(pattern))
    assert files
    return json.loads(files[-1].read_text(encoding="utf-8"))

def test_real_measurement_schema_has_no_claim_boundary():
    data = load_latest("real_measurement_intake_schema_*.json")
    assert data["status"] == "REAL_MEASUREMENT_INTAKE_SCHEMA_ONLY_NO_DATA_SUPPLIED"
    assert data["claim_boundary"]["new_physics_claim_allowed"] is False
    assert data["claim_boundary"]["darkness_medium_claim_allowed"] is False
    assert data["claim_boundary"]["darkness_field_existence_claim_allowed"] is False

def test_real_dataset_requirement_has_no_data():
    data = load_latest("real_concrete_trial_dataset_measurements_required_*.json")
    assert data["status"] == "MEASUREMENT_DATA_REQUIRED_NOT_SUPPLIED"
    assert data["actual_measurements_supplied"] is False
    assert data["trials"] == []
    assert data["null_result_proven"] is False
    assert data["anomaly_proven"] is False
    assert data["darkness_field_proven"] is False

def test_real_trial_record_required_fields_exist():
    data = load_latest("real_measurement_intake_schema_*.json")
    trial = data["real_trial_record_required_fields"]
    for key in [
        "trial_id",
        "timestamp_utc",
        "Phi_gamma_dark_field",
        "Phi_gamma_light_field",
        "environment_dark",
        "environment_light",
        "gamma_dark",
        "gamma_light",
        "K",
        "R_m",
        "residual_norm",
        "photon_flux_verdict",
        "environment_match_verdict",
        "null_verdict"
    ]:
        assert key in trial
