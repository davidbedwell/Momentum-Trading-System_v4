"""Causal diagnostic gate regressions; no full portfolio executions."""
import unittest
import experiment as e

class Reliability(unittest.TestCase):
    def test_no_unmatured_or_current_data(self):
        days,tapes,_=e.r.s1.generate(1101)
        tape=tapes['null']
        i=80
        before=e.reliability(days,tape,'strong',i)
        changed=list(days)
        changed[i:]=[(d,{}) for d,_ in days[i:]]
        changed_tape=list(tape)
        changed_tape[i-2:]=[[] for _ in tape[i-2:]]
        self.assertEqual(before,e.reliability(changed,changed_tape,'strong',i))
        self.assertEqual(before['latest_outcome_index'],i-1)

    def test_warmup_denies(self):
        days,tapes,_=e.r.s1.generate(1101)
        for i in (0,1,2,20,31):
            state=e.reliability(days,tapes['null'],'strong',i)
            self.assertFalse(state['allow'])
            self.assertLess(state['dates'],30)

    def test_miscalibrated_null_is_not_granted_reliability(self):
        days,tapes,_=e.r.s1.generate(1101)
        state=e.reliability(days,tapes['null'],'strong',251)
        self.assertFalse(state['allow'])
        self.assertLess(state['mean_error'],0)

if __name__=='__main__':unittest.main(verbosity=2)
