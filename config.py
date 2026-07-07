# ═══════════════════════════════════════════════════════════════════
#  config.py — Constantes globales, CSS, logos y categorías.
#  Cualquier cambio de marca o estilo se hace SÓLO acá.
# ═══════════════════════════════════════════════════════════════════

APP_NAME    = "SolucionApp"
APP_TAGLINE = "CONECTÁ TU PROBLEMA CON QUIEN LO RESUELVE"

# ── Canon por servicio ───────────────────────────────────────────
CANON_USUARIO     = 2000
CANON_PROFESIONAL = 2000
MODO_PAGO         = "simulado"   # cambiar a "mercadopago" cuando tengas credenciales

# ── Estados de solicitud ─────────────────────────────────────────
ESTADOS: dict[str, str] = {
    "pendiente":          "pendiente",
    "presupuestada":      "presupuestada",
    "aceptada":           "aceptada",
    "rechazada":          "rechazada",
    "turno_propuesto":    "turno_propuesto",
    "turno_confirmado":   "turno_confirmado",
    "turno_rechazado":    "turno_rechazado",
    "trabajo_completado": "trabajo_completado",
    "valorado":           "valorado",
}

# ── Categorías de servicio ───────────────────────────────────────
# Ahora el profesional puede elegir MÚLTIPLES rubros dentro de su grupo.
CATEGORIAS: dict[str, list[str]] = {
    "🏠 Hogar": [
        "Plomería", "Electricidad", "Gasista", "Carpintería", "Pintura",
        "Albañilería", "Limpieza", "Climatización / Aire acondicionado",
        "Herrería", "Jardinería", "Cerrajería", "Techista", "Otro - Hogar",
    ],
    "🚗 Vehículos": [
        "Taller mecánico", "Chapista y pintura automotor", "Electricidad automotor",
        "Gomería", "Cambio de aceite / Service", "Rectificación de motor",
        "Taller de motos", "Grúa / Auxilio mecánico", "Polarizado / Car audio",
        "Otro - Vehículos",
    ],
}

# ── Carpeta de uploads ───────────────────────────────────────────
UPLOADS_DIR = "uploads"   # se crea automáticamente si no existe

# ── CSS Global ───────────────────────────────────────────────────
CSS_GLOBAL = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
.page-header { border-bottom: 2px solid #E2E8F0; margin-bottom: 1.8rem; padding-bottom: 1rem; }
.page-title  { font-size: 1.8rem; font-weight: 800; color: #1E2A3A; text-transform: uppercase; }
.page-breadcrumb { font-size: 0.82rem; color: #8A9BAC; font-weight: 500; margin-bottom: 0.3rem; }
.role-card { background: white; border-radius: 24px; padding: 2rem; border: 1px solid #E9EEF3;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: 0.3s; height: 100%; }
.role-card:hover { transform: translateY(-4px); box-shadow: 0 10px 25px rgba(0,0,0,0.10); }
.card-icon  { font-size: 2.2rem; margin-bottom: 0.8rem; }
.card-title { font-size: 1.5rem; font-weight: 700; color: #1E2A3A; margin-bottom: 0.4rem; }
.card-desc  { color: #5A6E7E; font-size: 0.92rem; line-height: 1.55; }
.cat-btn-wrap { display: flex; flex-direction: column; align-items: center; justify-content: center;
    background: white; border-radius: 20px; padding: 1.6rem 1rem; border: 2px solid #E9EEF3;
    box-shadow: 0 3px 10px rgba(0,0,0,0.05); transition: 0.25s; width: 100%; }
.cat-btn-wrap:hover { border-color: #3B82F6; box-shadow: 0 6px 20px rgba(59,130,246,0.15); transform: translateY(-3px); }
.cat-btn-emoji { font-size: 3.5rem; line-height: 1; margin-bottom: 0.6rem; }
.cat-btn-label { font-size: 1.1rem; font-weight: 700; color: #1E2A3A; margin-top: 0.4rem; }
.cat-btn-sub   { font-size: 0.82rem; color: #5A6E7E; margin-top: 0.2rem; text-align: center; }
.cat-question  { text-align: center; font-size: 1.35rem; font-weight: 700; color: #1E2A3A; margin: 1.5rem 0 1.8rem 0; }
.sol-card { background: white; border-radius: 16px; padding: 1.2rem 1.4rem; border: 1px solid #E9EEF3;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 0.8rem; }
.sol-titulo { font-size: 1rem; font-weight: 700; color: #1E2A3A; }
.sol-meta   { font-size: 0.82rem; color: #8A9BAC; margin-top: 0.15rem; }
.badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.78rem; font-weight: 600; }
.badge-pendiente    { background:#FEF9C3; color:#854D0E; }
.badge-presupuestada{ background:#DBEAFE; color:#1E40AF; }
.badge-aceptada     { background:#DCFCE7; color:#166534; }
.badge-rechazada    { background:#FEE2E2; color:#991B1B; }
.badge-turno        { background:#D1FAE5; color:#065F46; }
.badge-propuesto    { background:#EDE9FE; color:#5B21B6; }
.badge-completado   { background:#FEF3C7; color:#92400E; }
.sidebar-brand { font-size: 1.1rem; font-weight: 800; color: #1E2A3A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.2rem; }
.sidebar-user  { font-size: 0.85rem; color: #5A6E7E; margin-bottom: 1rem; }
.presup-box   { background: #F0F7FF; border-left: 4px solid #3B82F6; border-radius: 0 12px 12px 0; padding: 0.9rem 1.1rem; margin: 0.6rem 0; }
.presup-monto { font-size: 1.4rem; font-weight: 800; color: #1E40AF; }
.presup-det   { font-size: 0.88rem; color: #475569; margin-top: 0.2rem; white-space: pre-wrap; }
.turno-box  { background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 0 12px 12px 0; padding: 0.8rem 1.1rem; margin-top: 0.5rem; }
.turno-txt  { font-size: 0.95rem; font-weight: 600; color: #065F46; }
.val-box { background: #FFFBEB; border-left: 3px solid #F59E0B; border-radius: 0 8px 8px 0; padding: 0.5rem 0.8rem; margin-top: 0.5rem; }
.foto-box { background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 12px; padding: 1rem; margin-top: 0.5rem; }
.fx-divider { height: 2px; background: linear-gradient(90deg,#1E2A3A 0%,#E2E8F0 100%); border: none; margin: 1.5rem 0; }
.reg-sep { display: flex; align-items: center; gap: 1rem; color: #8A9BAC; font-size: 0.82rem; margin: 1.4rem 0; }
.reg-sep::before, .reg-sep::after { content: ''; flex: 1; height: 1px; background: #E2E8F0; }
</style>
"""

# ── Logo SVG ─────────────────────────────────────────────────────
LOGO_BIG = f"""
<div style="margin-bottom:2rem">
<svg width="100%" viewBox="0 0 780 130" xmlns="http://www.w3.org/2000/svg">
  <style>
    @keyframes fp1{{0%,100%{{r:7}}50%{{r:10}}}}
    @keyframes fp2{{0%,100%{{r:5}}50%{{r:7.5}}}}
    @keyframes ffl{{to{{stroke-dashoffset:-24}}}}
    .fa{{animation:fp1 2.2s ease-in-out infinite}}
    .fb{{animation:fp2 2.6s ease-in-out infinite .3s}}
    .fc{{animation:fp2 3.0s ease-in-out infinite .7s}}
    .fd{{animation:fp1 2.4s ease-in-out infinite 1.1s}}
    .ff{{stroke-dasharray:6 6;animation:ffl 1.3s linear infinite}}
  </style>
  <line x1="44" y1="28" x2="82" y2="52"  stroke="#3B82F6" stroke-width="2" fill="none" class="ff"/>
  <line x1="44" y1="28" x2="44" y2="78"  stroke="#3B82F6" stroke-width="2" fill="none" class="ff"/>
  <line x1="82" y1="52" x2="44" y2="78"  stroke="#CBD5E1" stroke-width="1.5" fill="none"/>
  <line x1="82" y1="52" x2="82" y2="102" stroke="#3B82F6" stroke-width="2" fill="none" class="ff"/>
  <line x1="44" y1="78" x2="82" y2="102" stroke="#CBD5E1" stroke-width="1.5" fill="none"/>
  <circle cx="44" cy="28"  r="7" fill="#1E40AF" class="fa"/>
  <circle cx="82" cy="52"  r="5" fill="#3B82F6" class="fb"/>
  <circle cx="44" cy="78"  r="5" fill="#10B981" class="fc"/>
  <circle cx="82" cy="102" r="7" fill="#1E40AF" class="fd"/>
  <text x="104" y="86" style="font-family:'Inter',sans-serif;font-weight:900;font-size:58px;letter-spacing:-2px;fill:#1E2A3A">{APP_NAME}</text>
  <text x="106" y="108" style="font-family:'Inter',sans-serif;font-weight:400;font-size:11px;fill:#5A6E7E;letter-spacing:4px">{APP_TAGLINE}</text>
  <line x1="104" y1="118" x2="740" y2="118" stroke="#E2E8F0" stroke-width="1.5"/>
  <circle cx="104" cy="118" r="3" fill="#1E40AF"/>
  <circle cx="740" cy="118" r="3" fill="#10B981"/>
</svg></div>"""

LOGO_SMALL = f"""
<div style="margin-bottom:1.2rem">
<svg width="200" viewBox="0 0 600 80" xmlns="http://www.w3.org/2000/svg">
  <style>
    @keyframes sfp{{0%,100%{{r:6}}50%{{r:8.5}}}}
    @keyframes sff{{to{{stroke-dashoffset:-20}}}}
    .sfa{{animation:sfp 2.2s ease-in-out infinite}}
    .sff{{stroke-dasharray:5 5;animation:sff 1.3s linear infinite}}
  </style>
  <line x1="28" y1="14" x2="54" y2="32" stroke="#3B82F6" stroke-width="2" fill="none" class="sff"/>
  <line x1="28" y1="14" x2="28" y2="56" stroke="#3B82F6" stroke-width="2" fill="none" class="sff"/>
  <line x1="54" y1="32" x2="28" y2="56" stroke="#CBD5E1" stroke-width="1.5" fill="none"/>
  <circle cx="28" cy="14" r="6" fill="#1E40AF" class="sfa"/>
  <circle cx="54" cy="32" r="4" fill="#3B82F6"/>
  <circle cx="28" cy="56" r="4" fill="#10B981"/>
  <text x="70" y="54" style="font-family:'Inter',sans-serif;font-weight:900;font-size:40px;letter-spacing:-1px;fill:#1E2A3A">{APP_NAME}</text>
  <line x1="70" y1="66" x2="580" y2="66" stroke="#E2E8F0" stroke-width="1.5"/>
  <circle cx="70"  cy="66" r="2.5" fill="#1E40AF"/>
  <circle cx="580" cy="66" r="2.5" fill="#10B981"/>
</svg></div>"""
