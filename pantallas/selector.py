# ═══════════════════════════════════════════════════════════════════
#  pantallas/selector.py — Pantalla de bienvenida.
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
from config import LOGO_BIG

def pantalla_selector():
    # ── VOLVER AL INICIO (index.html) ────────────────────────────
    st.markdown("""
    <div style="margin-bottom:1rem">
        <a href="http://localhost:8080/index.html"
           style="display:inline-flex;align-items:center;gap:0.4rem;
                  color:#5A6E7E;font-size:0.88rem;text-decoration:none;
                  padding:0.4rem 0.8rem;border-radius:8px;border:1px solid #E2E8F0;
                  background:white;transition:all 0.2s"
           onmouseover="this.style.borderColor='#3B82F6';this.style.color='#1E40AF'"
           onmouseout="this.style.borderColor='#E2E8F0';this.style.color='#5A6E7E'">
           ← Volver al inicio
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(LOGO_BIG, unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("""<div class="role-card">
            <div class="card-icon">👤</div>
            <div class="card-title">Soy Usuario</div>
            <div class="card-desc">Necesito un especialista para mi hogar o vehículo.
            Pedí presupuestos y agendá un turno en minutos.</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="role-card">
            <div class="card-icon">🔧</div>
            <div class="card-title">Soy Especialista</div>
            <div class="card-desc">Ofrezco servicios profesionales. Gestioná consultas,
            enviá presupuestos y hacé crecer tu negocio.</div>
        </div>""", unsafe_allow_html=True)
    st.write("")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button("INGRESAR COMO USUARIO", use_container_width=True, type="primary"):
            st.session_state.update({"modo": "cliente", "auth_step": "auth"})
            st.rerun()
    with col2:
        if st.button("INGRESAR COMO ESPECIALISTA", use_container_width=True):
            st.session_state.update({"modo": "proveedor", "auth_step": "auth"})
            st.rerun()
