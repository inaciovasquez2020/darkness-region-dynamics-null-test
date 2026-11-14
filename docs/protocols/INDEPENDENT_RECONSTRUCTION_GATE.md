# Independent reconstruction: method consistency only

Apply separately to SHADOW_BOUNDARY and MATTER_TRAJECTORY observables. Two differently identified algorithms and provenance records must estimate the same observable in consistent units and coordinates. The API checks IDs and finite scalar estimates but cannot verify independence, calibration, matching preprocessing or provenance.

The rule abs(theta1-theta2) <= epsilon establishes estimator agreement only. Shared calibration and model biases can make both estimates wrong. Thus the output always reports physical_validation=false, independence_verified=false and common_mode_bias_excluded=false.

Published M87* reconstruction, DES lensing, Euclid catalogs and collider dark-sector studies are methodological references, **not** verified laboratory darkness-coupling measurements. They must not be passed as evidence that darkness is a medium or DarknessFieldD exists.
