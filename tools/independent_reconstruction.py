"""Comparison of independently identified estimators: not a physical evidence gate."""
from decimal import Decimal, InvalidOperation
from tools.uncertainty_exclusion import InvalidMeasurement, finite_nonnegative

def assess_independent_reconstructions(packet):
    if not isinstance(packet, dict) or type(packet.get('synthetic')) is not bool:
        raise InvalidMeasurement('packet and synthetic boolean required')
    if packet.get('observable_type') not in ('SHADOW_BOUNDARY', 'MATTER_TRAJECTORY'):
        raise InvalidMeasurement('observable type required')
    items = packet.get('reconstructions')
    if not isinstance(items, list) or len(items) != 2:
        raise InvalidMeasurement('exactly two reconstructions required')
    ids, values = [], []
    for item in items:
        if not isinstance(item, dict):
            raise InvalidMeasurement('invalid reconstruction')
        name, provenance = item.get('algorithm_id'), item.get('provenance_id')
        if not all(isinstance(v, str) and v.strip() for v in (name, provenance)):
            raise InvalidMeasurement('algorithm and provenance IDs required')
        ids.append((name, provenance))
        value = item.get('estimated_observable')
        if isinstance(value, bool):
            raise InvalidMeasurement('boolean estimate')
        try:
            d = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise InvalidMeasurement('invalid estimate')
        if not d.is_finite():
            raise InvalidMeasurement('nonfinite estimate')
        values.append(d)
    if ids[0][0] == ids[1][0] or ids[0][1] == ids[1][1]:
        raise InvalidMeasurement('identifiers must differ')
    epsilon = finite_nonnegative(packet.get('agreement_tolerance'), 'agreement_tolerance')
    disagreement = abs(values[0] - values[1])
    return {'verdict': 'ALGORITHM_AGREEMENT_ONLY' if disagreement <= epsilon else 'ALGORITHM_DISAGREEMENT',
            'absolute_disagreement': str(disagreement), 'agreement_tolerance': str(epsilon),
            'physical_validation': False, 'independence_verified': False,
            'common_mode_bias_excluded': False}
