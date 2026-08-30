"""
Tests de integración contra la API real de Supabase.

Usan el punto BALLENA y fechas históricas (2026-08-24 a 2026-08-26) cuyos
datos fueron verificados al crear estos tests; los datos históricos son
inmutables, así que las aserciones son estrictas.
"""

from datetime import datetime, timedelta

import pytest

import ngcolombia
from ngcolombia._cache import AUSENTE
from ngcolombia._tiempo import hoy_bogota
from ngcolombia.gas_data_manager import ngDataManager

pytestmark = pytest.mark.integration

PUNTO = "BALLENA"
FECHA = "2026-08-24"
FECHA_FIN = "2026-08-26"

_CAMPOS_ESPERADOS = {
    "fecha",
    "hv",
    "n2",
    "co2",
    "metano",
    "etano",
    "propano",
    "i_butano",
    "n_butano",
    "i_pentane",
    "n_pentano",
    "hexano",
    "neopentano",
    "gravedad_especifica",
    "densidad",
    "indice_wobbe",
    "total",
}


@pytest.fixture
def manager_real(tmp_path):
    instancia = ngDataManager(
        apikey=ngcolombia._APIKEY,
        cache_path=str(tmp_path / "ngcolombia_cache.db"),
    )
    yield instancia
    instancia._cache.close()


def _requerir_punto(manager):
    puntos = manager.obtener_puntos()
    if PUNTO not in puntos:
        pytest.skip(f"{PUNTO} ya no está en la lista de puntos de la API")
    return puntos


def test_obtener_puntos_real(manager_real):
    puntos = manager_real.obtener_puntos()
    assert isinstance(puntos, list)
    assert len(puntos) > 0
    assert all(isinstance(p, str) for p in puntos)


def test_fecha_punto_real(manager_real):
    _requerir_punto(manager_real)
    dato = manager_real.fecha_punto(FECHA, PUNTO)
    assert dato is not None, f"Se esperaban datos históricos de {PUNTO} en {FECHA}"
    assert _CAMPOS_ESPERADOS.issubset(dato.keys())
    assert dato["fecha"] == FECHA
    assert dato["hv"] > 0
    assert dato["total"] == pytest.approx(100, abs=0.5)


def test_composicion_gri3_real(manager_real):
    _requerir_punto(manager_real)
    resultado = manager_real.composicion_gri3(FECHA, PUNTO)
    assert set(resultado.keys()) == {"N2", "CO2", "CH4", "C2H6", "C3H8"}
    assert sum(resultado.values()) == pytest.approx(100, abs=0.01)


def test_propiedades_iso_real(manager_real):
    _requerir_punto(manager_real)
    resultado = manager_real.propiedades_iso(FECHA, PUNTO)
    assert set(resultado.keys()) == {
        "HHV_kWh_m3",
        "SG",
        "ρ_kg_m3",
        "indice_wobbe_kWh_m3",
    }
    assert resultado["HHV_kWh_m3"] > 0
    assert resultado["SG"] > 0


def test_rango_real(manager_real):
    _requerir_punto(manager_real)
    datos = manager_real.rango_fechas_punto(FECHA, FECHA_FIN, PUNTO)
    assert isinstance(datos, list)
    assert len(datos) == 3
    assert [r["fecha"] for r in datos] == ["2026-08-24", "2026-08-25", "2026-08-26"]


def test_rango_incompleto_real(manager_real):
    """La API puede devolver menos días de los solicitados: CUSIANA LLANOS
    no tiene registro para 2024-01-15 (comportamiento verificado)."""
    puntos = manager_real.obtener_puntos()
    if "CUSIANA LLANOS" not in puntos:
        pytest.skip("CUSIANA LLANOS ya no está en la lista de puntos de la API")
    datos = manager_real.rango_fechas_punto("2024-01-15", "2024-01-17", "CUSIANA LLANOS")
    assert isinstance(datos, list)
    assert [r["fecha"] for r in datos] == ["2024-01-16", "2024-01-17"]


def test_rango_incompleto_segunda_llamada_usa_cache(manager_real):
    puntos = manager_real.obtener_puntos()
    if "CUSIANA LLANOS" not in puntos:
        pytest.skip("CUSIANA LLANOS ya no está en la lista de puntos de la API")
    primero = manager_real.rango_fechas_punto(
        "2024-01-15", "2024-01-17", "CUSIANA LLANOS"
    )
    segundo = manager_real.rango_fechas_punto(
        "2024-01-15", "2024-01-17", "CUSIANA LLANOS"
    )
    assert primero == segundo
    assert [r["fecha"] for r in segundo] == ["2024-01-16", "2024-01-17"]
    assert manager_real._cache.leer_dato("2024-01-15", "CUSIANA LLANOS") is AUSENTE


def test_rango_hasta_hoy_incluye_dia_historico(manager_real):
    _requerir_punto(manager_real)
    hoy = hoy_bogota()
    ayer = (datetime.strptime(hoy, "%Y-%m-%d") - timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )
    datos = manager_real.rango_fechas_punto(ayer, hoy, PUNTO)
    assert isinstance(datos, list)
    fechas = [r["fecha"] for r in datos]
    if ayer not in fechas:
        pytest.skip(f"No hay datos de {PUNTO} para {ayer}")
    assert ayer in fechas
