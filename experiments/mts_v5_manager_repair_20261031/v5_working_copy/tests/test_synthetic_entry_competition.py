from discovery.competitive_ga.synthetic_entry_competition import choose
import pytest

def test_order_independence_and_rotation():
    entries=[('b',.06),('a',.08),('c',.04)]
    assert choose(entries,'XYZ',5)==choose(list(reversed(entries)),'XYZ',5)
    assert {choose(entries,'XYZ',i)[0] for i in range(3)}=={'a','b','c'}

def test_empty_and_duplicate():
    assert choose([], 'XYZ',0) is None
    with pytest.raises(ValueError,match='duplicate'):choose([('a',.1),('a',.05)],'XYZ',0)
