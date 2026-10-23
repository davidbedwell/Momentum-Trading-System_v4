import sys
sys.path.insert(0,'/opt/mts/ga5_redesign')
from niche_portfolio_pareto_v1 import rank_by_niche,portfolio_objectives,niche_portfolio_selection
class G:
 def __init__(self,n,id):self.niche=n;self.id=id
 def identity(self):return self.id
def item(n,id,c,dd,fills=5,shadow=999):
 return (shadow,G(n,id),dict(cagr_diagnostic=c,mdd_diagnostic=dd,fills=fills,exit_objectives=dict(expectancy=shadow)))
def test():
 a=item('A','a',.30,-.40)
 b=item('A','b',.25,-.20)
 c=item('A','c',.15,-.50)
 d=item('B','d',.02,-.01)
 e=item('A','e',.50,-.10,0)
 rows=[a,b,c,d,e]
 r=rank_by_niche(rows)
 assert r[0]==0 and r[1]==0 and r[2]==1 and r[3]==0 and 4 not in r,r
 x=niche_portfolio_selection(rows)
 assert set(x)=={'A','B'}
 assert len(x['A'])==3 and len(x['B'])==1
 assert portfolio_objectives(a)==(.30,-.40)
 print('PASS: niche isolation; portfolio-only objectives; dominance; invalid no-fills exclusion; shadow independence')
if __name__=='__main__':test()
