"""
Database Migration – Create aws_credentials table
Run directly with:
    python migrations/create_aws_credentials.py
Or import and call run_migration() from your app startup.
"""

import os
import sys

# Allow running standalone from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load .env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(env_path)


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    user = os.environ.get("DB_USERNAME", "")
    password = quote_plus(os.environ.get("DB_PASSWORD", ""))
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    db = os.environ.get("DATABASENAME_APP", "")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS aws_credentials (
    id                   SERIAL PRIMARY KEY,
    aws_access_key_id    TEXT        NOT NULL,
    aws_secret_access_key TEXT       NOT NULL,
    default_region       VARCHAR(64) NOT NULL,
    default_output_format VARCHAR(16) NOT NULL DEFAULT 'json',
    bucket_name          VARCHAR(255) NOT NULL,
    created_at           TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- Trigger to auto-update updated_at on row update
CREATE OR REPLACE FUNCTION update_aws_credentials_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'trg_aws_credentials_updated_at'
    ) THEN
        CREATE TRIGGER trg_aws_credentials_updated_at
        BEFORE UPDATE ON aws_credentials
        FOR EACH ROW EXECUTE FUNCTION update_aws_credentials_updated_at();
    END IF;
END;
$$;
"""


def run_migration():
    from sqlalchemy import create_engine, text
    engine = create_engine(get_database_url(), echo=False)
    with engine.connect() as conn:
        conn.execute(text(CREATE_TABLE_SQL))
        conn.commit()
    print("✅ aws_credentials table created / verified successfully.")


if __name__ == "__main__":
    run_migration()
