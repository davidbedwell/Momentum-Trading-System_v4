**MTS G2 H.4 Hypervolume Clarification — Independent Engineering Recommendation**

1. **Definition of "training-hypervolume gain < 0.5% over 40 generations"**  
   Use **baseline-subtracted/excess HV** (recommended specification filling the omission; frozen wording did not specify).  
   Formula:  
   Let \( R = (-1, -1) \).  
   \( \text{excessHV}_t = \text{HV}_t(R) - \text{area of reference rectangle to origin} = \text{HV}_t(-1,-1) - 1.0 \)  
   Gain = \( \frac{\text{excessHV}_{t} - \text{excessHV}_{t-40}}{\text{excessHV}_{t-40}} < 0.005 \)  
   (This removes the large fixed reference rectangle that dominates raw HV and makes the 0.5% threshold meaningful.)

   (a) Frozen wording is silent on reference, normalization, or excess.  
   (b) Excess HV is the mathematically defensible choice for a maximize/maximize objective with negative reference.

2. **H.4 should use cumulative archive HV.**  
   The original intent ("island training-hypervolume") refers to the archive built by the island, not the transient current population. Current-population HV would be noisy and non-monotonic.

3. **For MDD-band islands, HV should include only receiver-feasible/archive-admitted points.**  
   Yes. The archive already enforces feasibility; HV must be computed only on the admitted frontier. Including non-admitted points would violate island semantics.

4. **Gen40 can be salvaged.**  
   Recompute correct cumulative archive HV history on the preserved gen40 checkpoints using the new deterministic HV/Pareto code, then apply the corrected plateau test. No post-trigger generations have executed, so the decision remains valid.

5. **Checkpoints at gen0/10/20/30/40 are sufficient.**  
   Because the plateau test only compares HV at \( t \) vs \( t-40 \), and all generations 1–40 predate any intervention, the existing checkpoints allow exact reconstruction of the 40-generation excess-HV gain. Per-generation history is not required.

6. **Exact O(n log n) Pareto extraction is scientifically neutral.**  
   Yes, provided the brute-force-equivalence regression tests pass (which they do). It changes only computational cost, not the set of non-dominated points used for HV.

7. **Archives should be Pareto-pruned/deduplicated.**  
   They can (and should) retain only the current non-dominated front. Keeping dominated historical members is unnecessary for cumulative HV semantics under a fixed reference point and adds no value to H.4 decisions.

8. **Disposition: RESUME_FROM_GEN40**

   **Required steps:**
   - On all 36 island-fold checkpoints at gen40, recompute exact cumulative-archive excessHV using corrected HV and O(n log n) Pareto routines.
   - Apply the plateau test using the excess-HV definition above.
   - If first plateau triggers: inject 20% immigrants + up-weight structural mutation (as frozen).
   - If second consecutive plateau triggers: freeze archive and reallocate compute.
   - Proceed with remaining 460 generations under the corrected logic.
   - No scientific parameters are altered.

This respects the frozen wording while supplying the minimal mathematically necessary definitions that Claude omitted.