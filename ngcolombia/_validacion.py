"""
Funciones de validación de fechas y puntos de medida.
Módulo interno: no forma parte de la API pública del paquete.
"""

from datetime import datetime
from difflib import get_close_matches

FECHA_MINIMA = "2019-07-01"


def validar_fecha(fecha: str) -> datetime:
    """
    Valida que la fecha tenga formato YYYY-MM-DD y no sea posterior a hoy.
    Devuelve el datetime correspondiente o lanza ValueError.
    """
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError(f"La fecha ingresada no es válida. Formato esperado: YYYY-MM-DD. Fecha ingresada: {fecha}")
    if fecha_dt > datetime.now():
        raise ValueError(f"La fecha ingresada no puede ser posterior a la fecha actual. Fecha actual: {datetime.now().strftime('%Y-%m-%d')}")
    return fecha_dt


def validar_rango_fechas(fecha_inicio: str, fecha_fin: str) -> tuple:
    """
    Valida un rango de fechas: formato, límite inferior (2019-07-01),
    límite superior (hoy) y que inicio no sea posterior a fin.
    """
    inicio_dt = validar_fecha(fecha_inicio)
    fin_dt = validar_fecha(fecha_fin)
    minimo_dt = datetime.strptime(FECHA_MINIMA, "%Y-%m-%d")
    if inicio_dt < minimo_dt:
        raise ValueError(f"La fecha de inicio no puede ser anterior a {FECHA_MINIMA}. Fecha ingresada: {fecha_inicio}")
    if inicio_dt > fin_dt:
        raise ValueError(f"La fecha de inicio no puede ser posterior a la fecha de fin. Recibido: fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}")
    return inicio_dt, fin_dt


def validar_punto(punto: str, lista_puntos: list) -> bool:
    """
    Valida si el punto existe en la lista de puntos disponibles.
    Si no existe, imprime sugerencias y devuelve False.
    """
    if punto.upper() in lista_puntos:
        return True
    posibles = [p for p in lista_puntos if punto.upper() in p]
    if posibles:
        print(f"El punto '{punto}' no es válido. ¿Quizás quisiste decir?: {', '.join(posibles)}")
        return False
    sugerencias = get_close_matches(punto.upper(), lista_puntos, n=5, cutoff=0.6)
    if sugerencias:
        print(f"El punto '{punto}' no es válido. ¿Quizás quisiste decir?: {', '.join(sugerencias)}")
    else:
        print(f"El punto '{punto}' no es válido y no se encontraron sugerencias similares.")
    return False
