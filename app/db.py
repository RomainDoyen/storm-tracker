import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "db" / "migrations" / "001_cyclones.sql"
_pool = None

_INSERT = """
INSERT INTO cyclones (
    id_cyclone, name, vmax, mslp, lat, lon,
    classification, basin, is_invest, source, last_update
) VALUES (
    %(id_cyclone)s, %(name)s, %(vmax)s, %(mslp)s, %(lat)s, %(lon)s,
    %(classification)s, %(basin)s, %(is_invest)s, %(source)s, %(last_update)s
)
"""


def _record(storm):
    return {
        "id_cyclone": storm["idCyclone"],
        "name": storm["name"],
        "vmax": storm["vmax"],
        "mslp": storm["mslp"],
        "lat": storm["lat"],
        "lon": storm["lon"],
        "classification": storm["classification"],
        "basin": storm["basin"],
        "is_invest": bool(storm.get("is_invest")),
        "source": storm.get("source") or "",
        "last_update": storm.get("last_update") or "",
    }


def _to_api(row):
    return {
        "idCyclone": row[0],
        "name": row[1],
        "vmax": row[2],
        "mslp": row[3],
        "lat": row[4],
        "lon": row[5],
        "classification": row[6],
        "basin": row[7],
        "is_invest": row[8],
        "source": row[9],
        "last_update": row[10],
    }


def database_available():
    return _pool is not None


def init_database():
    """Crée la table via la connexion directe, puis ouvre un pool sur l'URL mutualisée."""
    global _pool
    if _pool is not None:
        return True

    pooled = os.getenv("DATABASE_URL")
    direct = os.getenv("DATABASE_URL_UNPOOLED")
    if not pooled or not direct:
        print("⚠️  DATABASE_URL absent")
        return False

    try:
        schema = _SCHEMA_PATH.read_text(encoding="utf-8")
        with psycopg.connect(direct, autocommit=True, prepare_threshold=None) as conn:
            conn.execute(schema)
        _pool = ConnectionPool(
            conninfo=pooled,
            min_size=0,
            max_size=4,
            kwargs={"prepare_threshold": None},
            open=True,
        )
        print("✅ Neon Postgres prêt")
        return True
    except Exception as error:
        _pool = None
        print(f"⚠️  Neon indisponible : {type(error).__name__}")
        return False


def list_cyclones():
    if _pool is None:
        return []
    with _pool.connection() as conn:
        rows = conn.execute(
            """
            SELECT id_cyclone, name, vmax, mslp, lat, lon,
                   classification, basin, is_invest, source, last_update
            FROM cyclones
            ORDER BY name
            """
        ).fetchall()
    return [_to_api(row) for row in rows]


def replace_cyclones(storms):
    """Remplace tout le stock dans une seule transaction."""
    if _pool is None:
        return False
    records = [_record(storm) for storm in storms]
    with _pool.connection() as conn:
        with conn.transaction():
            conn.execute("DELETE FROM cyclones")
            if records:
                with conn.cursor() as cur:
                    cur.executemany(_INSERT, records)
    return True


init_database()
