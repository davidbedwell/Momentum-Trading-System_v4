import unittest
from ga7.portfolio_competition import compare_banks
class PortfolioCompetitionTests(unittest.TestCase):
 def test_requires_unrestricted_fallback(self):
  with self.assertRaises(ValueError):compare_banks({'a':{}},[],lambda g,b:False)
if __name__=='__main__':unittest.main()
