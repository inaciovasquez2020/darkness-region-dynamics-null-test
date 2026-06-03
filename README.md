# Darkness Region Dynamics Null Test

Status: `CONDITIONAL_TEST_SCHEMA_ONLY_NO_NEW_PHYSICS_CLAIM`

## Purpose

This repository records a bounded null-test schema for dark-region matter traversal.

## Known physics baseline

Matter can move through spacetime regions with low detected photon flux.

## Valid claim

Controlled dark-region traversal experiments can exclude measurable matter-coupling effects above tolerance `τ` within a specified apparatus class.

## Not claimed

- Darkness is a medium.
- A `DarknessFieldD` exists.
- `T_D^{μν} ≠ 0`.
- New physics has been detected.
- A real null result has been measured.
- A real anomaly has been measured.

## Conditional theorem

If a measured dataset satisfies:

- photon flux below threshold in `U_dark`,
- photon flux at or above threshold in `U_light`,
- matched known fields,
- calibrated probe and apparatus,
- residuals computed as `R_m = γ_dark - γ_light - K`,
- all residual norms satisfy `||R_m|| ≤ τ`,
- reproducibility count satisfies `N ≥ N_min`,

then all tested couplings in `C_D` whose predicted residual exceeds `τ` are excluded for that apparatus class.

## Boundary

This is a schema, synthetic-data template, and no-claims package only.
