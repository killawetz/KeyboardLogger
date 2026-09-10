import logging
import sqlite3

logger = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 1

def get_connection(db_path: str = "app.db") -> sqlite3.Connection:
    logger.info("opening sqlite connection: %s", db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")

    current_version = conn.execute("PRAGMA user_version;").fetchone()[0]
    if current_version == 0:
        apply_schema(conn)
    elif current_version < CURRENT_SCHEMA_VERSION:
        logger.warning(
            "The %s version of the database is outdated; Version %s is expected — manual migration is required.",
            current_version, CURRENT_SCHEMA_VERSION
        )

    return conn

def apply_schema(conn: sqlite3.Connection, schema_path: str = "schema.sql"):
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.execute(f"PRAGMA user_version = {CURRENT_SCHEMA_VERSION}")
    conn.commit()
    logger.info("Schema applied, version=%s", CURRENT_SCHEMA_VERSION)