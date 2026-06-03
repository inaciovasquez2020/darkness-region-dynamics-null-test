import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
artifacts = sorted((ROOT / "artifacts" / "darkness").glob("sample_only_visha_nested_archive_extraction_*.json"))
assert artifacts, "missing sample-only ViSha extraction artifact"

data = json.loads(artifacts[-1].read_text())

assert data["object"] == "SampleOnlyViShaNestedArchiveExtraction"
assert data["status"] == "SAMPLE_ONLY_EXTRACTION_COMPLETED_EXTERNAL_COMPARISON_ONLY"
assert data["boundary_only"] is True
assert data["new_science"] is False
assert data["novelty_validated"] is False
assert data["real_measurement_dataset_supplied"] is False
assert data["external_comparison_dataset_downloaded"] is True
assert data["external_comparison_dataset_sample_extracted"] is True
assert data["full_extraction_completed"] is False
assert data["usable_for_boundary_extraction_smoke_test"] is True

required = {"train_images", "train_labels", "test_images", "test_labels"}
assert set(data["source_nested_zips"]) == required
assert set(data["source_nested_zip_sha256"]) == required

for digest in data["source_nested_zip_sha256"].values():
    assert isinstance(digest, str)
    assert len(digest) == 64

assert data["total_usable_entries"] > 0
assert data["total_sample_extracted_files"] > 0

sample_root = ROOT / data["sample_root"]
assert sample_root.exists()
assert any(p.is_file() for p in sample_root.rglob("*"))

invalid = set(data["invalid_use"])
assert "new_science_dataset" in invalid
assert "novelty_validation" in invalid
assert "real_measured_darkness_boundary_claim" in invalid
assert "self_recorded_calibrated_measurement" in invalid
assert "full_dataset_extraction_claim" in invalid

assert data["minimal_missing_object_for_new_science"] == "ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison"
assert data["next_admissible_object"] == "BuildViShaBoundaryExtractionSmokeTestOnSampleOrSupplySelfRecordedCalibratedRawVideo"

print("SAMPLE_ONLY_VISHA_NESTED_ARCHIVE_EXTRACTION_OK")
