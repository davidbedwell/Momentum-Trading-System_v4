from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from statistics import mean
from typing import Any, Mapping

SEQUENCE = ("AAPL","AMD","AMZN","BA","GOOGL","JPM","META","MSFT","NVDA","TSLA","XOM")
CALL_EVENTS = {"SOL_CALL_COMPLETE", "SOL_RD_CALL_COMPLETE"}

def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def _jsonl(path: Path) -> list[Mapping[str, Any]]:
    if not path.exists():
        return []
    out=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            item=json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, Mapping):
            out.append(item)
    return out

def _last_decision(state_dir: Path) -> Mapping[str, Any] | None:
    rows=_jsonl(state_dir/"batch_decisions.jsonl")
    if not rows:
        return None
    value=rows[-1].get("decision")
    return value if isinstance(value, Mapping) else None

def _audit_state(decision: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not decision:
        return {}
    rs=decision.get("research_state")
    if not isinstance(rs, Mapping):
        return {}
    state=rs.get("campaign_learning_audit_state")
    return state if isinstance(state, Mapping) else {}

def _telemetry(state_dir: Path) -> Mapping[str, Any]:
    calls=[]
    for row in _jsonl(state_dir/"sol_transport_telemetry.jsonl"):
        if row.get("event") not in CALL_EVENTS:
            continue
        usage=row.get("usage")
        usage=usage if isinstance(usage, Mapping) else {}
        prompt=int(usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0)
        completion=int(usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0)
        cost=None
        for key in ("actual_call_cost_usd","cost_usd","estimated_call_cost_usd"):
            try:
                if row.get(key) is not None:
                    cost=float(row[key]); break
            except (TypeError,ValueError):
                pass
        calls.append({"operation":row.get("operation"),"prompt_tokens":prompt,"completion_tokens":completion,"cost_usd":cost})
    spend=sum(x["cost_usd"] for x in calls if x["cost_usd"] is not None)
    return {
        "sol_calls":len(calls),
        "prompt_tokens":sum(x["prompt_tokens"] for x in calls),
        "completion_tokens":sum(x["completion_tokens"] for x in calls),
        "known_call_cost_count":sum(x["cost_usd"] is not None for x in calls),
        "summed_known_call_cost_usd":spend,
        "calls":calls,
    }

def _subject_summary(ticker: str, state_dir: Path) -> Mapping[str, Any]:
    audit=_audit_state(_last_decision(state_dir))
    known=list(audit.get("known_structure_applications", [])) if isinstance(audit.get("known_structure_applications"), list) else []
    novel=list(audit.get("novel_strategy_discoveries", [])) if isinstance(audit.get("novel_strategy_discoveries"), list) else []
    general=list(audit.get("cross_subject_generalizations", [])) if isinstance(audit.get("cross_subject_generalizations"), list) else []
    freq=audit.get("known_structure_opportunity_summary")
    freq=freq if isinstance(freq, Mapping) else {}
    def n(key: str):
        value=freq.get(key)
        return value if isinstance(value,(int,float)) and not isinstance(value,bool) else None
    months=n("observation_months")
    raw=n("raw_unique_opportunities")
    executable=n("executable_nonoverlapping_unique_opportunities")
    candidate=n("positive_net_ev_candidate_unique_opportunities")
    rates={}
    if months and months > 0:
        rates={
            "raw_unique_per_month": raw/months if raw is not None else None,
            "executable_nonoverlapping_per_month": executable/months if executable is not None else None,
            "positive_net_ev_candidate_per_month": candidate/months if candidate is not None else None,
        }
    return {
        "ticker":ticker,
        "state_dir":str(state_dir),
        "telemetry":_telemetry(state_dir),
        "known_structure_applications":known,
        "known_structure_opportunity_summary":dict(freq),
        "known_structure_opportunity_rates":rates,
        "novel_strategy_discoveries":novel,
        "cross_subject_generalizations":general,
        "audit_annotation_present":bool(audit),
    }

def build_audit(campaign_dir: Path) -> Mapping[str, Any]:
    manifest=_load_json(campaign_dir/"sequential_revisit_manifest.json")
    result_by_ticker={str(x.get("ticker")):x for x in manifest.get("results",[]) if isinstance(x,Mapping)}
    subjects=[]
    for ordinal,ticker in enumerate(SEQUENCE,1):
        item=result_by_ticker.get(ticker)
        if item and item.get("state_dir"):
            state=Path(str(item["state_dir"]))
        else:
            state=campaign_dir/f"{ordinal:02d}-{ticker.lower()}"
        if state.exists():
            subjects.append(_subject_summary(ticker,state))
    exact=[s for s in subjects if s["known_structure_opportunity_rates"]]
    aggregate={
        "subjects_present":len(subjects),
        "sol_calls":sum(s["telemetry"]["sol_calls"] for s in subjects),
        "prompt_tokens":sum(s["telemetry"]["prompt_tokens"] for s in subjects),
        "completion_tokens":sum(s["telemetry"]["completion_tokens"] for s in subjects),
        "summed_known_call_cost_usd":sum(s["telemetry"]["summed_known_call_cost_usd"] for s in subjects),
        "known_structure_applications":sum(len(s["known_structure_applications"]) for s in subjects),
        "novel_strategy_claims":sum(len(s["novel_strategy_discoveries"]) for s in subjects),
        "generalization_claims":sum(len(s["cross_subject_generalizations"]) for s in subjects),
        "subjects_with_exact_opportunity_frequency":len(exact),
    }
    if exact:
        for key in ("raw_unique_per_month","executable_nonoverlapping_per_month","positive_net_ev_candidate_per_month"):
            vals=[s["known_structure_opportunity_rates"].get(key) for s in exact]
            vals=[v for v in vals if isinstance(v,(int,float))]
            aggregate["mean_"+key]=mean(vals) if vals else None
    return {
        "format":"MTS_V4_11_TICKER_LEARNING_AUDIT_V1",
        "campaign_dir":str(campaign_dir),
        "sequence":list(SEQUENCE),
        "manifest_status":manifest.get("status"),
        "methodology":{
            "known_novel_generalization_authority":"SOL_AUTHORED_AUDIT_ANNOTATIONS",
            "deterministic_role":"AGGREGATION_ONLY",
            "opportunity_frequency_rule":"EXACT_COUNTS_ONLY_NULL_IF_UNAVAILABLE",
            "novelty_claims_are_not_independently_proven_by_this_REPORT":True,
            "generalization_claims_are_not_independently_proven_by_this_REPORT":True,
        },
        "aggregate":aggregate,
        "subjects":subjects,
    }

def _render_text(report: Mapping[str, Any]) -> str:
    a=report["aggregate"]
    lines=[
        "MTS V4 — 11 TICKER SOL LEARNING AUDIT",
        f"CAMPAIGN={report['campaign_dir']}",
        f"STATUS={report['manifest_status']}",
        f"SUBJECTS_PRESENT={a['subjects_present']}",
        f"SOL_CALLS={a['sol_calls']}",
        f"PROMPT_TOKENS={a['prompt_tokens']}",
        f"COMPLETION_TOKENS={a['completion_tokens']}",
        f"SUMMED_KNOWN_CALL_COST_USD={a['summed_known_call_cost_usd']:.6f}",
        f"KNOWN_STRUCTURE_APPLICATIONS={a['known_structure_applications']}",
        f"NOVEL_STRATEGY_CLAIMS={a['novel_strategy_claims']}",
        f"GENERALIZATION_CLAIMS={a['generalization_claims']}",
        f"SUBJECTS_WITH_EXACT_OPPORTUNITY_FREQUENCY={a['subjects_with_exact_opportunity_frequency']}",
    ]
    for key in ("mean_raw_unique_per_month","mean_executable_nonoverlapping_per_month","mean_positive_net_ev_candidate_per_month"):
        if key in a and a[key] is not None:
            lines.append(f"{key.upper()}={a[key]:.6f}")
    for s in report["subjects"]:
        lines += ["",f"=== {s['ticker']} ===",
                  f"SOL_CALLS={s['telemetry']['sol_calls']}",
                  f"PROMPT_TOKENS={s['telemetry']['prompt_tokens']}",
                  f"COMPLETION_TOKENS={s['telemetry']['completion_tokens']}",
                  f"KNOWN_APPLICATIONS={len(s['known_structure_applications'])}",
                  f"NOVEL_CLAIMS={len(s['novel_strategy_discoveries'])}",
                  f"GENERALIZATION_CLAIMS={len(s['cross_subject_generalizations'])}"]
        for k,v in s["known_structure_opportunity_rates"].items():
            lines.append(f"{k.upper()}={v:.6f}" if v is not None else f"{k.upper()}=UNKNOWN")
        for item in s["novel_strategy_discoveries"]:
            lines.append("NOVEL="+json.dumps(item,sort_keys=True,default=str))
        for item in s["cross_subject_generalizations"]:
            lines.append("GENERALIZATION="+json.dumps(item,sort_keys=True,default=str))
    return "\n".join(lines)+"\n"

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--campaign-dir",required=True)
    args=p.parse_args()
    root=Path(args.campaign_dir).expanduser().resolve()
    report=build_audit(root)
    jp=root/"MTS_V4_11_TICKER_LEARNING_AUDIT.json"
    tp=root/"MTS_V4_11_TICKER_LEARNING_AUDIT.txt"
    jp.write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n",encoding="utf-8")
    tp.write_text(_render_text(report),encoding="utf-8")
    print(f"AUDIT_JSON={jp}")
    print(f"AUDIT_TXT={tp}")
    print(f"SUBJECTS_PRESENT={report['aggregate']['subjects_present']}")
    print(f"NOVEL_STRATEGY_CLAIMS={report['aggregate']['novel_strategy_claims']}")
    print(f"GENERALIZATION_CLAIMS={report['aggregate']['generalization_claims']}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
