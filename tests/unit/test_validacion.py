import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from ngcolombia._validacion import (
    FECHA_MINIMA,
    validar_fecha,
    validar_punto,
    validar_rango_fechas,
)

MOCKUPS_DIR = Path(__file__).parent.parent / "mockups"

# Lista real de puntos capturada de la API.
PUNTOS_REALES = [
    p["punto"]
    for p in json.loads((MOCKUPS_DIR / "puntos.json").read_text(encoding="utf-8"))
]


def test_validar_fecha_valida_devuelve_datetime():
    assert validar_fecha("2024-01-15") == datetime(2024, 1, 15)


def test_validar_fecha_hoy_es_valida():
    hoy = datetime.now().strftime("%Y-%m-%d")
    resultado = validar_fecha(hoy)
    assert resultado.strftime("%Y-%m-%d") == hoy


def test_validar_fecha_minima_es_valida():
    assert validar_fecha(FECHA_MINIMA) == datetime(2019, 7, 1)


@pytest.mark.parametrize(
    "fecha",
    [
        "2024/01/15",
        "15-01-2024",
        "2024-13-45",
        "",
        "no-es-fecha",
        None,
        20240115,
    ],
)
def test_validar_fecha_formato_invalido(fecha):
    with pytest.raises(ValueError, match="no es válida"):
        validar_fecha(fecha)


def test_validar_fecha_futura_lanza():
    futura = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    with pytest.raises(ValueError, match="posterior a la fecha actual"):
        validar_fecha(futura)


def test_validar_fecha_anterior_a_minima_lanza():
    with pytest.raises(ValueError, match="anterior a 2019-07-01"):
        validar_fecha("2019-06-30")


def test_validar_rango_valido():
    inicio, fin = validar_rango_fechas("2024-01-01", "2024-01-31")
    assert inicio == datetime(2024, 1, 1)
    assert fin == datetime(2024, 1, 31)


def test_validar_rango_mismo_dia():
    inicio, fin = validar_rango_fechas("2024-01-15", "2024-01-15")
    assert inicio == fin == datetime(2024, 1, 15)


def test_validar_rango_inicio_posterior_a_fin_lanza():
    with pytest.raises(ValueError, match="posterior a la fecha de fin"):
        validar_rango_fechas("2024-02-01", "2024-01-01")


def test_validar_rango_inicio_anterior_a_minima_lanza():
    with pytest.raises(ValueError, match="anterior a 2019-07-01"):
        validar_rango_fechas("2019-06-30", "2024-01-01")


def test_validar_punto_exacto():
    assert validar_punto("BALLENA", PUNTOS_REALES) is True


def test_validar_punto_insensible_a_mayusculas():
    assert validar_punto("ballena", PUNTOS_REALES) is True


def test_validar_punto_subcadena_sugiere(capsys):
    # "BELLEZA" no existe pero es subcadena de puntos reales.
    assert validar_punto("BELLEZA", PUNTOS_REALES) is False
    salida = capsys.readouterr().out
    assert "LA BELLEZA" in salida
    assert "CG LA BELLEZA" in salida


def test_validar_punto_tipeo_sugiere(capsys):
    # Error de tipeo sin coincidencia por subcadena: sugiere por similitud.
    assert validar_punto("BALLENAS", PUNTOS_REALES) is False
    assert "BALLENA" in capsys.readouterr().out


def test_validar_punto_sin_sugerencias(capsys):
    assert validar_punto("XYZ123", PUNTOS_REALES) is False
    assert "no se encontraron sugerencias" in capsys.readouterr().out
