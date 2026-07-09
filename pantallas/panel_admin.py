# ═══════════════════════════════════════════════════════════════════
#  pantallas/panel_admin.py
#  FUNCIÓN: Panel de administrador
#  Acceso solo con usuario y contraseña de admin.
#  Permite ver estadísticas, usuarios y descargar backup de la base.
# ═══════════════════════════════════════════════════════════════════

import io
import csv
import json
import streamlit as st
from database import ejecutar
from ui_components import fx_header


# ── LOGIN ADMIN ──────────────────────────────────────────────────
def _verificar_admin() -> bool:
    """Verifica las credenciales del administrador contra los secrets."""
    import os
    def _secret(k, fb=""):
        try:    return st.secrets[k]
        except: return os.environ.get(k, fb)
    user_ok = st.session_state.get("admin_user","") == _secret("ADMIN_USER","admin")
    pw_ok   = st.session_state.get("admin_pw","")   == _secret("ADMIN_PASSWORD","")
    return user_ok and pw_ok


def pantalla_admin() -> None:
    """Pantalla de login y panel del administrador."""

    # ── LOGIN ────────────────────────────────────────────────────
    if not st.session_state.get("admin_logueado"):
        st.markdown("## 🔐 Administrador — SolucionApp")
        usuario = st.text_input("Usuario", key="admin_user")
        pw      = st.text_input("Contraseña", type="password", key="admin_pw")
        if st.button("INGRESAR", type="primary"):
            if _verificar_admin():
                st.session_state["admin_logueado"] = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")
        return

    # ── PANEL ADMIN ──────────────────────────────────────────────
    fx_header("ADMINISTRADOR", "PANEL DE CONTROL")

    if st.sidebar.button("🔒 Cerrar sesión admin"):
        st.session_state["admin_logueado"] = False
        st.session_state["auth_step"]      = "selector"
        st.rerun()

    opcion = st.sidebar.selectbox("Sección", [
        "📊 Estadísticas",
        "👤 Usuarios",
        "🔧 Especialistas",
        "📋 Solicitudes",
        "💾 Backup / Descarga",
    ])

    if   opcion == "📊 Estadísticas":   _seccion_stats()
    elif opcion == "👤 Usuarios":        _seccion_clientes()
    elif opcion == "🔧 Especialistas":   _seccion_proveedores()
    elif opcion == "📋 Solicitudes":     _seccion_solicitudes()
    elif opcion == "💾 Backup / Descarga": _seccion_backup()


# ── ESTADÍSTICAS ─────────────────────────────────────────────────
def _seccion_stats():
    st.markdown("### 📊 Estadísticas generales")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        n = ejecutar("SELECT COUNT(*) as n FROM clientes", fetch="one")
        st.metric("Usuarios registrados", n["n"] if n else 0)
    with c2:
        n = ejecutar("SELECT COUNT(*) as n FROM proveedores", fetch="one")
        st.metric("Especialistas", n["n"] if n else 0)
    with c3:
        n = ejecutar("SELECT COUNT(*) as n FROM solicitudes", fetch="one")
        st.metric("Solicitudes totales", n["n"] if n else 0)
    with c4:
        n = ejecutar("SELECT COUNT(*) as n FROM valoraciones", fetch="one")
        st.metric("Calificaciones", n["n"] if n else 0)

    st.markdown("### Solicitudes por estado")
    rows = ejecutar(
        "SELECT estado, COUNT(*) as n FROM solicitudes GROUP BY estado ORDER BY n DESC",
        fetch="all"
    ) or []
    for r in rows:
        st.write(f"**{r['estado']}:** {r['n']}")


# ── USUARIOS ─────────────────────────────────────────────────────
def _seccion_clientes():
    st.markdown("### 👤 Usuarios registrados")
    rows = ejecutar(
        "SELECT id, nombre, apellido, email, dni, fecha_creacion FROM clientes ORDER BY id DESC",
        fetch="all"
    ) or []
    if not rows:
        st.info("No hay usuarios registrados.")
        return
    for r in rows:
        with st.expander(f"#{r['id']} — {r['nombre']} {r['apellido']} — {r['email']}"):
            st.write(f"**DNI:** {r['dni']}")
            st.write(f"**Registrado:** {r['fecha_creacion']}")
            if st.button("🗑️ Eliminar usuario", key=f"del_cli_{r['id']}"):
                ejecutar("DELETE FROM clientes WHERE id=%s", (r["id"],))
                st.success("Usuario eliminado.")
                st.rerun()


# ── ESPECIALISTAS ────────────────────────────────────────────────
def _seccion_proveedores():
    st.markdown("### 🔧 Especialistas registrados")
    rows = ejecutar(
        "SELECT id, razon_social, email, rubros, grupo FROM proveedores ORDER BY id DESC",
        fetch="all"
    ) or []
    if not rows:
        st.info("No hay especialistas registrados.")
        return
    for r in rows:
        with st.expander(f"#{r['id']} — {r['razon_social']} — {r['email']}"):
            st.write(f"**Rubros:** {r['rubros']}")
            st.write(f"**Grupo:** {r['grupo']}")
            if st.button("🗑️ Eliminar especialista", key=f"del_prov_{r['id']}"):
                ejecutar("DELETE FROM proveedores WHERE id=%s", (r["id"],))
                st.success("Especialista eliminado.")
                st.rerun()


# ── SOLICITUDES ──────────────────────────────────────────────────
def _seccion_solicitudes():
    st.markdown("### 📋 Últimas solicitudes")
    rows = ejecutar(
        """SELECT s.id, c.nombre||' '||c.apellido as cliente,
                  p.razon_social as especialista, s.estado,
                  s.monto_presupuesto, s.fecha_creacion
           FROM solicitudes s
           JOIN clientes c ON c.id=s.cliente_id
           JOIN proveedores p ON p.id=s.proveedor_id
           ORDER BY s.id DESC LIMIT 50""",
        fetch="all"
    ) or []
    if not rows:
        st.info("No hay solicitudes.")
        return
    for r in rows:
        st.markdown(
            f"**#{r['id']}** — {r['cliente']} → {r['especialista']} "
            f"| Estado: `{r['estado']}` "
            f"| Monto: ${r['monto_presupuesto']:,.0f}" if r['monto_presupuesto'] else
            f"**#{r['id']}** — {r['cliente']} → {r['especialista']} | Estado: `{r['estado']}`"
        )


# ── BACKUP / DESCARGA ────────────────────────────────────────────
def _seccion_backup():
    st.markdown("### 💾 Backup y descarga de datos")
    st.info("Descargá cada tabla como CSV o el backup completo en JSON.")

    tablas = ["clientes", "proveedores", "solicitudes", "valoraciones",
              "turno_opciones", "rubros_personalizados", "canon_cobros"]

    # ── Descarga individual por tabla ────────────────────────────
    st.markdown("#### Descargar tabla individual")
    tabla_sel = st.selectbox("Elegí la tabla", tablas)
    if st.button("📥 DESCARGAR CSV", type="primary"):
        rows = ejecutar(f"SELECT * FROM {tabla_sel}", fetch="all") or []
        if not rows:
            st.warning("La tabla está vacía.")
        else:
            buf = io.StringIO()
            w   = csv.DictWriter(buf, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows([dict(r) for r in rows])
            st.download_button(
                label=f"⬇️ {tabla_sel}.csv",
                data=buf.getvalue().encode("utf-8"),
                file_name=f"{tabla_sel}.csv",
                mime="text/csv",
            )

    # ── Backup completo en JSON ──────────────────────────────────
    st.markdown("---")
    st.markdown("#### Backup completo (todas las tablas)")
    if st.button("📦 GENERAR BACKUP COMPLETO"):
        backup = {}
        for t in tablas:
            rows = ejecutar(f"SELECT * FROM {t}", fetch="all") or []
            backup[t] = [dict(r) for r in rows]

        # Convertir fechas a string para JSON
        backup_str = json.dumps(backup, default=str, ensure_ascii=False, indent=2)
        st.download_button(
            label="⬇️ backup_solucionapp.json",
            data=backup_str.encode("utf-8"),
            file_name="backup_solucionapp.json",
            mime="application/json",
        )
        st.success(f"✅ Backup generado con {sum(len(v) for v in backup.values())} registros en total.")
