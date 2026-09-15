# MTS v4 Nexus Durability Repair — 2026-09-15

## Status

Human-authorized implementation repair. This does not amend the Research Nexus architecture.

## Defect

MTS v4 Research Director campaign runners currently persist scientific state to campaign-local `research_nexus.json` files. The canonical `Core/research_nexus` implementation exists, but the audited Mac repository contained no canonical Class-II payload/database state. Campaign-local state therefore remained dependent on campaign/server survival unless separately copied.

## Governing boundary

`Architecture/RESEARCH_NEXUS_ARCHITECTURE.md` remains authoritative:

- Class I system/governance assets: Git.
- Class II durable research/knowledge/provenance assets: Research Nexus; Git prohibited except deliberate fixtures/examples; independent backup required.
- Class III reproducible/transient working data: not Git-tracked and normally not backed up.

## Phase 1 durability bridge

`scripts/import_campaign_nexus_to_canonical.py` provides a fail-closed, idempotent bridge for existing `MTS_V4_RESEARCH_NEXUS_V1` campaign state.

It:

1. validates the campaign Nexus format;
2. rejects a canonical destination inside a Git working tree;
3. hashes the source with SHA-256;
4. stores an immutable content-addressed copy under the independent canonical root;
5. records subject/count metadata in a SQLite durability manifest;
6. reads the stored object back and verifies its hash before reporting success;
7. treats an identical re-import as idempotent;
8. fails closed on manifest/object integrity mismatch.

This bridge deliberately preserves the original campaign Nexus byte-for-byte. It does not reinterpret, promote, merge, or scientifically upgrade findings.

## Mac canonical root

For the current single-user deployment, use a persistent Class-II root outside the Git repository:

`~/Documents/MTS_V4_Nexus`

This is an implementation location, not logical artifact identity.

## XOM recovery first

After pulling this branch locally, import the recovered XOM Nexus:

```bash
cd ~/Documents/Momentum-Trading-System_v4
python3 scripts/import_campaign_nexus_to_canonical.py \
  --source ~/Downloads/XOM_research_nexus_RESTORED_20260915.json \
  --canonical-root ~/Documents/MTS_V4_Nexus
```

Expected XOM audit characteristics from the recovered source are one XOM subject, three findings, sixteen evidence-metadata records, and 194 analysis-result-metadata records. The importer reports actual counts from the source; discrepancies must be investigated rather than normalized.

## Independent backup

The canonical root still requires an independent backup destination. Do not delete campaign/server originals merely because the local import succeeded until that independent backup is configured and verified.

## Next implementation phase

After XOM import verification:

1. reconcile/import surviving historical campaign Nexus state;
2. add a governed sync/publish step to campaign checkpoint/completion so Class-II state is durably acknowledged before cleanup;
3. configure and verify independent backup of the canonical root;
4. add tests for interrupted copy, corrupt source, duplicate import, object corruption, and Git-root rejection;
5. only then resume paid Research Director campaigns.

Research Packages not embedded in a campaign `research_nexus.json` require a separate governed artifact importer; they must not be silently dropped or copied into the canonical root without registration.
