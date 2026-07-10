# ═══════════════════════════════════════════════════════════════════
#  pantallas/panel_cliente.py — Panel del usuario logueado.
# ═══════════════════════════════════════════════════════════════════

import math, json, urllib.request, urllib.parse
import streamlit as st
from datetime import datetime
from config import APP_NAME, ESTADOS, CATEGORIAS
from auth import cerrar_sesion, sanitizar
from database import get_connection
from email_utils import (enviar_email, email_presupuesto_aceptado,
    email_turno_confirmado_cliente, email_turno_confirmado_prov, email_turnos_rechazados)
from ui_components import fx_header, btn_volver, sidebar_brand, render_sol_card, render_presup_box, formulario_cambiar_pw
from fotos import widget_subir_foto, guardar_foto, mostrar_foto

def panel_cliente():
    cliente_id     = st.session_state["cliente_id"]
    cliente_nombre = st.session_state["cliente_nombre"]
    sidebar_brand(cliente_nombre, "Usuario")

    # ── NOTIFICACIÓN AUTOMÁTICA DE CALIFICACIONES PENDIENTES ─────
    from database import ejecutar
    pendientes_val = ejecutar(
        """SELECT s.id, p.razon_social, s.descripcion, s.fecha_turno
           FROM solicitudes s
           JOIN proveedores p ON p.id = s.proveedor_id
           LEFT JOIN valoraciones v ON v.solicitud_id = s.id
           WHERE s.cliente_id = %s
             AND s.estado = 'trabajo_completado'
             AND v.id IS NULL""",
        (cliente_id,), fetch="all"
    ) or []

    if pendientes_val:
        for pv in pendientes_val:
            st.warning(
                f"⭐ **Tenés una calificación pendiente** — "
                f"{pv['razon_social']}: {(pv['descripcion'] or '')[:50]}... "
                f"— [**Calificar ahora →**](#)",
                icon="⭐"
            )
            if st.button(f"CALIFICAR A {pv['razon_social'].upper()}",
                         key=f"notif_val_{pv['id']}", type="primary"):
                st.session_state["ir_a_solicitud"] = pv["id"]
                st.session_state["menu_forzado"]   = "📬 Mis solicitudes"
                st.rerun()

    # ── Menú ─────────────────────────────────────────────────────
    default_menu = st.session_state.pop("menu_forzado", "🔎 Buscar especialista")
    opciones     = ["🔎 Buscar especialista", "📬 Mis solicitudes", "🔑 Cambiar contraseña"]
    idx          = opciones.index(default_menu) if default_menu in opciones else 0
    opcion = st.sidebar.selectbox("Menú", opciones,
                                  index=idx, label_visibility="collapsed")
    st.sidebar.markdown("<hr style='margin:1rem 0;border-color:#E2E8F0'>", unsafe_allow_html=True)
    if st.sidebar.button("🔒 Cerrar sesión", use_container_width=True):
        cerrar_sesion()

    if   opcion == "🔎 Buscar especialista": _buscar(cliente_id, cliente_nombre)
    elif opcion == "📬 Mis solicitudes":     _mis_solicitudes(cliente_id, cliente_nombre)
    elif opcion == "🔑 Cambiar contraseña":
        fx_header("USUARIO","CAMBIAR CONTRASEÑA")
        _, col, _ = st.columns([1,2,1])
        with col: formulario_cambiar_pw("clientes", cliente_id, "cli_pw")

# ── Buscar ───────────────────────────────────────────────────────
def _buscar(cliente_id, cliente_nombre):
    if st.session_state["prov_seleccionado"] is not None:
        _pantalla_solicitar(cliente_id, cliente_nombre)
        return
    fx_header("USUARIO","BUSCAR ESPECIALISTA")
    if not st.session_state["cat_buscada"]:
        st.markdown('<div class="cat-question">¿Qué especialidad buscás?</div>', unsafe_allow_html=True)
        col_h, col_a = st.columns(2, gap="large")
        with col_h:
            st.markdown('<div class="cat-btn-wrap"><div class="cat-btn-emoji">🏠</div>'
                        '<div class="cat-btn-label">Hogar</div>'
                        '<div class="cat-btn-sub">Plomería, electricidad, pintura y más</div></div>', unsafe_allow_html=True)
            if st.button("VER SERVICIOS DE HOGAR", key="cat_hogar", use_container_width=True, type="primary"):
                st.session_state.update({"cat_buscada":"__hogar__","grupo_buscado":"🏠 Hogar"})
                st.rerun()
        with col_a:
            st.markdown('<div class="cat-btn-wrap"><div class="cat-btn-emoji">🚗</div>'
                        '<div class="cat-btn-label">Vehículos</div>'
                        '<div class="cat-btn-sub">Mecánica, chapería, gomería y más</div></div>', unsafe_allow_html=True)
            if st.button("VER SERVICIOS DE VEHÍCULOS", key="cat_auto", use_container_width=True):
                st.session_state.update({"cat_buscada":"__auto__","grupo_buscado":"🚗 Vehículos"})
                st.rerun()
    else:
        grupo_activo = st.session_state["grupo_buscado"]
        btn_volver("Cambiar categoría", key_suffix="back_cat", cat_buscada="", grupo_buscado="", resultados_busq=[])
        st.markdown(f"**{grupo_activo}** — elegí el rubro")
        busqueda = st.selectbox("Rubro", CATEGORIAS[grupo_activo], key="sel_rubro_activo")
        with st.expander("📍 Ordenar por cercanía (opcional)"):
            mi_dir = st.text_input("Tu dirección", key="mi_dir", placeholder="Av. Colón 1234, Córdoba")
        if st.button("BUSCAR ESPECIALISTAS", key="btn_buscar", type="primary"):
            conn = get_connection()
            # Busca en el campo rubros (que puede tener múltiples separados por coma)
            res  = conn.execute(
                "SELECT id,razon_social,rubros,grupo,direccion,encargado,contacto,email,latitud,longitud FROM proveedores WHERE rubros LIKE ? ORDER BY razon_social",
                (f"%{busqueda}%",)
            ).fetchall()
            mi_lat, mi_lon = _geocodificar(st.session_state.get("mi_dir",""))
            res_dist = []
            for p in res:
                dist = _dist_km(mi_lat, mi_lon, p[8], p[9]) if mi_lat and p[8] else None
                res_dist.append((p, dist))
            res_dist.sort(key=lambda x: x[1] if x[1] is not None else 9999)
            st.session_state.update({"resultados_busq": res_dist, "cat_buscada": busqueda})

        resultados = st.session_state["resultados_busq"]
        if resultados and st.session_state["cat_buscada"] not in ("__hogar__","__auto__"):
            st.write(f"**{len(resultados)} especialistas encontrados**")
            for prov, dist in resultados:
                _card_proveedor(prov, dist)

def _card_proveedor(prov, dist):
    conn  = get_connection()
    stats = conn.execute(
        """SELECT COUNT(s.id), AVG(s.monto_presupuesto), COUNT(v.id), AVG(v.estrellas)
           FROM solicitudes s LEFT JOIN valoraciones v ON v.solicitud_id=s.id
           WHERE s.proveedor_id=? AND s.estado IN ('aceptada','turno_propuesto','turno_confirmado','trabajo_completado','valorado')
           AND s.monto_presupuesto IS NOT NULL""",
        (prov[0],)
    ).fetchone()
    partes = []
    if dist is not None:         partes.append(f"📍 {dist:.1f} km")
    if stats[1]:                 partes.append(f"💰 Promedio: ${stats[1]:,.0f}")
    if stats[3] and stats[2]>0: partes.append(f"{'⭐'*round(stats[3])} {stats[3]:.1f} ({stats[2]} opiniones)")
    elif stats[0]:               partes.append(f"📋 {stats[0]} trabajo{'s' if stats[0]>1 else ''}")
    stats_html = (f'<div style="margin-top:0.5rem;font-size:0.85rem;color:#374151">'+" &nbsp;|&nbsp; ".join(partes)+"</div>") if partes else ""
    # Mostrar rubros del proveedor
    rubros_html = f'<div style="margin-top:0.3rem;font-size:0.82rem;color:#3B82F6">🛠 {prov[2]}</div>'
    render_sol_card(
        titulo=f"🔧 {prov[1]}",
        meta=f"👤 {prov[5] or '—'} &nbsp;|&nbsp; 📞 {prov[6] or '—'} &nbsp;|&nbsp; 📍 {prov[4] or '—'}",
        extra_html=rubros_html+stats_html,
    )
    if st.button("SOLICITAR PRESUPUESTO →", key=f"sel_{prov[0]}", type="primary"):
        st.session_state["prov_seleccionado"] = prov
        st.rerun()

def _pantalla_solicitar(cliente_id, cliente_nombre):
    prov = st.session_state["prov_seleccionado"]
    fx_header("USUARIO / BUSCAR","SOLICITAR PRESUPUESTO")
    btn_volver("Volver a resultados", key_suffix="back_res", prov_seleccionado=None)
    render_sol_card(titulo=f"🔧 {prov[1]}", meta=f"🛠 {prov[2]} &nbsp;|&nbsp; 📍 {prov[4] or '—'}")
    es_vehiculo = "Vehículos" in (prov[3] if len(prov)>3 else "")
    if es_vehiculo:
        st.markdown("**Datos del vehículo**")
        c1,c2,c3 = st.columns(3)
        with c1: marca  = st.text_input("Marca *",  placeholder="Toyota")
        with c2: modelo = st.text_input("Modelo",   placeholder="Corolla")
        with c3: anio   = st.text_input("Año",      placeholder="2018")
    else:
        marca = modelo = anio = ""
    descripcion = st.text_area("Describí el problema o trabajo *", max_chars=500, height=120,
        placeholder="Cuanto más detalle des, mejor podrá presupuestarte el especialista.")

    # ── Foto del ANTES ────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**📷 Foto del problema / estado actual**")
    foto_obligatoria = es_vehiculo  # obligatoria en automotor, opcional en hogar
    foto_antes_file  = widget_subir_foto(
        "Foto del antes",
        key="foto_antes_solicitud",
        obligatoria=foto_obligatoria,
        ayuda="Subí una foto del problema o del vehículo antes de la reparación.",
    )

    conn    = get_connection()
    row_cli = conn.execute("SELECT email FROM clientes WHERE id=?", (cliente_id,)).fetchone()
    email_c = row_cli[0] if row_cli else ""
    st.write("")

    if st.button("ENVIAR SOLICITUD", type="primary", use_container_width=True):
        err = []
        if not descripcion:                    err.append("Descripción del trabajo")
        if es_vehiculo and not marca:          err.append("Marca del vehículo")
        if foto_obligatoria and not foto_antes_file: err.append("Foto del vehículo (obligatoria para automotor)")
        if err:
            st.error("Corregí: " + ", ".join(err))
        else:
            ruta_foto = guardar_foto(foto_antes_file) if foto_antes_file else None
            conn.execute(
                """INSERT INTO solicitudes
                   (cliente_id,proveedor_id,grupo,marca,modelo,anio,descripcion,email_cliente,foto_antes)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (cliente_id, prov[0], prov[3] if len(prov)>3 else "",
                 sanitizar(marca,50), sanitizar(modelo,50), sanitizar(anio,4),
                 sanitizar(descripcion,500), email_c, ruta_foto)
            )
            conn.commit()
            email_prov = prov[7] if len(prov)>7 else ""
            encargado  = prov[5] if len(prov)>5 else prov[1]
            enviar_email(email_prov, f"Nueva consulta — {APP_NAME}", encargado,
                f"<p>Recibiste una consulta de <b>{cliente_nombre}</b>.</p>"
                f"<p><b>Detalle:</b> {descripcion}</p>"
                + (f"<p><b>Vehículo:</b> {marca} {modelo} {anio}</p>" if marca else ""))
            enviar_email(email_c, f"Solicitud enviada — {APP_NAME}", cliente_nombre,
                f"<p>Tu solicitud fue enviada a <b>{prov[1]}</b>.</p>"
                f"<p>Te avisaremos cuando el especialista responda.</p>")
            st.success("✅ Solicitud enviada.")
            st.session_state.update({"prov_seleccionado": None, "resultados_busq": []})
            st.rerun()

# ── Mis solicitudes ───────────────────────────────────────────────
def _mis_solicitudes(cliente_id, cliente_nombre):
    fx_header("USUARIO","MIS SOLICITUDES")
    conn = get_connection()
    solicitudes = conn.execute(
        """SELECT s.id,p.razon_social,s.marca,s.modelo,s.anio,s.descripcion,s.estado,
                  s.monto_presupuesto,s.detalle_presupuesto,s.fecha_turno,s.hora_turno,
                  p.email,s.email_cliente,s.fecha_creacion,p.grupo,p.id,s.foto_antes,s.foto_despues
           FROM solicitudes s JOIN proveedores p ON p.id=s.proveedor_id
           WHERE s.cliente_id=? ORDER BY s.fecha_creacion DESC""",
        (cliente_id,)
    ).fetchall()
    if not solicitudes:
        st.info("Todavía no tenés solicitudes. ¡Buscá un especialista para empezar!")
        return
    for s in solicitudes:
        (sid,razon,marca,modelo,anio,desc,estado,monto,detalle,
         fecha_t,hora_t,email_p,email_c,fecha_cr,grupo,prov_id,foto_antes,foto_despues) = s
        veh = f"— {marca} {modelo} {anio}" if marca else ""
        turno_html = ""
        if estado in (ESTADOS["turno_confirmado"],ESTADOS["trabajo_completado"],ESTADOS["valorado"]) and fecha_t:
            turno_html = f'<div class="turno-box"><div class="turno-txt">📅 Turno: {fecha_t} a las {hora_t}</div></div>'
        render_sol_card(titulo=f"🔧 {razon} {veh}", meta=f"Solicitado: {fecha_cr}", estado=estado, extra_html=turno_html)

        # Fotos
        if foto_antes or foto_despues:
            with st.expander("📷 Ver fotos"):
                c1,c2 = st.columns(2)
                with c1: mostrar_foto(foto_antes,   "Antes", 280)
                with c2: mostrar_foto(foto_despues, "Después", 280)

        # ── Aceptar / rechazar presupuesto ──────────────────────
        if estado == ESTADOS["presupuestada"] and monto is not None:
            render_presup_box(monto, detalle or "")
            ca, cb = st.columns(2)
            with ca:
                if st.button("✅ ACEPTAR PRESUPUESTO", key=f"acep_{sid}",
                             type="primary", use_container_width=True):
                    conn.execute("UPDATE solicitudes SET estado=? WHERE id=?",
                                 (ESTADOS["aceptada"], sid))
                    conn.commit()
                    from pagos import registrar_canon
                    registrar_canon(sid, "usuario")
                    enviar_email(email_p or "", f"Presupuesto aceptado — {APP_NAME}", razon,
                        email_presupuesto_aceptado(razon, desc or ""))
                    st.rerun()
            with cb:
                if st.button("❌ RECHAZAR", key=f"rech_{sid}", use_container_width=True):
                    conn.execute("UPDATE solicitudes SET estado=? WHERE id=?",
                                 (ESTADOS["rechazada"], sid))
                    conn.commit()
                    st.rerun()

        # ── Elegir turno ─────────────────────────────────────────
        if estado == ESTADOS["turno_propuesto"]:
            opciones = conn.execute(
                "SELECT id,fecha,hora FROM turno_opciones WHERE solicitud_id=? AND estado='propuesta'", (sid,)
            ).fetchall()
            if opciones:
                st.markdown("**📅 El especialista propuso estas opciones — elegí una:**")
                for oid,ofecha,ohora in opciones:
                    col_op,col_btn = st.columns([3,1])
                    with col_op: st.markdown(f"📆 **{ofecha}** a las **{ohora}**")
                    with col_btn:
                        if st.button("ELEGIR", key=f"elegir_{oid}", type="primary"):
                            conn.execute("UPDATE turno_opciones SET estado='rechazada' WHERE solicitud_id=?", (sid,))
                            conn.execute("UPDATE turno_opciones SET estado='confirmada' WHERE id=?", (oid,))
                            conn.execute("UPDATE solicitudes SET estado=?,fecha_turno=?,hora_turno=? WHERE id=?",
                                         (ESTADOS["turno_confirmado"],ofecha,ohora,sid))
                            conn.commit()
                            enviar_email(email_p or "", f"Turno confirmado — {APP_NAME}", razon,
                                email_turno_confirmado_prov(cliente_nombre,ofecha,ohora,desc or ""))
                            enviar_email(email_c or "", f"Turno confirmado — {APP_NAME}", cliente_nombre,
                                email_turno_confirmado_cliente(razon,ofecha,ohora))
                            st.success(f"✅ Turno confirmado: {ofecha} a las {ohora}")
                            st.rerun()
                st.write("")
                if st.button("❌ RECHAZAR TODAS LAS OPCIONES", key=f"rech_turno_{sid}", use_container_width=True):
                    conn.execute("UPDATE turno_opciones SET estado='rechazada' WHERE solicitud_id=?", (sid,))
                    conn.execute("UPDATE solicitudes SET estado=? WHERE id=?", (ESTADOS["turno_rechazado"],sid))
                    conn.commit()
                    enviar_email(email_p or "", f"Opciones rechazadas — {APP_NAME}", razon, email_turnos_rechazados(razon))
                    st.rerun()

        # ── Calificar (solo después de trabajo_completado) ───────
        if estado == ESTADOS["trabajo_completado"]:
            ya_val = conn.execute("SELECT id FROM valoraciones WHERE solicitud_id=?", (sid,)).fetchone()
            if not ya_val:
                st.markdown("---")
                st.markdown("**⭐ El especialista terminó el trabajo. ¿Cómo te fue?**")

                # Botones de estrellas
                if f"estrellas_{sid}" not in st.session_state:
                    st.session_state[f"estrellas_{sid}"] = 0

                st.markdown("**Puntuación** *(obligatoria)* — tocá una estrella:")
                cols = st.columns(5)
                labels = {1:"😞 Muy malo", 2:"😐 Malo", 3:"🙂 Regular", 4:"😊 Bueno", 5:"🤩 Excelente"}
                for i, col in enumerate(cols, 1):
                    with col:
                        sel = st.session_state[f"estrellas_{sid}"] >= i
                        if st.button("⭐" if sel else "☆",
                                     key=f"star_{sid}_{i}",
                                     use_container_width=True,
                                     type="primary" if sel else "secondary"):
                            st.session_state[f"estrellas_{sid}"] = i
                            st.rerun()

                estrellas_sel = st.session_state[f"estrellas_{sid}"]
                if estrellas_sel > 0:
                    st.markdown(f"**{labels[estrellas_sel]}** — {estrellas_sel}/5")

                comentario = st.text_area("Comentario (opcional)", key=f"coment_{sid}",
                                          max_chars=300,
                                          placeholder="Contá cómo fue la experiencia...")
                if st.button("ENVIAR CALIFICACIÓN", key=f"val_{sid}",
                             type="primary", use_container_width=True):
                    if estrellas_sel == 0:
                        st.error("Por favor elegí una puntuación antes de enviar.")
                    else:
                        conn.execute(
                            "INSERT INTO valoraciones (solicitud_id,cliente_id,proveedor_id,estrellas,comentario) VALUES (?,?,?,?,?)",
                            (sid, cliente_id, prov_id, estrellas_sel, sanitizar(comentario, 300))
                        )
                        conn.execute("UPDATE solicitudes SET estado=? WHERE id=?",
                                     (ESTADOS["valorado"], sid))
                        conn.commit()
                        st.success("✅ ¡Gracias por tu calificación!")
                        st.rerun()
            else:
                st.success("✅ Ya calificaste este trabajo.")
        st.write("")

# ── Helpers geoespaciales ────────────────────────────────────────
def _geocodificar(dir):
    if not dir or len(dir)<5: return None,None
    try:
        q   = urllib.parse.urlencode({"q":dir,"format":"json","limit":"1"})
        req = urllib.request.Request(f"https://nominatim.openstreetmap.org/search?{q}", headers={"User-Agent":"SolucionApp/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        if data: return float(data[0]["lat"]), float(data[0]["lon"])
    except: pass
    return None,None

def _dist_km(lat1,lon1,lat2,lon2):
    if not all([lat1,lon1,lat2,lon2]): return None
    R=6371; dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R*2*math.atan2(math.sqrt(a),math.sqrt(1-a))
