from pathlib import Path
import json
import csv
import sys

ROOT = Path(__file__).resolve().parents[1]

raw = ROOT / "data/real_measurements/raw/light_occluder_boundary_trial_001.mov"
metadata = ROOT / "data/real_measurements/metadata/light_occluder_boundary_trial_001.metadata.json"
observations = ROOT / "data/real_measurements/extracted/light_occluder_boundary_trial_001.boundary_observations.csv"

missing = [str(p.relative_to(ROOT)) for p in [raw, metadata, observations] if not p.exists()]

if missing:
    print("STATUS=RAW_REAL_MEASUREMENT_INPUTS_MISSING")
    print("MINIMAL_MISSING_OBJECT=RawRealMeasurementRecording")
    print("MISSING_FILES=" + ",".join(missing))
    sys.exit(2)

data = json.loads(metadata.read_text())
assert data["dataset_id"] == "light_occluder_boundary_trial_001"
assert data["raw_video_file"] == "data/real_measurements/raw/light_occluder_boundary_trial_001.mov"
assert data["instrumentation"]["frame_rate_hz"] > 0
assert data["spatial_calibration"]["pixels_per_scale_unit"] > 0
assert data["uncertainty_model"]["position_uncertainty_pixels"] >= 0
assert data["uncertainty_model"]["time_uncertainty_seconds"] >= 0

rows = list(csv.DictReader(observations.read_text().splitlines()))
assert len(rows) >= 2, "need at least two boundary observations"

for row in rows:
    float(row["t_seconds"])
    float(row["boundary_x_pixels"])
    float(row["boundary_y_pixels"])
    float(row["position_uncertainty_pixels"])

print("REAL_MEASUREMENT_INPUTS_PRESENT_OK")
