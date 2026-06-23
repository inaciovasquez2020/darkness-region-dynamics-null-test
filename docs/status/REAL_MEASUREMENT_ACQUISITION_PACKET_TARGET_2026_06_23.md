# Real Measurement Acquisition Packet Target

Status: `REAL_MEASUREMENT_ACQUISITION_PACKET_TARGET_ONLY`

Target object: `RealMeasurementAcquisitionPacketTarget`

This record names the bounded real-measurement acquisition packet required before this repository can check a real null result or real anomaly.

## Minimal missing object

`ConcreteTrialDatasetWithRealMeasurements`

## Required packet files

- `data/real_measurements/raw/light_occluder_boundary_trial_001.mov`
- `data/real_measurements/metadata/light_occluder_boundary_trial_001.metadata.json`
- `data/real_measurements/extracted/light_occluder_boundary_trial_001.boundary_observations.csv`

## Required future checks

- metadata `dataset_id` matches `light_occluder_boundary_trial_001`
- metadata `raw_video_file` points to the raw recording
- instrumentation `frame_rate_hz` is positive
- spatial calibration `pixels_per_scale_unit` is positive
- uncertainty model is explicit
- extracted observations contain at least two boundary observations
- boundary observation rows parse as numeric time and position values

## Current checker expectation

The current expected result of `tools/check_real_measurement_inputs.py` is a stopped missing-input status:

- `STATUS=RAW_REAL_MEASUREMENT_INPUTS_MISSING`
- `MINIMAL_MISSING_OBJECT=RawRealMeasurementRecording`

## Boundary

This target does not supply a real measured trajectory dataset.

This target does not prove a real null result.

This target does not prove a real anomaly.

This target does not detect new physics.

This target does not assert `DarknessFieldD` exists.

This target does not assert darkness is a medium.
