"""Causal feature discrimination check across independent synthetic regimes; no GA."""
import json
from .long_sequence_edge_probe import make

def run():
    result={}
    for name,seed in [('initial',7),('unseen',91),('reordered',19)]:
        days=make(seed,'train' if name=='initial' else 'unseen',128)
        groups={'positive_momentum':[],'negative_momentum':[],'high_volatility':[],'low_volatility':[]}
        for ticker in ('AAA','BBB','CCC'):
            closes=[bars[ticker].close for _,bars in days]
            for i in range(20,len(closes)-5):
                momentum=closes[i]/closes[i-5]-1
                rr=[closes[j]/closes[j-1]-1 for j in range(i-19,i+1)]
                mean=sum(rr)/len(rr);vol=(sum((x-mean)**2 for x in rr)/len(rr))**.5
                future=closes[i+5]/closes[i]-1
                groups['positive_momentum' if momentum>0 else 'negative_momentum'].append(future)
                groups['high_volatility' if vol>.015 else 'low_volatility'].append(future)
        result[name]={k:{'n':len(v),'mean_5day_forward_return':sum(v)/len(v) if v else None,'win_rate':sum(x>0 for x in v)/len(v) if v else None} for k,v in groups.items()}
    return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
