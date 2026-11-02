"""Chronological orchestration: persist predictions before computing next labels."""
from dataclasses import asdict
from pathlib import Path
import json
from .core import Config, ARMS, development_year, digest, features, labels, predict, metrics
from .adapters import validate


def write_new(path, obj):
    with Path(path).open('x') as f:
        f.write(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+'\n')


def freeze(directory, cfg=Config()):
    directory = Path(directory)
    directory.mkdir(parents=True,exist_ok=True)
    root = Path(__file__).parent
    sources = {p.name:digest(p.read_text()) for p in sorted(root.glob('*.py'))}
    tests = {p.name:digest(p.read_text()) for p in sorted((root/'tests').glob('*.py'))}
    definition = {'config':asdict(cfg),'source_hashes':sources,'test_hashes':tests,
                  'arms':ARMS,'holdout_years':[2010,2011], 'holdouts_accessible':False,
                  'policy':'Discovery only. No evaluation unlocking implemented.',
                  'prior_exposure':'No 2010/2011 labels inspected in this implementation session; exposure elsewhere unknown.',
                  'target':'Annual first eligible session adjusted open to terminal adjusted value; chronological strictly later-session low-to-high advance. Winner is OR of thresholds.',
                  'training_target':'max(calendar_return,advance)',
                  'feature_definition':'YTD return, mean adjusted dollar volume, YTD market return; annual revenue growth between latest two usable original reports.',
                  'metric_definition':'Annual winner recall/precision; average-tie Spearman vs annual opportunity rank; calendar days to annual advance peak; post-snapshot maximum high relative to snapshot close.',
                  'development_status':'Known-winner development; never pristine. 2005 warmup; subsequent folds train on earlier years only.'}
    result = dict(definition, freeze_hash=digest(definition))
    write_new(directory/'freeze.json',result)
    return result


def verify_freeze(directory, cfg):
    frozen = json.loads((Path(directory)/'freeze.json').read_text())
    expected = frozen.pop('freeze_hash')
    if digest(frozen)!=expected:raise ValueError('Freeze manifest changed')
    if digest(frozen['config'])!=digest(asdict(cfg)):raise ValueError('Config differs from freeze')
    root = Path(__file__).parent
    current = {p.name:digest(p.read_text()) for p in sorted(root.glob('*.py'))}
    tests = {p.name:digest(p.read_text()) for p in sorted((root/'tests').glob('*.py'))}
    if current!=frozen['source_hashes'] or tests!=frozen['test_hashes']:raise ValueError('Code differs from freeze')
    return expected


def run(adapters, directory, cfg=Config()):
    years = sorted(adapters)
    for y in years:development_year(y)
    if not years or years!=list(range(2005,years[-1]+1)):raise ValueError('Contiguous folds starting in 2005 required')
    directory = Path(directory)
    freeze_hash = verify_freeze(directory,cfg)
    training = {arm:[] for arm in ARMS}
    broad_train = []
    reports = []
    for year in years:
        data = validate(adapters[year].load(year),year)
        day, xs, exclusions = features(data,year,cfg)
        intersection = {s:x for s,x in xs.items() if x['revenue_growth'] is not None}
        scores, fits = {},{}
        if year > 2005:
            for candidate in cfg.candidates:
                for arm,columns in ARMS.items():
                    key = candidate+'/'+arm
                    if training[arm] and intersection:
                        scores[key], fits[key] = predict(training[arm],intersection,columns,candidate)
                if broad_train and xs:
                    key = candidate+'/broad_chart'
                    scores[key], fits[key] = predict(broad_train,xs,ARMS['chart'],candidate)
            # Explicit naive baselines evaluated on the identical intersection.
            scores['baseline/momentum'] = {s:x['momentum'] for s,x in intersection.items()}
            scores['baseline/liquidity'] = {s:x['log_dollar_volume'] for s,x in intersection.items()}
            scores['baseline/constant'] = {s:0.0 for s in intersection}
        prediction = {'year':year,'asof':day,'freeze_hash':freeze_hash,'input_hash':digest(data),
                      'provenance':adapters[year].provenance(),'scores':scores,'fits':fits,
                      'training_years':years[:years.index(year)],'intersection':sorted(intersection),
                      'broad_chart_ids':sorted(xs),'missing_fundamentals':sorted(set(xs)-set(intersection)),
                      'exclusions':exclusions,'warmup':year==2005}
        # Exclusive files: reruns cannot replace already frozen predictions.
        write_new(directory/f'{year}_predictions.json',prediction)
        actual = labels(data,year,cfg)
        after = {s:dict(x,future_high=max((p['high'] for p in data['prices'] if p['id']==s and p['date']>day),default=x['snapshot_close'])) for s,x in xs.items()}
        results = {key:metrics(sc,actual,after,day,cfg.top_k) for key,sc in scores.items()}
        increments = {}
        for candidate in cfg.candidates:
            chart,combined = results.get(candidate+'/chart'),results.get(candidate+'/combined')
            fund = results.get(candidate+'/fundamentals')
            if chart and combined and fund:
                increments[candidate] = {f'combined_minus_{arm}':{m:combined[m]-other[m] if combined[m] is not None and other[m] is not None else None
                                            for m in ('recall_at_k','precision_at_k','spearman')}
                                         for arm,other in [('chart',chart),('fundamentals',fund)]}
        report = {'year':year,'prediction_hash':digest(prediction),'labels':actual,'metrics':results,
                  'incremental_value':increments,'coverage':{'broad_chart':len(xs),'intersection':len(intersection),
                  'missing_fundamentals':len(xs)-len(intersection)},
                  'warning':'Synthetic functionality only' if adapters[year].provenance().get('synthetic') else 'Development years; no causal or pristine validation claim'}
        write_new(directory/f'{year}_evaluation.json',report)
        reports.append(report)
        for sid,x in intersection.items():
            if sid in actual:
                for arm in ARMS:training[arm].append((x,actual[sid]['rank_value']))
        broad_train.extend((x,actual[sid]['rank_value']) for sid,x in xs.items() if sid in actual)
    write_new(directory/'summary.json',{'freeze_hash':freeze_hash,'years':years,'reports':reports,'locked_years':[2010,2011]})
    return reports
