import tempfile
import unittest
from pathlib import Path
import pandas as pd
from Core.layered_ga.ga4_stage1_context_link import verify_context_link

class TestContextLink(unittest.TestCase):
    def setUp(self):
        self.rows=pd.DataFrame({"security_id":["A","B"],"effective_date":["2020-01-02","2020-01-03"]})
    def test_alignment_and_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"context.parquet"
            self.rows.to_parquet(p)
            r=verify_context_link(self.rows,self.rows,p,scope="DEV80")
            self.assertEqual(r["aligned_rows"],2)
            self.assertEqual(r["status"],"ALIGNED_NOT_SCIENTIFICALLY_CERTIFIED")
            self.assertEqual(len(r["sha256"]),64)
    def test_missing_context_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"context.parquet"
            self.rows.iloc[:1].to_parquet(p)
            with self.assertRaises(ValueError):
                verify_context_link(self.rows,self.rows.iloc[:1],p,scope="DEV80")
    def test_duplicate_context_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"context.parquet"
            dup=pd.concat([self.rows,self.rows.iloc[:1]])
            dup.to_parquet(p)
            with self.assertRaises(ValueError):
                verify_context_link(self.rows,dup,p,scope="DEV80")
if __name__=="__main__": unittest.main()
