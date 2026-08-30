from datetime import datetime
from urllib.parse import unquote

import pytest
import requests
import responses

from ngcolombia.gas_data_manager import ngDataManager

# Fecha de los registros reales en tests/mockups/registro_dia.json
FECHA_DIA = "2026-08-24"
FECHA_FIN = "2026-08-26"


def _pesados(registro: dict) -> float:
    """Suma de componentes pesados, igual que composicion_gri3."""
    return (
        registro["propano"]
        + registro["i_butano"]
        + registro["n_butano"]
        + registro["i_pentane"]
        + registro["n_pentano"]
        + registro["hexano"]
        + registro["neopentano"]
    )


def _livianos(registro: dict) -> float:
    return registro["n2"] + registro["co2"] + registro["metano"] + registro["etano"]


def test_constructor_sin_apikey_lanza():
    with pytest.raises(ValueError, match="API key es requerida"):
        ngDataManager(apikey=None)
    with pytest.raises(ValueError, match="API key es requerida"):
        ngDataManager(apikey="")


@responses.activate
def test_obtener_puntos_exito(manager, cargar_mockup):
    crudo = cargar_mockup("puntos.json")
    responses.get(manager.puntos_url, json=crudo)
    puntos = manager.obtener_puntos()
    assert puntos == [p["punto"] for p in crudo]
    assert "BALLENA" in puntos
    assert len(puntos) > 400


@responses.activate
def test_obtener_puntos_usa_cache_en_segunda_llamada(manager, cargar_mockup):
    responses.get(manager.puntos_url, json=cargar_mockup("puntos.json"))
    primero = manager.obtener_puntos()
    segundo = manager.obtener_puntos()
    assert primero == segundo
    assert len(responses.calls) == 1


@responses.activate
def test_obtener_puntos_401_lanza(manager):
    responses.get(manager.puntos_url, status=401, json=[])
    with pytest.raises(ValueError, match="API key es inválida"):
        manager.obtener_puntos()


@responses.activate
def test_obtener_puntos_error_conexion_lanza(manager):
    responses.get(manager.puntos_url, body=requests.exceptions.ConnectionError())
    with pytest.raises(ValueError, match="No se pudo conectar"):
        manager.obtener_puntos()


@responses.activate
def test_obtener_puntos_timeout_lanza(manager):
    responses.get(manager.puntos_url, body=requests.exceptions.Timeout())
    with pytest.raises(ValueError, match="tardó demasiado"):
        manager.obtener_puntos()


@responses.activate
def test_obtener_puntos_json_invalido_lanza(manager):
    responses.get(
        manager.puntos_url,
        body="<html>error</html>",
        content_type="text/html",
    )
    with pytest.raises(ValueError, match="formato válido"):
        manager.obtener_puntos()


@responses.activate
def test_obtener_puntos_error_http_lanza(manager):
    responses.get(manager.puntos_url, body=requests.exceptions.RequestException("boom"))
    with pytest.raises(ValueError, match="Error al obtener la lista de puntos"):
        manager.obtener_puntos()


@responses.activate
def test_obtener_puntos_lista_vacia_no_se_cachea(manager):
    responses.get(manager.puntos_url, json=[])
    responses.get(manager.puntos_url, json=[])
    assert manager.obtener_puntos() == []
    assert manager.obtener_puntos() == []
    assert len(responses.calls) == 2


@responses.activate
def test_fecha_punto_exito(manager_con_puntos, cargar_mockup):
    registro = cargar_mockup("registro_dia.json")
    responses.get(manager_con_puntos.data_url, json=[registro])
    assert manager_con_puntos.fecha_punto(FECHA_DIA, "BALLENA") == registro


@responses.activate
def test_fecha_punto_envia_punto_en_mayusculas(manager_con_puntos, cargar_mockup):
    registro = cargar_mockup("registro_dia.json")
    responses.get(manager_con_puntos.data_url, json=[registro])
    manager_con_puntos.fecha_punto(FECHA_DIA, "ballena")
    url = unquote(responses.calls[0].request.url)
    assert "punto=eq.BALLENA" in url


@responses.activate
def test_fecha_punto_invalido_devuelve_none(manager_con_puntos, capsys):
    assert manager_con_puntos.fecha_punto(FECHA_DIA, "NOEXISTE") is None
    assert len(responses.calls) == 0
    assert "no es válido" in capsys.readouterr().out


def test_fecha_punto_fecha_invalida_lanza(manager_con_puntos):
    with pytest.raises(ValueError, match="no es válida"):
        manager_con_puntos.fecha_punto("2024-13-01", "BALLENA")


def test_fecha_punto_fecha_anterior_a_minima_lanza(manager_con_puntos):
    with pytest.raises(ValueError, match="anterior a 2019-07-01"):
        manager_con_puntos.fecha_punto("2019-06-30", "BALLENA")


@responses.activate
def test_fecha_punto_sin_datos_devuelve_none(manager_con_puntos, capsys):
    responses.get(manager_con_puntos.data_url, json=[])
    assert manager_con_puntos.fecha_punto(FECHA_DIA, "BALLENA") is None
    assert "No hay datos disponibles" in capsys.readouterr().out


@responses.activate
def test_fecha_punto_error_conexion_devuelve_none(manager_con_puntos, capsys):
    responses.get(
        manager_con_puntos.data_url,
        body=requests.exceptions.ConnectionError(),
    )
    assert manager_con_puntos.fecha_punto(FECHA_DIA, "BALLENA") is None
    assert "No se pudo conectar" in capsys.readouterr().out


@responses.activate
def test_fecha_punto_timeout_devuelve_none(manager_con_puntos, capsys):
    responses.get(manager_con_puntos.data_url, body=requests.exceptions.Timeout())
    assert manager_con_puntos.fecha_punto(FECHA_DIA, "BALLENA") is None
    assert "tardó demasiado" in capsys.readouterr().out


@responses.activate
def test_fecha_punto_json_invalido_devuelve_none(manager_con_puntos, capsys):
    responses.get(
        manager_con_puntos.data_url,
        body="<html>error</html>",
        content_type="text/html",
    )
    assert manager_con_puntos.fecha_punto(FECHA_DIA, "BALLENA") is None
    assert "formato válido" in capsys.readouterr().out


@responses.activate
def test_fecha_punto_error_http_devuelve_none(manager_con_puntos, capsys):
    responses.get(manager_con_puntos.data_url, status=500, json=[])
    assert manager_con_puntos.fecha_punto(FECHA_DIA, "BALLENA") is None
    assert "Error al obtener datos" in capsys.readouterr().out


@responses.activate
def test_fecha_punto_usa_cache_en_segunda_llamada(manager_con_puntos, cargar_mockup):
    registro = cargar_mockup("registro_dia.json")
    responses.get(manager_con_puntos.data_url, json=[registro])
    primero = manager_con_puntos.fecha_punto(FECHA_DIA, "BALLENA")
    segundo = manager_con_puntos.fecha_punto(FECHA_DIA, "BALLENA")
    assert primero == segundo == registro
    assert len(responses.calls) == 1


@responses.activate
def test_fecha_punto_no_cachea_datos_de_hoy(manager_con_puntos, cargar_mockup):
    registro = dict(cargar_mockup("registro_dia.json"))
    registro["fecha"] = datetime.now().strftime("%Y-%m-%d")
    responses.get(manager_con_puntos.data_url, json=[registro])
    responses.get(manager_con_puntos.data_url, json=[registro])
    hoy = registro["fecha"]
    primero = manager_con_puntos.fecha_punto(hoy, "BALLENA")
    segundo = manager_con_puntos.fecha_punto(hoy, "BALLENA")
    assert primero == segundo == registro
    assert len(responses.calls) == 2


@responses.activate
def test_rango_exito(manager_con_puntos, cargar_mockup):
    registros = cargar_mockup("registros_rango.json")
    responses.get(manager_con_puntos.data_url, json=registros)
    resultado = manager_con_puntos.rango_fechas_punto(FECHA_DIA, FECHA_FIN, "BALLENA")
    assert resultado == registros
    assert len(resultado) == 3


@responses.activate
def test_rango_sirve_desde_cache(manager_con_puntos, cargar_mockup):
    registros = cargar_mockup("registros_rango.json")
    responses.get(manager_con_puntos.data_url, json=registros)
    primero = manager_con_puntos.rango_fechas_punto(FECHA_DIA, FECHA_FIN, "BALLENA")
    segundo = manager_con_puntos.rango_fechas_punto(FECHA_DIA, FECHA_FIN, "BALLENA")
    assert primero == segundo
    assert len(responses.calls) == 1


@responses.activate
def test_rango_incompleto_de_api_no_queda_cacheado(manager_con_puntos, cargar_mockup):
    """Comportamiento real capturado de la API: CUSIANA LLANOS no tiene datos
    para 2024-01-15, así que un rango de 3 días devuelve solo 2 registros.
    La caché exige el rango completo, por lo que la segunda llamada vuelve
    a consultar la API en lugar de servir el rango incompleto."""
    registros = cargar_mockup("registros_rango_incompleto.json")
    responses.get(manager_con_puntos.data_url, json=registros)
    responses.get(manager_con_puntos.data_url, json=registros)
    primero = manager_con_puntos.rango_fechas_punto(
        "2024-01-15", "2024-01-17", "CUSIANA LLANOS"
    )
    segundo = manager_con_puntos.rango_fechas_punto(
        "2024-01-15", "2024-01-17", "CUSIANA LLANOS"
    )
    assert primero == segundo == registros
    assert len(primero) == 2
    assert [r["fecha"] for r in primero] == ["2024-01-16", "2024-01-17"]
    assert len(responses.calls) == 2


def test_rango_invalido_lanza(manager_con_puntos):
    with pytest.raises(ValueError, match="posterior a la fecha de fin"):
        manager_con_puntos.rango_fechas_punto("2024-02-01", "2024-01-01", "BALLENA")


@responses.activate
def test_rango_punto_invalido_devuelve_none(manager_con_puntos):
    assert (
        manager_con_puntos.rango_fechas_punto(FECHA_DIA, FECHA_FIN, "NOEXISTE")
        is None
    )
    assert len(responses.calls) == 0


@responses.activate
def test_rango_error_conexion_devuelve_none(manager_con_puntos, capsys):
    responses.get(
        manager_con_puntos.data_url,
        body=requests.exceptions.ConnectionError(),
    )
    assert (
        manager_con_puntos.rango_fechas_punto(FECHA_DIA, FECHA_FIN, "BALLENA") is None
    )
    assert "No se pudo conectar" in capsys.readouterr().out


@responses.activate
def test_rango_timeout_devuelve_none(manager_con_puntos, capsys):
    responses.get(manager_con_puntos.data_url, body=requests.exceptions.Timeout())
    assert (
        manager_con_puntos.rango_fechas_punto(FECHA_DIA, FECHA_FIN, "BALLENA") is None
    )
    assert "tardó demasiado" in capsys.readouterr().out


@responses.activate
def test_rango_json_invalido_devuelve_none(manager_con_puntos, capsys):
    responses.get(
        manager_con_puntos.data_url,
        body="<html>error</html>",
        content_type="text/html",
    )
    assert (
        manager_con_puntos.rango_fechas_punto(FECHA_DIA, FECHA_FIN, "BALLENA") is None
    )
    assert "formato válido" in capsys.readouterr().out


@responses.activate
def test_rango_error_http_devuelve_none(manager_con_puntos, capsys):
    responses.get(manager_con_puntos.data_url, status=500, json=[])
    assert (
        manager_con_puntos.rango_fechas_punto(FECHA_DIA, FECHA_FIN, "BALLENA") is None
    )
    assert "Error al obtener datos" in capsys.readouterr().out


@responses.activate
def test_rango_sin_datos_devuelve_lista_vacia(manager_con_puntos):
    responses.get(manager_con_puntos.data_url, json=[])
    resultado = manager_con_puntos.rango_fechas_punto(FECHA_DIA, FECHA_FIN, "BALLENA")
    assert resultado == []


@responses.activate
def test_composicion_gri3_registro_real(manager_con_puntos, cargar_mockup):
    registro = cargar_mockup("registro_dia.json")
    responses.get(manager_con_puntos.data_url, json=[registro])
    resultado = manager_con_puntos.composicion_gri3(FECHA_DIA, "BALLENA")
    assert resultado["N2"] == pytest.approx(registro["n2"])
    assert resultado["CO2"] == pytest.approx(registro["co2"])
    assert resultado["CH4"] == pytest.approx(registro["metano"])
    assert resultado["C2H6"] == pytest.approx(registro["etano"])
    assert resultado["C3H8"] == pytest.approx(_pesados(registro), abs=1e-4)
    assert sum(resultado.values()) == pytest.approx(100)


@responses.activate
def test_composicion_total_mayor_100(manager_con_puntos, cargar_mockup):
    registro = cargar_mockup("registro_total_mayor_100.json")
    responses.get(manager_con_puntos.data_url, json=[registro])
    resultado = manager_con_puntos.composicion_gri3(FECHA_DIA, "BALLENA")
    # El exceso se descuenta de C3H8 para que la suma cierre en 100.
    assert resultado["C3H8"] == pytest.approx(100 - _livianos(registro))
    assert resultado["C3H8"] < _pesados(registro)
    assert sum(resultado.values()) == pytest.approx(100)


@responses.activate
def test_composicion_total_menor_100(manager_con_puntos, cargar_mockup):
    registro = cargar_mockup("registro_total_menor_100.json")
    responses.get(manager_con_puntos.data_url, json=[registro])
    resultado = manager_con_puntos.composicion_gri3(FECHA_DIA, "BALLENA")
    # El faltante se agrega a C3H8 para que la suma cierre en 100.
    assert resultado["C3H8"] == pytest.approx(100 - _livianos(registro))
    assert resultado["C3H8"] > _pesados(registro)
    assert sum(resultado.values()) == pytest.approx(100)


@responses.activate
def test_composicion_sin_datos_lanza(manager_con_puntos):
    responses.get(manager_con_puntos.data_url, json=[])
    with pytest.raises(ValueError, match="No hay datos disponibles"):
        manager_con_puntos.composicion_gri3(FECHA_DIA, "BALLENA")


@responses.activate
def test_propiedades_iso_conversiones(manager_con_puntos, cargar_mockup):
    registro = cargar_mockup("registro_dia.json")
    responses.get(manager_con_puntos.data_url, json=[registro])
    resultado = manager_con_puntos.propiedades_iso(FECHA_DIA, "BALLENA")
    assert resultado["HHV_kWh_m3"] == pytest.approx(registro["hv"] * (1000 / 96.6211))
    assert resultado["SG"] == pytest.approx(registro["gravedad_especifica"])
    assert resultado["ρ_kg_m3"] == pytest.approx(registro["densidad"] * 16.018)
    assert resultado["indice_wobbe_kWh_m3"] == pytest.approx(
        registro["indice_wobbe"] * (1000 / 96.6211)
    )


@responses.activate
def test_propiedades_iso_campos_historicos_en_cero(manager_con_puntos, cargar_mockup):
    """Comportamiento real capturado de la API: los registros históricos de
    2024 traen densidad e indice_wobbe en 0.0, así que las propiedades
    convertidas también resultan en 0.0."""
    registro = cargar_mockup("registro_propiedades_cero.json")
    responses.get(manager_con_puntos.data_url, json=[registro])
    resultado = manager_con_puntos.propiedades_iso("2024-01-15", "BALLENA")
    assert resultado["HHV_kWh_m3"] == pytest.approx(registro["hv"] * (1000 / 96.6211))
    assert resultado["HHV_kWh_m3"] > 0
    assert resultado["ρ_kg_m3"] == 0.0
    assert resultado["indice_wobbe_kWh_m3"] == 0.0


@responses.activate
def test_propiedades_iso_sin_datos_lanza(manager_con_puntos):
    responses.get(manager_con_puntos.data_url, json=[])
    with pytest.raises(ValueError, match="No hay datos disponibles"):
        manager_con_puntos.propiedades_iso(FECHA_DIA, "BALLENA")
