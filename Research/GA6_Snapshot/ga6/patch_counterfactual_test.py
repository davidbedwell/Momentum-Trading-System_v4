from pathlib import Path
p=Path('/opt/mts/ga6/test_counterfactuals.py');s=p.read_text().replace("['temporary_drawdown']['count']==1","['avoided_loss']['count']==1");p.write_text(s)
print('corrected expected category: negative net hold is avoided loss')
