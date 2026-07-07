# ═══════════════════════════════════════════════════════════════════
#  app.py — Punto de entrada de SolucionApp.
#
#  CÓMO EJECUTAR:
#    cd solucionapp
#    python -m streamlit run app.py
#
#  SECRETS (crear .streamlit/secrets.toml):
#    EMAIL_REMITENTE = "tumail@gmail.com"
#    EMAIL_PASSWORD  = "xxxx xxxx xxxx xxxx"
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
from config import APP_NAME, CSS_GLOBAL
from database import inicializar_esquema
from auth import inicializar_sesion
from pantallas.selector     import pantalla_selector
from pantallas.auth_cliente import auth_cliente, pantalla_reset_cliente
from pantallas.auth_prov    import auth_proveedor, pantalla_reset_proveedor
from pantallas.panel_cliente import panel_cliente
from pantallas.panel_prov    import panel_proveedor

st.set_page_config(page_title=APP_NAME, page_icon="🔧", layout="wide")
st.markdown(CSS_GLOBAL, unsafe_allow_html=True)
inicializar_esquema()
inicializar_sesion()

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
