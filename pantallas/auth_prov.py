# ═══════════════════════════════════════════════════════════════════
#  pantallas/auth_prov.py — Login, registro y recupero especialista.
#  El profesional puede elegir MÚLTIPLES rubros al registrarse.
# ═══════════════════════════════════════════════════════════════════

import json, urllib.request, urllib.parse
import streamlit as st
from config import LOGO_BIG, APP_NAME, CATEGORIAS
from auth import login_proveedor, validar_email, validar_cuit, limpiar_cuit, sanitizar, hash_pw, generar_token_reset, token_valido
from database import get_connection
from email_utils import enviar_email, email_bienvenida_proveedor, email_reset_password
from ui_components import fx_header, btn_volver

def auth_proveedor():
    st.markdown(LOGO_BIG, unsafe_allow_html=True)
    fx_header("ESPECIALISTA", "ACCESO")
    btn_volver("Volver al inicio", key_suffix="auth_prov", modo=None, auth_step="selector")
    st.write("")
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("#### Iniciá sesión")
        email_l = st.text_input("Email", key="prov_login_email", placeholder="empresa@mail.com")
        pw_l    = st.text_input("Contraseña", type="password", key="prov_login_pw")
        st.write("")
        if st.button("INGRESAR", type="primary", use_container_width=True, key="prov_btn_login"):
            if not validar_email(email_l): st.error("Ingresá un email válido.")
            elif not pw_l:                 st.error("Ingresá tu contraseña.")
            else:
                ok, msg = login_proveedor(email_l, pw_l)
                if not ok: st.error(msg)
                else:      st.rerun()
        st.markdown('<div class="reg-sep">¿Olvidaste tu contraseña?</div>', unsafe_allow_html=True)
        if st.button("RECUPERAR CONTRASEÑA", use_container_width=True, key="prov_rec_pw"):
            st.session_state.update({"pantalla_reset": True, "reset_modo": "proveedor"})
            st.rerun()
        st.markdown('<div class="reg-sep">¿No registraste tu empresa?</div>', unsafe_allow_html=True)
        if not st.session_state.get("mostrar_reg_especialista"):
            if st.button("REGISTRATE", use_container_width=True, key="prov_show_reg"):
                st.session_state["mostrar_reg_especialista"] = True
                st.rerun()
        else:
            btn_volver("Volver al login", key_suffix="collapse_reg_prov", mostrar_reg_especialista=False)
            st.markdown("#### Registrar empresa")
            _registro_especialista()

def _geocodificar(direccion):
    try:
        query = urllib.parse.urlencode({"q": direccion, "format": "json", "limit": "1"})
        req   = urllib.request.Request(
            f"https://nominatim.openstreetmap.org/search?{query}",
            headers={"User-Agent": "SolucionApp/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None, None

def _registro_especialista():
    st.write("")
    grupo_r = st.selectbox("Grupo de servicio *", list(CATEGORIAS.keys()), key="prov_reg_grupo")

    # ── MÚLTIPLES RUBROS ─────────────────────────────────────────
    st.markdown("**Rubros / Actividades *** *(podés elegir más de uno)*")
    rubros_sel = st.multiselect(
        "Seleccioná tus especialidades",
        CATEGORIAS[grupo_r],
        key="prov_reg_rubros",
        placeholder="Elegí uno o más rubros...",
    )

    razon_r     = st.text_input("Razón social *",       key="prov_reg_razon",  placeholder="Mi Empresa S.R.L.")
    cuit_r      = st.text_input("CUIT (sin guiones) *", key="prov_reg_cuit",   placeholder="20123456789")
    c1, c2 = st.columns(2)
    with c1: encargado_r = st.text_input("Encargado *", key="prov_reg_enc", placeholder="Nombre y apellido")
    with c2: contacto_r  = st.text_input("Teléfono",   key="prov_reg_tel", placeholder="351 000 0000")
    email_r     = st.text_input("Email de contacto *", key="prov_reg_email", placeholder="empresa@mail.com")
    direccion_r = st.text_input("Dirección *",         key="prov_reg_dir",   placeholder="Calle y número, Ciudad")
    pw_r        = st.text_input("Contraseña * (mín. 6 caracteres)", type="password", key="prov_reg_pw")
    pw_r2       = st.text_input("Repetir contraseña *",             type="password", key="prov_reg_pw2")

    with st.expander("📄 Términos y Condiciones para Especialistas — leer antes de registrarse"):
        st.markdown(f"""
**TÉRMINOS Y CONDICIONES PARA ESPECIALISTAS — {APP_NAME.upper()}**
*Versión vigente — Última actualización: Julio 2026*

Al registrarse en {APP_NAME} como especialista, declarás haber leído, comprendido
y aceptado en su totalidad los presentes Términos y Condiciones.

---

**1. Objeto de la plataforma**
{APP_NAME} es una plataforma digital de intermediación que facilita la conexión entre
especialistas que ofrecen servicios del hogar o automotor y usuarios que los requieren.
{APP_NAME} no es parte de la relación contractual entre el especialista y el usuario,
actuando únicamente como intermediario tecnológico.

**2. Presupuestos y costo de servicio**
Los presupuestos son elaborados íntegramente por el especialista y reflejan su propio
criterio profesional. {APP_NAME} no modifica el contenido de los mismos.
No obstante, al momento de cerrar un presupuesto aceptado, la plataforma podrá
incorporar un cargo adicional denominado **"Costo de servicio {APP_NAME}"**, el cual
representará el canon por uso de la plataforma. Dicho cargo, en caso de aplicarse,
será visible para el especialista en su panel bajo la opción **"Abonar costo de servicio"**,
con el correspondiente enlace de pago.

> 📌 **Aclaración vigente:** A la fecha de estos términos, {APP_NAME} **no aplica ni
> cobra** el ítem "Costo de servicio" a ningún especialista. La plataforma se encuentra
> en etapa de crecimiento y este cargo podrá implementarse en el futuro únicamente cuando
> sea necesario para costear el mantenimiento y desarrollo de la plataforma. Tanto
> especialistas como usuarios serán notificados con un mínimo de **30 días de anticipación**
> antes de cualquier implementación de este cargo.

**3. Obligaciones del especialista**
El especialista se compromete a:
- Brindar servicios de calidad y con la idoneidad profesional requerida.
- Cumplir con los turnos acordados a través de la plataforma.
- Documentar el trabajo realizado con fotografías del resultado final.
- Brindar información veraz al momento del registro y en cada presupuesto.
- Rendir el costo de servicio a {APP_NAME} cuando corresponda, en los plazos establecidos.

**4. Calificaciones**
Al finalizar cada trabajo, el usuario podrá calificar al especialista con una puntuación
del 1 al 5 y un comentario opcional. Las calificaciones son públicas y visibles para
otros usuarios de la plataforma. El especialista no podrá solicitar la eliminación de
calificaciones verídicas, pero podrá reportar aquellas que considere falsas u ofensivas
para su revisión por parte de {APP_NAME}.

**5. Suspensión y baja de cuenta**
{APP_NAME} podrá suspender o dar de baja cuentas de especialistas que:
- Acumulen calificaciones negativas reiteradas.
- Incumplan con la rendición del costo de servicio cuando corresponda.
- Brinden información falsa en el registro o en los presupuestos.
- Violen cualquiera de los presentes términos y condiciones.

**6. Responsabilidad**
La calidad, idoneidad y resultado de los trabajos realizados son responsabilidad exclusiva
del especialista. {APP_NAME} no asume responsabilidad alguna por daños, pérdidas o
perjuicios derivados de la prestación del servicio.

**7. Privacidad y protección de datos**
Los datos de la empresa y del encargado ingresados serán tratados de forma confidencial
y utilizados exclusivamente para el funcionamiento de la plataforma. No serán cedidos
ni comercializados con terceros sin consentimiento expreso, en cumplimiento de la
Ley N° 25.326 de Protección de Datos Personales de la República Argentina.

**8. Modificaciones**
{APP_NAME} se reserva el derecho de modificar los presentes Términos y Condiciones
notificando a los especialistas registrados con un mínimo de 15 días de anticipación.
La continuación del uso de la plataforma luego de la notificación implicará la
aceptación de los nuevos términos.

**9. Jurisdicción**
Ante cualquier controversia derivada del uso de la plataforma, las partes se someten
a la jurisdicción de los Tribunales Ordinarios de la Ciudad de Córdoba, República Argentina.
        """)
    acepta_tyc = st.checkbox("Leí y acepto los Términos y Condiciones *", key="prov_reg_tyc")
    st.write("")

    if st.button("REGISTRAR MI EMPRESA", type="primary", use_container_width=True, key="prov_btn_reg"):
        err = []
        if not rubros_sel:             err.append("Al menos un rubro")
        if not razon_r:                err.append("Razón social")
        if not validar_cuit(cuit_r):   err.append("CUIT válido (11 dígitos)")
        if not encargado_r:            err.append("Nombre del encargado")
        if not validar_email(email_r): err.append("Email válido")
        if not direccion_r:            err.append("Dirección")
        if len(pw_r) < 6:             err.append("Contraseña de al menos 6 caracteres")
        if pw_r != pw_r2:             err.append("Las contraseñas no coinciden")
        if not acepta_tyc:            err.append("Debés aceptar los Términos y Condiciones")
        if err:
            st.error("Corregí: " + ", ".join(err))
        else:
            lat, lon = _geocodificar(direccion_r)
            # Guardamos los rubros como string separado por comas
            rubros_str = ", ".join(rubros_sel)
            conn = get_connection()
            try:
                conn.execute(
                    """INSERT INTO proveedores
                       (razon_social,rubros,grupo,cuit,direccion,encargado,contacto,email,password_hash,latitud,longitud)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (sanitizar(razon_r,100), rubros_str, grupo_r, limpiar_cuit(cuit_r),
                     sanitizar(direccion_r,150), sanitizar(encargado_r,80), sanitizar(contacto_r,30),
                     email_r.strip().lower(), hash_pw(pw_r), lat, lon)
                )
                conn.commit()
                enviar_email(email_r.strip(), f"¡Bienvenido a {APP_NAME}!", encargado_r, email_bienvenida_proveedor(razon_r))
                st.success("✅ ¡Empresa registrada! Revisá tu email e iniciá sesión.")
                st.session_state["mostrar_reg_especialista"] = False
                st.rerun()
            except Exception:
                st.error("Ese CUIT o email ya está registrado.")

def pantalla_reset_proveedor():
    st.markdown(LOGO_BIG, unsafe_allow_html=True)
    fx_header("ESPECIALISTA", "RECUPERAR CONTRASEÑA")
    btn_volver("Volver al login", key_suffix="reset_prov", pantalla_reset=False, reset_modo=None)
    st.write("")
    params    = st.query_params
    token_url = params.get("reset_token","")
    modo_url  = params.get("reset_modo","")
    if token_url and modo_url == "proveedor":
        _nueva_pw_proveedor(token_url)
        return
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("Ingresá tu email y te enviamos un link para crear una nueva contraseña.")
        email_r = st.text_input("Email de tu cuenta", key="reset_email_prov")
        if st.button("ENVIAR LINK", type="primary", use_container_width=True, key="btn_reset_prov"):
            if not validar_email(email_r):
                st.error("Email inválido.")
            else:
                conn = get_connection()
                row  = conn.execute("SELECT id,encargado FROM proveedores WHERE email=?", (email_r.strip().lower(),)).fetchone()
                st.success("Si el email existe, te enviamos el link en unos segundos.")
                if row:
                    token, expiry = generar_token_reset()
                    conn.execute("UPDATE proveedores SET reset_token=?,reset_expiry=? WHERE id=?", (token, expiry, row[0]))
                    conn.commit()
                    enviar_email(email_r.strip(), f"Recuperá tu contraseña — {APP_NAME}", row[1] or "Especialista", email_reset_password(row[1] or "Especialista", token, "proveedor"))

def _nueva_pw_proveedor(token):
    conn = get_connection()
    row  = conn.execute("SELECT id,encargado,reset_expiry FROM proveedores WHERE reset_token=?", (token,)).fetchone()
    if not row or not token_valido(row[2]):
        st.error("El link expiró o no es válido.")
        return
    st.success(f"Hola {row[1]}! Creá tu nueva contraseña.")
    _, col, _ = st.columns([1,2,1])
    with col:
        pw_n  = st.text_input("Nueva contraseña (mín. 6 caracteres)", type="password", key="new_pw_prov")
        pw_n2 = st.text_input("Repetir contraseña",                   type="password", key="new_pw_prov2")
        if st.button("GUARDAR CONTRASEÑA", type="primary", use_container_width=True, key="save_pw_prov"):
            if len(pw_n) < 6:   st.error("Mínimo 6 caracteres.")
            elif pw_n != pw_n2: st.error("Las contraseñas no coinciden.")
            else:
                conn.execute("UPDATE proveedores SET password_hash=?,reset_token=NULL,reset_expiry=NULL WHERE id=?", (hash_pw(pw_n), row[0]))
                conn.commit()
                st.query_params.clear()
                st.success("✅ ¡Contraseña actualizada!")
                st.session_state["pantalla_reset"] = False
                st.rerun()
