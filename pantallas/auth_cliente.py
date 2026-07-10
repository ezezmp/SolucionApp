# ═══════════════════════════════════════════════════════════════════
#  pantallas/auth_cliente.py — Login, registro y recupero usuario.
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
from config import LOGO_BIG, APP_NAME
from auth import login_cliente, validar_email, validar_dni, limpiar_dni, sanitizar, hash_pw, generar_token_reset, token_valido
from database import get_connection
from email_utils import enviar_email, email_bienvenida_cliente, email_reset_password
from ui_components import fx_header, btn_volver

def auth_cliente():
    st.markdown(LOGO_BIG, unsafe_allow_html=True)
    fx_header("USUARIO", "ACCESO")
    btn_volver("Volver al inicio", key_suffix="auth_cli", modo=None, auth_step="selector")
    st.write("")
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("#### Iniciá sesión")
        email_l = st.text_input("Email", key="cli_login_email", placeholder="ejemplo@mail.com")
        pw_l    = st.text_input("Contraseña", type="password", key="cli_login_pw")
        st.write("")
        if st.button("INGRESAR", type="primary", use_container_width=True, key="cli_btn_login"):
            if not validar_email(email_l): st.error("Ingresá un email válido.")
            elif not pw_l:                 st.error("Ingresá tu contraseña.")
            else:
                ok, msg = login_cliente(email_l, pw_l)
                if not ok: st.error(msg)
                else:      st.rerun()
        st.markdown('<div class="reg-sep">¿Olvidaste tu contraseña?</div>', unsafe_allow_html=True)
        if st.button("RECUPERAR CONTRASEÑA", use_container_width=True, key="cli_rec_pw"):
            st.session_state.update({"pantalla_reset": True, "reset_modo": "cliente"})
            st.rerun()
        st.markdown('<div class="reg-sep">¿No tenés cuenta?</div>', unsafe_allow_html=True)
        if not st.session_state.get("mostrar_reg_usuario"):
            if st.button("REGISTRATE", use_container_width=True, key="cli_show_reg"):
                st.session_state["mostrar_reg_usuario"] = True
                st.rerun()
        else:
            btn_volver("Volver al login", key_suffix="collapse_reg_cli", mostrar_reg_usuario=False)
            st.markdown("#### Crear cuenta")
            _registro_usuario()

def _registro_usuario():
    st.write("")
    c1, c2 = st.columns(2)
    with c1: nombre_r   = st.text_input("Nombre *",   key="cli_reg_nom", placeholder="Juan")
    with c2: apellido_r = st.text_input("Apellido *", key="cli_reg_ape", placeholder="Pérez")
    dni_r       = st.text_input("DNI (sin puntos) *",  key="cli_reg_dni",   placeholder="12345678")
    email_r     = st.text_input("Email *",             key="cli_reg_email", placeholder="ejemplo@mail.com")
    domicilio_r = st.text_input("Domicilio",           key="cli_reg_dom",   placeholder="Av. Siempre Viva 742")
    pw_r        = st.text_input("Contraseña * (mín. 6 caracteres)", type="password", key="cli_reg_pw")
    pw_r2       = st.text_input("Repetir contraseña *",             type="password", key="cli_reg_pw2")

    with st.expander("📄 Términos y Condiciones — leer antes de registrarse"):
        st.markdown(f"""
**Términos y Condiciones de {APP_NAME}**

**1. Sobre los presupuestos**
Los presupuestos enviados por los especialistas pueden incluir, a criterio de la plataforma,
un ítem denominado **"Costo de servicio {APP_NAME}"**. Dicho ítem, en caso de figurar,
representa el canon por uso de la plataforma y será cobrado por el especialista al usuario
al momento de abonar el trabajo. El especialista será responsable de rendir dicho importe
a {APP_NAME} conforme a los términos acordados.

**2. Modificación de presupuestos**
{APP_NAME} se reserva el derecho de incorporar el ítem "Costo de servicio" en los
presupuestos cuando lo considere pertinente, de acuerdo con las políticas vigentes
de la plataforma. El usuario será informado de cualquier cargo adicional antes de
confirmar la aceptación del presupuesto.

**3. Responsabilidad**
{APP_NAME} actúa como intermediario entre usuarios y especialistas. La calidad del
trabajo es responsabilidad exclusiva del especialista contratado.

**4. Privacidad**
Los datos personales ingresados serán utilizados únicamente para el funcionamiento
de la plataforma y no serán compartidos con terceros sin consentimiento previo.
        """)
    acepta_tyc = st.checkbox("Leí y acepto los Términos y Condiciones *", key="cli_reg_tyc")
    st.write("")

    if st.button("CREAR MI CUENTA", type="primary", use_container_width=True, key="cli_btn_reg"):
        err = []
        if not nombre_r:               err.append("Nombre")
        if not apellido_r:             err.append("Apellido")
        if not validar_dni(dni_r):     err.append("DNI válido (7-8 dígitos)")
        if not validar_email(email_r): err.append("Email válido")
        if len(pw_r) < 6:             err.append("Contraseña de al menos 6 caracteres")
        if pw_r != pw_r2:             err.append("Las contraseñas no coinciden")
        if not acepta_tyc:            err.append("Debés aceptar los Términos y Condiciones")
        if err:
            st.error("Corregí: " + ", ".join(err))
        else:
            conn = get_connection()
            try:
                conn.execute(
                    "INSERT INTO clientes (nombre,apellido,dni,domicilio,email,password_hash) VALUES (?,?,?,?,?,?)",
                    (sanitizar(nombre_r,50), sanitizar(apellido_r,50), limpiar_dni(dni_r),
                     sanitizar(domicilio_r,150), email_r.strip().lower(), hash_pw(pw_r))
                )
                conn.commit()
                enviar_email(email_r.strip(), f"¡Bienvenido a {APP_NAME}!", nombre_r, email_bienvenida_cliente(nombre_r))
                st.success("✅ ¡Cuenta creada! Revisá tu email y luego iniciá sesión.")
                st.session_state["mostrar_reg_usuario"] = False
                st.rerun()
            except Exception:
                st.error("Ese DNI o email ya está registrado.")

def pantalla_reset_cliente():
    st.markdown(LOGO_BIG, unsafe_allow_html=True)
    fx_header("USUARIO", "RECUPERAR CONTRASEÑA")
    btn_volver("Volver al login", key_suffix="reset_cli", pantalla_reset=False, reset_modo=None)
    st.write("")
    params    = st.query_params
    token_url = params.get("reset_token","")
    modo_url  = params.get("reset_modo","")
    if token_url and modo_url == "cliente":
        _nueva_pw_cliente(token_url)
        return
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("Ingresá tu email y te enviamos un link para crear una nueva contraseña.")
        email_r = st.text_input("Email de tu cuenta", key="reset_email_cli")
        if st.button("ENVIAR LINK", type="primary", use_container_width=True, key="btn_reset_cli"):
            if not validar_email(email_r):
                st.error("Email inválido.")
            else:
                conn = get_connection()
                row  = conn.execute("SELECT id,nombre FROM clientes WHERE email=?", (email_r.strip().lower(),)).fetchone()
                st.success("Si el email existe, te enviamos el link en unos segundos.")
                if row:
                    token, expiry = generar_token_reset()
                    conn.execute("UPDATE clientes SET reset_token=?,reset_expiry=? WHERE id=?", (token, expiry, row[0]))
                    conn.commit()
                    enviar_email(email_r.strip(), f"Recuperá tu contraseña — {APP_NAME}", row[1], email_reset_password(row[1], token, "cliente"))

def _nueva_pw_cliente(token):
    conn = get_connection()
    row  = conn.execute("SELECT id,nombre,reset_expiry FROM clientes WHERE reset_token=?", (token,)).fetchone()
    if not row or not token_valido(row[2]):
        st.error("El link expiró o no es válido. Solicitá uno nuevo.")
        return
    st.success(f"Hola {row[1]}! Creá tu nueva contraseña.")
    _, col, _ = st.columns([1,2,1])
    with col:
        pw_n  = st.text_input("Nueva contraseña (mín. 6 caracteres)", type="password", key="new_pw_cli")
        pw_n2 = st.text_input("Repetir contraseña",                   type="password", key="new_pw_cli2")
        if st.button("GUARDAR CONTRASEÑA", type="primary", use_container_width=True, key="save_pw_cli"):
            if len(pw_n) < 6:    st.error("Mínimo 6 caracteres.")
            elif pw_n != pw_n2:  st.error("Las contraseñas no coinciden.")
            else:
                conn.execute("UPDATE clientes SET password_hash=?,reset_token=NULL,reset_expiry=NULL WHERE id=?", (hash_pw(pw_n), row[0]))
                conn.commit()
                st.query_params.clear()
                st.success("✅ ¡Contraseña actualizada! Ya podés iniciar sesión.")
                st.session_state["pantalla_reset"] = False
                st.rerun()
