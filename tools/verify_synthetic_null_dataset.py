#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
artifacts = sorted((ROOT / "artifacts" / "darkness").glob("concrete_trial_dataset_synthetic_null_*.json"))
if not artifacts:
    raise SystemExit("NO_SYNTHETIC_DATASET_FOUND")

p = artifacts[-1]
data = json.loads(p.read_text(encoding="utf-8"))

assert data["object"] == "ConcreteTrialDatasetWithSyntheticNullData"
assert data["status"] == "SYNTHETIC_NULL_DATASET_ONLY_NO_EMPIRICAL_CLAIM"
assert data["synthetic"] is True
assert data["actual_measurements_supplied"] is False
assert data["null_result_proven"] is False
assert data["anomaly_proven"] is False
assert data["darkness_field_proven"] is False
assert len(data["trials"]) >= data["N_min"]

epsilon = data["epsilon"]
tau = data["tau"]

for trial in data["trials"]:
    assert max(trial["Phi_gamma_dark_field"]) < epsilon
    assert min(trial["Phi_gamma_light_field"]) >= epsilon
    assert trial["residual_norm"] <= tau
    assert trial["photon_flux_verdict"] is True
    assert trial["environment_match_verdict"] is True
    assert trial["null_verdict"] is True

for forbidden in [
    "real_null_result",
    "real_anomaly",
    "new_physics_detected",
    "DarknessFieldD_exists",
    "darkness_is_a_medium"
]:
    assert forbidden in data["forbidden_conclusions"]

print("SYNTHETIC_NULL_DATASET_OK")
print(f"artifact={p}")
print("status=SYNTHETIC_NULL_DATASET_ONLY_NO_EMPIRICAL_CLAIM")
print("next_admissible_object=RealConcreteTrialDatasetWithMeasurementsOrStop")
