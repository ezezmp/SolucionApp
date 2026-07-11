# ═══════════════════════════════════════════════════════════════════
#  pantallas/panel_prov.py — Panel del especialista logueado.
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
from datetime import datetime
from config import APP_NAME, ESTADOS, CANON_PROFESIONAL
from auth import cerrar_sesion, sanitizar
from database import ejecutar
from email_utils import (enviar_email, email_presupuesto_recibido,
    email_turnos_propuestos, email_trabajo_completado)
from ui_components import fx_header, sidebar_brand, render_sol_card, formulario_cambiar_pw
from fotos import widget_subir_foto, guardar_foto, mostrar_foto


def panel_proveedor():
    prov_id     = st.session_state["proveedor_id"]
    prov_nombre = st.session_state["proveedor_nombre"]
    prov_data   = ejecutar(
        "SELECT id,razon_social,email,rubros,grupo FROM proveedores WHERE id=%s",
        (prov_id,), fetch="one"
    )
    if not prov_data:
        st.error("Especialista no encontrado.")
        cerrar_sesion()
        return

    sidebar_brand(prov_nombre, "Especialista")
    st.sidebar.caption(f"🛠 {prov_data['rubros']}")

    # ── NOTIFICACIÓN FOTO DE PERFIL FALTANTE ─────────────────────
    if not prov_data.get("foto_perfil"):
        with st.expander("📸 Completá tu perfil — subí una foto", expanded=True):
            st.info("Una foto de perfil o logo genera más confianza en los usuarios y aumenta tus posibilidades de ser contactado.")
            foto_nueva = st.file_uploader("Foto de perfil o logo", type=["jpg","jpeg","png","webp"],
                                          key="prov_foto_perfil_update")
            if foto_nueva:
                st.image(foto_nueva, width=80, caption="Vista previa")
                if st.button("GUARDAR FOTO", type="primary", key="prov_save_foto"):
                    from fotos import guardar_foto
                    ruta = guardar_foto(foto_nueva)
                    ejecutar("UPDATE proveedores SET foto_perfil=%s WHERE id=%s",
                             (ruta, prov_id))
                    st.success("✅ Foto guardada.")
                    st.rerun()
            if st.button("Ahora no", key="prov_skip_foto"):
                st.rerun()
    st.sidebar.markdown("<hr style='margin:1rem 0;border-color:#E2E8F0'>", unsafe_allow_html=True)
    opcion = st.sidebar.selectbox("Menú", ["📋 Panel principal", "🔑 Cambiar contraseña"],
                                  label_visibility="collapsed")
    st.sidebar.markdown("<hr style='margin:1rem 0;border-color:#E2E8F0'>", unsafe_allow_html=True)
    if st.sidebar.button("🔒 Cerrar sesión", use_container_width=True):
        cerrar_sesion()

    if opcion == "🔑 Cambiar contraseña":
        fx_header("ESPECIALISTA", "CAMBIAR CONTRASEÑA")
        _, col, _ = st.columns([1, 2, 1])
        with col:
            formulario_cambiar_pw("proveedores", prov_id, "prov_pw")
        return

    _panel_principal(prov_id, prov_nombre, prov_data["email"] or "")


def _panel_principal(prov_id, prov_nombre, email_prov):
    fx_header("ESPECIALISTA", "MI PANEL")

    solicitudes = ejecutar(
        """SELECT s.id, c.nombre||' '||c.apellido as cliente,
                  s.marca, s.modelo, s.anio, s.descripcion, s.estado, s.email_cliente,
                  s.monto_presupuesto, s.detalle_presupuesto,
                  s.fecha_turno, s.hora_turno, s.fecha_creacion,
                  s.foto_antes, s.foto_despues, s.grupo
           FROM solicitudes s JOIN clientes c ON c.id=s.cliente_id
           WHERE s.proveedor_id=%s ORDER BY s.fecha_creacion DESC""",
        (prov_id,), fetch="all"
    ) or []

    pendientes = [s for s in solicitudes if s["estado"] == ESTADOS["pendiente"]]
    pend_turno = [s for s in solicitudes if s["estado"] in (ESTADOS["aceptada"], ESTADOS["turno_rechazado"])]
    en_curso   = [s for s in solicitudes if s["estado"] == ESTADOS["turno_confirmado"]]
    otras      = [s for s in solicitudes if s["estado"] not in (
                    ESTADOS["pendiente"], ESTADOS["aceptada"],
                    ESTADOS["turno_rechazado"], ESTADOS["turno_confirmado"])]

    _titulo(f"NUEVAS CONSULTAS ({len(pendientes)})")
    if not pendientes:
        st.info("No hay consultas nuevas por el momento.")
    for s in pendientes:
        _card_consulta(s, prov_nombre, email_prov)

    if pend_turno:
        st.markdown("<hr class='fx-divider'>", unsafe_allow_html=True)
        _titulo(f"PENDIENTES DE TURNO ({len(pend_turno)})")
        for s in pend_turno:
            _card_proponer_turno(s, prov_nombre, email_prov)

    if en_curso:
        st.markdown("<hr class='fx-divider'>", unsafe_allow_html=True)
        _titulo(f"TRABAJOS EN CURSO ({len(en_curso)})")
        for s in en_curso:
            _card_completar(s, prov_nombre, email_prov)

    if otras:
        st.markdown("<hr class='fx-divider'>", unsafe_allow_html=True)
        _titulo(f"HISTORIAL ({len(otras)})")
        for s in otras:
            _card_historial(s)


def _card_consulta(s, prov_nombre, email_prov):
    sid      = s["id"]
    cliente  = s["cliente"]
    marca    = s["marca"] or ""
    modelo   = s["modelo"] or ""
    anio     = s["anio"] or ""
    desc     = s["descripcion"] or ""
    email_c  = s["email_cliente"] or ""
    grupo    = s["grupo"] or ""
    foto_antes = s["foto_antes"]

    veh = f"— {marca} {modelo} {anio}" if marca else ""
    render_sol_card(titulo=f"👤 {cliente} {veh}",
                    meta=f"📧 {email_c} &nbsp;|&nbsp; {s['fecha_creacion']}",
                    descripcion=desc)

    if foto_antes:
        with st.expander("📷 Ver foto del antes"):
            mostrar_foto(foto_antes, "Estado actual", 350)
    elif "Vehículos" in grupo:
        st.caption("⚠️ El usuario no subió foto del vehículo.")

    with st.expander("💰 Responder con presupuesto"):
        st.markdown("**Agregá los ítems del trabajo** — el total se calcula automáticamente.")
        st.markdown("""
        <style>
        .presup-tabla { width:100%; border-collapse:collapse; margin:0.6rem 0; font-size:0.95rem; }
        .presup-tabla th { background:#1E2A3A; color:white; padding:10px 14px; text-align:left; font-weight:600; }
        .presup-tabla th:last-child { text-align:right; width:160px; }
        .presup-tabla td { padding:4px 8px; vertical-align:middle; }
        .presup-tabla td:last-child { text-align:right; width:160px; }
        .presup-tabla tr.total-row td { background:#1E2A3A; color:white; font-weight:800; font-size:1.05rem; }
        </style>
        <table class="presup-tabla">
          <thead><tr><th>Descripción del ítem</th><th>Monto ($)</th></tr></thead>
        </table>""", unsafe_allow_html=True)

        n_items = st.number_input("Cantidad de ítems", min_value=1, max_value=10,
                                  value=2, step=1, key=f"n_items_{sid}")
        items = []
        total = 0.0
        for i in range(int(n_items)):
            c1, c2 = st.columns([3, 1])
            with c1:
                desc_i = st.text_input(f"desc_{i}", key=f"item_desc_{sid}_{i}",
                                       placeholder="Ej: Mano de obra, Material...",
                                       label_visibility="collapsed")
            with c2:
                monto_i = st.number_input(f"monto_{i}", min_value=0.0, step=100.0,
                                          key=f"item_monto_{sid}_{i}",
                                          label_visibility="collapsed")
            if desc_i:
                items.append((desc_i, monto_i))
                total += monto_i

        st.markdown(f"""
        <table class="presup-tabla">
          <tbody>
            <tr class="total-row"><td>TOTAL</td><td>${total:,.0f}</td></tr>
          </tbody>
        </table>""", unsafe_allow_html=True)

        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("ENVIAR PRESUPUESTO", key=f"env_{sid}", type="primary", use_container_width=True):
                items_validos = [(d, m) for d, m in items if d.strip()]
                if not items_validos:
                    st.error("Agregá al menos un ítem.")
                else:
                    lineas  = "\n".join([f"• {d}: ${m:,.0f}" for d, m in items_validos])
                    lineas += f"\n──────────────\nTOTAL: ${total:,.0f}"
                    ejecutar(
                        "UPDATE solicitudes SET estado=%s,monto_presupuesto=%s,detalle_presupuesto=%s WHERE id=%s",
                        (ESTADOS["presupuestada"], total, lineas, sid)
                    )
                    trabajo = f"{marca} {modelo} {anio}" if marca else desc[:60]
                    enviar_email(email_c, f"Recibiste un presupuesto — {APP_NAME}", cliente,
                        email_presupuesto_recibido(cliente, prov_nombre, total, lineas, trabajo))
                    st.success("✅ Presupuesto enviado.")
                    st.rerun()
        with c2:
            if st.button("IGNORAR", key=f"ign_{sid}", use_container_width=True):
                ejecutar("UPDATE solicitudes SET estado=%s WHERE id=%s", (ESTADOS["rechazada"], sid))
                st.rerun()

        # ── CANCELAR / ELIMINAR SOLICITUD (especialista) ─────────
        st.markdown("---")
        with st.expander("🗑️ Eliminar esta solicitud"):
            st.warning("⚠️ La solicitud se eliminará completamente para ambas partes.")
            if st.button("CONFIRMAR ELIMINACIÓN", key=f"del_sol_{sid}", use_container_width=True):
                ejecutar("DELETE FROM turno_opciones WHERE solicitud_id=%s", (sid,))
                ejecutar("DELETE FROM canon_cobros WHERE solicitud_id=%s", (sid,))
                ejecutar("DELETE FROM valoraciones WHERE solicitud_id=%s", (sid,))
                ejecutar("DELETE FROM solicitudes WHERE id=%s", (sid,))
                enviar_email(
                    email_c, f"Solicitud cancelada — {APP_NAME}", cliente,
                    f"<p>El especialista canceló tu solicitud.</p>"
                    f"<p><b>Trabajo:</b> {desc}</p>"
                    f"<p>Podés buscar otro especialista en <b>{APP_NAME}</b>.</p>"
                )
                st.success("✅ Solicitud eliminada.")
                st.rerun()
    st.write("")


def _card_proponer_turno(s, prov_nombre, email_prov):
    sid     = s["id"]
    cliente = s["cliente"]
    desc    = s["descripcion"] or ""
    email_c = s["email_cliente"] or ""
    marca   = s["marca"] or ""
    modelo  = s["modelo"] or ""
    anio    = s["anio"] or ""
    estado  = s["estado"]

    veh   = f"— {marca} {modelo} {anio}" if marca else ""
    label = "Presupuesto aceptado" if estado == ESTADOS["aceptada"] else "⚠️ Usuario rechazó opciones — proponé nuevas"
    render_sol_card(titulo=f"👤 {cliente} {veh}", meta=f"📧 {email_c} &nbsp;|&nbsp; {label}", descripcion=desc)

    with st.expander("📅 Proponer opciones de turno (hasta 3)"):
        n_op = int(st.number_input("¿Cuántas opciones?", min_value=1, max_value=3,
                                   value=2, step=1, key=f"nop_{sid}"))
        opciones_prop = []
        for i in range(n_op):
            ci, cj = st.columns(2)
            with ci:
                f = st.date_input(f"Fecha opción {i+1}", min_value=datetime.today(), key=f"tf_{sid}_{i}")
            with cj:
                h = st.selectbox(f"Hora opción {i+1}", [f"{hr:02d}:00" for hr in range(7, 21)], key=f"th_{sid}_{i}")
            opciones_prop.append((str(f), h))

        if st.button("ENVIAR OPCIONES", key=f"envt_{sid}", type="primary", use_container_width=True):
            ejecutar("DELETE FROM turno_opciones WHERE solicitud_id=%s", (sid,))
            for fo, ho in opciones_prop:
                ejecutar("INSERT INTO turno_opciones (solicitud_id,fecha,hora) VALUES (%s,%s,%s)", (sid, fo, ho))
            ejecutar("UPDATE solicitudes SET estado=%s WHERE id=%s", (ESTADOS["turno_propuesto"], sid))
            enviar_email(email_c, f"El especialista propuso turnos — {APP_NAME}", cliente,
                email_turnos_propuestos(prov_nombre, opciones_prop))
            st.success("✅ Opciones enviadas.")
            st.rerun()
    st.write("")


def _card_completar(s, prov_nombre, email_prov):
    sid     = s["id"]
    cliente = s["cliente"]
    desc    = s["descripcion"] or ""
    email_c = s["email_cliente"] or ""
    marca   = s["marca"] or ""
    modelo  = s["modelo"] or ""
    anio    = s["anio"] or ""
    foto_antes = s["foto_antes"]

    veh = f"— {marca} {modelo} {anio}" if marca else ""
    render_sol_card(titulo=f"👤 {cliente} {veh}",
                    meta=f"📅 Turno: {s['fecha_turno']} a las {s['hora_turno']}",
                    estado=s["estado"], descripcion=desc)

    if foto_antes:
        with st.expander("📷 Ver foto del antes"):
            mostrar_foto(foto_antes, "Antes", 300)

    with st.expander("🏁 Finalizar trabajo"):
        st.markdown("Subí la foto del trabajo terminado y marcalo como finalizado.")
        foto_despues_file = widget_subir_foto("Foto del trabajo terminado",
                                              key=f"foto_despues_{sid}", obligatoria=True)
        if st.button("🏁 CONFIRMAR TRABAJO FINALIZADO", key=f"comp_{sid}",
                     type="primary", use_container_width=True):
            if not foto_despues_file:
                st.error("La foto es obligatoria.")
            else:
                ruta = guardar_foto(foto_despues_file)
                ejecutar("UPDATE solicitudes SET estado=%s,foto_despues=%s WHERE id=%s",
                         (ESTADOS["trabajo_completado"], ruta, sid))
                trabajo = f"{marca} {modelo} {anio} — {desc[:60]}" if marca else desc[:80]
                enviar_email(email_c, f"Tu trabajo fue completado — {APP_NAME}", cliente,
                    email_trabajo_completado(prov_nombre, trabajo))
                st.success("✅ Trabajo finalizado.")
                st.rerun()
    st.write("")


def _card_historial(s):
    sid     = s["id"]
    cliente = s["cliente"]
    marca   = s["marca"] or ""
    modelo  = s["modelo"] or ""
    anio    = s["anio"] or ""
    monto   = s["monto_presupuesto"]
    foto_antes  = s["foto_antes"]
    foto_despues = s["foto_despues"]

    veh       = f"— {marca} {modelo} {anio}" if marca else ""
    monto_txt = f"&nbsp;|&nbsp; 💰 ${monto:,.0f}" if monto else ""
    turno_html = ""
    if s["estado"] in (ESTADOS["turno_confirmado"], ESTADOS["trabajo_completado"], ESTADOS["valorado"]) and s["fecha_turno"]:
        turno_html = (f'<div class="turno-box" style="margin-top:0.5rem">'
                      f'<div class="turno-txt">📅 Turno: {s["fecha_turno"]} a las {s["hora_turno"]}</div></div>')

    val = ejecutar("SELECT estrellas,comentario FROM valoraciones WHERE solicitud_id=%s", (sid,), fetch="one")
    val_html = ""
    if val:
        stars  = "⭐" * val["estrellas"]
        coment = f'<div style="font-size:0.85rem;color:#374151;margin-top:0.3rem">"{val["comentario"]}"</div>' if val["comentario"] else ""
        val_html = f'<div class="val-box"><span style="font-size:1rem">{stars}</span>{coment}</div>'

    render_sol_card(titulo=f"👤 {cliente} {veh}", meta=f"{s['fecha_creacion']}{monto_txt}",
                    estado=s["estado"], extra_html=turno_html + val_html)

    if foto_antes or foto_despues:
        with st.expander("📷 Ver fotos"):
            c1, c2 = st.columns(2)
            with c1: mostrar_foto(foto_antes,   "Antes",   280)
            with c2: mostrar_foto(foto_despues, "Después", 280)


def _titulo(texto):
    st.markdown(f"<div class='page-breadcrumb' style='font-size:1rem;font-weight:700;"
                f"color:#1E2A3A;margin-bottom:1rem'>{texto}</div>", unsafe_allow_html=True)
