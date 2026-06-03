# Real Measurement Intake Schema

Status: `REAL_MEASUREMENT_INTAKE_SCHEMA_ONLY_NO_DATA_SUPPLIED`

This document defines the required input structure for real dark-region traversal measurements.

## Boundary

No real measurements are supplied here.

Therefore:

- no real null result is proven,
- no anomaly is proven,
- no DarknessField is proven,
- no new physics is detected,
- no darkness-medium claim is made.

## Required real-data object

`ConcreteTrialDatasetWithRealMeasurements`

The object must include:

- calibrated photon flux fields,
- matched environment logs,
- dark-region trajectory arrays,
- illuminated-control trajectory arrays,
- known-field correction arrays,
- computed residuals,
- residual norms,
- null verdicts,
- reproducibility count.

## Valid downstream theorem

Only after real measurements are supplied:

`FiniteSensitivityDarknessCouplingExclusionTheorem`

may exclude tested couplings whose predicted residual exceeds apparatus tolerance `τ`.
