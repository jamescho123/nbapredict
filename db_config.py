import os

from dotenv import load_dotenv

load_dotenv()


def _env(*names, default=None):
    for name in names:
        value = os.getenv(name)
        if value not in (None, ""):
            return value
    return default


def _is_true(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _running_on_streamlit_cloud():
    return os.name != "nt" and _env("HOME", "").startswith("/home/adminuser")


def _resolve_use_supabase():
    explicit = os.getenv("USE_SUPABASE")
    if explicit is not None:
        return _is_true(explicit)
    if _env("DATABASE_URL", "DB_HOST", "PGHOST", "POSTGRES_HOST", "host"):
        return True
    return _running_on_streamlit_cloud()


USE_SUPABASE = _resolve_use_supabase()


LOCAL_DB_CONFIG = {
    "host": _env("LOCAL_DB_HOST", default="localhost"),
    "database": _env("LOCAL_DB_NAME", default="James"),
    "user": _env("LOCAL_DB_USER", default="postgres"),
    "password": _env("LOCAL_DB_PASSWORD", default="jcjc1749"),
    "port": int(_env("LOCAL_DB_PORT", default="5432")),
}


SUPABASE_DB_CONFIG = {
    "host": _env("DB_HOST", "PGHOST", "POSTGRES_HOST", "host", default="aws-1-ap-southeast-1.pooler.supabase.com"),
    "database": _env("DB_NAME", "PGDATABASE", "POSTGRES_DB", "dbname", default="postgres"),
    "user": _env("DB_USER", "PGUSER", "POSTGRES_USER", "user", default="postgres.mxnpfsiyaqqwdcokukij"),
    "password": _env("DB_PASSWORD", "PGPASSWORD", "POSTGRES_PASSWORD", "password", default="Jcjc1749!!!!"),
    "port": int(_env("DB_PORT", "PGPORT", "POSTGRES_PORT", "port", default="5432")),
}


DB_CONFIG = SUPABASE_DB_CONFIG if USE_SUPABASE else LOCAL_DB_CONFIG
DB_SCHEMA = _env("DB_SCHEMA", default="NBA")


def get_connection():
    database_url = _env("DATABASE_URL")
    try:
        import psycopg2
    except ImportError:
        psycopg2 = None

    if psycopg2 is not None:
        if database_url:
            return psycopg2.connect(database_url)
        return psycopg2.connect(**DB_CONFIG)

    try:
        import pg8000.dbapi as pg8000
    except ImportError as exc:
        raise RuntimeError(
            "No PostgreSQL driver is installed. Install psycopg2-binary or pg8000."
        ) from exc

    config = dict(DB_CONFIG)
    if "database" in config and "dbname" not in config:
        config["dbname"] = config.pop("database")
    return pg8000.connect(
        host=config.get("host"),
        database=config.get("dbname"),
        user=config.get("user"),
        password=config.get("password"),
        port=config.get("port", 5432),
    )


def get_connection_string():
    database_url = _env("DATABASE_URL")
    if database_url:
        return database_url

    host = DB_CONFIG["host"]
    user = DB_CONFIG["user"]
    password = DB_CONFIG["password"]
    port = DB_CONFIG.get("port", 5432)
    database = DB_CONFIG["database"]
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"
