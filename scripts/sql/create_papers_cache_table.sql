-- Cache des réponses API Pappers (éviter les rappels facturés pour le même SIREN).
-- À exécuter sur PostgreSQL ≥ 12 (JSONB). Adapter le schéma si vous utilisez MySQL / autre.

CREATE TABLE IF NOT EXISTS papers (
    id              BIGSERIAL PRIMARY KEY,
    siren           CHAR(9) NOT NULL,
    expert_id       TEXT,
    http_status     INTEGER,
    api_path        TEXT NOT NULL DEFAULT '/v2/entreprise',
    payload_json    JSONB NOT NULL,
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE papers IS
    'Réponses brutes API Pappers (entreprise par SIREN) ; historique ou upsert selon politique applicative.';

COMMENT ON COLUMN papers.payload_json IS
    'Corps JSON intégral renvoyé par Pappers (toutes les clés conservées).';

COMMENT ON COLUMN papers.expert_id IS
    'Lien optionnel vers l’artisan SÉRÉNO ayant déclenché la recherche (pas de FK imposée en pilote).';

CREATE INDEX IF NOT EXISTS idx_papers_siren_fetched
    ON papers (siren, fetched_at DESC);

CREATE INDEX IF NOT EXISTS idx_papers_expert
    ON papers (expert_id)
    WHERE expert_id IS NOT NULL AND expert_id <> '';

CREATE INDEX IF NOT EXISTS idx_papers_payload_gin
    ON papers USING GIN (payload_json jsonb_path_ops);

-- Optionnel : une seule ligne « courante » par SIREN
-- ALTER TABLE papers ADD CONSTRAINT papers_siren_key UNIQUE (siren);
-- INSERT ... ON CONFLICT (siren) DO UPDATE SET payload_json = EXCLUDED.payload_json, fetched_at = now();
