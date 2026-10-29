PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT NOT NULL,
    artifact_version INTEGER NOT NULL,
    artifact_type TEXT NOT NULL,
    schema_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    producer_json TEXT NOT NULL,
    provenance_json TEXT NOT NULL,
    lifecycle_state TEXT NOT NULL,
    persistence_class TEXT NOT NULL,
    retention_class TEXT NOT NULL,
    backup_requirement TEXT NOT NULL,
    tags_json TEXT NOT NULL,
    PRIMARY KEY (artifact_id, artifact_version)
);

CREATE TABLE IF NOT EXISTS representations (
    artifact_id TEXT NOT NULL,
    artifact_version INTEGER NOT NULL,
    locator TEXT NOT NULL UNIQUE,
    media_type TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    verification_state TEXT NOT NULL,
    PRIMARY KEY (artifact_id, artifact_version, locator),
    FOREIGN KEY (artifact_id, artifact_version)
        REFERENCES artifacts (artifact_id, artifact_version)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS relationships (
    relationship_key TEXT PRIMARY KEY,
    source_ref_json TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    target_ref_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    producer_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_relationship_source
    ON relationships (relationship_type, source_ref_json);

CREATE INDEX IF NOT EXISTS idx_relationship_target
    ON relationships (relationship_type, target_ref_json);

CREATE TABLE IF NOT EXISTS publication_records (
    artifact_id TEXT NOT NULL,
    artifact_version INTEGER NOT NULL,
    publication_state TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    PRIMARY KEY (artifact_id, artifact_version, publication_state, recorded_at),
    FOREIGN KEY (artifact_id, artifact_version)
        REFERENCES artifacts (artifact_id, artifact_version)
        ON DELETE CASCADE
);
