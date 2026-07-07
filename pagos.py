# ═══════════════════════════════════════════════════════════════════
#  pagos.py — Canon por servicio.
#  El canon se registra internamente pero NO se muestra al usuario
#  como un cobro explícito. Se cobra como "Costo de servicio"
#  dentro del presupuesto que envía el profesional.
# ═══════════════════════════════════════════════════════════════════

from database import get_connection
from config import CANON_PROFESIONAL

def registrar_canon(solicitud_id: int, tipo: str) -> None:
    """Registra el canon internamente sin mostrar pantalla de pago."""
    monto = CANON_PROFESIONAL
    conn  = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO canon_cobros (solicitud_id,tipo,monto,estado) VALUES (?,?,?,'registrado')",
        (solicitud_id, tipo, monto)
    )
    conn.commit()

def ya_pago(solicitud_id: int, tipo: str) -> bool:
    conn = get_connection()
    return bool(conn.execute(
        "SELECT id FROM canon_cobros WHERE solicitud_id=? AND tipo=?",
        (solicitud_id, tipo)
    ).fetchone())
