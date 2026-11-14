# Distinct experimental targets

SHADOW_BOUNDARY: a camera/occluder trial measures an optical intensity boundary; its speed is not a material probe trajectory and cannot establish a force on matter.

MATTER_COUPLING: requires time-aligned dark/light calibrated probe trajectories, raw records, flux controls, matched known fields, correction K, an explicit uncertainty budget and repeated trials. The software intake checks structure only, not provenance authenticity.

## Deterministic exclusion theorem

Let r be the observed corrected residual and p the candidate's predicted residual in a normed space. Under a *justified* discrepancy bound ||p-r|| <= delta for any compatible candidate, and an observed null ||r|| <= tau, the triangle inequality implies ||p|| <= tau+delta. Therefore a candidate satisfying ||p|| > tau+delta is incompatible with the null and bound. The older rule ||p|| > tau is insufficient when delta > 0.

Delta must cover model discrepancy and experimental uncertainty; a standard deviation is **not** automatically a deterministic bound. A statistical exclusion instead requires a predeclared confidence procedure with coverage and nuisance-parameter treatment.

No real physical exclusion follows without authenticated measurements and independently justified calibration, uncertainties, and controls. Synthetic data and schema-only checks are never physical evidence.
