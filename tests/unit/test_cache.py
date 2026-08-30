import sqlite3
from datetime import datetime, timedelta

from ngcolombia._cache import CacheLocal

# Fechas de los registros reales en tests/mockups/registros_rango.json
FECHA_DIA = "2026-08-24"
FECHA_FIN = "2026-08-26"


def test_leer_puntos_cache_vacia_devuelve_none(tmp_path):
    cache = CacheLocal(str(tmp_path / "cache.db"))
    assert cache.leer_puntos() is None


def test_guardar_y_leer_puntos(tmp_path):
    cache = CacheLocal(str(tmp_path / "cache.db"))
    cache.guardar_puntos(["A", "B"])
    assert cache.leer_puntos() == ["A", "B"]


def test_guardar_puntos_reemplaza_lista_anterior(tmp_path):
    cache = CacheLocal(str(tmp_path / "cache.db"))
    cache.guardar_puntos(["A"])
    cache.guardar_puntos(["B", "C"])
    assert cache.leer_puntos() == ["B", "C"]


def test_guardar_puntos_vacios_leer_devuelve_none(tmp_path):
    cache = CacheLocal(str(tmp_path / "cache.db"))
    cache.guardar_puntos([])
    assert cache.leer_puntos() is None


def test_puntos_expiran_a_las_24_horas(tmp_path):
    ruta = tmp_path / "cache.db"
    cache = CacheLocal(str(ruta))
    cache.guardar_puntos(["BALLENA"])

    vieja = (datetime.now() - timedelta(hours=25)).isoformat()
    con = sqlite3.connect(str(ruta))
    con.execute(
        "UPDATE meta SET valor = ? WHERE clave = 'puntos_actualizado'",
        (vieja,),
    )
    con.commit()
    con.close()

    assert cache.leer_puntos() is None


def test_leer_dato_inexistente_devuelve_none(tmp_path):
    cache = CacheLocal(str(tmp_path / "cache.db"))
    assert cache.leer_dato(FECHA_DIA, "BALLENA") is None


def test_guardar_y_leer_dato(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "cache.db"))
    registro = cargar_mockup("registro_dia.json")
    cache.guardar_datos([registro], "ballena")
    assert cache.leer_dato(FECHA_DIA, "BALLENA") == registro
    assert cache.leer_dato(FECHA_DIA, "ballena") == registro


def test_guardar_datos_omite_fecha_de_hoy(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "cache.db"))
    registro = dict(cargar_mockup("registro_dia.json"))
    hoy = datetime.now().strftime("%Y-%m-%d")
    registro["fecha"] = hoy
    cache.guardar_datos([registro], "BALLENA")
    assert cache.leer_dato(hoy, "BALLENA") is None


def test_guardar_datos_omite_registro_sin_fecha(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "cache.db"))
    registro = dict(cargar_mockup("registro_dia.json"))
    del registro["fecha"]
    cache.guardar_datos([registro], "BALLENA")
    assert cache.leer_dato(FECHA_DIA, "BALLENA") is None


def test_leer_rango_completo(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "cache.db"))
    registros = cargar_mockup("registros_rango.json")
    cache.guardar_datos(registros, "BALLENA")
    leidos = cache.leer_rango(FECHA_DIA, FECHA_FIN, "BALLENA")
    assert leidos == registros
    assert [r["fecha"] for r in leidos] == ["2026-08-24", "2026-08-25", "2026-08-26"]


def test_leer_rango_incompleto_devuelve_none(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "cache.db"))
    registros = cargar_mockup("registros_rango.json")
    incompletos = [registros[0], registros[2]]
    cache.guardar_datos(incompletos, "BALLENA")
    assert cache.leer_rango(FECHA_DIA, FECHA_FIN, "BALLENA") is None
