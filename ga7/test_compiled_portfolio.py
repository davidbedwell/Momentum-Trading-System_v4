import unittest
import numpy as np
from ga7.compiled_portfolio import replay

class CompiledPortfolioTests(unittest.TestCase):
    def inputs(self):
        shape = (5, 2)
        op = np.full(shape, 100., dtype=np.float64)
        cl = np.full(shape, 100., dtype=np.float64)
        lo = np.full(shape, 98., dtype=np.float64)
        cl[1:, 0] = [101., 105., 108., 110.]
        op[1:, 0] = [101., 105., 108., 110.]
        return (op, cl, lo, np.zeros(shape), np.zeros(shape),
                np.ones(shape, dtype=np.bool_), np.ones(shape, dtype=np.bool_),
                np.zeros(shape, dtype=np.int16), np.zeros(5, dtype=np.bool_))

    def test_cash_funded_close_all(self):
        a = self.inputs()
        sig = np.zeros((5, 2), dtype=np.bool_)
        sig[1, 0] = True
        result = replay(*a, sig, 4, .10, 2, cash_yield=0.)
        self.assertEqual(result[6], 1)
        self.assertGreater(result[0], 100000.)
        self.assertEqual(result[8].shape, (5,))

    def test_cash_yield_without_settlement_parity_rejected(self):
        a = self.inputs()
        sig = np.zeros((5, 2), dtype=np.bool_)
        with self.assertRaises(ValueError):
            replay(*a, sig, 4, .10, 2, cash_yield=.03)

    def test_hold_limit_above_40_rejected(self):
        a = self.inputs()
        sig = np.zeros((5, 2), dtype=np.bool_)
        with self.assertRaises(ValueError):
            replay(*a, sig, 41, .10, 2, cash_yield=0.)

    def test_defense_prevents_entry(self):
        a = list(self.inputs())
        a[8][0] = True
        sig = np.zeros((5, 2), dtype=np.bool_)
        sig[1, 0] = True
        result = replay(*a, sig, 4, .10, 2, cash_yield=0.)
        self.assertEqual(result[6], 0)

    def test_split_adjusted_basis_does_not_multiply_shares(self):
        a = list(self.inputs())
        a[4][2, 0] = 2.
        sig = np.zeros((5, 2), dtype=np.bool_)
        sig[1, 0] = True
        adjusted = replay(*a, sig, 4, .10, 2, cash_yield=0.)
        a[4][2, 0] = 0.
        no_split_event = replay(*a, sig, 4, .10, 2, cash_yield=0.)
        self.assertAlmostEqual(adjusted[0], no_split_event[0], places=6)

if __name__ == "__main__":
    unittest.main()
