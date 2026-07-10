# ═══════════════════════════════════════════════════════════════════
#  email_utils.py — Envío de emails HTML.
# ═══════════════════════════════════════════════════════════════════

import os, smtplib
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import APP_NAME, APP_TAGLINE

def _secret(k, fb=""):
    try:    return st.secrets[k]
    except: return os.environ.get(k, fb)

EMAIL_REMITENTE  = _secret("EMAIL_REMITENTE")
EMAIL_PASSWORD   = _secret("EMAIL_PASSWORD")
EMAIL_HABILITADO = bool(EMAIL_REMITENTE and EMAIL_PASSWORD)

def _html(nombre, cuerpo):
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#F1F5F9;font-family:'Helvetica Neue',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F1F5F9;padding:30px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0"
       style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);max-width:600px;width:100%;">
<tr><td style="background:linear-gradient(135deg,#1E2A3A 0%,#2D4A6E 100%);padding:32px 40px;text-align:center;">
  <div style="font-size:30px;font-weight:900;color:#fff;">🔧 {APP_NAME}</div>
  <div style="font-size:11px;color:#94A3B8;letter-spacing:4px;margin-top:6px;">{APP_TAGLINE}</div>
</td></tr>
<tr><td style="padding:36px 40px 0 40px;">
  <p style="font-size:18px;font-weight:700;color:#1E2A3A;margin:0 0 8px 0;">Hola, {nombre} 👋</p>
</td></tr>
<tr><td style="padding:16px 40px 36px 40px;font-size:15px;color:#374151;line-height:1.7;">{cuerpo}</td></tr>
<tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #E2E8F0;margin:0;"></td></tr>
<tr><td style="padding:24px 40px;text-align:center;">
  <p style="font-size:12px;color:#94A3B8;margin:0;">Este email fue enviado por <b>{APP_NAME}</b>.</p>
</td></tr>
</table></td></tr></table></body></html>"""

def enviar_email(dest, asunto, nombre, cuerpo_html):
    from auth import validar_email
    if not dest or not validar_email(dest): return
    if not EMAIL_HABILITADO:
        st.info(f"📧 [DEMO] → **{dest}** | {asunto}")
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["From"]    = f"{APP_NAME} <{EMAIL_REMITENTE}>"
        msg["To"]      = dest
        msg["Subject"] = asunto
        msg.attach(MIMEText(f"Hola {nombre},\n\n{cuerpo_html}", "plain", "utf-8"))
        msg.attach(MIMEText(_html(nombre, cuerpo_html), "html", "utf-8"))
        with smtplib.SMTP("smtp.office365.com", 587) as s:
            s.ehlo()
            s.starttls()
            s.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
            s.sendmail(EMAIL_REMITENTE, dest, msg.as_string())
    except Exception as e:
        st.warning(f"⚠️ No se pudo enviar email a {dest}: {e}")

# ── Templates ────────────────────────────────────────────────────
def email_bienvenida_cliente(nombre):
    return f"<p>Tu cuenta en <b>{APP_NAME}</b> fue creada con éxito.</p><p>Ya podés buscar especialistas, pedir presupuestos y agendar turnos.</p>"

def email_bienvenida_proveedor(razon):
    return f"<p>Tu empresa <b>{razon}</b> fue registrada en <b>{APP_NAME}</b>.</p><p>Ya podés recibir consultas, enviar presupuestos y proponer turnos.</p>"

def email_presupuesto_recibido(cliente, prov, monto, detalle, trabajo):
    return (f"<p>Recibiste un presupuesto de <b>{prov}</b>.</p>"
            f"<div style='background:#F0F7FF;border-left:4px solid #3B82F6;border-radius:0 8px 8px 0;padding:16px 20px;margin:20px 0;'>"
            f"<div style='font-size:28px;font-weight:900;color:#1E40AF;'>${monto:,.0f}</div>"
            f"<div style='font-size:13px;color:#475569;margin-top:8px;white-space:pre-wrap;'>{detalle}</div></div>"
            f"<p><b>Trabajo:</b> {trabajo}</p>"
            f"<p>Ingresá a <b>{APP_NAME} → Mis solicitudes</b> para aceptar o rechazar.</p>")

def email_presupuesto_aceptado(prov, trabajo):
    return f"<p>¡El usuario aceptó tu presupuesto!</p><p><b>Trabajo:</b> {trabajo}</p><p>Ingresá a <b>{APP_NAME}</b> para proponer opciones de turno.</p>"

def email_turnos_propuestos(prov, opciones):
    items = "".join(f"<li style='margin:6px 0;'>📅 <b>{f}</b> a las <b>{h}</b></li>" for f,h in opciones)
    return f"<p><b>{prov}</b> te propuso estas opciones de turno:</p><ul style='padding-left:20px;margin:16px 0;'>{items}</ul><p>Ingresá a <b>{APP_NAME} → Mis solicitudes</b> para elegir.</p>"

def email_turno_confirmado_cliente(prov, fecha, hora):
    return (f"<p>Tu turno con <b>{prov}</b> quedó confirmado.</p>"
            f"<div style='background:#ECFDF5;border-left:4px solid #10B981;border-radius:0 8px 8px 0;padding:16px 20px;margin:20px 0;'>"
            f"<div style='font-size:20px;font-weight:700;color:#065F46;'>📅 {fecha} a las {hora}</div></div>")

def email_turno_confirmado_prov(cliente, fecha, hora, trabajo):
    return (f"<p><b>{cliente}</b> confirmó el turno.</p>"
            f"<div style='background:#ECFDF5;border-left:4px solid #10B981;border-radius:0 8px 8px 0;padding:16px 20px;margin:20px 0;'>"
            f"<div style='font-size:20px;font-weight:700;color:#065F46;'>📅 {fecha} a las {hora}</div></div>"
            f"<p><b>Trabajo:</b> {trabajo}</p>")

def email_turnos_rechazados(prov):
    return f"<p>El usuario rechazó las opciones de turno.</p><p>Podés ingresar a <b>{APP_NAME}</b> para proponer nuevas fechas.</p>"

def email_trabajo_completado(prov, trabajo):
    return (f"<p><b>{prov}</b> marcó tu trabajo como completado.</p>"
            f"<p><b>Trabajo realizado:</b> {trabajo}</p>"
            f"<p>Por favor ingresá a <b>{APP_NAME} → Mis solicitudes</b> para calificar la atención del especialista. "
            f"Tu opinión ayuda a otros usuarios a elegir mejor.</p>"
            f"<p style='text-align:center;margin:28px 0;'>"
            f"<span style='background:#F59E0B;color:white;padding:12px 28px;border-radius:8px;font-weight:700;font-size:1rem;'>⭐ Calificar ahora</span>"
            f"</p>")

def email_reset_password(nombre, token, modo):
    url = f"?reset_token={token}&reset_modo={modo}"
    return (f"<p>Recibimos una solicitud para restablecer tu contraseña.</p>"
            f"<p style='text-align:center;margin:32px 0;'>"
            f"<a href='{url}' style='background:#1E40AF;color:white;padding:14px 32px;border-radius:8px;"
            f"text-decoration:none;font-weight:700;font-size:15px;display:inline-block;'>🔑 Restablecer contraseña</a></p>"
            f"<p style='font-size:12px;color:#94A3B8;'>Válido por 30 minutos. Si no solicitaste esto, ignorá este email.</p>")
