#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

target_path = ROOT / "artifacts/darkness/real_measurement_acquisition_packet_target_2026_06_23.json"
doc_path = ROOT / "docs/status/REAL_MEASUREMENT_ACQUISITION_PACKET_TARGET_2026_06_23.md"
terminal_boundary_files = sorted((ROOT / "artifacts" / "darkness").glob("real_measurements_terminal_boundary_*.json"))

if not target_path.exists():
    raise SystemExit("MISSING_OBJECT := real_measurement_acquisition_packet_target_artifact")

if not doc_path.exists():
    raise SystemExit("MISSING_OBJECT := real_measurement_acquisition_packet_target_doc")

if not terminal_boundary_files:
    raise SystemExit("MISSING_OBJECT := real_measurements_terminal_boundary")

target = json.loads(target_path.read_text(encoding="utf-8"))
doc = doc_path.read_text(encoding="utf-8")
terminal = json.loads(terminal_boundary_files[-1].read_text(encoding="utf-8"))

assert terminal["status"] == "STOPPED_AT_REAL_MEASUREMENTS_BOUNDARY"
assert terminal["minimal_missing_object"] == "ConcreteTrialDatasetWithRealMeasurements"

assert target["object"] == "RealMeasurementAcquisitionPacketTarget"
assert target["status"] == "REAL_MEASUREMENT_ACQUISITION_PACKET_TARGET_ONLY"
assert target["theorem_closure"] is False
assert target["empirical_claim"] is False
assert target["minimal_missing_object"] == "ConcreteTrialDatasetWithRealMeasurements"

required_files = [
    "data/real_measurements/raw/light_occluder_boundary_trial_001.mov",
    "data/real_measurements/metadata/light_occluder_boundary_trial_001.metadata.json",
    "data/real_measurements/extracted/light_occluder_boundary_trial_001.boundary_observations.csv",
]

assert target["required_packet_files"] == required_files

required_checks = [
    "metadata dataset_id matches light_occluder_boundary_trial_001",
    "metadata raw_video_file points to the raw recording",
    "instrumentation frame_rate_hz is positive",
    "spatial calibration pixels_per_scale_unit is positive",
    "uncertainty model is explicit",
    "extracted observations contain at least two boundary observations",
    "boundary observation rows parse as numeric time and position values",
]

for token in required_checks:
    assert token in target["required_future_checks"], token
    assert token.replace("metadata ", "metadata `").split(" is ")[0].split(" points ")[0].split(" matches ")[0] or True

required_non_claims = [
    "does not supply a real measured trajectory dataset",
    "does not prove a real null result",
    "does not prove a real anomaly",
    "does not detect new physics",
    "does not assert DarknessFieldD exists",
    "does not assert darkness is a medium",
]

for token in required_non_claims:
    assert token in target["non_claims"], token

required_doc_tokens = [
    "Status: `REAL_MEASUREMENT_ACQUISITION_PACKET_TARGET_ONLY`",
    "RealMeasurementAcquisitionPacketTarget",
    "`ConcreteTrialDatasetWithRealMeasurements`",
    "`data/real_measurements/raw/light_occluder_boundary_trial_001.mov`",
    "`data/real_measurements/metadata/light_occluder_boundary_trial_001.metadata.json`",
    "`data/real_measurements/extracted/light_occluder_boundary_trial_001.boundary_observations.csv`",
    "`STATUS=RAW_REAL_MEASUREMENT_INPUTS_MISSING`",
    "`MINIMAL_MISSING_OBJECT=RawRealMeasurementRecording`",
    "does not supply a real measured trajectory dataset",
    "does not prove a real null result",
    "does not prove a real anomaly",
    "does not detect new physics",
    "does not assert `DarknessFieldD` exists",
    "does not assert darkness is a medium",
]

for token in required_doc_tokens:
    if token not in doc:
        raise SystemExit(f"missing doc token: {token}")

result = subprocess.run(
    [sys.executable, "tools/check_real_measurement_inputs.py"],
    cwd=ROOT,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

assert result.returncode == 2, result.stdout + result.stderr
assert "STATUS=RAW_REAL_MEASUREMENT_INPUTS_MISSING" in result.stdout
assert "MINIMAL_MISSING_OBJECT=RawRealMeasurementRecording" in result.stdout
assert "REAL_MEASUREMENT_INPUTS_PRESENT_OK" not in result.stdout

expected = target["current_expected_checker_status"]
assert expected["tool"] == "tools/check_real_measurement_inputs.py"
assert expected["exit_code"] == 2
assert expected["status_line"] in result.stdout
assert expected["minimal_missing_object_line"] in result.stdout

print("REAL_MEASUREMENT_ACQUISITION_PACKET_TARGET_OK")
