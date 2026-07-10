# ═══════════════════════════════════════════════════════════════════
#  pantallas/auth_cliente.py — Login, registro y recupero usuario.
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
from config import LOGO_BIG, APP_NAME
from auth import (login_cliente, validar_email, validar_dni, limpiar_dni,
                  sanitizar, hash_pw, generar_token_reset, token_valido)
from database import ejecutar
from email_utils import enviar_email, email_bienvenida_cliente, email_reset_password
from ui_components import fx_header, btn_volver


def auth_cliente():
    st.markdown(LOGO_BIG, unsafe_allow_html=True)
    fx_header("USUARIO", "ACCESO")
    btn_volver("Volver al inicio", key_suffix="auth_cli", modo=None, auth_step="selector")
    st.write("")
    _, col, _ = st.columns([1, 2, 1])
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
**TÉRMINOS Y CONDICIONES DE USO — {APP_NAME.upper()}**
*Versión vigente — Última actualización: Julio 2026*

Al registrarse en {APP_NAME}, el usuario declara haber leído, comprendido y aceptado
en su totalidad los presentes Términos y Condiciones.

---

**1. Objeto de la plataforma**
{APP_NAME} es una plataforma digital de intermediación que facilita la conexión entre
usuarios que requieren servicios del hogar o automotor y especialistas registrados que
ofrecen dichos servicios. {APP_NAME} no es parte de la relación contractual entre el
usuario y el especialista, actuando únicamente como intermediario tecnológico.

**2. Presupuestos y costo de servicio**
Los presupuestos son elaborados íntegramente por los especialistas y reflejan su propio
criterio profesional. {APP_NAME} no interviene ni modifica el contenido de los mismos.
No obstante, la plataforma podrá agregar de forma automática un ítem adicional denominado
**"Costo de servicio {APP_NAME}"**, el cual representa el canon por uso de la plataforma.
Dicho ítem, en caso de incorporarse, será visible para el usuario previo a la aceptación
del presupuesto, y será responsabilidad del especialista su rendición a {APP_NAME}
conforme a los términos vigentes.

> 📌 **Aclaración vigente:** A la fecha de estos términos, {APP_NAME} **no aplica ni
> cobra** el ítem "Costo de servicio" en ningún presupuesto. La plataforma se encuentra
> en etapa de crecimiento y este cargo podrá implementarse en el futuro únicamente cuando
> sea necesario para costear el mantenimiento y desarrollo de la plataforma. Tanto usuarios
> como especialistas serán notificados con un mínimo de **30 días de anticipación** antes
> de cualquier implementación de este cargo.

**3. Aceptación de presupuestos**
La aceptación de un presupuesto por parte del usuario implica su conformidad con el
monto total detallado, incluyendo el ítem de costo de servicio en caso de figurar.
Una vez aceptado el presupuesto, el usuario no podrá solicitar modificaciones sobre
el mismo salvo acuerdo expreso con el especialista.

**4. Turnos y prestación del servicio**
La coordinación de turnos se realiza entre el usuario y el especialista a través de la
plataforma. {APP_NAME} no garantiza la disponibilidad horaria de los especialistas ni
se responsabiliza por demoras o cancelaciones que pudieran surgir.

**5. Calificaciones y reseñas**
Al finalizar un trabajo, el usuario podrá calificar al especialista con una puntuación
del 1 al 5 y dejar un comentario opcional. Las calificaciones deberán ser verídicas
y basadas en la experiencia real del servicio recibido.

**6. Responsabilidad**
{APP_NAME} actúa exclusivamente como intermediario tecnológico. La calidad,
idoneidad y resultado de los trabajos realizados son responsabilidad exclusiva
del especialista contratado. {APP_NAME} no asume responsabilidad alguna por
daños, pérdidas o perjuicios derivados de la prestación del servicio.

**7. Conducta del usuario**
El usuario se compromete a hacer un uso responsable de la plataforma, a brindar
información veraz al momento del registro y al realizar solicitudes.

**8. Privacidad y protección de datos**
Los datos personales ingresados serán tratados de forma confidencial y utilizados
exclusivamente para el funcionamiento de la plataforma, en cumplimiento de la
Ley N° 25.326 de Protección de Datos Personales de la República Argentina.

**9. Modificaciones**
{APP_NAME} se reserva el derecho de modificar los presentes Términos y Condiciones
notificando a los usuarios con un mínimo de 15 días de anticipación.

**10. Plataforma y origen**
{APP_NAME} es una plataforma digital desarrollada y operada en la provincia de Córdoba,
República Argentina. Las relaciones entre usuarios y especialistas son de carácter
estrictamente privado. {APP_NAME} no interviene ni asume responsabilidad en conflictos
entre las partes, los cuales deberán resolverse directamente entre ellas.
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
            try:
                ejecutar(
                    "INSERT INTO clientes (nombre,apellido,dni,domicilio,email,password_hash) VALUES (%s,%s,%s,%s,%s,%s)",
                    (sanitizar(nombre_r,50), sanitizar(apellido_r,50), limpiar_dni(dni_r),
                     sanitizar(domicilio_r,150), email_r.strip().lower(), hash_pw(pw_r))
                )
                enviar_email(email_r.strip(), f"¡Bienvenido a {APP_NAME}!", nombre_r,
                             email_bienvenida_cliente(nombre_r))
                st.success("✅ ¡Cuenta creada! Iniciá sesión.")
                st.session_state["mostrar_reg_usuario"] = False
                st.rerun()
            except Exception as e:
                st.error("Ese DNI o email ya está registrado.")


def pantalla_reset_cliente():
    st.markdown(LOGO_BIG, unsafe_allow_html=True)
    fx_header("USUARIO", "RECUPERAR CONTRASEÑA")
    btn_volver("Volver al login", key_suffix="reset_cli", pantalla_reset=False, reset_modo=None)
    st.write("")
    params    = st.query_params
    token_url = params.get("reset_token", "")
    modo_url  = params.get("reset_modo", "")
    if token_url and modo_url == "cliente":
        _nueva_pw_cliente(token_url)
        return
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("Ingresá tu email y te enviamos un link para crear una nueva contraseña.")
        email_r = st.text_input("Email de tu cuenta", key="reset_email_cli")
        if st.button("ENVIAR LINK", type="primary", use_container_width=True, key="btn_reset_cli"):
            if not validar_email(email_r):
                st.error("Email inválido.")
            else:
                row = ejecutar("SELECT id,nombre FROM clientes WHERE email=%s",
                               (email_r.strip().lower(),), fetch="one")
                st.success("Si el email existe, te enviamos el link en unos segundos.")
                if row:
                    token, expiry = generar_token_reset()
                    ejecutar("UPDATE clientes SET reset_token=%s,reset_expiry=%s WHERE id=%s",
                             (token, expiry, row["id"]))
                    enviar_email(email_r.strip(), f"Recuperá tu contraseña — {APP_NAME}",
                                 row["nombre"], email_reset_password(row["nombre"], token, "cliente"))


def _nueva_pw_cliente(token):
    row = ejecutar("SELECT id,nombre,reset_expiry FROM clientes WHERE reset_token=%s",
                   (token,), fetch="one")
    if not row or not token_valido(row["reset_expiry"]):
        st.error("El link expiró o no es válido.")
        return
    st.success(f"Hola {row['nombre']}! Creá tu nueva contraseña.")
    _, col, _ = st.columns([1, 2, 1])
    with col:
        pw_n  = st.text_input("Nueva contraseña (mín. 6 caracteres)", type="password", key="new_pw_cli")
        pw_n2 = st.text_input("Repetir contraseña",                   type="password", key="new_pw_cli2")
        if st.button("GUARDAR CONTRASEÑA", type="primary", use_container_width=True, key="save_pw_cli"):
            if len(pw_n) < 6:   st.error("Mínimo 6 caracteres.")
            elif pw_n != pw_n2: st.error("Las contraseñas no coinciden.")
            else:
                ejecutar("UPDATE clientes SET password_hash=%s,reset_token=NULL,reset_expiry=NULL WHERE id=%s",
                         (hash_pw(pw_n), row["id"]))
                st.query_params.clear()
                st.success("✅ ¡Contraseña actualizada!")
                st.session_state["pantalla_reset"] = False
                st.rerun()
