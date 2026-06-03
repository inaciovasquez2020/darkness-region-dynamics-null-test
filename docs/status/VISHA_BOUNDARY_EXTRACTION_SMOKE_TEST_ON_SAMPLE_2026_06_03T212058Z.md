# ViSha boundary extraction smoke test on sample

Generated: 2026_06_03T212058Z

Status:
VISHA_BOUNDARY_EXTRACTION_SMOKE_TEST_ON_SAMPLE_PASSED_EXTERNAL_COMPARISON_ONLY

Current claim:
- external_comparison_dataset_sample_extracted=true
- full_dataset_extraction_completed=false
- new_science=false
- novelty_validated=false
- real_measurement_dataset_supplied=false

Input counts:
- train_images=5
- train_labels=5
- test_images=5
- test_labels=5

Smoke-test result:
- sample_pair_count=10
- pil_available=true
- dimension_checked_count=10
- dimension_match_count=10
- boundary_stats_count=10

Valid use:
- boundary-extraction smoke test on external comparison sample
- pipeline sanity check
- shadow-mask processing check

Invalid use:
- new science dataset
- novelty validation
- real measured darkness-boundary claim
- self-recorded calibrated measurement
- full dataset benchmark claim

Minimal missing object for new science:
ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison

Next admissible object:
SupplySelfRecordedCalibratedRawVideoOrObtainExternalExpertValidationReply
