import unittest
from tools.independent_reconstruction import assess_independent_reconstructions
from tools.uncertainty_exclusion import InvalidMeasurement

class ReconstructionTests(unittest.TestCase):
    def packet(self):
        return dict(synthetic=True,observable_type='SHADOW_BOUNDARY',agreement_tolerance='0.1',
            reconstructions=[dict(algorithm_id='threshold',provenance_id='pipeline-A',
                estimated_observable='42.2'),dict(algorithm_id='edges',provenance_id='pipeline-B',
                estimated_observable='42.25')])
    def test_agreement_not_validation(self):
        r=assess_independent_reconstructions(self.packet())
        self.assertEqual(r['verdict'],'ALGORITHM_AGREEMENT_ONLY')
        for key in ('physical_validation','independence_verified','common_mode_bias_excluded'):
            self.assertFalse(r[key])
    def test_disagreement(self):
        p=self.packet();p['reconstructions'][1]['estimated_observable']='43'
        self.assertEqual(assess_independent_reconstructions(p)['verdict'],'ALGORITHM_DISAGREEMENT')
    def test_exact_boundary(self):
        p=self.packet();p['reconstructions'][1]['estimated_observable']='42.3'
        self.assertEqual(assess_independent_reconstructions(p)['verdict'],'ALGORITHM_AGREEMENT_ONLY')
    def test_same_algorithm(self):
        p=self.packet();p['reconstructions'][1]['algorithm_id']='threshold'
        with self.assertRaises(InvalidMeasurement):assess_independent_reconstructions(p)
    def test_same_provenance(self):
        p=self.packet();p['reconstructions'][1]['provenance_id']='pipeline-A'
        with self.assertRaises(InvalidMeasurement):assess_independent_reconstructions(p)
    def test_nan(self):
        p=self.packet();p['reconstructions'][1]['estimated_observable']='NaN'
        with self.assertRaises(InvalidMeasurement):assess_independent_reconstructions(p)
    def test_negative_tolerance(self):
        p=self.packet();p['agreement_tolerance']=-1
        with self.assertRaises(InvalidMeasurement):assess_independent_reconstructions(p)
    def test_bad_type(self):
        p=self.packet();p['observable_type']='UNKNOWN'
        with self.assertRaises(InvalidMeasurement):assess_independent_reconstructions(p)
    def test_boolean_measurement(self):
        p=self.packet();p['reconstructions'][0]['estimated_observable']=True
        with self.assertRaises(InvalidMeasurement):assess_independent_reconstructions(p)
