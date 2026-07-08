"""
Módulo para obtener datos de gas natural desde 2019-07-01 hasta un día antes de la fecha actual.

Autor: Ricardo Nájera Giraldo
Contacto: ricardo.najera@udea.edu.co
Fecha: 2026-07-08
Versión: 0.3.0
"""

import base64

import requests

from ._cache import CacheLocal
from ._validacion import validar_fecha, validar_punto, validar_rango_fechas

_CAMPOS = (
    'fecha,hv,n2,co2,metano,etano,propano,i_butano,n_butano,'
    'i_pentane,n_pentano,hexano,neopentano,gravedad_especifica,'
    'densidad,indice_wobbe,total'
)


class ngDataManager:
    def __init__(self, apikey: str = None, cache_path: str = None):

        """
        ## Natural Gas Data Manager:
        Gestiona la conexión y obtención de datos del gas natural de Colombia desde 2019-07-01 hasta un día antes de la fecha actual.
        Los datos se actualizan a las 1:10 a.m. (UTC-5) todos los días.
        Fuente de los datos: https://beo.tgi.com.co/estadisticas/poder-calorifico-del-gas/

        Las consultas se almacenan en una caché local

        Ejemplo de uso:
        ```python
        from ngcolombia import reporte_cromatografias

        # Obtener la lista de puntos disponibles
        puntos = reporte_cromatografias.obtener_puntos()
        print(puntos)

        # Obtener los datos de un punto para una fecha específica
        datos = reporte_cromatografias.fecha_punto(fecha='YYYY-MM-DD', punto='PUNTO DE MEDIDA')
        print(datos)

        # Obtener los datos de un punto para un rango de fechas
        datos = reporte_cromatografias.rango_fechas_punto(fecha_inicio='YYYY-MM-DD', fecha_fin='YYYY-MM-DD', punto='PUNTO DE MEDIDA')
        print(datos)

        # Obtener la composición GRI-3 para un punto y una fecha específica
        composicion = reporte_cromatografias.composicion_gri3(fecha='YYYY-MM-DD', punto='PUNTO DE MEDIDA')
        print(composicion)

        # Obtener las propiedades ISO para un punto y una fecha específica
        propiedades = reporte_cromatografias.propiedades_iso(fecha='YYYY-MM-DD', punto='PUNTO DE MEDIDA')
        print(propiedades)
        ```
        """
        if not apikey:
            raise ValueError("La API key es requerida.")
        self.apikey: str = self._decode(apikey)
        self._endpoints: dict = {
            'host': 'aHR0cHM6Ly9zYW9jd3N6dXlha29jcWpqY2dmei5zdXBhYmFzZS5jby9yZXN0L3YxLw==',
            'pts': 'cHVudG9zX3VuaWNvcz9zZWxlY3Q9cHVudG8=',
            'dt': 'bmF0dXJhbF9nYXNfZGF0YQ=='
        }
        self.base_url: str = self._decode(self._endpoints['host'])
        self.puntos_url: str = self.base_url + self._decode(self._endpoints['pts'])
        self.data_url: str = self.base_url + self._decode(self._endpoints['dt'])
        self.headers: dict = {
            'apikey': self.apikey,
            'Authorization': f'Bearer {self.apikey}',
            'Accept': 'application/json'
        }
        self._cache = CacheLocal(cache_path)

    def _decode(self, string: str) -> str:
        return base64.b64decode(string).decode('utf-8')

    def obtener_puntos(self) -> list:
        """
        Entrega la lista de puntos disponibles.
        Algunos puntos pueden no tener datos para todas las fechas disponibles.
        La lista se cachea localmente durante 24 horas.
        """
        puntos = self._cache.leer_puntos()
        if puntos is not None:
            return puntos
        try:
            response = requests.get(self.puntos_url, headers=self.headers)
            if response.status_code == 401:
                raise ValueError("La API key es inválida. Por favor, verifique la API key ingresada.")
            puntos = [p['punto'] for p in response.json()]
        except Exception as e:
            raise ValueError(f"Error al obtener la lista de puntos: {e}")
        if puntos:
            self._cache.guardar_puntos(puntos)
        return puntos

    def fecha_punto(self, fecha: str, punto: str) -> dict:
        """
        Args:
            fecha: str = Fecha en formato YYYY-MM-DD
            punto: str = Punto de medida. Debe ser un punto de medida válido. No es sensible a mayúsculas o minúsculas.
        Returns:
            dict: Diccionario con los datos de gas natural solicitados

        Datos entregados:

        - Fecha (YYYY-MM-DD): Fecha de la medición.
        - Poder calorífico superior (HHV) [kBTU/ft³]
        - N2 [%]
        - CO2 [%]
        - Metano [%]
        - Etano [%]
        - Propano [%]
        - I-Butano [%]
        - N-Butano [%]
        - I-Pentano [%]
        - N-Pentano [%]
        - Hexano [%]
        - Neopentano [%]
        - Gravedad específica (SG)
        - Densidad (ρ) [lb/ft³]
        - Índice de Wobbe respecto al HHV [kBTU/ft³]
        - Total: Suma de los porcentajes en la composición presentada
        """
        validar_fecha(fecha)
        dato = self._cache.leer_dato(fecha, punto)
        if dato is not None:
            return dato
        if not validar_punto(punto, self.obtener_puntos()):
            return None
        try:
            params = [
                ('fecha', f'eq.{fecha}'),
                ('punto', f'eq.{punto.upper()}'),
                ('select', _CAMPOS)
            ]
            response = requests.get(self.data_url, headers=self.headers, params=params)
            response.raise_for_status()
            registros = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos de gas natural: {e}")
            return None
        if not registros:
            print(f"No hay datos disponibles para el punto '{punto.upper()}' en la fecha {fecha}.")
            return None
        self._cache.guardar_datos(registros, punto)
        return registros[0]

    def rango_fechas_punto(self, fecha_inicio: str, fecha_fin: str, punto: str) -> list:
        """
        Args:
            fecha_inicio: str = Fecha de inicio en formato YYYY-MM-DD
            fecha_fin: str = Fecha de fin en formato YYYY-MM-DD
            punto: str = Punto de medida. Debe ser un punto de medida válido. No es sensible a mayúsculas o minúsculas.
        Returns:
            list[dict]: Lista de diccionarios con los datos de gas natural solicitados

        Datos entregados: los mismos campos que fecha_punto, un diccionario por día.
        """
        validar_rango_fechas(fecha_inicio, fecha_fin)
        datos = self._cache.leer_rango(fecha_inicio, fecha_fin, punto)
        if datos is not None:
            return datos
        if not validar_punto(punto, self.obtener_puntos()):
            return None
        try:
            params = [
                ('fecha', f'gte.{fecha_inicio}'),
                ('fecha', f'lte.{fecha_fin}'),
                ('punto', f'eq.{punto.upper()}'),
                ('select', _CAMPOS)
            ]
            response = requests.get(self.data_url, headers=self.headers, params=params)
            response.raise_for_status()
            registros = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos de gas natural: {e}")
            return None
        if registros:
            self._cache.guardar_datos(registros, punto)
        return registros

    def composicion_gri3(self, fecha: str, punto: str) -> dict:
        """
        Args:
            fecha: str = Fecha en formato YYYY-MM-DD
            punto: str = Punto de medida. Debe ser un punto de medida válido. No es sensible a mayúsculas o minúsculas.
        Returns:
            dict: Diccionario con los datos de la composición para GRI-3 (C3H8: Propano + I-Butano + N-Butano + I-Pentano + N-Pentano + Hexano + Neopentano)

        - N2: Nitrógeno
        - CO2: Dióxido de carbono
        - CH4: Metano
        - C2H6: Etano
        - C3H8: Propano + I-Butano + N-Butano + I-Pentano + N-Pentano + Hexano + Neopentano
        """
        raw_data = self.fecha_punto(fecha, punto)
        if raw_data is None:
            raise ValueError(f"No hay datos disponibles para el punto '{punto.upper()}' en la fecha {fecha}.")
        pesados = raw_data['propano']+raw_data['i_butano']+raw_data['n_butano']+raw_data['i_pentane']+raw_data['n_pentano']+raw_data['hexano']+raw_data['neopentano']
        data = {
                'N2':raw_data['n2'],
                'CO2':raw_data['co2'],
                'CH4':raw_data['metano'],
                'C2H6':raw_data['etano'],
                'C3H8': round(pesados, 5)
                }

        total = sum(data.values())
        if total != 100:
            if total > 100:
                decrease = total - 100
                data['C3H8'] = round(data['C3H8'] - decrease, 5)
            else:
                increase = 100 - total
                data['C3H8'] = round(data['C3H8'] + increase, 5)
        return data


    def propiedades_iso(self, fecha: str, punto: str) -> dict:
        """
        Args:
            fecha: str = Fecha en formato YYYY-MM-DD
            punto: str = Punto de medida. Debe ser un punto de medida válido. No es sensible a mayúsculas o minúsculas.
        Returns:
            dict: Diccionario con las propiedades ISO para el gas natural

        - HHV_kWh_m3: Poder calorífico superior [kWh/m³]
        - SG: Gravedad específica
        - ρ_kg_m3: Densidad [kg/m³]
        - indice_wobbe_kWh_m3: Índice de Wobbe [kWh/m³]
        """
        data = self.fecha_punto(fecha, punto)
        if data is None:
            raise ValueError(f"No hay datos disponibles para el punto '{punto.upper()}' en la fecha {fecha}.")

        return {
                'HHV_kWh_m3':data['hv']*(1000/96.6211),
                'SG':data['gravedad_especifica'],
                'ρ_kg_m3':data['densidad']*16.018,
                'indice_wobbe_kWh_m3':data['indice_wobbe']*(1000/96.6211)
                }