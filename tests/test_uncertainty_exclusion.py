import unittest
from tools.uncertainty_exclusion import classify_exclusion, validate_matter_packet, InvalidMeasurement

class ExclusionTests(unittest.TestCase):
    def test_excluded(self):
        self.assertEqual(classify_exclusion('0.9','1.3','1','0.25'),'EXCLUDED_CONDITIONALLY')
    def test_old_rule_counterexample(self):
        self.assertEqual(classify_exclusion('0.9','1.1','1','0.25'),'INSUFFICIENT_SENSITIVITY')
    def test_strict_boundary(self):
        self.assertEqual(classify_exclusion('0','1.25','1','0.25'),'INSUFFICIENT_SENSITIVITY')
    def test_non_null(self):
        self.assertEqual(classify_exclusion('1.01','100','1','0.25'),'NOT_A_NULL_OBSERVATION')
    def test_invalid_numbers(self):
        for x in ('NaN','Infinity','-1',True):
            with self.subTest(x=x), self.assertRaises(InvalidMeasurement):
                classify_exclusion('0','2','1',x)
    def packet(self):
        def sample(t):
            return dict(time_s=t,dark_position_m='1',light_position_m='1',
                        known_field_correction_m='0',difference_error_bound_m='0.01')
        return dict(experiment_type='MATTER_COUPLING',synthetic=False,dataset_id='d',
            apparatus_id='a',probe_id='p',known_field_model_id='k',calibration_record_id='c',
            uncertainty_provenance='traceable bound',raw_data_reference='instrument-id',
            paired_trials=[dict(trial_id='t1',matched_known_fields=True,
                flux_dark_below_threshold=True,flux_light_at_or_above_threshold=True,
                paired_trajectory_samples=[sample('0'),sample('1')])])
    def test_structural_only(self):
        self.assertEqual(validate_matter_packet(self.packet()),
            'STRUCTURAL_INTAKE_ONLY_NOT_PHYSICAL_VALIDATION')
    def test_shadow_rejected(self):
        p=self.packet();p['experiment_type']='SHADOW_BOUNDARY'
        with self.assertRaises(InvalidMeasurement):validate_matter_packet(p)
    def test_synthetic_rejected(self):
        p=self.packet();p['synthetic']=True
        with self.assertRaises(InvalidMeasurement):validate_matter_packet(p)
    def test_missing_calibration(self):
        p=self.packet();del p['calibration_record_id']
        with self.assertRaises(InvalidMeasurement):validate_matter_packet(p)
    def test_missing_uncertainty(self):
        p=self.packet();del p['paired_trials'][0]['paired_trajectory_samples'][0]['difference_error_bound_m']
        with self.assertRaises(InvalidMeasurement):validate_matter_packet(p)
    def test_missing_pairs(self):
        p=self.packet();p['paired_trials'][0]['paired_trajectory_samples']=[]
        with self.assertRaises(InvalidMeasurement):validate_matter_packet(p)
    def test_unmatched_fields(self):
        p=self.packet();p['paired_trials'][0]['matched_known_fields']=False
        with self.assertRaises(InvalidMeasurement):validate_matter_packet(p)
    def test_repeated_time(self):
        p=self.packet();p['paired_trials'][0]['paired_trajectory_samples'][1]['time_s']='0'
        with self.assertRaises(InvalidMeasurement):validate_matter_packet(p)
