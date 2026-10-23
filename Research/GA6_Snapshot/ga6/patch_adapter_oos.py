from pathlib import Path
p=Path('/opt/mts/ga6/evaluator_adapter.py');s=p.read_text()
needle="            result['ga6_prospective_baseline']="
assert s.count(needle)==1
insert='''            if len(train)>=50 and len(valid)>=50:
                from ga6.policy_evolution_oos import train_validate
                import random
                result['ga6_policy_oos']=train_validate(paths,random.Random(6106),cutoff,population=8,generations=2,fee=kwargs.get('fee',.001),cash_daily=daily)
            else:
                result['ga6_policy_oos']={'eligible':False,'train_count':len(train),'validation_count':len(valid)}
'''
s=s.replace(needle,insert+needle)
p.write_text(s)
print('Integrated OOS GA6 policy research into adapter')
