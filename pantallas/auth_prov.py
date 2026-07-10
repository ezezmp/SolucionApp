# ═══════════════════════════════════════════════════════════════════
#  pantallas/auth_prov.py — Login, registro y recupero especialista.
# ═══════════════════════════════════════════════════════════════════

import json, urllib.request, urllib.parse
import streamlit as st
from config import LOGO_BIG, APP_NAME, CATEGORIAS
from auth import (login_proveedor, validar_email, validar_cuit, limpiar_cuit,
                  sanitizar, hash_pw, generar_token_reset, token_valido)
from database import ejecutar, get_rubros, agregar_rubro_personalizado
from email_utils import enviar_email, email_bienvenida_proveedor, email_reset_password
from ui_components import fx_header, btn_volver


def auth_proveedor():
    st.markdown(LOGO_BIG, unsafe_allow_html=True)
    fx_header("ESPECIALISTA", "ACCESO")
    btn_volver("Volver al inicio", key_suffix="auth_prov", modo=None, auth_step="selector")
    st.write("")
    _, col, _ = st.columns([1, 2, 1])
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
    rubros_disponibles = get_rubros(grupo_r)
    st.markdown("**Rubros / Actividades *** *(podés elegir más de uno)*")
    rubros_sel = st.multiselect("Seleccioná tus especialidades", rubros_disponibles,
                                key="prov_reg_rubros", placeholder="Elegí uno o más rubros...")

    with st.expander("➕ Mi rubro no está en la lista — agregarlo"):
        st.caption("El rubro que agregues quedará disponible para todos los especialistas.")
        nuevo_rubro = st.text_input("Nombre del rubro nuevo", key="prov_nuevo_rubro",
                                    placeholder="Ej: Herrería, Soldadura...", max_chars=60)
        if st.button("AGREGAR RUBRO", key="btn_nuevo_rubro"):
            if not nuevo_rubro.strip():
                st.error("Escribí el nombre del rubro.")
            elif nuevo_rubro.strip().title() in rubros_disponibles:
                st.warning("Ese rubro ya existe.")
            else:
                if "rubros_nuevos_temp" not in st.session_state:
                    st.session_state["rubros_nuevos_temp"] = []
                nombre_limpio = nuevo_rubro.strip().title()
                if nombre_limpio not in st.session_state["rubros_nuevos_temp"]:
                    st.session_state["rubros_nuevos_temp"].append(nombre_limpio)
                st.success(f"✅ '{nombre_limpio}' agregado. Seleccionalo arriba.")
                st.rerun()
    if st.session_state.get("rubros_nuevos_temp"):
        st.info(f"Rubros nuevos: {', '.join(st.session_state['rubros_nuevos_temp'])}")

    razon_r     = st.text_input("Razón social *",       key="prov_reg_razon",  placeholder="Mi Empresa S.R.L.")
    cuit_r      = st.text_input("CUIT (sin guiones) *", key="prov_reg_cuit",   placeholder="20123456789")
    c1, c2 = st.columns(2)
    with c1: encargado_r = st.text_input("Encargado *", key="prov_reg_enc", placeholder="Nombre y apellido")
    with c2: contacto_r  = st.text_input("Teléfono",   key="prov_reg_tel", placeholder="351 000 0000")
    email_r     = st.text_input("Email de contacto *", key="prov_reg_email", placeholder="empresa@mail.com")
    direccion_r = st.text_input("Dirección *",         key="prov_reg_dir",   placeholder="Calle y número")
    c1, c2 = st.columns(2)
    with c1: localidad_r  = st.text_input("Localidad",  key="prov_reg_loc",  placeholder="Córdoba")
    with c2: provincia_r  = st.text_input("Provincia",  key="prov_reg_prov", placeholder="Córdoba")
    pw_r        = st.text_input("Contraseña * (mín. 6 caracteres)", type="password", key="prov_reg_pw")
    pw_r2       = st.text_input("Repetir contraseña *",             type="password", key="prov_reg_pw2")

    with st.expander("📄 Términos y Condiciones para Especialistas — leer antes de registrarse"):
        st.markdown(f"""
**TÉRMINOS Y CONDICIONES PARA ESPECIALISTAS — {APP_NAME.upper()}**
*Versión vigente — Última actualización: Julio 2026*

**1. Objeto de la plataforma**
{APP_NAME} es una plataforma digital de intermediación. Actúa únicamente como
intermediario tecnológico entre especialistas y usuarios.

**2. Presupuestos y costo de servicio**
Los presupuestos son elaborados íntegramente por el especialista. {APP_NAME} no los
modifica. Al momento de cerrar un presupuesto aceptado, la plataforma podrá incorporar
un cargo adicional denominado **"Costo de servicio {APP_NAME}"**. Dicho cargo, en caso
de aplicarse, será visible en el panel del especialista bajo **"Abonar costo de servicio"**
con el correspondiente enlace de pago.

> 📌 **Aclaración vigente:** A la fecha, {APP_NAME} **no aplica ni cobra** el costo de
> servicio. Este cargo podrá implementarse en el futuro solo cuando sea necesario para
> costear el mantenimiento de la plataforma, con **30 días de anticipación** de aviso.

**3. Obligaciones del especialista**
- Brindar servicios de calidad y con idoneidad profesional.
- Cumplir con los turnos acordados.
- Documentar el trabajo con fotografías del resultado final.
- Brindar información veraz al registrarse y en cada presupuesto.

**4. Calificaciones**
Los usuarios podrán calificar al especialista con puntuación del 1 al 5 y comentario
opcional. Las calificaciones son públicas y visibles para otros usuarios.

**5. Suspensión de cuenta**
{APP_NAME} podrá suspender cuentas por calificaciones negativas reiteradas, información
falsa o incumplimiento de estos términos.

**6. Responsabilidad**
La calidad y resultado de los trabajos son responsabilidad exclusiva del especialista.
{APP_NAME} no asume responsabilidad por daños derivados de la prestación del servicio.

**7. Privacidad**
Los datos serán tratados conforme a la Ley N° 25.326 de Protección de Datos Personales.

**8. Modificaciones**
{APP_NAME} podrá modificar estos términos con 15 días de anticipación.

**9. Plataforma y origen**
{APP_NAME} opera en Córdoba, Argentina. Las relaciones entre especialistas y usuarios
son estrictamente privadas. {APP_NAME} no interviene en conflictos entre las partes.
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
            lat, lon   = _geocodificar(direccion_r)
            rubros_str = ", ".join(rubros_sel)
            try:
                ejecutar(
                    """INSERT INTO proveedores
                       (razon_social,rubros,grupo,cuit,direccion,localidad,provincia,encargado,contacto,email,password_hash,latitud,longitud)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (sanitizar(razon_r,100), rubros_str, grupo_r, limpiar_cuit(cuit_r),
                     sanitizar(direccion_r,150), sanitizar(localidad_r,80), sanitizar(provincia_r,80),
                     sanitizar(encargado_r,80), sanitizar(contacto_r,30),
                     email_r.strip().lower(), hash_pw(pw_r), lat, lon)
                )
                prov_nuevo = ejecutar("SELECT id FROM proveedores WHERE email=%s",
                                      (email_r.strip().lower(),), fetch="one")
                if prov_nuevo and st.session_state.get("rubros_nuevos_temp"):
                    for rubro_nuevo in st.session_state["rubros_nuevos_temp"]:
                        agregar_rubro_personalizado(grupo_r, rubro_nuevo, prov_nuevo["id"])
                    st.session_state["rubros_nuevos_temp"] = []
                enviar_email(email_r.strip(), f"¡Bienvenido a {APP_NAME}!", encargado_r,
                             email_bienvenida_proveedor(razon_r))
                st.success("✅ ¡Empresa registrada! Iniciá sesión.")
                st.session_state["mostrar_reg_especialista"] = False
                st.rerun()
            except Exception as e:
                st.error("Ese CUIT o email ya está registrado.")


def pantalla_reset_proveedor():
    st.markdown(LOGO_BIG, unsafe_allow_html=True)
    fx_header("ESPECIALISTA", "RECUPERAR CONTRASEÑA")
    btn_volver("Volver al login", key_suffix="reset_prov", pantalla_reset=False, reset_modo=None)
    st.write("")
    params    = st.query_params
    token_url = params.get("reset_token", "")
    modo_url  = params.get("reset_modo", "")
    if token_url and modo_url == "proveedor":
        _nueva_pw_proveedor(token_url)
        return
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("Ingresá tu email y te enviamos un link para crear una nueva contraseña.")
        email_r = st.text_input("Email de tu cuenta", key="reset_email_prov")
        if st.button("ENVIAR LINK", type="primary", use_container_width=True, key="btn_reset_prov"):
            if not validar_email(email_r):
                st.error("Email inválido.")
            else:
                row = ejecutar("SELECT id,encargado FROM proveedores WHERE email=%s",
                               (email_r.strip().lower(),), fetch="one")
                st.success("Si el email existe, te enviamos el link en unos segundos.")
                if row:
                    token, expiry = generar_token_reset()
                    ejecutar("UPDATE proveedores SET reset_token=%s,reset_expiry=%s WHERE id=%s",
                             (token, expiry, row["id"]))
                    enviar_email(email_r.strip(), f"Recuperá tu contraseña — {APP_NAME}",
                                 row["encargado"] or "Especialista",
                                 email_reset_password(row["encargado"] or "Especialista", token, "proveedor"))


def _nueva_pw_proveedor(token):
    row = ejecutar("SELECT id,encargado,reset_expiry FROM proveedores WHERE reset_token=%s",
                   (token,), fetch="one")
    if not row or not token_valido(row["reset_expiry"]):
        st.error("El link expiró o no es válido.")
        return
    st.success(f"Hola {row['encargado']}! Creá tu nueva contraseña.")
    _, col, _ = st.columns([1, 2, 1])
    with col:
        pw_n  = st.text_input("Nueva contraseña (mín. 6 caracteres)", type="password", key="new_pw_prov")
        pw_n2 = st.text_input("Repetir contraseña",                   type="password", key="new_pw_prov2")
        if st.button("GUARDAR CONTRASEÑA", type="primary", use_container_width=True, key="save_pw_prov"):
            if len(pw_n) < 6:   st.error("Mínimo 6 caracteres.")
            elif pw_n != pw_n2: st.error("Las contraseñas no coinciden.")
            else:
                ejecutar("UPDATE proveedores SET password_hash=%s,reset_token=NULL,reset_expiry=NULL WHERE id=%s",
                         (hash_pw(pw_n), row["id"]))
                st.query_params.clear()
                st.success("✅ ¡Contraseña actualizada!")
                st.session_state["pantalla_reset"] = False
                st.rerun()
