CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS chunks;
DROP TABLE IF EXISTS audit_log;

CREATE TABLE chunks (
    id                TEXT PRIMARY KEY,
    source_file       TEXT NOT NULL,
    chunk_index       INTEGER NOT NULL,
    content           TEXT NOT NULL,
    embedding         vector(384) NOT NULL,
    clearance_level   TEXT NOT NULL CHECK (clearance_level IN
                        ('PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED')),
    tenant_id         TEXT NOT NULL
);

CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE INDEX chunks_clearance_idx ON chunks (clearance_level);
CREATE INDEX chunks_tenant_idx ON chunks (tenant_id);

DROP TABLE IF EXISTS audit_log;

CREATE TABLE audit_log (
    id                 SERIAL PRIMARY KEY,
    ts                 TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id            TEXT NOT NULL,
    role               TEXT NOT NULL,
    tenant_id          TEXT NOT NULL,
    query              TEXT NOT NULL,
    route              TEXT,
    returned_chunk_ids TEXT[] NOT NULL,
    refused            BOOLEAN NOT NULL DEFAULT FALSE,
    reason             TEXT,
    prompt_tokens      INTEGER,
    completion_tokens  INTEGER,
    latency_ms         INTEGER
);

CREATE INDEX audit_log_ts_idx ON audit_log (ts DESC);
CREATE INDEX audit_log_user_idx ON audit_log (user_id);
CREATE INDEX audit_log_route_idx ON audit_log (route);