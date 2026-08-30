"""
Fecha actual en America/Bogotá (UTC-5, sin horario de verano).
Módulo interno: no forma parte de la API pública del paquete.
"""

from datetime import datetime, timedelta, timezone

_TZ_BOGOTA = timezone(timedelta(hours=-5))


def hoy_bogota() -> str:
    """Devuelve la fecha actual en America/Bogotá como YYYY-MM-DD."""
    return datetime.now(_TZ_BOGOTA).strftime("%Y-%m-%d")
