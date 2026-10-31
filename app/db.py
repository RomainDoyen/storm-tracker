import os
import threading
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.conninfo import conninfo_to_dict, make_conninfo

load_dotenv()

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "db" / "migrations" / "001_cyclones.sql"
_lock = threading.Lock()
_conninfo = None
_ready = False

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
    return _ready or bool(os.getenv("DATABASE_URL"))


def reset_after_fork():
    """Le pool et ses fils ne survivent pas au fork de Gunicorn."""
    global _lock, _conninfo, _ready
    _lock = threading.Lock()
    _conninfo = None
    _ready = False


def _conninfo_from(url, channel_binding):
    info = conninfo_to_dict(url)
    info["channel_binding"] = channel_binding
    info["sslmode"] = "require"
    info["connect_timeout"] = "15"
    info["gssencmode"] = "disable"
    return make_conninfo(**info)


def _candidates():
    pooled = os.getenv("DATABASE_URL")
    direct = os.getenv("DATABASE_URL_UNPOOLED")
    found = []
    if pooled:
        found.append(("pooler", _conninfo_from(pooled, "disable")))
    if direct:
        found.append(("direct", _conninfo_from(direct, "prefer")))
    return found


def ensure_database():
    """Ouvre une connexion neuve pour choisir une URL, puis crée la table."""
    global _conninfo, _ready
    if _ready and _conninfo:
        return True
    with _lock:
        if _ready and _conninfo:
            return True
        candidates = _candidates()
        if not candidates:
            print("⚠️  DATABASE_URL absent")
            return False
        schema = _SCHEMA_PATH.read_text(encoding="utf-8")
        for label, info in candidates:
            try:
                with psycopg.connect(info, autocommit=True, prepare_threshold=None) as conn:
                    conn.execute(schema)
                _conninfo = info
                _ready = True
                print(f"✅ Neon Postgres prêt ({label})")
                return True
            except Exception as error:
                print(f"⚠️  {label} refusé : {type(error).__name__}")
        return False


def _connect():
    if not ensure_database():
        raise RuntimeError("Neon indisponible")
    return psycopg.connect(_conninfo, prepare_threshold=None)


def list_cyclones():
    if not ensure_database():
        return []
    with _connect() as conn:
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
    if not ensure_database():
        return False
    records = [_record(storm) for storm in storms]
    with _connect() as conn:
        with conn.transaction():
            conn.execute("DELETE FROM cyclones")
            if records:
                with conn.cursor() as cur:
                    cur.executemany(_INSERT, records)
    return True
