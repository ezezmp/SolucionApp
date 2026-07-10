# ═══════════════════════════════════════════════════════════════════
#  config.py
#  FUNCIÓN: Configuración global de la aplicación
#  Acá se define TODO lo que tiene que ver con la identidad visual,
#  los nombres, colores, categorías y estados de la app.
#  Si querés cambiar el nombre, un color o agregar un rubro,
#  este es el ÚNICO archivo que tenés que tocar.
# ═══════════════════════════════════════════════════════════════════

# ── NOMBRE Y SLOGAN ─────────────────────────────────────────────
# Nombre de la aplicación — aparece en el logo, emails y títulos
APP_NAME    = "SolucionApp"
# Slogan que aparece debajo del logo
APP_TAGLINE = "CONECTÁ TU PROBLEMA CON QUIEN LO RESUELVE"

# ── CANON POR SERVICIO ───────────────────────────────────────────
# Monto fijo que se cobra a cada parte cuando se completa un trabajo
CANON_USUARIO     = 2000   # lo paga el usuario
CANON_PROFESIONAL = 2000   # lo paga el especialista
# "simulado" = no cobra nada real, solo lo registra internamente
# Cambiar a "mercadopago" cuando tengas las credenciales de MP
MODO_PAGO = "simulado"

# ── ESTADOS DE UNA SOLICITUD ─────────────────────────────────────
# Ciclo de vida de cada pedido de presupuesto.
# El orden es: pendiente → presupuestada → aceptada → turno_propuesto
#              → turno_confirmado → trabajo_completado → valorado
ESTADOS: dict[str, str] = {
    "pendiente":          "pendiente",          # recién creada, sin respuesta del especialista
    "presupuestada":      "presupuestada",      # el especialista envió el presupuesto
    "aceptada":           "aceptada",           # el usuario aceptó el presupuesto
    "rechazada":          "rechazada",          # el usuario rechazó el presupuesto
    "turno_propuesto":    "turno_propuesto",    # el especialista propuso fechas de turno
    "turno_confirmado":   "turno_confirmado",   # el usuario eligió una fecha
    "turno_rechazado":    "turno_rechazado",    # el usuario rechazó todas las fechas
    "trabajo_completado": "trabajo_completado", # el especialista marcó el trabajo como terminado
    "valorado":           "valorado",           # el usuario dejó su calificación
}

# ── CATEGORÍAS DE SERVICIO ───────────────────────────────────────
# Grupos de rubros disponibles. El especialista elige uno o más rubros
# al momento de registrarse. El usuario busca por rubro.
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

# ── CARPETA DE FOTOS ─────────────────────────────────────────────
# Las fotos del antes y después se guardan en esta carpeta local.
# En producción (hosting), esta carpeta vive en el servidor.
UPLOADS_DIR = "uploads"

# ── ESTILOS CSS GLOBALES ─────────────────────────────────────────
# Todo el diseño visual de la app está acá.
# Usa variables de color para mantener consistencia.
# Si querés cambiar colores principales: buscar #1E2A3A (oscuro) y #3B82F6 (azul)
CSS_GLOBAL = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1100px; }

/* ── HEADERS ── */
.page-header { border-bottom: 2px solid #E2E8F0; margin-bottom: 1.8rem; padding-bottom: 1rem; }
.page-title  { font-size: 1.8rem; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: -0.5px; }
.page-breadcrumb { font-size: 0.78rem; color: #3B82F6; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 0.3rem; }

/* ── CARDS SELECTOR ── */
.role-card { background: white; border-radius: 20px; padding: 2rem; border: 1px solid #E2E8F0;
    transition: all 0.3s; height: 100%; }
.role-card:hover { transform: translateY(-5px); border-color: #3B82F6; box-shadow: 0 8px 24px rgba(59,130,246,0.12); }
.card-icon  { font-size: 2.2rem; margin-bottom: 0.8rem; }
.card-title { font-size: 1.4rem; font-weight: 800; color: #0F172A; margin-bottom: 0.4rem; letter-spacing: -0.3px; }
.card-desc  { color: #64748B; font-size: 0.9rem; line-height: 1.6; }

/* ── CATEGORIA BOTONES ── */
.cat-btn-wrap { display: flex; flex-direction: column; align-items: center; justify-content: center;
    background: white; border-radius: 20px; padding: 1.6rem 1rem; border: 1px solid #E2E8F0;
    transition: all 0.25s; width: 100%; }
.cat-btn-wrap:hover { border-color: #3B82F6; box-shadow: 0 6px 20px rgba(59,130,246,0.12); transform: translateY(-3px); }
.cat-btn-emoji { font-size: 3.5rem; line-height: 1; margin-bottom: 0.6rem; }
.cat-btn-label { font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-top: 0.4rem; }
.cat-btn-sub   { font-size: 0.82rem; color: #64748B; margin-top: 0.2rem; text-align: center; }
.cat-question  { text-align: center; font-size: 1.35rem; font-weight: 800; color: #0F172A; margin: 1.5rem 0 1.8rem 0; letter-spacing: -0.3px; }

/* ── CARDS SOLICITUD ── */
.sol-card { background: white; border-radius: 16px; padding: 1.2rem 1.4rem; border: 1px solid #E2E8F0;
    margin-bottom: 0.8rem; transition: all 0.2s; }
.sol-card:hover { border-color: rgba(59,130,246,0.3); box-shadow: 0 4px 16px rgba(0,0,0,0.05); }
.sol-titulo { font-size: 1rem; font-weight: 700; color: #0F172A; }
.sol-meta   { font-size: 0.82rem; color: #94A3B8; margin-top: 0.15rem; }

/* ── BADGES ── */
.badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }
.badge-pendiente    { background:#FEF9C3; color:#854D0E; }
.badge-presupuestada{ background:#DBEAFE; color:#1E40AF; }
.badge-aceptada     { background:#DCFCE7; color:#166534; }
.badge-rechazada    { background:#FEE2E2; color:#991B1B; }
.badge-turno        { background:#D1FAE5; color:#065F46; }
.badge-propuesto    { background:#EDE9FE; color:#5B21B6; }
.badge-completado   { background:#FEF3C7; color:#92400E; }

/* ── SIDEBAR ── */
.sidebar-brand { font-size: 1rem; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.2rem; }
.sidebar-user  { font-size: 0.82rem; color: #64748B; margin-bottom: 1rem; }
[data-testid="stSidebar"] { background: #0F172A !important; }
[data-testid="stSidebar"] * { color: #94A3B8 !important; }
[data-testid="stSidebar"] .sidebar-brand { color: #fff !important; }
[data-testid="stSidebar"] .sidebar-user  { color: #64748B !important; }
[data-testid="stSidebar"] hr { border-color: #1E2A3A !important; }
[data-testid="stSidebarNav"] { display: none; }
[data-testid="stSidebar"] button { background: #1E2A3A !important; color: #94A3B8 !important; border: none !important; }
[data-testid="stSidebar"] button:hover { background: #1E40AF !important; color: #fff !important; }
[data-testid="stSidebar"] select { background: #1E2A3A !important; color: #fff !important; border: none !important; }

/* ── PRESUPUESTO / TURNO / VALORACIÓN ── */
.presup-box   { background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 0 12px 12px 0; padding: 0.9rem 1.1rem; margin: 0.6rem 0; }
.presup-monto { font-size: 1.4rem; font-weight: 800; color: #1E40AF; }
.presup-det   { font-size: 0.88rem; color: #475569; margin-top: 0.2rem; white-space: pre-wrap; }
.turno-box  { background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 0 12px 12px 0; padding: 0.8rem 1.1rem; margin-top: 0.5rem; }
.turno-txt  { font-size: 0.95rem; font-weight: 600; color: #065F46; }
.val-box { background: #FFFBEB; border-left: 3px solid #F59E0B; border-radius: 0 8px 8px 0; padding: 0.5rem 0.8rem; margin-top: 0.5rem; }
.foto-box { background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 12px; padding: 1rem; margin-top: 0.5rem; }

/* ── DIVIDERS ── */
.fx-divider { height: 2px; background: linear-gradient(90deg,#0F172A 0%,#E2E8F0 100%); border: none; margin: 1.5rem 0; }
.reg-sep { display: flex; align-items: center; gap: 1rem; color: #94A3B8; font-size: 0.82rem; margin: 1.4rem 0; }
.reg-sep::before, .reg-sep::after { content: ''; flex: 1; height: 1px; background: #E2E8F0; }

/* ── BOTONES STREAMLIT ── */
.stButton > button {
    background: #0F172A !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-family: 'Inter', sans-serif !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { background: #1E40AF !important; transform: translateY(-1px) !important; }
.stButton > button[kind="secondary"] {
    background: white !important; color: #0F172A !important;
    border: 1px solid #E2E8F0 !important;
}
.stButton > button[kind="secondary"]:hover { border-color: #3B82F6 !important; color: #1E40AF !important; }

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    border-radius: 10px !important;
    border: 1.5px solid #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}
</style>
"""

# ── LOGOS SVG ANIMADOS ───────────────────────────────────────────
# Logo grande: aparece en la pantalla de bienvenida y login
# Logo pequeño: aparece en la barra lateral cuando el usuario está logueado
LOGO_BIG = f"""
<div style="margin-bottom:2rem">
<a href="https://solucionapp.com.ar" target="_self" style="text-decoration:none;display:block">
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
  <text x="104" y="86" style="font-family:'Inter',sans-serif;font-weight:900;font-size:58px;letter-spacing:-2px;fill:#0F172A">{APP_NAME}</text>
  <text x="106" y="108" style="font-family:'Inter',sans-serif;font-weight:400;font-size:11px;fill:#64748B;letter-spacing:4px">{APP_TAGLINE}</text>
  <line x1="104" y1="118" x2="740" y2="118" stroke="#E2E8F0" stroke-width="1.5"/>
  <circle cx="104" cy="118" r="3" fill="#1E40AF"/>
  <circle cx="740" cy="118" r="3" fill="#10B981"/>
</svg>
</a></div>"""

LOGO_SMALL = f"""
<div style="margin-bottom:1.2rem">
<a href="https://solucionapp.com.ar" target="_self" style="text-decoration:none;display:block">
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
  <text x="70" y="54" style="font-family:'Inter',sans-serif;font-weight:900;font-size:40px;letter-spacing:-1px;fill:#ffffff">{APP_NAME}</text>
  <line x1="70" y1="66" x2="580" y2="66" stroke="#1E2A3A" stroke-width="1.5"/>
  <circle cx="70"  cy="66" r="2.5" fill="#1E40AF"/>
  <circle cx="580" cy="66" r="2.5" fill="#10B981"/>
</svg>
</a></div>"""
