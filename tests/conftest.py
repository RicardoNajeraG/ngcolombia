import base64
import json
from pathlib import Path

import pytest

from ngcolombia.gas_data_manager import ngDataManager

MOCKUPS_DIR = Path(__file__).parent / "mockups"


def leer_mockup(nombre: str):
    """Carga un archivo JSON de tests/mockups/ (datos reales capturados de la API)."""
    return json.loads((MOCKUPS_DIR / nombre).read_text(encoding="utf-8"))


# Lista real de puntos capturada de la API (misma fuente que puntos.json).
PUNTOS_REALES = [p["punto"] for p in leer_mockup("puntos.json")]


@pytest.fixture
def cargar_mockup():
    """Devuelve una función que carga un archivo JSON de tests/mockups/."""
    return leer_mockup


@pytest.fixture
def manager(tmp_path):
    """ngDataManager con apikey de prueba y caché en directorio temporal."""
    apikey = base64.b64encode(b"clave-de-prueba").decode()
    return ngDataManager(apikey=apikey, cache_path=str(tmp_path / "cache.db"))


@pytest.fixture
def manager_con_puntos(manager):
    """Manager con la caché de puntos pre-sembrada (lista real) para que
    obtener_puntos() no haga HTTP durante la validación del punto."""
    manager._cache.guardar_puntos(PUNTOS_REALES)
    return manager
