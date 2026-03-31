import os
import time
from urllib.parse import parse_qsl, unquote, urlparse

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False

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
DB_CONNECT_RETRIES = int(_env("DB_CONNECT_RETRIES", default="2"))
DB_RETRY_DELAY_SECONDS = float(_env("DB_RETRY_DELAY_SECONDS", default="0.6"))


def _clean_env_value(value):
    if value is None:
        return None
    return str(value).strip().strip("\ufeff").replace("\x00", "")


def _connection_params_from_url(database_url):
    cleaned_url = _clean_env_value(database_url)
    if not cleaned_url:
        return None

    parsed = urlparse(cleaned_url)
    if parsed.scheme not in {"postgresql", "postgres"}:
        return None

    params = {
        "host": parsed.hostname,
        "database": unquote(parsed.path.lstrip("/")) or None,
        "user": unquote(parsed.username) if parsed.username else None,
        "password": unquote(parsed.password) if parsed.password else None,
        "port": parsed.port or 5432,
    }

    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        params[key] = value

    return {key: value for key, value in params.items() if value not in (None, "")}


def _extract_supabase_project_ref(hostname):
    cleaned = _clean_env_value(hostname)
    if not cleaned:
        return None
    if cleaned.startswith("db.") and cleaned.endswith(".supabase.co"):
        return cleaned[3:].removesuffix(".supabase.co")
    if cleaned.endswith(".supabase.co") and cleaned.count(".") == 2:
        return cleaned.removesuffix(".supabase.co")
    return None


def _prefer_supabase_pooler(config):
    normalized = {
        key: _clean_env_value(value) if isinstance(value, str) else value
        for key, value in (config or {}).items()
    }

    explicit_pooler_host = _clean_env_value(_env("SUPABASE_POOLER_HOST"))
    explicit_pooler_port = _env("SUPABASE_POOLER_PORT")
    if explicit_pooler_host:
        normalized["host"] = explicit_pooler_host
        if explicit_pooler_port:
            normalized["port"] = int(explicit_pooler_port)
        normalized.setdefault("ssl_context", True)
        normalized.setdefault("timeout", 15)
        normalized.setdefault("connect_timeout", 15)
        return normalized

    host = normalized.get("host")
    project_ref = _extract_supabase_project_ref(host)
    if not project_ref:
        supabase_url = _clean_env_value(_env("SUPABASE_URL"))
        if supabase_url:
            parsed = urlparse(supabase_url)
            project_ref = _extract_supabase_project_ref(parsed.hostname)

    if not project_ref:
        return normalized

    default_pooler_host = normalized.get("host")
    if not default_pooler_host or str(default_pooler_host).startswith("db."):
        default_pooler_host = _clean_env_value(_env("DB_POOLER_HOST", default=f"{project_ref}.supabase.co"))

    normalized["host"] = default_pooler_host
    normalized["port"] = int(_env("SUPABASE_POOLER_PORT", "DB_POOLER_PORT", default="6543"))

    user = normalized.get("user")
    if user and "." not in user:
        normalized["user"] = f"{user}.{project_ref}"

    normalized.setdefault("ssl_context", True)
    normalized.setdefault("timeout", 15)
    normalized.setdefault("connect_timeout", 15)
    return normalized


def _normalized_db_config():
    return {
        key: _clean_env_value(value) if isinstance(value, str) else value
        for key, value in DB_CONFIG.items()
    }


def _is_timeout_error(error):
    message = str(error).lower()
    return any(token in message for token in ["timed out", "timeout", "can't create a connection to host"])


def _psycopg2_compatible_config(config):
    compatible = dict(config)
    compatible.pop("ssl_context", None)
    compatible.pop("timeout", None)
    return compatible


def _connect_with_pg8000(config):
    import pg8000.dbapi as pg8000

    if "database" in config and "dbname" not in config:
        config["dbname"] = config.pop("database")
    return pg8000.connect(
        host=config.get("host"),
        database=config.get("dbname"),
        user=config.get("user"),
        password=config.get("password"),
        port=config.get("port", 5432),
        timeout=config.get("timeout"),
        ssl_context=config.get("ssl_context"),
    )


def _connect_with_psycopg2(config, database_url=None):
    import psycopg2

    if database_url and config is None:
        return psycopg2.connect(database_url)
    return psycopg2.connect(**_psycopg2_compatible_config(config))


def _try_connect(config, database_url=None):
    last_error = None

    for attempt in range(DB_CONNECT_RETRIES):
        if os.name == "nt":
            try:
                return _connect_with_pg8000(dict(config) if config else None)
            except ImportError:
                pass
            except Exception as exc:
                last_error = exc
                if not _is_timeout_error(exc) or attempt == DB_CONNECT_RETRIES - 1:
                    break
                time.sleep(DB_RETRY_DELAY_SECONDS)
                continue

        try:
            return _connect_with_psycopg2(dict(config) if config else None, database_url=database_url)
        except ImportError:
            last_error = None
        except UnicodeDecodeError as exc:
            last_error = exc
        except Exception as exc:
            last_error = exc
            if not _is_timeout_error(exc) or attempt == DB_CONNECT_RETRIES - 1:
                break
            time.sleep(DB_RETRY_DELAY_SECONDS)
            continue

        try:
            return _connect_with_pg8000(dict(config) if config else None)
        except ImportError as exc:
            raise RuntimeError(
                "No PostgreSQL driver is installed. Install psycopg2-binary or pg8000."
            ) from exc
        except Exception as exc:
            last_error = exc
            if not _is_timeout_error(exc) or attempt == DB_CONNECT_RETRIES - 1:
                break
            time.sleep(DB_RETRY_DELAY_SECONDS)

    if last_error is not None:
        raise last_error

    raise RuntimeError("No PostgreSQL driver is installed. Install psycopg2-binary or pg8000.")


def get_connection():
    database_url = _clean_env_value(_env("DATABASE_URL"))
    connection_params = _prefer_supabase_pooler(_connection_params_from_url(database_url))
    normalized_config = _prefer_supabase_pooler(_normalized_db_config())
    primary_config = connection_params or normalized_config

    try:
        return _try_connect(primary_config, database_url=database_url if connection_params is None else None)
    except Exception as primary_error:
        should_fallback_local = USE_SUPABASE and _is_timeout_error(primary_error)
        if should_fallback_local:
            local_config = _normalized_db_config() if DB_CONFIG is LOCAL_DB_CONFIG else {
                key: _clean_env_value(value) if isinstance(value, str) else value
                for key, value in LOCAL_DB_CONFIG.items()
            }
            return _try_connect(local_config)
        raise


def get_connection_string():
    database_url = _clean_env_value(_env("DATABASE_URL"))
    if database_url:
        return database_url

    host = DB_CONFIG["host"]
    user = DB_CONFIG["user"]
    password = DB_CONFIG["password"]
    port = DB_CONFIG.get("port", 5432)
    database = DB_CONFIG["database"]
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"
