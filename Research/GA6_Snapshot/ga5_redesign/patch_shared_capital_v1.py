from pathlib import Path
p=Path('/opt/mts/ga5_redesign/shared_capital_13_niche_v1.py')
s=p.read_text()
a=s.index('source=pd.read_csv(')
b=s.index("print('SELECTED'",a)
s=s[:a]+"""ledger_path=root/'dev79_niche_origin_500x1000_20261019'/'all_evaluations.jsonl'
selected={}
for line in ledger_path.open():
 x=json.loads(line);r=x['result'];n=x['origin_niche']
 if r.get('fills',0)<100:continue
 if n not in selected or r['cagr_diagnostic']>selected[n]['result']['cagr_diagnostic']:selected[n]=x
genomes={n:Genome(**x['genome']) for n,x in selected.items()}
if len(genomes)!=13:raise RuntimeError('Insufficient trade-active niches')
"""+s[b:]
s=s.replace('one best available source-ledger chromosome per niche with >=100 fills; missing novel offspring genomes cannot be reconstructed from result-only files.','one best full-sample chromosome per niche with >=100 fills; selected from historical evaluation ledger rather than corrected-breeder offspring.')
p.write_text(s)
print('PATCHED')
