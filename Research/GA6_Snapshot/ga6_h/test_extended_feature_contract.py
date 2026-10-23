import unittest
from historical_feature_adapter import feature_value

class ExtendedFeatureContract(unittest.TestCase):
    def test_all_declared_families_use_exact_columns(self):
        for family in ('acceleration','trend','liquidity','relative_strength','sector_strength','breadth'):
            self.assertEqual(feature_value({f'{family}_20':0.42},family,20),0.42)
    def test_uncomputed_indicators_fail_closed(self):
        for family in ('acceleration','trend','liquidity','relative_strength','sector_strength','breadth'):
            self.assertIsNone(feature_value({'return_20':0.42},family,20))
    def test_future_labels_not_features(self):
        self.assertIsNone(feature_value({'forward_adj_return_20':1.0},'momentum',20))
