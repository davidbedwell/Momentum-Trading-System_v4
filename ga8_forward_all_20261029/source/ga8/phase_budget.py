"""Protect chronological phases against exhaustion of a shared wall-clock budget."""
def phase_budget_due(phase, elapsed_seconds, total_budget_seconds, phase_generations, minimum_generations=30):
    """Reserve 80% of time for phases 1+2 and 50% for phase 2.
    Never terminate phase 2 early. Ordinary generation/stagnation caps still apply.
    """
    if phase not in (0, 1) or phase_generations < minimum_generations:
        return False
    return elapsed_seconds >= total_budget_seconds * (0.20 if phase == 0 else 0.50)

if __name__ == "__main__":
    assert not phase_budget_due(0, 1000, 7200, 30)
    assert phase_budget_due(0, 1500, 7200, 30)
    assert not phase_budget_due(0, 1500, 7200, 29)
    assert phase_budget_due(1, 4000, 7200, 30)
    assert not phase_budget_due(2, 7000, 7200, 100)
    print("phase budget tests passed")
