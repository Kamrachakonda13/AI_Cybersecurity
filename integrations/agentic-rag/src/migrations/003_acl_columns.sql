-- Migration 003: ACL columns for federated search
--
-- Adds the columns needed for the ACL filter:
--   owner_team   - the team that owns the canonical document
--   share_scope  - "team" | "org" | JSON array of teams
--   acl          - JSONB array of explicit principal grants

ALTER TABLE chunks ADD COLUMN IF NOT EXISTS owner_team TEXT DEFAULT 'unknown';
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS share_scope JSONB DEFAULT '"team"'::jsonb;
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS acl JSONB DEFAULT '[]'::jsonb;

CREATE INDEX IF NOT EXISTS chunks_owner_team_idx ON chunks (owner_team);
CREATE INDEX IF NOT EXISTS chunks_share_scope_idx ON chunks USING GIN (share_scope);
CREATE INDEX IF NOT EXISTS chunks_acl_idx ON chunks USING GIN (acl);
