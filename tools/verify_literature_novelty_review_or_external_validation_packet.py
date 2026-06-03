import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
artifacts = sorted((ROOT / "artifacts" / "darkness").glob("literature_novelty_review_or_external_validation_packet_*.json"))
assert artifacts, "missing literature novelty review packet artifact"

path = artifacts[-1]
data = json.loads(path.read_text())

assert data["object"] == "LiteratureNoveltyReviewOrExternalExpertValidation"
assert data["status"] == "REQUEST_PACKET_CREATED_REVIEW_NOT_COMPLETED"
assert data["boundary_only"] is True
assert data["new_science"] is False
assert data["novelty_validated"] is False
assert data["new_science_requires"] == "ConcreteTrialDatasetWithRealMeasurements"
assert data["novelty_claim_requires"] == "CompletedLiteratureNoveltyReviewOrExternalExpertValidation"
assert data["next_admissible_object"] == "CompletedLiteratureNoveltyReviewOrExternalExpertValidation"

required = {
    "repository_schema": True,
    "synthetic_null_dataset": True,
    "real_measurement_intake_schema": True,
    "terminal_boundary": True,
}
assert data["valid_current_status"] == required

queries = data["literature_review_queries"]
assert len(queries) >= 6
assert any("shadow boundary" in q for q in queries)
assert any("extinction front" in q for q in queries)
assert any("causal speed" in q for q in queries)

forbidden = set(data["forbidden_claims_until_completion"])
assert "new science" in forbidden
assert "novel discovery" in forbidden
assert "physical effect validated" in forbidden

drafts = sorted((ROOT / "drafts").glob("literature_novelty_review_or_external_validation_request_*.md"))
assert drafts, "missing review request draft"
draft_text = drafts[-1].read_text()
assert "REQUEST_PACKET_CREATED_REVIEW_NOT_COMPLETED" in draft_text
assert "CompletedLiteratureNoveltyReviewOrExternalExpertValidation" in draft_text

print("LITERATURE_NOVELTY_REVIEW_OR_EXTERNAL_VALIDATION_PACKET_OK")
