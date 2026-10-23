"""Independent frozen-evaluator chromosome comparisons; research-only."""
from ga6.learning.reference_fill_capture import run_reference_with_fills
from ga6.learning.reference_decision_capture import evaluate_with_decision_trace
from ga6.learning.reconciled_shadow import reconcile_shadow
from ga6.learning.counterfactual_comparison import link_fills_to_signals,compare_completed_shadow_trades

def evaluate_bank(evaluator,prepared,genomes,*,run_id,as_of,**policies):
    if not run_id or not genomes: raise ValueError("missing run or genomes")
    results={}
    for chromosome,genome in genomes.items():
        fills=run_reference_with_fills(evaluator,prepared,genome,**policies)
        signals=evaluate_with_decision_trace(evaluator,prepared,genome,**policies)
        if fills["metrics"]!=signals["metrics"]:
            raise RuntimeError("frozen evaluator parity mismatch")
        positions=reconcile_shadow(fills,[s[0] for s in prepared.sessions])
        linked=link_fills_to_signals(fills["fills"],signals["decision_signals"],
                                    run_id=run_id,chromosome_id=chromosome)
        results[str(chromosome)]=dict(metrics=fills["metrics"],fills=linked,
            decisions=signals["decision_signals"],positions=positions)
    comparisons=compare_completed_shadow_trades(
        {k:v["positions"]["completed"] for k,v in results.items()},as_of=as_of)
    return dict(chromosomes=results,comparisons=comparisons,
                status="FULL_REFERENCE_RESEARCH_ONLY_NOT_SELECTOR_CERTIFIED")
