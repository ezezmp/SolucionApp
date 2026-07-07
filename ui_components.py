# ═══════════════════════════════════════════════════════════════════
#  ui_components.py — Componentes visuales reutilizables.
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
from config import APP_NAME, ESTADOS, LOGO_SMALL

_BADGE: dict[str, tuple[str,str]] = {
    ESTADOS["pendiente"]:          ("🟡 Pendiente",          "badge-pendiente"),
    ESTADOS["presupuestada"]:      ("🔵 Presupuestada",      "badge-presupuestada"),
    ESTADOS["aceptada"]:           ("🟢 Aceptada",           "badge-aceptada"),
    ESTADOS["rechazada"]:          ("🔴 Rechazada",          "badge-rechazada"),
    ESTADOS["turno_propuesto"]:    ("📅 Turno propuesto",    "badge-propuesto"),
    ESTADOS["turno_confirmado"]:   ("✅ Turno confirmado",   "badge-turno"),
    ESTADOS["turno_rechazado"]:    ("🔴 Turno rechazado",   "badge-rechazada"),
    ESTADOS["trabajo_completado"]: ("🏁 Trabajo completado","badge-completado"),
    ESTADOS["valorado"]:           ("⭐ Valorado",            "badge-aceptada"),
}

def badge_html(estado):
    txt, css = _BADGE.get(estado, (estado, "badge-pendiente"))
    return f'<span class="badge {css}">{txt}</span>'

def fx_header(breadcrumb, titulo):
    st.markdown(f"""
    <div class="page-header">
        <div class="page-breadcrumb">{APP_NAME} / {breadcrumb}</div>
        <div class="page-title">{titulo}</div>
    </div>""", unsafe_allow_html=True)

def btn_volver(label, key_suffix="", **cambios):
    if st.button(f"← {label}", key=f"back_{key_suffix or label.replace(' ','_')}"):
        for k, v in cambios.items():
            st.session_state[k] = v
        st.rerun()

def sidebar_brand(nombre, rol):
    st.sidebar.markdown(LOGO_SMALL, unsafe_allow_html=True)
    st.sidebar.markdown(f'<div class="sidebar-brand">🔧 {rol}</div><div class="sidebar-user">{nombre}</div>', unsafe_allow_html=True)

def render_sol_card(titulo, meta, estado=None, descripcion=None, extra_html=""):
    badge     = badge_html(estado) if estado else ""
    desc_html = f'<div style="margin-top:0.5rem;font-size:0.92rem;color:#374151">{descripcion}</div>' if descripcion else ""
    st.markdown(
        f'<div class="sol-card">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
        f'<div><div class="sol-titulo">{titulo}</div><div class="sol-meta">{meta}</div></div>'
        f'{badge}</div>{desc_html}{extra_html}</div>',
        unsafe_allow_html=True
    )

def render_presup_box(monto, detalle):
    st.markdown(f'<div class="presup-box"><div class="presup-monto">$ {monto:,.0f}</div>'
                f'<div class="presup-det">{detalle or ""}</div></div>', unsafe_allow_html=True)

def formulario_cambiar_pw(tabla, id_usuario, key_prefix):
    from auth import verificar_pw, hash_pw
    from database import get_connection
    pw_a  = st.text_input("Contraseña actual",                    type="password", key=f"{key_prefix}_a")
    pw_n  = st.text_input("Nueva contraseña (mín. 6 caracteres)", type="password", key=f"{key_prefix}_n")
    pw_n2 = st.text_input("Repetir nueva contraseña",             type="password", key=f"{key_prefix}_n2")
    if st.button("ACTUALIZAR CONTRASEÑA", type="primary", use_container_width=True, key=f"{key_prefix}_btn"):
        conn = get_connection()
        row  = conn.execute(f"SELECT password_hash FROM {tabla} WHERE id=?", (id_usuario,)).fetchone()
        if not row or not verificar_pw(pw_a, row[0]):
            st.error("La contraseña actual es incorrecta.")
        elif len(pw_n) < 6:
            st.error("Mínimo 6 caracteres.")
        elif pw_n != pw_n2:
            st.error("Las contraseñas no coinciden.")
        else:
            conn.execute(f"UPDATE {tabla} SET password_hash=? WHERE id=?", (hash_pw(pw_n), id_usuario))
            conn.commit()
            st.success("✅ Contraseña actualizada.")
