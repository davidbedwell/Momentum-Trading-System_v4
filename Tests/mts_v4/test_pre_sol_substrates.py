from types import SimpleNamespace

from MTS_V4 import pre_sol_substrates


def test_pre_sol_composer_assembles_daily_sec_and_intraday_before_rd(monkeypatch):
    calls = []

    def builder(name, logical_id):
        def build(**kwargs):
            calls.append(name)
            return {logical_id: SimpleNamespace(outputs={"source": name})}
        return build

    monkeypatch.setattr(pre_sol_substrates, "build_daily", builder("daily", "analysis:neutral-standard-ohlcv-substrate:v1"))
    monkeypatch.setattr(pre_sol_substrates, "build_sec", builder("sec", "analysis:sec-share-structure-point-in-time:v1"))
    monkeypatch.setattr(pre_sol_substrates, "build_intraday", builder("intraday", "analysis:intraday-participation-substrate:v1"))

    results = pre_sol_substrates.build_for_subject(
        subject=SimpleNamespace(subject_id="equity:TEST"),
        evidence=(),
        cache=object(),
        analysis=object(),
    )

    assert calls == ["daily", "sec", "intraday"]
    assert set(results) == {
        "analysis:neutral-standard-ohlcv-substrate:v1",
        "analysis:sec-share-structure-point-in-time:v1",
        "analysis:intraday-participation-substrate:v1",
    }
