import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

artifacts = sorted(
    (ROOT / "artifacts" / "darkness").glob(
        "download_or_reference_external_comparison_dataset_*.json"
    )
)
assert artifacts, "missing download/reference artifact"
data = json.loads(artifacts[-1].read_text())

assert data["object"] == "DownloadOrReferenceExternalComparisonDataset"
assert data["status"] == "EXTERNAL_COMPARISON_DATASETS_REFERENCED_NOT_MIRRORED"
assert data["boundary_only"] is True
assert data["new_science"] is False
assert data["novelty_validated"] is False
assert data["real_measurement_dataset_supplied"] is False
assert data["external_comparison_dataset_referenced"] is True
assert data["external_comparison_dataset_downloaded"] is False

ids = set(data["referenced_dataset_ids"])
assert "visha_video_shadow_dataset" in ids
assert "slow_flow_high_speed_optical_flow_dataset" in ids
assert "s_eo_geometry_aware_shadow_dataset" in ids
assert "nature_2026_optical_phase_singularity" in ids

invalid = set(data["invalid_use"])
assert "new_science_dataset" in invalid
assert "novelty_validation" in invalid
assert "real_measured_darkness_boundary_claim" in invalid
assert "prior_literature_surpassed" in invalid

assert data["minimal_missing_object_for_new_science"] == "ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison"
assert data["next_admissible_object"] == "SupplySelfRecordedCalibratedRawVideoOrObtainExternalExpertValidationReply"

manifests = sorted(
    (ROOT / "data" / "external_comparison" / "references").glob(
        "external_comparison_dataset_references_*.json"
    )
)
assert manifests, "missing reference manifest"
manifest = json.loads(manifests[-1].read_text())

assert manifest["object"] == "ExternalComparisonDatasetReferences"
assert manifest["status"] == "REFERENCED_NOT_MIRRORED"

manifest_ids = {item["id"] for item in manifest["datasets"]}
assert ids == manifest_ids

for item in manifest["datasets"]:
    assert item["official_page"].startswith("https://")
    assert item["local_status"].startswith("REFERENCE_ONLY")

notes = sorted(
    (ROOT / "data" / "external_comparison" / "references").glob(
        "DOWNLOAD_NOTES_*.md"
    )
)
assert notes, "missing download notes"
text = notes[-1].read_text()
assert "ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison" in text
assert "REFERENCED_NOT_MIRRORED" in text

print("DOWNLOAD_OR_REFERENCE_EXTERNAL_COMPARISON_DATASET_OK")
