import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

artifacts = sorted((ROOT / "artifacts" / "darkness").glob("real_measurement_acquisition_and_baseline_comparison_target_*.json"))
assert artifacts, "missing target artifact"

data = json.loads(artifacts[-1].read_text())

assert data["object"] == "RealMeasurementAcquisitionAndBaselineComparisonTarget"
assert data["status"] == "TARGET_DEFINED_DATASET_NOT_SUPPLIED"
assert data["boundary_only"] is True
assert data["new_science"] is False
assert data["novelty_validated"] is False
assert data["real_measurement_dataset_supplied"] is False
assert data["minimal_missing_object_for_new_science"] == "ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison"
assert data["next_admissible_object"] == "ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison"

required = set(data["required_dataset_fields"])
for key in [
    "raw_data_files",
    "timestamp_calibration",
    "spatial_calibration",
    "baseline_models",
    "measured_boundary_velocity_series",
    "negative_control",
    "comparison_result",
    "reproducibility_script",
]:
    assert key in required

baselines = set(data["baseline_models_required"])
assert "geometric_projection_baseline" in baselines
assert "optical_phase_singularity_baseline" in baselines
assert "shadow_boundary_kinematic_baseline" in baselines
assert "null_noise_baseline" in baselines

gate = data["new_science_gate"]
assert gate["replicates_known_dark_point_or_shadow_motion"]["new_science"] is False
assert gate["detects_real_measured_deviation_from_baseline"]["new_science"] == "conditional"
assert gate["detects_new_quantitative_law_with_reproducible_real_data"]["new_science"] == "plausible"

schema = ROOT / "schemas" / "concrete_trial_dataset_with_baseline_comparison.schema.json"
assert schema.exists(), "missing schema"
schema_data = json.loads(schema.read_text())
assert schema_data["title"] == "ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison"

templates = sorted((ROOT / "data" / "real_measurements").glob("concrete_trial_dataset_template_*.json"))
assert templates, "missing dataset template"
template = json.loads(templates[-1].read_text())
assert template["raw_data_files"] == ["MISSING_RAW_REAL_MEASUREMENT_FILE"]
assert template["comparison_result"]["interpretation"] == "REPLICATION_OR_EDUCATIONAL_ARTIFACT"

print("REAL_MEASUREMENT_ACQUISITION_AND_BASELINE_COMPARISON_TARGET_OK")
