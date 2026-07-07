# ═══════════════════════════════════════════════════════════════════
#  database.py
#  FUNCIÓN: Base de datos — conexión y estructura de tablas
# ═══════════════════════════════════════════════════════════════════

import sqlite3
import streamlit as st


# ── CONEXIÓN ─────────────────────────────────────────────────────
@st.cache_resource
def get_connection() -> sqlite3.Connection:
    """Retorna la conexión única a la base de datos."""
    c = sqlite3.connect("solucionapp.db", check_same_thread=False)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA foreign_keys=ON")
    return c


def get_cursor() -> sqlite3.Cursor:
    return get_connection().cursor()


# ── CREAR TABLAS ─────────────────────────────────────────────────
def inicializar_esquema() -> None:
    """Crea todas las tablas si no existen y ejecuta migraciones."""
    conn = get_connection()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS clientes (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre        TEXT NOT NULL,
        apellido      TEXT NOT NULL,
        dni           TEXT UNIQUE NOT NULL,
        domicilio     TEXT,
        email         TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL DEFAULT '',
        reset_token   TEXT,
        reset_expiry  TEXT
    );

    CREATE TABLE IF NOT EXISTS proveedores (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
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
        longitud      REAL
    );

    CREATE TABLE IF NOT EXISTS solicitudes (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
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
        fecha_creacion      TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS turno_opciones (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        solicitud_id INTEGER NOT NULL REFERENCES solicitudes(id),
        fecha        TEXT NOT NULL,
        hora         TEXT NOT NULL,
        estado       TEXT NOT NULL DEFAULT 'propuesta'
    );

    CREATE TABLE IF NOT EXISTS valoraciones (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        solicitud_id INTEGER NOT NULL UNIQUE REFERENCES solicitudes(id),
        cliente_id   INTEGER NOT NULL REFERENCES clientes(id),
        proveedor_id INTEGER NOT NULL REFERENCES proveedores(id),
        estrellas    INTEGER NOT NULL CHECK(estrellas BETWEEN 1 AND 5),
        comentario   TEXT,
        fecha        TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS canon_cobros (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        solicitud_id INTEGER NOT NULL REFERENCES solicitudes(id),
        tipo         TEXT NOT NULL CHECK(tipo IN ('usuario','profesional')),
        monto        REAL NOT NULL,
        estado       TEXT NOT NULL DEFAULT 'pendiente',
        referencia   TEXT,
        fecha        TEXT DEFAULT (datetime('now','localtime')),
        UNIQUE(solicitud_id, tipo)
    );

    CREATE TABLE IF NOT EXISTS rubros_personalizados (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        grupo        TEXT NOT NULL,
        nombre       TEXT NOT NULL,
        agregado_por INTEGER REFERENCES proveedores(id),
        fecha        TEXT DEFAULT (datetime('now','localtime')),
        UNIQUE(grupo, nombre)
    );
    """)
    conn.commit()
    _migraciones(conn)


# ── AGREGAR COLUMNA (migración segura) ───────────────────────────
def _col(conn, tabla, col, tipo="TEXT"):
    """Agrega una columna si no existe — migración segura."""
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({tabla})").fetchall()]
    if col not in cols:
        conn.execute(f"ALTER TABLE {tabla} ADD COLUMN {col} {tipo.replace('NOT NULL','').strip()}")
        conn.commit()


# ── MIGRACIONES ──────────────────────────────────────────────────
def _migraciones(conn):
    """Actualiza bases de datos antiguas con columnas nuevas."""
    for col, tipo in [
        ("rubros","TEXT DEFAULT ''"), ("grupo","TEXT DEFAULT 'Sin grupo'"),
        ("email","TEXT"), ("contacto","TEXT"), ("reset_token","TEXT"),
        ("reset_expiry","TEXT"), ("latitud","REAL"), ("longitud","REAL"),
    ]:
        _col(conn, "proveedores", col, tipo)
    for col, tipo in [
        ("password_hash","TEXT DEFAULT ''"), ("reset_token","TEXT"), ("reset_expiry","TEXT"),
    ]:
        _col(conn, "clientes", col, tipo)
    for col, tipo in [
        ("foto_antes","TEXT"), ("foto_despues","TEXT"), ("grupo","TEXT"),
    ]:
        _col(conn, "solicitudes", col, tipo)


# ── RUBROS DINÁMICOS ─────────────────────────────────────────────
def get_rubros(grupo: str) -> list:
    """
    OBTENER RUBROS — retorna rubros fijos + personalizados para un grupo.
    Los rubros personalizados los agregan los especialistas al registrarse.
    """
    from config import CATEGORIAS
    conn   = get_connection()
    fijos  = CATEGORIAS.get(grupo, [])
    custom = [r[0] for r in conn.execute(
        "SELECT nombre FROM rubros_personalizados WHERE grupo=? ORDER BY nombre",
        (grupo,)
    ).fetchall()]
    # Mantener "Otro" al final, agregar personalizados en el medio
    otros = [r for r in fijos if r.startswith("Otro")]
    base  = [r for r in fijos if not r.startswith("Otro")]
    return base + [r for r in custom if r not in fijos] + otros


def agregar_rubro_personalizado(grupo: str, nombre: str, proveedor_id: int) -> bool:
    """
    AGREGAR RUBRO — guarda un rubro nuevo en la base de datos.
    Retorna True si se agregó, False si ya existía.
    """
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO rubros_personalizados (grupo,nombre,agregado_por) VALUES (?,?,?)",
            (grupo, nombre.strip().title(), proveedor_id)
        )
        conn.commit()
        return True
    except Exception:
        return False  # ya existía (UNIQUE constraint)
