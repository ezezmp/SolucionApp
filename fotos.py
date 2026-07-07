# ═══════════════════════════════════════════════════════════════════
#  fotos.py — Manejo de subida y visualización de fotos.
#  Las fotos se guardan en la carpeta local UPLOADS_DIR.
#  Cuando tengas hosting, esa carpeta vive en el servidor.
# ═══════════════════════════════════════════════════════════════════

import os
import uuid
import streamlit as st
from config import UPLOADS_DIR


def _asegurar_dir():
    """Crea la carpeta de uploads si no existe."""
    os.makedirs(UPLOADS_DIR, exist_ok=True)


def guardar_foto(archivo_subido) -> str | None:
    """
    Guarda el archivo subido en disco y retorna el path relativo.
    Retorna None si no hay archivo.
    """
    if archivo_subido is None:
        return None
    _asegurar_dir()
    ext      = os.path.splitext(archivo_subido.name)[1].lower()
    nombre   = f"{uuid.uuid4().hex}{ext}"
    ruta     = os.path.join(UPLOADS_DIR, nombre)
    with open(ruta, "wb") as f:
        f.write(archivo_subido.getbuffer())
    return ruta


def mostrar_foto(ruta: str | None, caption: str = "", ancho: int = 300) -> None:
    """Muestra una foto si la ruta existe."""
    if ruta and os.path.exists(ruta):
        st.image(ruta, caption=caption, width=ancho)
    elif ruta:
        st.caption(f"📷 Foto no encontrada: {ruta}")


def widget_subir_foto(
    label: str,
    key: str,
    obligatoria: bool = False,
    ayuda: str = "",
) -> object:
    """
    Widget estandarizado para subir una foto.
    Retorna el archivo subido o None.
    Muestra un asterisco rojo si es obligatoria.
    """
    label_full = f"{label} {'*(obligatoria)*' if obligatoria else '*(opcional)*'}"
    archivo = st.file_uploader(
        label_full,
        type=["jpg", "jpeg", "png", "webp"],
        key=key,
        help=ayuda or ("Formatos aceptados: JPG, PNG, WEBP" ),
    )
    if archivo:
        st.image(archivo, caption="Vista previa", width=250)
    return archivo
