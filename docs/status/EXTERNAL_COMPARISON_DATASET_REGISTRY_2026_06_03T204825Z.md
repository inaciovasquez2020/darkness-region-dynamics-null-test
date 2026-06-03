# External comparison dataset registry

Generated: 2026_06_03T204825Z

Status:
COMPARISON_DATASETS_IDENTIFIED_REAL_MEASUREMENT_NOT_SUPPLIED

Current boundary:
- new_science=false
- novelty_validated=false
- real_measurement_dataset_supplied=false

Candidate comparison datasets:
- Nature 2026 optical phase-singularity supplementary video: prior-art baseline only.
- ViSha video shadow dataset: shadow-boundary extraction benchmark.
- Complex-world shadow detection dataset: image shadow segmentation baseline.
- S-EO geometry-aware shadow dataset: geometry-aware shadow comparison.
- Slow Flow high-speed optical-flow dataset: velocity-extraction validation.

Best repository path:
1. Use public datasets for extraction/baseline validation.
2. Use self-recorded calibrated video for the actual real-measurement dataset.
3. Compare against geometric projection, shadow kinematics, optical phase-singularity literature, and null-noise baselines.

Minimal missing object for new science:
ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison
