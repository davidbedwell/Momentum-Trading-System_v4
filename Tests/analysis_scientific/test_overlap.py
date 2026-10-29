from datetime import datetime, timezone

from Engines.Analysis.overlap import EventWindow, OverlapPolicy, OverlapService


def event(event_id, start_day, end_day, magnitude):
    return EventWindow(
        event_id=event_id,
        start=datetime(2026, 1, start_day, tzinfo=timezone.utc),
        end=datetime(2026, 1, end_day, tzinfo=timezone.utc),
        magnitude=magnitude,
    )


def test_allow_keeps_all_events_in_deterministic_chronological_order():
    result = OverlapService().apply(
        [event("b", 3, 4, 2), event("a", 1, 2, 1)],
        policy=OverlapPolicy.ALLOW,
    )
    assert [x.event_id for x in result.selected] == ["a", "b"]


def test_first_qualifying_wins_drops_overlapping_later_event():
    result = OverlapService().apply(
        [event("first", 1, 3, 1), event("later", 2, 4, 10)],
        policy="FIRST_QUALIFYING_WINS",
    )
    assert [x.event_id for x in result.selected] == ["first"]
    assert result.excluded_event_ids == ("later",)


def test_highest_magnitude_wins_overlap_cluster():
    result = OverlapService().apply(
        [
            event("weak", 1, 4, 1),
            event("strong", 2, 3, 5),
            event("independent", 8, 9, 2),
        ],
        policy="HIGHEST_MAGNITUDE_WINS",
    )
    assert [x.event_id for x in result.selected] == ["strong", "independent"]
    assert result.excluded_event_ids == ("weak",)


def test_chronological_exclusion_window_is_deterministic():
    result = OverlapService().apply(
        [
            event("a", 1, 1, 1),
            event("b", 2, 2, 1),
            event("c", 4, 4, 1),
        ],
        policy="CHRONOLOGICAL_EXCLUSION_WINDOW",
        exclusion_window_days=1,
    )
    assert [x.event_id for x in result.selected] == ["a", "c"]
