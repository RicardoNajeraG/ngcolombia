from datetime import datetime, timedelta, timezone

from ngcolombia._tiempo import hoy_bogota


def test_hoy_bogota_formato_yyyy_mm_dd():
    hoy = hoy_bogota()
    datetime.strptime(hoy, "%Y-%m-%d")


def test_hoy_bogota_coincide_con_utc_menos_5():
    esperado = datetime.now(timezone(timedelta(hours=-5))).strftime("%Y-%m-%d")
    assert hoy_bogota() == esperado
