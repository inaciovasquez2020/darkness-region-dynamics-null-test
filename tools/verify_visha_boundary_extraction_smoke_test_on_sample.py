import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
artifacts = sorted((ROOT / "artifacts" / "darkness").glob("visha_boundary_extraction_smoke_test_on_sample_*.json"))
assert artifacts, "missing ViSha boundary extraction smoke-test artifact"

data = json.loads(artifacts[-1].read_text())

assert data["object"] == "ViShaBoundaryExtractionSmokeTestOnSample"
assert data["status"] == "VISHA_BOUNDARY_EXTRACTION_SMOKE_TEST_ON_SAMPLE_PASSED_EXTERNAL_COMPARISON_ONLY"
assert data["boundary_only"] is True
assert data["new_science"] is False
assert data["novelty_validated"] is False
assert data["real_measurement_dataset_supplied"] is False
assert data["external_comparison_dataset_sample_extracted"] is True
assert data["full_dataset_extraction_completed"] is False

counts = data["input_counts"]
assert counts["train_images"] + counts["test_images"] > 0
assert counts["train_labels"] + counts["test_labels"] > 0

assert data["sample_pair_count"] > 0
assert len(data["pair_results"]) == data["sample_pair_count"]

for result in data["pair_results"]:
    assert result["image"].startswith("data/external_comparison/visha/extracted/sample_frames/")
    assert result["label"].startswith("data/external_comparison/visha/extracted/sample_frames/")
    assert len(result["image_sha256"]) == 64
    assert len(result["label_sha256"]) == 64

if data["pil_available"]:
    assert data["boundary_stats_count"] > 0

invalid = set(data["invalid_use"])
assert "new_science_dataset" in invalid
assert "novelty_validation" in invalid
assert "real_measured_darkness_boundary_claim" in invalid
assert "self_recorded_calibrated_measurement" in invalid
assert "full_dataset_benchmark_claim" in invalid

assert data["minimal_missing_object_for_new_science"] == "ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison"
assert data["next_admissible_object"] == "SupplySelfRecordedCalibratedRawVideoOrObtainExternalExpertValidationReply"

print("VISHA_BOUNDARY_EXTRACTION_SMOKE_TEST_ON_SAMPLE_OK")
