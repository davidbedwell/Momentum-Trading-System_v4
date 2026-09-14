# SEC Share-Structure Data Boundary

This note documents the evidence boundary presented to the AI Research Director by the SEC share-structure substrate.

- Historical shares outstanding: available from SEC point-in-time disclosures and aligned by `known_at`.
- Historical tradable/public float shares: not available from the current free SEC source.
- SEC `EntityPublicFloat`: preserved in its reported unit and must not be relabeled as tradable-float shares.
- Current float snapshots must not be back-projected into historical periods.
- The AI Research Director may identify historical tradable-float shares as a missing variable or next-data requirement when the observed evidence justifies that research direction.
- The AI Research Director must not claim that a historical tradable-float relationship has been tested unless actual historical float-share evidence is present.

This boundary is descriptive, not scientific. It does not rank float as important, require SOL to pursue float hypotheses, define thresholds, or constrain scientific interpretation beyond accurately representing which evidence is and is not available.
