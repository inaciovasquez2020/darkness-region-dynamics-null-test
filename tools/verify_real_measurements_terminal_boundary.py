#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = sorted((ROOT / "artifacts" / "darkness").glob("real_measurements_terminal_boundary_*.json"))

if not files:
    raise SystemExit("NO_REAL_MEASUREMENTS_TERMINAL_BOUNDARY_FOUND")

p = files[-1]
data = json.loads(p.read_text(encoding="utf-8"))

assert data["object"] == "RealMeasurementsTerminalBoundary"
assert data["status"] == "STOPPED_AT_REAL_MEASUREMENTS_BOUNDARY"
assert data["minimal_missing_object"] == "ConcreteTrialDatasetWithRealMeasurements"
assert data["next_admissible_object"] == "SupplyConcreteTrialDatasetWithRealMeasurementsOrStop"

for forbidden in [
    "real_null_result",
    "real_anomaly",
    "new_physics_detected",
    "DarknessFieldD_exists",
    "darkness_is_a_medium"
]:
    assert forbidden in data["not_proven"]

state = data["verified_repository_state"]
assert state["no_claims_package_committed"] is True
assert state["repository_hygiene_committed"] is True
assert state["pycache_removed"] is True
assert state["gitignore_added"] is True

print("REAL_MEASUREMENTS_TERMINAL_BOUNDARY_OK")
print(f"artifact={p}")
print("status=STOPPED_AT_REAL_MEASUREMENTS_BOUNDARY")
print("minimal_missing_object=ConcreteTrialDatasetWithRealMeasurements")
