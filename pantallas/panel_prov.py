# ═══════════════════════════════════════════════════════════════════
#  pantallas/panel_prov.py — Panel del especialista logueado.
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
from datetime import datetime
from config import APP_NAME, ESTADOS
from auth import cerrar_sesion, sanitizar
from database import get_connection
from email_utils import (enviar_email, email_presupuesto_recibido,
    email_turnos_propuestos, email_trabajo_completado)
from ui_components import fx_header, sidebar_brand, render_sol_card, formulario_cambiar_pw
from fotos import widget_subir_foto, guardar_foto, mostrar_foto


def panel_proveedor():
    prov_id     = st.session_state["proveedor_id"]
    prov_nombre = st.session_state["proveedor_nombre"]
    conn        = get_connection()
    prov_data   = conn.execute(
        "SELECT id,razon_social,email,rubros,grupo FROM proveedores WHERE id=?", (prov_id,)
    ).fetchone()
    if not prov_data:
        st.error("Especialista no encontrado.")
        cerrar_sesion()
        return

    sidebar_brand(prov_nombre, "Especialista")
    st.sidebar.caption(f"🛠 {prov_data[3]}")
    st.sidebar.markdown("<hr style='margin:1rem 0;border-color:#E2E8F0'>", unsafe_allow_html=True)
    opcion = st.sidebar.selectbox("", ["📋 Panel principal", "🔑 Cambiar contraseña"])
    st.sidebar.markdown("<hr style='margin:1rem 0;border-color:#E2E8F0'>", unsafe_allow_html=True)
    if st.sidebar.button("🔒 Cerrar sesión", use_container_width=True):
        cerrar_sesion()

    if opcion == "🔑 Cambiar contraseña":
        fx_header("ESPECIALISTA", "CAMBIAR CONTRASEÑA")
        _, col, _ = st.columns([1, 2, 1])
        with col:
            formulario_cambiar_pw("proveedores", prov_id, "prov_pw")
        return

    _panel_principal(prov_id, prov_nombre, prov_data[2] or "")


def _panel_principal(prov_id, prov_nombre, email_prov):
    fx_header("ESPECIALISTA", "MI PANEL")
    conn = get_connection()
    solicitudes = conn.execute(
        """SELECT s.id, c.nombre||' '||c.apellido, s.marca, s.modelo, s.anio,
                  s.descripcion, s.estado, s.email_cliente, s.monto_presupuesto,
                  s.detalle_presupuesto, s.fecha_turno, s.hora_turno, s.fecha_creacion,
                  s.foto_antes, s.foto_despues, s.grupo
           FROM solicitudes s JOIN clientes c ON c.id=s.cliente_id
           WHERE s.proveedor_id=? ORDER BY s.fecha_creacion DESC""",
        (prov_id,)
    ).fetchall()

    pendientes = [s for s in solicitudes if s[6] == ESTADOS["pendiente"]]
    pend_turno = [s for s in solicitudes if s[6] in (ESTADOS["aceptada"], ESTADOS["turno_rechazado"])]
    en_curso   = [s for s in solicitudes if s[6] == ESTADOS["turno_confirmado"]]
    otras      = [s for s in solicitudes if s[6] not in (
                    ESTADOS["pendiente"], ESTADOS["aceptada"],
                    ESTADOS["turno_rechazado"], ESTADOS["turno_confirmado"])]

    # ── Nuevas consultas ─────────────────────────────────────────
    _titulo(f"NUEVAS CONSULTAS ({len(pendientes)})")
    if not pendientes:
        st.info("No hay consultas nuevas por el momento.")
    for s in pendientes:
        _card_consulta(s, prov_nombre, email_prov, conn)

    # ── Pendientes de turno ──────────────────────────────────────
    if pend_turno:
        st.markdown("<hr class='fx-divider'>", unsafe_allow_html=True)
        _titulo(f"PENDIENTES DE TURNO ({len(pend_turno)})")
        for s in pend_turno:
            _card_proponer_turno(s, prov_nombre, email_prov, conn)

    # ── En curso ─────────────────────────────────────────────────
    if en_curso:
        st.markdown("<hr class='fx-divider'>", unsafe_allow_html=True)
        _titulo(f"TRABAJOS EN CURSO ({len(en_curso)})")
        for s in en_curso:
            _card_completar(s, prov_nombre, email_prov, conn)

    # ── Historial ────────────────────────────────────────────────
    if otras:
        st.markdown("<hr class='fx-divider'>", unsafe_allow_html=True)
        _titulo(f"HISTORIAL ({len(otras)})")
        for s in otras:
            _card_historial(s, conn)


# ── Card: nueva consulta → presupuesto en tabla ──────────────────
def _card_consulta(s, prov_nombre, email_prov, conn):
    (sid, cliente, marca, modelo, anio, desc, estado, email_c, monto, detalle,
     fecha_t, hora_t, fecha_cr, foto_antes, foto_despues, grupo) = s

    veh = f"— {marca} {modelo} {anio}" if marca else ""
    render_sol_card(
        titulo=f"👤 {cliente} {veh}",
        meta=f"📧 {email_c or '—'} &nbsp;|&nbsp; {fecha_cr}",
        descripcion=desc,
    )

    if foto_antes:
        with st.expander("📷 Ver foto del antes (enviada por el usuario)"):
            mostrar_foto(foto_antes, "Estado actual del problema", 350)
    elif "Vehículos" in (grupo or ""):
        st.caption("⚠️ El usuario no subió foto del vehículo.")

    with st.expander("💰 Responder con presupuesto"):
        st.markdown("**Agregá los ítems del trabajo** — el total se calcula automáticamente.")

        # CSS tabla
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
                desc_i = st.text_input(
                    f"desc_{i}", key=f"item_desc_{sid}_{i}",
                    placeholder="Ej: Mano de obra, Material, Traslado...",
                    label_visibility="collapsed",
                )
            with c2:
                monto_i = st.number_input(
                    f"monto_{i}", min_value=0.0, step=100.0,
                    key=f"item_monto_{sid}_{i}",
                    label_visibility="collapsed",
                )
            if desc_i:
                items.append((desc_i, monto_i))
                total += monto_i

        st.markdown(f"""
        <table class="presup-tabla">
          <tbody>
            <tr class="total-row">
              <td>TOTAL</td>
              <td>${total:,.0f}</td>
            </tr>
          </tbody>
        </table>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("ENVIAR PRESUPUESTO", key=f"env_{sid}", type="primary", use_container_width=True):
                items_validos = [(d, m) for d, m in items if d.strip()]
                if not items_validos:
                    st.error("Agregá al menos un ítem con descripción.")
                else:
                    lineas  = "\n".join([f"• {d}: ${m:,.0f}" for d, m in items_validos])
                    lineas += f"\n──────────────\nTOTAL: ${total:,.0f}"
                    conn.execute(
                        "UPDATE solicitudes SET estado=?,monto_presupuesto=?,detalle_presupuesto=? WHERE id=?",
                        (ESTADOS["presupuestada"], total, lineas, sid)
                    )
                    conn.commit()
                    trabajo = f"{marca} {modelo} {anio}" if marca else desc[:60]
                    enviar_email(email_c or "", f"Recibiste un presupuesto — {APP_NAME}", cliente,
                        email_presupuesto_recibido(cliente, prov_nombre, total, lineas, trabajo))
                    st.success("✅ Presupuesto enviado.")
                    st.rerun()
        with c2:
            if st.button("IGNORAR", key=f"ign_{sid}", use_container_width=True):
                conn.execute("UPDATE solicitudes SET estado=? WHERE id=?", (ESTADOS["rechazada"], sid))
                conn.commit()
                st.rerun()
    st.write("")


# ── Card: proponer turnos ────────────────────────────────────────
def _card_proponer_turno(s, prov_nombre, email_prov, conn):
    (sid, cliente, marca, modelo, anio, desc, estado, email_c, monto, detalle,
     fecha_t, hora_t, fecha_cr, foto_antes, foto_despues, grupo) = s

    veh   = f"— {marca} {modelo} {anio}" if marca else ""
    label = ("Presupuesto aceptado" if estado == ESTADOS["aceptada"]
             else "⚠️ Usuario rechazó las opciones — proponé nuevas")
    render_sol_card(
        titulo=f"👤 {cliente} {veh}",
        meta=f"📧 {email_c or '—'} &nbsp;|&nbsp; {label}",
        descripcion=desc,
    )

    with st.expander("📅 Proponer opciones de turno (hasta 3)"):
        st.markdown("Elegí hasta 3 fechas y horarios. El usuario elige la que le quede mejor.")
        n_op = int(st.number_input("¿Cuántas opciones?", min_value=1, max_value=3,
                                   value=2, step=1, key=f"nop_{sid}"))
        opciones_prop = []
        for i in range(n_op):
            ci, cj = st.columns(2)
            with ci:
                f = st.date_input(f"Fecha opción {i+1}", min_value=datetime.today(),
                                  key=f"tf_{sid}_{i}")
            with cj:
                h = st.selectbox(f"Hora opción {i+1}",
                                 [f"{hr:02d}:00" for hr in range(7, 21)],
                                 key=f"th_{sid}_{i}")
            opciones_prop.append((str(f), h))

        if st.button("ENVIAR OPCIONES DE TURNO", key=f"envt_{sid}",
                     type="primary", use_container_width=True):
            conn.execute("DELETE FROM turno_opciones WHERE solicitud_id=?", (sid,))
            for fo, ho in opciones_prop:
                conn.execute(
                    "INSERT INTO turno_opciones (solicitud_id,fecha,hora) VALUES (?,?,?)",
                    (sid, fo, ho)
                )
            conn.execute("UPDATE solicitudes SET estado=? WHERE id=?",
                         (ESTADOS["turno_propuesto"], sid))
            conn.commit()
            enviar_email(email_c or "", f"El especialista propuso turnos — {APP_NAME}", cliente,
                email_turnos_propuestos(prov_nombre, opciones_prop))
            st.success("✅ Opciones enviadas al usuario.")
            st.rerun()
    st.write("")


# ── Card: finalizar trabajo + foto del después ───────────────────
def _card_completar(s, prov_nombre, email_prov, conn):
    (sid, cliente, marca, modelo, anio, desc, estado, email_c, monto, detalle,
     fecha_t, hora_t, fecha_cr, foto_antes, foto_despues, grupo) = s

    veh = f"— {marca} {modelo} {anio}" if marca else ""
    render_sol_card(
        titulo=f"👤 {cliente} {veh}",
        meta=f"📅 Turno: {fecha_t} a las {hora_t}",
        estado=estado,
        descripcion=desc,
    )

    if foto_antes:
        with st.expander("📷 Ver foto del antes"):
            mostrar_foto(foto_antes, "Estado antes del trabajo", 300)

    with st.expander("🏁 Finalizar trabajo"):
        st.markdown("Subí la foto del trabajo terminado y marcalo como finalizado.")
        st.markdown("El cliente recibirá un email para que califique tu atención.")

        foto_despues_file = widget_subir_foto(
            "Foto del trabajo terminado",
            key=f"foto_despues_{sid}",
            obligatoria=True,
            ayuda="Subí una foto del trabajo finalizado.",
        )

        if st.button("🏁 CONFIRMAR TRABAJO FINALIZADO", key=f"comp_{sid}",
                     type="primary", use_container_width=True):
            if not foto_despues_file:
                st.error("La foto del trabajo terminado es obligatoria.")
            else:
                ruta_despues = guardar_foto(foto_despues_file)
                conn.execute(
                    "UPDATE solicitudes SET estado=?,foto_despues=? WHERE id=?",
                    (ESTADOS["trabajo_completado"], ruta_despues, sid)
                )
                conn.commit()
                trabajo = f"{marca} {modelo} {anio} — {desc[:60]}" if marca else desc[:80]
                enviar_email(email_c or "", f"Tu trabajo fue completado — {APP_NAME}", cliente,
                    email_trabajo_completado(prov_nombre, trabajo))
                st.success("✅ Trabajo finalizado. El cliente fue notificado para calificar.")
                st.rerun()
    st.write("")


# ── Card: historial con valoraciones ────────────────────────────
def _card_historial(s, conn):
    (sid, cliente, marca, modelo, anio, desc, estado, email_c, monto, detalle,
     fecha_t, hora_t, fecha_cr, foto_antes, foto_despues, grupo) = s

    veh       = f"— {marca} {modelo} {anio}" if marca else ""
    monto_txt = f"&nbsp;|&nbsp; 💰 ${monto:,.0f}" if monto else ""
    turno_html = ""
    if estado in (ESTADOS["turno_confirmado"], ESTADOS["trabajo_completado"], ESTADOS["valorado"]) and fecha_t:
        turno_html = (f'<div class="turno-box" style="margin-top:0.5rem">'
                      f'<div class="turno-txt">📅 Turno: {fecha_t} a las {hora_t}</div></div>')

    val = conn.execute(
        "SELECT estrellas,comentario FROM valoraciones WHERE solicitud_id=?", (sid,)
    ).fetchone()
    val_html = ""
    if val:
        stars  = "⭐" * val[0]
        coment = (f'<div style="font-size:0.85rem;color:#374151;margin-top:0.3rem">"{val[1]}"</div>'
                  if val[1] else "")
        val_html = f'<div class="val-box"><span style="font-size:1rem">{stars}</span>{coment}</div>'

    render_sol_card(
        titulo=f"👤 {cliente} {veh}",
        meta=f"{fecha_cr}{monto_txt}",
        estado=estado,
        extra_html=turno_html + val_html,
    )

    if foto_antes or foto_despues:
        with st.expander("📷 Ver fotos del trabajo"):
            c1, c2 = st.columns(2)
            with c1: mostrar_foto(foto_antes,   "Antes",   280)
            with c2: mostrar_foto(foto_despues, "Después", 280)


def _titulo(texto):
    st.markdown(
        f"<div class='page-breadcrumb' style='font-size:1rem;font-weight:700;"
        f"color:#1E2A3A;margin-bottom:1rem'>{texto}</div>",
        unsafe_allow_html=True,
    )
