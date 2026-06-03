import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
artifacts = sorted((ROOT / "artifacts" / "darkness").glob("annotated_literature_review_*.json"))
assert artifacts, "missing annotated literature review artifact"

data = json.loads(artifacts[-1].read_text())

assert data["object"] == "AnnotatedLiteratureReview"
assert data["status"] == "OVERLAP_FOUND_NOVELTY_NOT_VALIDATED"
assert data["boundary_only"] is True
assert data["new_science"] is False
assert data["novelty_validated"] is False
assert data["real_measurement_dataset_supplied"] is False
assert data["review_decision"] == "DO_NOT_CLAIM_NEW_SCIENCE_OR_NOVELTY"

sources = data["annotated_sources"]
assert len(sources) >= 6

ids = {source["id"] for source in sources}
assert "nature_2026_phase_singularities" in ids
assert "scientific_american_2026_darkness_framing" in ids
assert "nye_berry_1974_wave_dislocations" in ids
assert "nye_1981_motion_structure_dislocations" in ids
assert "indebetouw_1993_optical_vortices" in ids
assert "freund_2000_optical_vortex_trajectories" in ids

invalid = set(data["invalid_claims"])
assert "new science" in invalid
assert "novel discovery" in invalid
assert "physical darkness propagation validated" in invalid
assert "external novelty validated" in invalid

assert data["send_external_expert_validation_request"]["status"] == "BLOCKED_RECIPIENT_NOT_SUPPLIED"
assert data["send_external_expert_validation_request"]["minimal_missing_object"] == "ExternalExpertRecipient"
assert data["supply_concrete_trial_dataset"]["status"] == "BLOCKED_DATASET_NOT_SUPPLIED"
assert data["supply_concrete_trial_dataset"]["minimal_missing_object"] == "ConcreteTrialDatasetWithRealMeasurements"

drafts = sorted((ROOT / "drafts").glob("external_expert_validation_request_*.md"))
assert drafts, "missing external expert validation draft"
draft = drafts[-1].read_text()
assert "Request for novelty check" in draft
assert "No new-science or novelty claim is currently valid" in draft

print("ANNOTATED_LITERATURE_REVIEW_OK")
