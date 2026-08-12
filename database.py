from sqlalchemy import create_engine
from urllib.parse import quote_plus


# ============================================================
# SUPABASE POSTGRESQL CONNECTION
# ============================================================

SUPABASE_HOST = "aws-0-ap-northeast-1.pooler.supabase.com"
SUPABASE_PORT = 5432
SUPABASE_DATABASE = "postgres"
SUPABASE_USER = "postgres.hbxsfehykzpfeesmrxhc"

# IMPORTANT:
# Put your actual Supabase database password here.
SUPABASE_PASSWORD = "Sada@8febsnp"


connection_url = (
    f"postgresql+psycopg2://"
    f"{quote_plus(SUPABASE_USER)}:"
    f"{quote_plus(SUPABASE_PASSWORD)}@"
    f"{SUPABASE_HOST}:"
    f"{SUPABASE_PORT}/"
    f"{SUPABASE_DATABASE}"
)


engine = create_engine(
    connection_url,
    pool_pre_ping=True
)


print("Supabase PostgreSQL database connection successful.")