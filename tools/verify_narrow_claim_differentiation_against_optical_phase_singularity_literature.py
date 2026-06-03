import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
artifacts = sorted(
    (ROOT / "artifacts" / "darkness").glob(
        "narrow_claim_differentiation_against_optical_phase_singularity_literature_*.json"
    )
)
assert artifacts, "missing narrow claim differentiation artifact"

data = json.loads(artifacts[-1].read_text())

assert data["object"] == "NarrowClaimDifferentiationAgainstOpticalPhaseSingularityLiterature"
assert data["status"] == "NARROW_DIFFERENTIATION_CREATED_NOVELTY_NOT_VALIDATED"
assert data["boundary_only"] is True
assert data["new_science"] is False
assert data["novelty_validated"] is False
assert data["real_measurement_dataset_supplied"] is False
assert data["external_expert_validation_supplied"] is False
assert data["broad_claim_blocked"] is True

prior = {item["id"] for item in data["prior_art_anchors"]}
assert "nature_2026_phase_singularity_ensembles" in prior
assert "scientific_american_2026_darkness_framing" in prior
assert "nye_berry_1974_wave_dislocations" in prior

invalid = set(data["invalid_claims"])
assert "new science" in invalid
assert "novel physics" in invalid
assert "speed of darkness discovered" in invalid
assert "relativity violation" in invalid
assert "real measured effect established" in invalid

claim_rows = data["claim_boundary_table"]
row_by_claim = {row["claim"]: row for row in claim_rows}

assert row_by_claim["Dark points can appear superluminal"]["status"] == "PRIOR_ART"
assert row_by_claim["Dark points can appear superluminal"]["repository_may_claim"] is False

assert row_by_claim["Boundary-only schema and null-test harness"]["status"] == "CURRENT_REPOSITORY_ARTIFACT"
assert row_by_claim["Boundary-only schema and null-test harness"]["repository_may_claim"] is True

assert row_by_claim["New measured deviation from prior baselines"]["status"] == "BLOCKED_DATASET_NOT_SUPPLIED"
assert row_by_claim["New measured deviation from prior baselines"]["repository_may_claim"] is False

future = data["possible_future_novelty_claim"]
assert future["status"] == "CONDITIONAL_ON_NEW_INPUT"
assert "ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison" in future["requires"]
assert "ExternalExpertValidationOrIndependentReplication" in future["requires"]

assert data["next_admissible_object"] == "ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparisonOrExternalExpertValidationReply"
assert data["minimal_missing_object"] == "ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison"

print("NARROW_CLAIM_DIFFERENTIATION_AGAINST_OPTICAL_PHASE_SINGULARITY_LITERATURE_OK")
