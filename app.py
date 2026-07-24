# ═══════════════════════════════════════════════════════════════════
#  app.py — Punto de entrada de SolucionApp
#  CÓMO EJECUTAR: python -m streamlit run app.py
# ═══════════════════════════════════════════════════════════════════

import threading
import urllib.request
import time
import streamlit as st
from config import APP_NAME, CSS_GLOBAL
from database import inicializar_esquema
from auth import inicializar_sesion
from pantallas.selector      import pantalla_selector
from pantallas.auth_cliente  import auth_cliente, pantalla_reset_cliente
from pantallas.auth_prov     import auth_proveedor, pantalla_reset_proveedor
from pantallas.panel_cliente import panel_cliente
from pantallas.panel_prov    import panel_proveedor
from pantallas.panel_admin   import pantalla_admin


# ── KEEPALIVE — evita que Streamlit duerma la app ────────────────
# Hilo de fondo que hace una request a la app cada 4 minutos.
# No interfiere con ninguna función ni con los usuarios.
def _keepalive():
    time.sleep(30)  # espera 30 seg al arrancar para no interferir con la inicialización
    while True:
        try:
            urllib.request.urlopen(
                "https://solucionapp.streamlit.app",
                timeout=10
            )
        except Exception:
            pass  # si falla no hace nada, reintenta en 4 minutos
        time.sleep(240)  # 4 minutos

if "keepalive_started" not in st.session_state:
    st.session_state["keepalive_started"] = True
    t = threading.Thread(target=_keepalive, daemon=True)
    t.start()
# ─────────────────────────────────────────────────────────────────


st.set_page_config(page_title=APP_NAME, page_icon="🔧", layout="wide")
st.markdown(CSS_GLOBAL, unsafe_allow_html=True)

inicializar_esquema()
inicializar_sesion()

# ── ACCESO ADMIN por parámetro URL: ?admin=1 ─────────────────────
params = st.query_params
if params.get("admin") == "1":
    pantalla_admin()
    st.stop()

step = st.session_state["auth_step"]
modo = st.session_state["modo"]

if st.session_state.get("pantalla_reset"):
    if st.session_state.get("reset_modo") == "cliente": pantalla_reset_cliente()
    else:                                                pantalla_reset_proveedor()
elif step == "selector":
    pantalla_selector()
elif step == "auth":
    if   modo == "cliente":   auth_cliente()
    elif modo == "proveedor": auth_proveedor()
elif step == "panel":
    if   modo == "cliente"   and st.session_state["cliente_id"]:   panel_cliente()
    elif modo == "proveedor" and st.session_state["proveedor_id"]: panel_proveedor()
    else:
        from auth import cerrar_sesion
        cerrar_sesion()
