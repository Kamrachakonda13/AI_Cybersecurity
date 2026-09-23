-- Migration 002: Enterprise ingestion columns
--
-- Adds the columns needed by the Phase 6 ingestion pipeline:
--   source_system       - which connector produced this chunk
--   alternate_sources   - JSONB array of alternate source references
--   fingerprint         - content fingerprint of the parent document
--   deleted_at          - soft-delete timestamp (NULL = active)
--
-- All ALTERs are idempotent: they use IF NOT EXISTS so re-running is safe.

ALTER TABLE chunks ADD COLUMN IF NOT EXISTS source_system TEXT;
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS alternate_sources JSONB DEFAULT '[]'::jsonb;
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS fingerprint TEXT;
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS chunks_source_system_idx ON chunks (source_system);
CREATE INDEX IF NOT EXISTS chunks_fingerprint_idx ON chunks (fingerprint);
CREATE INDEX IF NOT EXISTS chunks_deleted_at_idx ON chunks (deleted_at)
    WHERE deleted_at IS NULL;
