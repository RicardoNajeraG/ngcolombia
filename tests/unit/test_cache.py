import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

from ngcolombia._cache import AUSENTE, CacheLocal, _ruta_por_defecto
from ngcolombia._tiempo import hoy_bogota

# Fechas de los registros reales en tests/mockups/registros_rango.json
FECHA_DIA = "2026-08-24"
FECHA_MEDIO = "2026-08-25"
FECHA_FIN = "2026-08-26"


def _ayer_bogota() -> str:
    return (datetime.strptime(hoy_bogota(), "%Y-%m-%d") - timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )


def test_leer_puntos_cache_vacia_devuelve_none(tmp_path):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    assert cache.leer_puntos() is None


def test_guardar_y_leer_puntos(tmp_path):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    cache.guardar_puntos(["A", "B"])
    assert cache.leer_puntos() == ["A", "B"]


def test_guardar_puntos_reemplaza_lista_anterior(tmp_path):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    cache.guardar_puntos(["A"])
    cache.guardar_puntos(["B", "C"])
    assert cache.leer_puntos() == ["B", "C"]


def test_guardar_puntos_vacios_leer_devuelve_none(tmp_path):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    cache.guardar_puntos([])
    assert cache.leer_puntos() is None


def test_puntos_expiran_a_las_24_horas(tmp_path):
    ruta = tmp_path / "ngcolombia_cache.db"
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
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    assert cache.leer_dato(FECHA_DIA, "BALLENA") is None


def test_guardar_y_leer_dato(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    registro = cargar_mockup("registro_dia.json")
    cache.guardar_datos([registro], "ballena")
    assert cache.leer_dato(FECHA_DIA, "BALLENA") == registro
    assert cache.leer_dato(FECHA_DIA, "ballena") == registro


def test_guardar_datos_omite_fecha_de_hoy(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    registro = dict(cargar_mockup("registro_dia.json"))
    hoy = hoy_bogota()
    registro["fecha"] = hoy
    cache.guardar_datos([registro], "BALLENA")
    assert cache.leer_dato(hoy, "BALLENA") is None


def test_guardar_datos_omite_registro_sin_fecha(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    registro = dict(cargar_mockup("registro_dia.json"))
    del registro["fecha"]
    cache.guardar_datos([registro], "BALLENA")
    assert cache.leer_dato(FECHA_DIA, "BALLENA") is None


def test_leer_rango_completo(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    registros = cargar_mockup("registros_rango.json")
    cache.guardar_datos(registros, "BALLENA")
    cacheados, faltantes = cache.leer_rango(FECHA_DIA, FECHA_FIN, "BALLENA")
    assert cacheados == registros
    assert faltantes == []
    assert [r["fecha"] for r in cacheados] == ["2026-08-24", "2026-08-25", "2026-08-26"]


def test_leer_rango_hueco_sin_registrar_es_faltante(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    registros = cargar_mockup("registros_rango.json")
    incompletos = [registros[0], registros[2]]
    cache.guardar_datos(incompletos, "BALLENA")
    cacheados, faltantes = cache.leer_rango(FECHA_DIA, FECHA_FIN, "BALLENA")
    assert cacheados == incompletos
    assert faltantes == [FECHA_MEDIO]


def test_leer_rango_hueco_con_ausencia_no_es_faltante(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    registros = cargar_mockup("registros_rango.json")
    incompletos = [registros[0], registros[2]]
    cache.guardar_datos(incompletos, "BALLENA")
    cache.guardar_ausencias([FECHA_MEDIO], "BALLENA")
    cacheados, faltantes = cache.leer_rango(FECHA_DIA, FECHA_FIN, "BALLENA")
    assert cacheados == incompletos
    assert faltantes == []


def test_leer_rango_incluye_hoy_siempre_faltante(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    registro = dict(cargar_mockup("registro_dia.json"))
    ayer = _ayer_bogota()
    hoy = hoy_bogota()
    registro["fecha"] = ayer
    cache.guardar_datos([registro], "BALLENA")
    cacheados, faltantes = cache.leer_rango(ayer, hoy, "BALLENA")
    assert [r["fecha"] for r in cacheados] == [ayer]
    assert hoy in faltantes


def test_guardar_ausencias_leer_dato_devuelve_ausente(tmp_path):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    cache.guardar_ausencias([FECHA_DIA], "BALLENA")
    assert cache.leer_dato(FECHA_DIA, "BALLENA") is AUSENTE
    assert cache.leer_dato(FECHA_DIA, "ballena") is AUSENTE


def test_guardar_ausencias_omite_hoy(tmp_path):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    hoy = hoy_bogota()
    cache.guardar_ausencias([hoy], "BALLENA")
    assert cache.leer_dato(hoy, "BALLENA") is None


def test_guardar_datos_limpia_ausencia(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    registro = cargar_mockup("registro_dia.json")
    cache.guardar_ausencias([FECHA_DIA], "BALLENA")
    assert cache.leer_dato(FECHA_DIA, "BALLENA") is AUSENTE
    cache.guardar_datos([registro], "BALLENA")
    assert cache.leer_dato(FECHA_DIA, "BALLENA") == registro


def test_crea_directorios_anidados(tmp_path):
    ruta = tmp_path / "a" / "b" / "ngcolombia_cache.db"
    cache = CacheLocal(str(ruta))
    cache.guardar_puntos(["A"])
    assert ruta.exists()
    assert cache.leer_puntos() == ["A"]


def test_close_cierra_y_reabre(tmp_path):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    cache.guardar_puntos(["A"])
    cache.close()
    assert cache._conexion is None
    assert cache.leer_puntos() == ["A"]
    cache.close()


def test_close_sin_abrir_es_seguro(tmp_path):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    cache.close()
    assert cache._conexion is None


def test_vaciar_borra_todo(tmp_path, cargar_mockup):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    registro = cargar_mockup("registro_dia.json")
    cache.guardar_puntos(["BALLENA"])
    cache.guardar_datos([registro], "BALLENA")
    cache.guardar_ausencias([FECHA_MEDIO], "BALLENA")
    cache.vaciar()
    assert cache.leer_puntos() is None
    assert cache.leer_dato(FECHA_DIA, "BALLENA") is None
    assert cache.leer_dato(FECHA_MEDIO, "BALLENA") is None


def test_wal_activo(tmp_path):
    cache = CacheLocal(str(tmp_path / "ngcolombia_cache.db"))
    modo = cache._db().execute("PRAGMA journal_mode").fetchone()[0]
    assert modo.lower() == "wal"


def test_ruta_env_var(monkeypatch, tmp_path):
    destino = str(tmp_path / "custom.db")
    monkeypatch.setenv("NGCOLOMBIA_CACHE", destino)
    assert _ruta_por_defecto() == destino


def test_ruta_windows(monkeypatch, tmp_path):
    monkeypatch.delenv("NGCOLOMBIA_CACHE", raising=False)
    monkeypatch.setattr(sys, "platform", "win32")
    local = str(tmp_path / "Local")
    monkeypatch.setenv("LOCALAPPDATA", local)
    assert _ruta_por_defecto() == str(Path(local) / "ngcolombia" / "ngcolombia_cache.db")


def test_ruta_windows_sin_localappdata(monkeypatch, tmp_path):
    monkeypatch.delenv("NGCOLOMBIA_CACHE", raising=False)
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    assert _ruta_por_defecto() == str(
        tmp_path / "AppData" / "Local" / "ngcolombia" / "ngcolombia_cache.db"
    )


def test_ruta_macos(monkeypatch, tmp_path):
    monkeypatch.delenv("NGCOLOMBIA_CACHE", raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    assert _ruta_por_defecto() == str(
        tmp_path / "Library" / "Application Support" / "ngcolombia" / "ngcolombia_cache.db"
    )


def test_ruta_linux_xdg(monkeypatch, tmp_path):
    monkeypatch.delenv("NGCOLOMBIA_CACHE", raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    xdg = str(tmp_path / "xdg")
    monkeypatch.setenv("XDG_DATA_HOME", xdg)
    assert _ruta_por_defecto() == str(Path(xdg) / "ngcolombia" / "ngcolombia_cache.db")


def test_ruta_linux_sin_xdg(monkeypatch, tmp_path):
    monkeypatch.delenv("NGCOLOMBIA_CACHE", raising=False)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    assert _ruta_por_defecto() == str(
        tmp_path / ".local" / "share" / "ngcolombia" / "ngcolombia_cache.db"
    )
