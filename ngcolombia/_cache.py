"""
Caché local persistente (SQLite) para las consultas a la API.
Módulo interno: no forma parte de la API pública del paquete.

Tablas:
- puntos: lista de puntos de medida disponibles (expira a las 24 horas).
- datos: mediciones por (fecha, punto). Los datos históricos son inmutables,
  por lo que no expiran. Los datos de la fecha actual no se cachean.
- ausencias: días históricos en los que la API no devolvió datos.
- meta: pares clave-valor internos (marca de tiempo de la tabla puntos).
"""

import json
import os
import sqlite3
import sys
import threading
from datetime import datetime, timedelta
from pathlib import Path

from ._tiempo import hoy_bogota

_TTL_PUNTOS = timedelta(hours=24)

AUSENTE = object()


def _ruta_por_defecto() -> str:
    """Ruta del archivo de caché según el sistema operativo y NGCOLOMBIA_CACHE."""
    env = os.environ.get("NGCOLOMBIA_CACHE")
    if env:
        return env
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            return str(Path(base) / "ngcolombia" / "ngcolombia_cache.db")
        return str(Path.home() / "AppData" / "Local" / "ngcolombia" / "ngcolombia_cache.db")
    if sys.platform == "darwin":
        return str(Path.home() / "Library" / "Application Support" / "ngcolombia" / "ngcolombia_cache.db")
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return str(Path(xdg) / "ngcolombia" / "ngcolombia_cache.db")
    return str(Path.home() / ".local" / "share" / "ngcolombia" / "ngcolombia_cache.db")


def _fechas_en_rango(fecha_inicio: str, fecha_fin: str) -> list:
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    dias = (fin - inicio).days + 1
    return [(inicio + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(dias)]


class CacheLocal:
    def __init__(self, ruta: str = None):
        self._ruta = str(ruta) if ruta else _ruta_por_defecto()
        self._conexion = None
        self._lock = threading.Lock()

    def _db(self) -> sqlite3.Connection:
        """Abre la conexión y crea las tablas la primera vez que se necesita."""
        if self._conexion is None:
            Path(self._ruta).parent.mkdir(parents=True, exist_ok=True)
            self._conexion = sqlite3.connect(self._ruta, check_same_thread=False)
            self._conexion.execute("PRAGMA journal_mode=WAL")
            self._conexion.execute("PRAGMA busy_timeout=5000")
            self._conexion.execute(
                "CREATE TABLE IF NOT EXISTS puntos (punto TEXT PRIMARY KEY)"
            )
            self._conexion.execute(
                """CREATE TABLE IF NOT EXISTS datos (
                    fecha TEXT NOT NULL,
                    punto TEXT NOT NULL,
                    datos TEXT NOT NULL,
                    PRIMARY KEY (fecha, punto)
                )"""
            )
            self._conexion.execute(
                """CREATE TABLE IF NOT EXISTS ausencias (
                    fecha TEXT NOT NULL,
                    punto TEXT NOT NULL,
                    PRIMARY KEY (fecha, punto)
                )"""
            )
            self._conexion.execute(
                "CREATE TABLE IF NOT EXISTS meta (clave TEXT PRIMARY KEY, valor TEXT NOT NULL)"
            )
            self._conexion.commit()
        return self._conexion

    def close(self) -> None:
        with self._lock:
            if self._conexion is not None:
                self._conexion.close()
                self._conexion = None

    def vaciar(self) -> None:
        with self._lock:
            db = self._db()
            db.execute("DELETE FROM puntos")
            db.execute("DELETE FROM datos")
            db.execute("DELETE FROM ausencias")
            db.execute("DELETE FROM meta")
            db.commit()

    def leer_puntos(self) -> list:
        """Devuelve la lista de puntos cacheada, o None si no existe o expiró."""
        with self._lock:
            fila = self._db().execute(
                "SELECT valor FROM meta WHERE clave = 'puntos_actualizado'"
            ).fetchone()
            if fila is None:
                return None
            if datetime.now() - datetime.fromisoformat(fila[0]) > _TTL_PUNTOS:
                return None
            filas = self._db().execute("SELECT punto FROM puntos").fetchall()
            if not filas:
                return None
            return [f[0] for f in filas]

    def guardar_puntos(self, puntos: list) -> None:
        with self._lock:
            db = self._db()
            db.execute("DELETE FROM puntos")
            db.executemany("INSERT INTO puntos (punto) VALUES (?)", [(p,) for p in puntos])
            db.execute(
                "INSERT OR REPLACE INTO meta (clave, valor) VALUES ('puntos_actualizado', ?)",
                (datetime.now().isoformat(),),
            )
            db.commit()

    def leer_dato(self, fecha: str, punto: str):
        """
        Devuelve el registro cacheado, el sentinela AUSENTE si se sabe que no
        hay datos, o None si no está en caché.
        """
        with self._lock:
            punto_u = punto.upper()
            fila = self._db().execute(
                "SELECT datos FROM datos WHERE fecha = ? AND punto = ?",
                (fecha, punto_u),
            ).fetchone()
            if fila:
                return json.loads(fila[0])
            ausencia = self._db().execute(
                "SELECT 1 FROM ausencias WHERE fecha = ? AND punto = ?",
                (fecha, punto_u),
            ).fetchone()
            if ausencia:
                return AUSENTE
            return None

    def leer_rango(self, fecha_inicio: str, fecha_fin: str, punto: str) -> tuple:
        """
        Clasifica cada día del rango.

        Devuelve (registros_cacheados, fechas_faltantes). Una fecha histórica
        está cubierta si tiene fila en datos o en ausencias. Hoy (Bogotá) y
        posteriores siempre cuentan como faltantes.
        """
        with self._lock:
            hoy = hoy_bogota()
            punto_u = punto.upper()
            db = self._db()
            filas_datos = db.execute(
                "SELECT fecha, datos FROM datos WHERE punto = ? AND fecha >= ? AND fecha <= ?",
                (punto_u, fecha_inicio, fecha_fin),
            ).fetchall()
            datos_por_fecha = {fila[0]: json.loads(fila[1]) for fila in filas_datos}
            filas_ausencias = db.execute(
                "SELECT fecha FROM ausencias WHERE punto = ? AND fecha >= ? AND fecha <= ?",
                (punto_u, fecha_inicio, fecha_fin),
            ).fetchall()
            ausencias = {fila[0] for fila in filas_ausencias}

            registros = []
            faltantes = []
            for fecha in _fechas_en_rango(fecha_inicio, fecha_fin):
                if fecha >= hoy:
                    faltantes.append(fecha)
                    continue
                if fecha in datos_por_fecha:
                    registros.append(datos_por_fecha[fecha])
                elif fecha in ausencias:
                    continue
                else:
                    faltantes.append(fecha)
            return registros, faltantes

    def guardar_datos(self, registros: list, punto: str) -> None:
        """
        Guarda una lista de registros; cada uno debe incluir la clave 'fecha'.
        Los registros de la fecha actual (America/Bogotá) no se guardan.
        Si un día estaba marcado como ausencia, se elimina esa marca.
        """
        with self._lock:
            hoy = hoy_bogota()
            db = self._db()
            punto_u = punto.upper()
            for registro in registros:
                fecha = registro.get("fecha")
                if not fecha or fecha >= hoy:
                    continue
                db.execute(
                    "INSERT OR REPLACE INTO datos (fecha, punto, datos) VALUES (?, ?, ?)",
                    (fecha, punto_u, json.dumps(registro)),
                )
                db.execute(
                    "DELETE FROM ausencias WHERE fecha = ? AND punto = ?",
                    (fecha, punto_u),
                )
            db.commit()

    def guardar_ausencias(self, fechas: list, punto: str) -> None:
        """Registra días históricos sin datos. Hoy (Bogotá) nunca se marca ausente."""
        with self._lock:
            hoy = hoy_bogota()
            db = self._db()
            punto_u = punto.upper()
            for fecha in fechas:
                if not fecha or fecha >= hoy:
                    continue
                db.execute(
                    "INSERT OR REPLACE INTO ausencias (fecha, punto) VALUES (?, ?)",
                    (fecha, punto_u),
                )
            db.commit()
