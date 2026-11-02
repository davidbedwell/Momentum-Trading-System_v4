from discovery.competitive_ga.competitive_selector import Genes, select

def test_ga6_wins_when_ga7_has_more_drawdown():
    assert select(Genes(.01, 2, .012), [(('GA6','a'), .04, .005, .02), (('GA7','b'), .06, .03, .02)]) == ('GA6','a')

def test_ga7_can_win():
    assert select(Genes(.01, 2, .012), [(('GA7','b'), .05, .001, .01), (('GA6','a'), .04, .005, .01)]) == ('GA7','b')

def test_no_trade_when_inferior_to_alternatives():
    assert select(Genes(.01, 2, .012), [(('GA6','a'), .005, 0, 0), (('GA7','b'), .02, .01, .03)]) is None
