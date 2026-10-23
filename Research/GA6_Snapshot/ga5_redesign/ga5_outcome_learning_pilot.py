import pandas as pd,numpy as np,json
from pathlib import Path
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss
p=Path('/opt/mts/ga5_redesign/dev79_niche_origin_500x1000_20261019/niche0001_signal_study')
d=pd.read_parquet(p/'intratrade_time_t_samples.parquet')
d=d.sort_values('date');features=['ret5','ret20','vol','rs','breadth']
train=d[d.date<'2017-01-01'];test=d[d.date>='2017-01-01']
# Exclude final 10 calendar days of training to purge labels crossing boundary
train=train[train.date<'2016-12-15']
models={}
for kind,cols in [('volatility',['vol']),('multifeature',features)]:
 m=HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=9,l2_regularization=20,learning_rate=.05,min_samples_leaf=300,random_state=17)
 m.fit(train[cols],train.future_adverse5.astype(int))
 prob=m.predict_proba(test[cols])[:,1];y=test.future_adverse5.astype(int).to_numpy()
 models[kind]={'train_observations':len(train),'test_observations':len(test),'test_base_rate':float(y.mean()),'roc_auc':float(roc_auc_score(y,prob)),'average_precision':float(average_precision_score(y,prob)),'brier':float(brier_score_loss(y,prob))}
 q=np.quantile(prob,.9);sel=prob>=q
 models[kind]['top_decile_adverse_rate']=float(y[sel].mean());models[kind]['top_decile_count']=int(sel.sum())
 test[['date','ticker','cohort','future_adverse5']].assign(probability=prob).to_parquet(p/f'{kind}_holdout_predictions.parquet',index=False)
(p/'outcome_learning_first_pass.json').write_text(json.dumps(models,indent=2))
print(json.dumps(models,indent=2),flush=True)
