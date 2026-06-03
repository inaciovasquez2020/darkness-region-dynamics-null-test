import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
artifacts = sorted((ROOT / "artifacts" / "darkness").glob("external_comparison_archive_zip_intake_*.json"))
assert artifacts, "missing external comparison archive ZIP intake artifact"

data = json.loads(artifacts[-1].read_text())

assert data["object"] == "ExternalComparisonArchiveZipIntake"
assert data["status"] == "EXTERNAL_COMPARISON_ARCHIVE_SAVED_AND_EXTRACTED_NO_FRAME_FILES_DETECTED"
assert data["boundary_only"] is True
assert data["new_science"] is False
assert data["novelty_validated"] is False
assert data["real_measurement_dataset_supplied"] is False
assert data["external_comparison_dataset_downloaded"] is True
assert data["archive_local_path"] == "data/external_comparison/visha/downloads/Archive.zip"
assert data["extracted_local_path"] == "data/external_comparison/visha/extracted/Archive"
assert data["archive_size_bytes"] > 0
assert len(data["archive_sha256"]) == 64
assert data["zip_entry_count"] > 0
assert data["extracted_file_count"] > 0
assert data["contains_train_entries"] is True
assert data["contains_test_entries"] is True
assert data["contains_video_or_frame_like_files"] is False
assert data["usable_for_boundary_extraction_smoke_test"] is False

invalid = set(data["invalid_use"])
assert "new_science_dataset" in invalid
assert "novelty_validation" in invalid
assert "real_measured_darkness_boundary_claim" in invalid
assert "self_recorded_calibrated_measurement" in invalid

assert data["minimal_missing_object_for_new_science"] == "ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison"
assert data["next_admissible_object"] == "InspectExternalComparisonArchiveEntriesOrDownloadCorrectViShaFrameZipOrSupplySelfRecordedCalibratedRawVideo"

print("EXTERNAL_COMPARISON_ARCHIVE_ZIP_INTAKE_NO_FRAME_FILES_DETECTED_OK")
