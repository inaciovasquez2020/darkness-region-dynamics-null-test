#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

schema_files = sorted((ROOT / "artifacts" / "darkness").glob("real_measurement_intake_schema_*.json"))
dataset_files = sorted((ROOT / "artifacts" / "darkness").glob("real_concrete_trial_dataset_measurements_required_*.json"))

if not schema_files:
    raise SystemExit("NO_REAL_MEASUREMENT_INTAKE_SCHEMA_FOUND")
if not dataset_files:
    raise SystemExit("NO_REAL_DATASET_REQUIREMENT_FOUND")

schema = json.loads(schema_files[-1].read_text(encoding="utf-8"))
dataset = json.loads(dataset_files[-1].read_text(encoding="utf-8"))

assert schema["object"] == "RealMeasurementIntakeSchema"
assert schema["status"] == "REAL_MEASUREMENT_INTAKE_SCHEMA_ONLY_NO_DATA_SUPPLIED"
assert schema["claim_boundary"]["new_physics_claim_allowed"] is False
assert schema["claim_boundary"]["darkness_medium_claim_allowed"] is False
assert schema["claim_boundary"]["darkness_field_existence_claim_allowed"] is False

for key in [
    "dataset_id",
    "apparatus_id",
    "probe_id",
    "operator_id_or_lab_id",
    "timestamp_utc",
    "epsilon",
    "bandwidth_B",
    "tau",
    "eta",
    "N_min",
    "known_field_model_id",
    "calibration_files",
    "trials"
]:
    assert key in schema["required_fields"]

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
    assert key in schema["real_trial_record_required_fields"]

assert dataset["object"] == "RealConcreteTrialDatasetWithMeasurements"
assert dataset["status"] == "MEASUREMENT_DATA_REQUIRED_NOT_SUPPLIED"
assert dataset["synthetic"] is False
assert dataset["actual_measurements_supplied"] is False
assert dataset["null_result_proven"] is False
assert dataset["anomaly_proven"] is False
assert dataset["darkness_field_proven"] is False
assert dataset["new_physics_detected"] is False
assert dataset["trials"] == []

for forbidden in [
    "real_null_result_without_real_measurements",
    "real_anomaly_without_real_measurements",
    "new_physics_detected",
    "DarknessFieldD_exists",
    "darkness_is_a_medium"
]:
    assert forbidden in dataset["forbidden_claims"]

print("REAL_MEASUREMENT_INTAKE_SCHEMA_OK")
print(f"schema={schema_files[-1]}")
print(f"dataset_requirement={dataset_files[-1]}")
print("status=MEASUREMENT_DATA_REQUIRED_NOT_SUPPLIED")
print("next_admissible_object=SupplyConcreteTrialDatasetWithRealMeasurementsOrStop")
