"""
Caché local persistente (SQLite) para las consultas a la API.
Módulo interno: no forma parte de la API pública del paquete.

Tablas:
- puntos: lista de puntos de medida disponibles (expira a las 24 horas).
- datos: mediciones por (fecha, punto). Los datos históricos son inmutables,
  por lo que no expiran. Los datos de la fecha actual no se cachean.
- meta: pares clave-valor internos (marca de tiempo de la tabla puntos).
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

_TTL_PUNTOS = timedelta(hours=24)


class CacheLocal:
    def __init__(self, ruta: str = None):
        self._ruta = str(ruta) if ruta else str(Path.home() / ".ngcolombia_cache.db")
        self._conexion = None

    def _db(self) -> sqlite3.Connection:
        """Abre la conexión y crea las tablas la primera vez que se necesita."""
        if self._conexion is None:
            self._conexion = sqlite3.connect(self._ruta)
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
                "CREATE TABLE IF NOT EXISTS meta (clave TEXT PRIMARY KEY, valor TEXT NOT NULL)"
            )
            self._conexion.commit()
        return self._conexion

    def leer_puntos(self) -> list:
        """Devuelve la lista de puntos cacheada, o None si no existe o expiró."""
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
        db = self._db()
        db.execute("DELETE FROM puntos")
        db.executemany("INSERT INTO puntos (punto) VALUES (?)", [(p,) for p in puntos])
        db.execute(
            "INSERT OR REPLACE INTO meta (clave, valor) VALUES ('puntos_actualizado', ?)",
            (datetime.now().isoformat(),),
        )
        db.commit()

    def leer_dato(self, fecha: str, punto: str) -> dict:
        """Devuelve el registro cacheado para (fecha, punto), o None si no está."""
        fila = self._db().execute(
            "SELECT datos FROM datos WHERE fecha = ? AND punto = ?",
            (fecha, punto.upper()),
        ).fetchone()
        return json.loads(fila[0]) if fila else None

    def leer_rango(self, fecha_inicio: str, fecha_fin: str, punto: str) -> list:
        """
        Devuelve los datos del rango solo si TODOS los días están en caché.
        Si falta al menos un día, devuelve None.
        """
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
        dias_esperados = (fin - inicio).days + 1
        filas = self._db().execute(
            "SELECT datos FROM datos WHERE punto = ? AND fecha >= ? AND fecha <= ? ORDER BY fecha",
            (punto.upper(), fecha_inicio, fecha_fin),
        ).fetchall()
        if len(filas) < dias_esperados:
            return None
        return [json.loads(f[0]) for f in filas]

    def guardar_datos(self, registros: list, punto: str) -> None:
        """
        Guarda una lista de registros; cada uno debe incluir la clave 'fecha'.
        Los registros de la fecha actual no se guardan (pueden estar incompletos).
        """
        hoy = datetime.now().strftime("%Y-%m-%d")
        db = self._db()
        for registro in registros:
            fecha = registro.get("fecha")
            if not fecha or fecha == hoy:
                continue
            db.execute(
                "INSERT OR REPLACE INTO datos (fecha, punto, datos) VALUES (?, ?, ?)",
                (fecha, punto.upper(), json.dumps(registro)),
            )
        db.commit()
