import sqlite3,json,collections
p='/opt/mts/thunder-migration/mts-certification-20261011/cagr_mdd_library_20261013/STRATEGY_BANK_INDEX.sqlite';c=sqlite3.connect('file:'+p+'?mode=ro',uri=True)
queries={'all_recorded':"select count(*) from measurements where calmar>2",'all_with_positive_cagr':"select count(*) from measurements where calmar>2 and cagr>0",'dev80':"select count(*) from measurements where calmar>2 and cohort='DEV80'",'dev80_filtered':"select count(*) from measurements where calmar>2 and cohort='DEV80' and cagr between 0 and 150 and abs(mdd) between 3 and 90"}
for k,q in queries.items():print(k,c.execute(q).fetchone()[0])
print('COHORTS',c.execute('select cohort,count(*) from measurements where calmar>2 group by cohort order by count(*) desc limit 25').fetchall())
print('STUDIES',c.execute('select s.study,count(*) from measurements m join strategies s on m.strategy_key=s.strategy_key where m.calmar>2 group by s.study').fetchall())
print('TOP',c.execute('select s.study,s.chromosome,s.horizon,m.cohort,m.cagr,m.mdd,m.calmar,m.status,m.source from measurements m join strategies s on m.strategy_key=s.strategy_key where m.calmar>2 order by m.calmar desc limit 15').fetchall())
