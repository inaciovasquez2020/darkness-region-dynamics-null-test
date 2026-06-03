import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

artifacts = sorted((ROOT / "artifacts" / "darkness").glob("raw_real_measurement_recording_protocol_*.json"))
assert artifacts, "missing raw real measurement recording protocol artifact"

data = json.loads(artifacts[-1].read_text())

assert data["object"] == "RawRealMeasurementRecordingProtocol"
assert data["status"] == "PROTOCOL_ONLY_RAW_VIDEO_NOT_SUPPLIED"
assert data["boundary_only"] is True
assert data["new_science"] is False
assert data["novelty_validated"] is False
assert data["real_measurement_dataset_supplied"] is False
assert data["next_admissible_object"] == "RawRealMeasurementRecording"

assert (ROOT / "docs" / "protocols").exists()
assert (ROOT / "data" / "real_measurements" / "raw").exists()
assert (ROOT / "data" / "real_measurements" / "metadata").exists()
assert (ROOT / "data" / "real_measurements" / "extracted").exists()

templates = sorted((ROOT / "data" / "real_measurements" / "metadata").glob("raw_video_metadata_template_*.json"))
assert templates, "missing metadata template"
template = json.loads(templates[-1].read_text())
assert template["dataset_id"] == "light_occluder_boundary_trial_001"
assert template["raw_video_file"] == "data/real_measurements/raw/light_occluder_boundary_trial_001.mov"

csv_templates = sorted((ROOT / "data" / "real_measurements" / "extracted").glob("manual_boundary_observations_template_*.csv"))
assert csv_templates, "missing observation template"
assert "frame_index,t_seconds,boundary_x_pixels" in csv_templates[-1].read_text()

print("RAW_REAL_MEASUREMENT_RECORDING_PROTOCOL_OK")
