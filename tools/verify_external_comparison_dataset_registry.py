import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
artifacts = sorted((ROOT / "artifacts" / "darkness").glob("external_comparison_dataset_registry_*.json"))
assert artifacts, "missing external comparison dataset registry"

data = json.loads(artifacts[-1].read_text())

assert data["object"] == "ExternalComparisonDatasetRegistry"
assert data["status"] == "COMPARISON_DATASETS_IDENTIFIED_REAL_MEASUREMENT_NOT_SUPPLIED"
assert data["boundary_only"] is True
assert data["new_science"] is False
assert data["novelty_validated"] is False
assert data["real_measurement_dataset_supplied"] is False

ids = {d["id"] for d in data["datasets"]}
assert "nature_2026_optical_phase_singularity_supplementary_video" in ids
assert "visha_video_shadow_dataset" in ids
assert "complex_world_shadow_detection_dataset" in ids
assert "s_eo_geometry_aware_shadow_dataset" in ids
assert "slow_flow_high_speed_optical_flow_dataset" in ids

assert data["minimal_missing_object_for_new_science"] == "ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison"
assert data["next_admissible_object"] == "DownloadOrReferenceExternalComparisonDatasetOrSupplyConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison"

print("EXTERNAL_COMPARISON_DATASET_REGISTRY_OK")
