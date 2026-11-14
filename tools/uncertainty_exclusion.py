"""Conservative deterministic null-test exclusion; never physical validation."""
from decimal import Decimal, InvalidOperation

class InvalidMeasurement(ValueError):
    pass

def finite_nonnegative(value, name):
    if isinstance(value, bool):
        raise InvalidMeasurement(name + ': boolean is not a measurement')
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise InvalidMeasurement(name + ': not numeric')
    if not d.is_finite() or d < 0:
        raise InvalidMeasurement(name + ': expected finite, nonnegative')
    return d

def classify_exclusion(residual_norm, predicted_norm, tolerance, error_bound):
    """delta bounds ||p-r|| under candidate compatibility, not merely detector noise."""
    r = finite_nonnegative(residual_norm, 'residual_norm')
    p = finite_nonnegative(predicted_norm, 'predicted_norm')
    tau = finite_nonnegative(tolerance, 'tolerance')
    delta = finite_nonnegative(error_bound, 'error_bound')
    if r > tau:
        return 'NOT_A_NULL_OBSERVATION'
    if p > tau + delta:
        return 'EXCLUDED_CONDITIONALLY'
    return 'INSUFFICIENT_SENSITIVITY'

def validate_matter_packet(packet):
    """Structural intake gate only; not authenticating a real experiment."""
    if not isinstance(packet, dict) or packet.get('experiment_type') != 'MATTER_COUPLING':
        raise InvalidMeasurement('MATTER_COUPLING experiment required')
    if packet.get('synthetic') is not False:
        raise InvalidMeasurement('synthetic data forbidden for real-data intake')
    for field in ('dataset_id', 'apparatus_id', 'probe_id', 'known_field_model_id',
                  'calibration_record_id', 'uncertainty_provenance', 'raw_data_reference'):
        if not isinstance(packet.get(field), str) or not packet[field].strip():
            raise InvalidMeasurement('missing ' + field)
    trials = packet.get('paired_trials')
    if not isinstance(trials, list) or not trials:
        raise InvalidMeasurement('paired_trials required')
    ids = set()
    for trial in trials:
        if not isinstance(trial, dict):
            raise InvalidMeasurement('trial must be object')
        ident = trial.get('trial_id')
        if not isinstance(ident, str) or not ident.strip() or ident in ids:
            raise InvalidMeasurement('invalid/repeated trial_id')
        ids.add(ident)
        if trial.get('matched_known_fields') is not True:
            raise InvalidMeasurement('known fields not matched')
        if trial.get('flux_dark_below_threshold') is not True or trial.get('flux_light_at_or_above_threshold') is not True:
            raise InvalidMeasurement('calibrated photon-flux controls required')
        samples = trial.get('paired_trajectory_samples')
        if not isinstance(samples, list) or len(samples) < 2:
            raise InvalidMeasurement('two paired trajectory samples required')
        previous = None
        for sample in samples:
            if not isinstance(sample, dict):
                raise InvalidMeasurement('sample must be object')
            t = finite_nonnegative(sample.get('time_s'), 'time_s')
            if previous is not None and t <= previous:
                raise InvalidMeasurement('sample times must increase')
            previous = t
            for field in ('dark_position_m', 'light_position_m', 'known_field_correction_m'):
                if isinstance(sample.get(field), bool):
                    raise InvalidMeasurement('boolean ' + field)
                try:
                    value = Decimal(str(sample.get(field)))
                except (ValueError, InvalidOperation):
                    raise InvalidMeasurement('nonnumeric ' + field)
                if not value.is_finite():
                    raise InvalidMeasurement('nonfinite ' + field)
            finite_nonnegative(sample.get('difference_error_bound_m'), 'difference_error_bound_m')
    return 'STRUCTURAL_INTAKE_ONLY_NOT_PHYSICAL_VALIDATION'
