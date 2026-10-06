from Core.conforming_ga.compute_plan import plan
def test_thunder_six_stays_one_fold_six_workers(monkeypatch):
 monkeypatch.setenv("MTS_CPU_RESERVE","0");p=plan(6);assert (p["parallel_folds"],p["workers_per_fold"])==(1,6)
def test_64_cpu_target_parallelizes_four_folds_without_scientific_change(monkeypatch):
 monkeypatch.setenv("MTS_CPU_RESERVE","2");p=plan(64);assert p["parallel_folds"]==4 and p["workers_per_fold"]==15 and not p["scientific_configuration_changed"]
def test_96_cpu_target_parallelizes_four_folds(monkeypatch):
 monkeypatch.setenv("MTS_CPU_RESERVE","2");p=plan(96);assert p["parallel_folds"]==4 and p["workers_per_fold"]==23
