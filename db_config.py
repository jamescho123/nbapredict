import os

USE_SUPABASE = os.getenv('USE_SUPABASE', 'false').lower() == 'true'

if USE_SUPABASE:
    DB_CONFIG = {
        'host': 'aws-1-ap-southeast-1.pooler.supabase.com',
        'database': 'postgres',
        'user': 'postgres.mxnpfsiyaqqwdcokukij',
        'password': 'Jcjc1749!!!!',
        'port': 5432
    }
    DB_SCHEMA = 'NBA'
else:
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'James',
        'user': 'postgres',
        'password': 'jcjc1749'
    }
    DB_SCHEMA = 'NBA'

def get_connection():
    try:
        import psycopg2
        if hasattr(psycopg2, "connect"):
            return psycopg2.connect(**DB_CONFIG)
    except Exception:
        pass

    import pg8000.dbapi as pg8000
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
    if USE_SUPABASE:
        return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    else:
        return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
