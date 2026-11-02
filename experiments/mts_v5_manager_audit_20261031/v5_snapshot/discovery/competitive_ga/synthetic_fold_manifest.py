"""Read-only manifests for five parallel synthetic scenarios and 20 causal folds."""
from .synthetic_fiveyear_panel import load_year
from .synthetic_fold_schedule import make_folds

def build_manifest():
    result=[]
    for scenario in range(1,6):
        frame=load_year(scenario,columns=['open','close'])
        dates=sorted(frame.date.unique())
        for f in make_folds(scenario,dates):
            result.append({'scenario':scenario,'fold':f.number,
                           'train_first':str(dates[0]),'train_last':str(dates[f.train_stop-1]),
                           'evaluation_first':str(dates[f.test_start]),
                           'evaluation_last':str(dates[f.test_stop-1]),
                           'training_sessions':f.train_stop,
                           'evaluation_sessions':f.test_stop-f.test_start,
                           'stocks':int(frame.ticker.nunique())})
    return result
