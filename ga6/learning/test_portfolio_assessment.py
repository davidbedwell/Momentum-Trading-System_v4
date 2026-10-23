from ga6.learning.portfolio_assessment import assess_shared_portfolio

def test_portfolio_metrics_and_drawdown():
    rows=[("2025-01-02",105),("2025-01-03",90),("2025-07-02",120)]
    result=assess_shared_portfolio(rows,starting_cash=100)
    assert abs(result["net_growth"]-.2)<1e-12
    assert abs(result["max_drawdown"]-(15/105))<1e-12
    assert result["cagr"]>0
    assert result["calmar"]>0

def test_nonchronological_rejected():
    try:
        assess_shared_portfolio([("2025-01-03",100),("2025-01-02",120)],starting_cash=100)
    except ValueError:
        pass
    else:
        raise AssertionError("must reject look-ahead/nonchronological NAV")
