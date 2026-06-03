#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
artifacts = sorted((ROOT / "artifacts" / "darkness").glob("dark_region_dynamics_null_test_*.json"))
if not artifacts:
    raise SystemExit("NO_ARTIFACT_FOUND")

p = artifacts[-1]
data = json.loads(p.read_text(encoding="utf-8"))

required_top = [
    "object",
    "status",
    "known_physics_baseline",
    "hypothesis_under_test",
    "definitions",
    "conditional_theorem",
    "forbidden_claims",
    "valid_claim",
    "dataset_schema_required",
    "actual_measurements_supplied",
    "null_result_proven",
    "anomaly_proven",
    "darkness_field_proven",
    "next_admissible_object"
]

for key in required_top:
    if key not in data:
        raise SystemExit(f"MISSING_KEY={key}")

assert data["object"] == "DarknessRegionDynamicsNullTest"
assert data["status"] == "CONDITIONAL_TEST_SCHEMA_ONLY_NO_NEW_PHYSICS_CLAIM"
assert data["known_physics_baseline"]["medium_claim"] is False
assert data["actual_measurements_supplied"] is False
assert data["null_result_proven"] is False
assert data["anomaly_proven"] is False
assert data["darkness_field_proven"] is False

for forbidden in [
    "DarknessFieldD_exists",
    "darkness_is_a_medium",
    "new_physics_detected",
    "matter_travels_inside_darkness_as_substance"
]:
    assert forbidden in data["forbidden_claims"]

theorem = data["conditional_theorem"]
assert theorem["name"] == "FiniteSensitivityDarknessCouplingExclusionTheorem"
assert "MeasuredNullDataset" in theorem["assumptions"]
assert "predicted residual norm exceeds tau" in theorem["conclusion"]

schema = data["dataset_schema_required"]
for key in ["dataset_id", "apparatus_id", "probe_id", "epsilon", "tau", "N_min", "trials"]:
    assert key in schema

print("DARK_REGION_DYNAMICS_NULL_TEST_OK")
print(f"artifact={p}")
print("status=CONDITIONAL_TEST_SCHEMA_ONLY_NO_NEW_PHYSICS_CLAIM")
print("next_admissible_object=ConcreteTrialDatasetWithMeasurementsOrStop")
