# ═══════════════════════════════════════════════════════════════════
#  database.py
#  FUNCIÓN: Base de datos — conexión a PostgreSQL (Supabase)
#  Los datos persisten siempre, no se borran al reiniciar la app.
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
import psycopg2
import psycopg2.extras
import os


# ── CONEXIÓN A SUPABASE (PostgreSQL) ────────────────────────────
@st.cache_resource
def get_connection():
    """
    CONEXIÓN ÚNICA — se conecta a Supabase via Transaction Pooler.
    Más estable desde Streamlit Cloud que la conexión directa.
    """
    import os
    def _get_secret(key, fb=""):
        try:    return st.secrets[key]
        except: return os.environ.get(key, fb)

    password = _get_secret("DB_PASSWORD", "")
    url = f"postgresql://postgres.mwhuzbrfvwuqdjjpzkdk:{password}@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

    conn = psycopg2.connect(url, sslmode="require")
    conn.autocommit = False
    return conn


def ejecutar(sql: str, params=None, fetch=None):
    """
    EJECUTAR QUERY — función central para todas las consultas.
    fetch: None = solo ejecutar, "one" = un resultado, "all" = todos
    Reconecta automáticamente si la conexión se cortó.
    """
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        if fetch == "one":
            return cur.fetchone()
        if fetch == "all":
            return cur.fetchall()
        conn.commit()
        return None
    except psycopg2.OperationalError:
        # Reconectar si la conexión expiró
        st.cache_resource.clear()
        conn = get_connection()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        if fetch == "one":  return cur.fetchone()
        if fetch == "all":  return cur.fetchall()
        conn.commit()
        return None


# ── CREAR TABLAS ─────────────────────────────────────────────────
def inicializar_esquema() -> None:
    """Crea todas las tablas si no existen. Seguro de llamar siempre."""
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id            SERIAL PRIMARY KEY,
        nombre        TEXT NOT NULL,
        apellido      TEXT NOT NULL,
        dni           TEXT UNIQUE NOT NULL,
        domicilio     TEXT,
        email         TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL DEFAULT '',
        reset_token   TEXT,
        reset_expiry  TEXT,
        foto_perfil   TEXT
    );

    CREATE TABLE IF NOT EXISTS proveedores (
        id            SERIAL PRIMARY KEY,
        razon_social  TEXT NOT NULL,
        rubros        TEXT NOT NULL,
        grupo         TEXT NOT NULL DEFAULT 'Sin grupo',
        cuit          TEXT UNIQUE NOT NULL,
        direccion     TEXT,
        encargado     TEXT,
        contacto      TEXT,
        email         TEXT UNIQUE,
        password_hash TEXT NOT NULL DEFAULT '',
        reset_token   TEXT,
        reset_expiry  TEXT,
        latitud       REAL,
        longitud      REAL,
        foto_perfil   TEXT
    );

    CREATE TABLE IF NOT EXISTS solicitudes (
        id                  SERIAL PRIMARY KEY,
        cliente_id          INTEGER NOT NULL REFERENCES clientes(id),
        proveedor_id        INTEGER NOT NULL REFERENCES proveedores(id),
        grupo               TEXT,
        marca               TEXT,
        modelo              TEXT,
        anio                TEXT,
        descripcion         TEXT,
        email_cliente       TEXT,
        estado              TEXT NOT NULL DEFAULT 'pendiente',
        monto_presupuesto   REAL,
        detalle_presupuesto TEXT,
        fecha_turno         TEXT,
        hora_turno          TEXT,
        foto_antes          TEXT,
        foto_despues        TEXT,
        fecha_creacion      TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS turno_opciones (
        id           SERIAL PRIMARY KEY,
        solicitud_id INTEGER NOT NULL REFERENCES solicitudes(id),
        fecha        TEXT NOT NULL,
        hora         TEXT NOT NULL,
        estado       TEXT NOT NULL DEFAULT 'propuesta'
    );

    CREATE TABLE IF NOT EXISTS valoraciones (
        id           SERIAL PRIMARY KEY,
        solicitud_id INTEGER NOT NULL UNIQUE REFERENCES solicitudes(id),
        cliente_id   INTEGER NOT NULL REFERENCES clientes(id),
        proveedor_id INTEGER NOT NULL REFERENCES proveedores(id),
        estrellas    INTEGER NOT NULL CHECK(estrellas BETWEEN 1 AND 5),
        comentario   TEXT,
        fecha        TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS canon_cobros (
        id           SERIAL PRIMARY KEY,
        solicitud_id INTEGER NOT NULL REFERENCES solicitudes(id),
        tipo         TEXT NOT NULL CHECK(tipo IN ('usuario','profesional')),
        monto        REAL NOT NULL,
        estado       TEXT NOT NULL DEFAULT 'pendiente',
        referencia   TEXT,
        fecha        TIMESTAMP DEFAULT NOW(),
        UNIQUE(solicitud_id, tipo)
    );

    CREATE TABLE IF NOT EXISTS rubros_personalizados (
        id           SERIAL PRIMARY KEY,
        grupo        TEXT NOT NULL,
        nombre       TEXT NOT NULL,
        agregado_por INTEGER REFERENCES proveedores(id),
        fecha        TIMESTAMP DEFAULT NOW(),
        UNIQUE(grupo, nombre)
    );
    """)
    conn.commit()
    cur.close()


# ── RUBROS DINÁMICOS ─────────────────────────────────────────────
def get_rubros(grupo: str) -> list:
    """OBTENER RUBROS — fijos + personalizados para un grupo."""
    from config import CATEGORIAS
    fijos  = CATEGORIAS.get(grupo, [])
    custom = ejecutar(
        "SELECT nombre FROM rubros_personalizados WHERE grupo=%s ORDER BY nombre",
        (grupo,), fetch="all"
    ) or []
    custom_nombres = [r["nombre"] for r in custom]
    otros = [r for r in fijos if r.startswith("Otro")]
    base  = [r for r in fijos if not r.startswith("Otro")]
    return base + [r for r in custom_nombres if r not in fijos] + otros


def agregar_rubro_personalizado(grupo: str, nombre: str, proveedor_id: int) -> bool:
    """AGREGAR RUBRO — guarda un rubro nuevo. Retorna True si se agregó."""
    try:
        ejecutar(
            "INSERT INTO rubros_personalizados (grupo,nombre,agregado_por) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
            (grupo, nombre.strip().title(), proveedor_id)
        )
        return True
    except Exception:
        return False
