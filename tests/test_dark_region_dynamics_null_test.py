import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_artifact():
    artifacts = sorted((ROOT / "artifacts" / "darkness").glob("dark_region_dynamics_null_test_*.json"))
    assert artifacts
    return json.loads(artifacts[-1].read_text(encoding="utf-8"))

def test_status_is_schema_only():
    data = load_artifact()
    assert data["status"] == "CONDITIONAL_TEST_SCHEMA_ONLY_NO_NEW_PHYSICS_CLAIM"
    assert data["actual_measurements_supplied"] is False

def test_forbidden_claims_present():
    data = load_artifact()
    forbidden = set(data["forbidden_claims"])
    assert "darkness_is_a_medium" in forbidden
    assert "new_physics_detected" in forbidden
    assert "DarknessFieldD_exists" in forbidden

def test_conditional_theorem_boundary():
    data = load_artifact()
    theorem = data["conditional_theorem"]
    assert theorem["name"] == "FiniteSensitivityDarknessCouplingExclusionTheorem"
    assert "MeasuredNullDataset" in theorem["assumptions"]
    assert data["darkness_field_proven"] is False

def test_dataset_schema_contains_trial_fields():
    data = load_artifact()
    trial = data["dataset_schema_required"]["trials"][0]
    for key in [
        "trial_id",
        "timestamp",
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
