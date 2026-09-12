from __future__ import annotations

import json
import unittest

from MTS_V4.validation_source_selection import (
    ValidationSourceSelectionError,
    decode_validation_source_selection,
)


class ValidationSourceSelectionTests(unittest.TestCase):
    HYPOTHESIS_ID = "AMD-H001"

    def test_external_route_requires_ai_authored_criteria(self):
        payload = {
            "hypothesis_id": self.HYPOTHESIS_ID,
            "route": "EXTERNAL_UNSEEN_SUBJECT",
            "rationale": "The proposition explicitly claims applicability beyond AMD itself.",
            "external_subject_criteria": "Daily equity subject with scientifically comparable price-location dynamics and no prior MTS historical exposure.",
            "proposed_external_subject_id": None,
            "additional_information_required": ["candidate subject metadata"],
        }
        decoded = decode_validation_source_selection(
            json.dumps(payload),
            expected_hypothesis_id=self.HYPOTHESIS_ID,
        )
        self.assertEqual(decoded.route, "EXTERNAL_UNSEEN_SUBJECT")
        self.assertIsNotNone(decoded.external_subject_criteria)
        self.assertIsNone(decoded.proposed_external_subject_id)

    def test_future_same_subject_route_preserves_hypothesis_identity(self):
        payload = {
            "hypothesis_id": self.HYPOTHESIS_ID,
            "route": "FUTURE_SAME_SUBJECT",
            "rationale": "Future AMD observations provide the cleanest prospective test.",
            "external_subject_criteria": None,
            "proposed_external_subject_id": None,
            "additional_information_required": [],
        }
        decoded = decode_validation_source_selection(
            json.dumps(payload),
            expected_hypothesis_id=self.HYPOTHESIS_ID,
        )
        self.assertEqual(decoded.hypothesis_id, self.HYPOTHESIS_ID)
        self.assertEqual(decoded.route, "FUTURE_SAME_SUBJECT")

    def test_hypothesis_identity_cannot_change(self):
        payload = {
            "hypothesis_id": "AMD-H002",
            "route": "FUTURE_SAME_SUBJECT",
            "rationale": "Changed identity must fail mechanically.",
            "external_subject_criteria": None,
            "proposed_external_subject_id": None,
            "additional_information_required": [],
        }
        with self.assertRaises(ValidationSourceSelectionError):
            decode_validation_source_selection(
                json.dumps(payload),
                expected_hypothesis_id=self.HYPOTHESIS_ID,
            )

    def test_external_route_without_criteria_is_rejected(self):
        payload = {
            "hypothesis_id": self.HYPOTHESIS_ID,
            "route": "EXTERNAL_UNSEEN_SUBJECT",
            "rationale": "External route selected.",
            "external_subject_criteria": None,
            "proposed_external_subject_id": None,
            "additional_information_required": [],
        }
        with self.assertRaises(ValidationSourceSelectionError):
            decode_validation_source_selection(
                json.dumps(payload),
                expected_hypothesis_id=self.HYPOTHESIS_ID,
            )


if __name__ == "__main__":
    unittest.main()
