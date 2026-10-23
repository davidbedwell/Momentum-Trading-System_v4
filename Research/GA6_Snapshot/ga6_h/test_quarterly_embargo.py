import unittest
from datetime import date
from quarterly_embargo import embargo_sessions, entry_allowed

class EmbargoTests(unittest.TestCase):
    def setUp(self):
        self.sessions=['2026-10-19','2026-10-20','2026-10-21','2026-10-22','2026-10-23','2026-10-26','2026-10-27','2026-10-28']
        self.events={'ABC':[{'date':'2026-10-22','known_at':'2026-10-19T12:00:00+00:00'}]}
        self.known={'ABC'}
    def test_five_sessions(self):
        self.assertEqual(embargo_sessions(['2026-10-22'],self.sessions),{date.fromisoformat(x) for x in self.sessions[1:6]})
    def test_weekend_mapping(self):
        self.assertEqual(embargo_sessions(['2026-10-24'],self.sessions),{date.fromisoformat(x) for x in self.sessions[3:8]})
    def test_known_at_causality(self):
        e=self.events['ABC']
        self.assertEqual(len(embargo_sessions(e,self.sessions,'2026-10-19T11:00:00+00:00')),0)
        self.assertEqual(len(embargo_sessions(e,self.sessions,'2026-10-21T21:00:00+00:00')),5)
    def test_no_hindsight(self):
        self.assertFalse(embargo_sessions(['2026-10-22'],self.sessions,'2026-10-19T21:00:00+00:00'))
        self.assertFalse(embargo_sessions([{'date':'2026-10-22'}],self.sessions,'2026-10-19T21:00:00+00:00'))
    def test_entry_blocked(self):
        self.assertFalse(entry_allowed('ABC','2026-10-20',self.events,self.sessions,'2026-10-19T21:00:00+00:00',self.known))
        self.assertTrue(entry_allowed('ABC','2026-10-27',self.events,self.sessions,'2026-10-26T21:00:00+00:00',self.known))
    def test_unknown_schedule_fail_closed(self):
        self.assertFalse(entry_allowed('XYZ','2026-10-20',self.events,self.sessions,'2026-10-19T21:00:00+00:00',self.known))
        self.assertFalse(entry_allowed('ABC','2026-10-20',self.events,self.sessions,'2026-10-19T21:00:00+00:00'))
    def test_timezone_required(self):
        with self.assertRaises(ValueError): entry_allowed('ABC','2026-10-20',self.events,self.sessions,'2026-10-19T21:00:00',self.known)

if __name__=='__main__': unittest.main()
