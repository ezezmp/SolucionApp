# ═══════════════════════════════════════════════════════════════════
#  auth.py — Seguridad, validaciones, sesión y tokens.
# ═══════════════════════════════════════════════════════════════════

import re, hashlib, secrets
import streamlit as st
from datetime import datetime, timedelta
from database import ejecutar

_EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
_DNI_RE   = re.compile(r"^\d{7,8}$")
_CUIT_RE  = re.compile(r"^\d{11}$")

def validar_email(e):  return bool(e and _EMAIL_RE.match(e.strip()))
def validar_dni(d):    return bool(d and _DNI_RE.match(limpiar_dni(d)))
def validar_cuit(c):   return bool(_CUIT_RE.match(limpiar_cuit(c)))
def limpiar_cuit(c):   return c.strip().replace("-","").replace(".","")
def limpiar_dni(d):    return d.strip().replace(".","").replace(",","")
def sanitizar(t,n=500):return t.strip()[:n] if t else ""

def hash_pw(pw, sal=None):
    if sal is None: sal = secrets.token_hex(16)
    d = hashlib.pbkdf2_hmac("sha256", pw.encode(), sal.encode(), 260_000)
    return f"{sal}${d.hex()}"

def verificar_pw(pw, stored):
    if not stored: return False
    if "$" not in stored:
        return hashlib.sha256(pw.encode()).hexdigest() == stored
    sal, _ = stored.split("$", 1)
    return hash_pw(pw, sal) == stored

def es_hash_antiguo(stored): return "$" not in stored

EXPIRY_MIN = 30
def generar_token_reset():
    token  = secrets.token_urlsafe(32)
    expiry = (datetime.now() + timedelta(minutes=EXPIRY_MIN)).isoformat()
    return token, expiry

def token_valido(expiry_str):
    if not expiry_str: return False
    try:    return datetime.fromisoformat(str(expiry_str)) > datetime.now()
    except: return False

_DEFAULTS = {
    "modo": None, "auth_step": "selector",
    "cliente_id": None, "cliente_nombre": "",
    "proveedor_id": None, "proveedor_nombre": "",
    "prov_seleccionado": None, "resultados_busq": [],
    "grupo_buscado": "", "cat_buscada": "",
    "mostrar_reg_usuario": False, "mostrar_reg_especialista": False,
    "pantalla_reset": False, "reset_modo": None,
    "admin_logueado": False,
}

def inicializar_sesion():
    for k, v in _DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v

def cerrar_sesion():
    for k, v in _DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()

def login_cliente(email, password):
    row = ejecutar(
        "SELECT id,nombre,apellido,password_hash FROM clientes WHERE email=%s",
        (email.strip().lower(),), fetch="one"
    )
    if not row:        return False, "Email o contraseña incorrectos."
    if not row["password_hash"]: return False, "Cuenta sin contraseña."
    if not verificar_pw(password, row["password_hash"]): return False, "Email o contraseña incorrectos."
    if es_hash_antiguo(row["password_hash"]):
        ejecutar("UPDATE clientes SET password_hash=%s WHERE id=%s",
                 (hash_pw(password), row["id"]))
    st.session_state.update({
        "cliente_id":     row["id"],
        "cliente_nombre": f"{row['nombre']} {row['apellido']}",
        "auth_step":      "panel"
    })
    return True, ""

def login_proveedor(email, password):
    row = ejecutar(
        "SELECT id,razon_social,password_hash FROM proveedores WHERE email=%s",
        (email.strip().lower(),), fetch="one"
    )
    if not row:    return False, "Email o contraseña incorrectos."
    if not row["password_hash"]: return False, "Empresa de versión anterior."
    if not verificar_pw(password, row["password_hash"]): return False, "Email o contraseña incorrectos."
    if es_hash_antiguo(row["password_hash"]):
        ejecutar("UPDATE proveedores SET password_hash=%s WHERE id=%s",
                 (hash_pw(password), row["id"]))
    st.session_state.update({
        "proveedor_id":     row["id"],
        "proveedor_nombre": row["razon_social"],
        "auth_step":        "panel"
    })
    return True, ""
