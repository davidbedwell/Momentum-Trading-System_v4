"""Conservative GA4 search-budget timing; no automatic launch approval."""
import argparse,json,math
from pathlib import Path

def estimate(*,unique_evaluations,observed_unique,observed_seconds,observed_workers,target_workers,hourly_cost):
 if min(unique_evaluations,observed_unique,observed_seconds,observed_workers,target_workers)<=0:raise ValueError('All inputs must be positive')
 if hourly_cost<0:raise ValueError('Hourly cost must be nonnegative')
 base_hours=unique_evaluations*observed_seconds/observed_unique/3600
 return {'unique_evaluations_assumed':unique_evaluations,'baseline_hours_at_observed_workers':round(base_hours,2),'optimistic_linear_scaling_hours':round(base_hours*observed_workers/target_workers,2),'conservative_no_scaling_hours':round(base_hours,2),'optimistic_cost':round(base_hours*observed_workers/target_workers*hourly_cost,2),'conservative_cost':round(base_hours*hourly_cost,2),'approved':False,'warning':'Assumes all evaluation durations match benchmark; actual duplicate rates and scaling unknown'}

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--unique',type=int,required=True);p.add_argument('--observed-unique',type=int,required=True)
 p.add_argument('--observed-seconds',type=float,required=True);p.add_argument('--observed-workers',type=int,required=True)
 p.add_argument('--target-workers',type=int,required=True);p.add_argument('--hourly-cost',type=float,required=True)
 a=p.parse_args();print(json.dumps(estimate(unique_evaluations=a.unique,observed_unique=a.observed_unique,observed_seconds=a.observed_seconds,observed_workers=a.observed_workers,target_workers=a.target_workers,hourly_cost=a.hourly_cost),indent=2))
if __name__=='__main__':main()