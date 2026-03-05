"""
Módulo para obtener datos de gas natural desde 2019-07-01 hasta la fecha actual.

Autor: Ricardo Nájera Giraldo
Contacto: ricardo.najera@udea.edu.co
Fecha: 2026-02-21
Versión: 0.1.0
"""

import requests
from datetime import datetime
from difflib import get_close_matches
import base64

class ngDataManager:
    def __init__(self, apikey: str = None):
        """
        ## Natural Gas Data Manager:
        Gestiona la conexión y obtención de datos del gas natural de Colombia desde 2019-07-01 hasta la fecha actual.
        Los datos se actualizan a las 6:00 a.m. (UTC-5) todos los días.
        Fuente de los datos: https://beo.tgi.com.co/estadisticas/poder-calorifico-del-gas/
        Para obtener una API key, por favor, contacte a ricardo.najera@udea.edu.co

        Ejemplo de uso:
        ```python
        # Obtener la lista de puntos disponibles
        from ngcolombia import ngDataManager

        ngData = NgDataManager(apikey='su_api_key') # Reemplazar su_api_key por la API key obtenida
        puntos = ngData.obtener_puntos()
        print(puntos)

        # Obtener los datos de un punto para una fecha específica
        datos = ngData.datos_fecha_punto(fecha='YYYY-MM-DD', punto='PUNTO DE MEDIDA')
        print(datos)

        # Obtener los datos de un punto para un rango de fechas
        datos = ngData.datos_rango_fechas_punto(fecha_inicio='YYYY-MM-DD', fecha_fin='YYYY-MM-DD', punto='PUNTO DE MEDIDA')
        print(datos)
        ```
        """
        if apikey:
            self.apikey: str = apikey
        else:
            raise ValueError("La API key es requerida. Para obtener una API key, por favor, contacte a ricardo.najera@udea.edu.co")
        self._endpoints: dict[str, str] = {
            'host': 'aHR0cHM6Ly9zYW9jd3N6dXlha29jcWpqY2dmei5zdXBhYmFzZS5jby9yZXN0L3YxLw==',
            'pts': 'cHVudG9zX3VuaWNvcz9zZWxlY3Q9cHVudG8=',
            'dt':'bmF0dXJhbF9nYXNfZGF0YQ=='
        }
        self.base_url: str = self._decode(self._endpoints['host'])
        self.puntos_url: str = self.base_url + self._decode(self._endpoints['pts'])
        self.data_url: str = self.base_url + self._decode(self._endpoints['dt'])
        self.headers: dict[str, str] = {
            'apikey': self.apikey,
            'Authorization': f'Bearer {self.apikey}',
            'Accept': 'application/json'
        }
    def _decode(self, string: str) -> str:
        return base64.b64decode(string).decode('utf-8')

    def obtener_puntos(self) -> list[str]:
        """
        Entrega la lista de puntos disponibles.
        Algunos puntos pueden no tener datos para todas las fechas disponibles.
        """

        try:
            response = requests.get(self.puntos_url, headers=self.headers)
            if response.status_code == 401:
                raise ValueError("La API key es inválida. Por favor, verifique la API key ingresada.")
            puntos_data = response.json()
            return [p['punto'] for p in puntos_data]

        except Exception as e:
            raise ValueError(f"Error al obtener la lista de puntos: {e}")
            

    def _validar_punto(self, punto: str) -> bool:
        """
        Valida si el punto solicitado es válido.
        (Algunos puntos pueden no tener datos para todas las fechas)
        """
        lista_puntos = self.obtener_puntos()
            
        if punto.upper() in lista_puntos:
            return True

        posibles = [p for p in lista_puntos if punto.upper() in p]
        if posibles:
            print(f"El punto '{punto}' no es válido. ¿Quizás quisiste decir?: {', '.join(posibles)}")
            return False
        else:
            sugerencias = get_close_matches(punto.upper(), lista_puntos, n=5, cutoff=0.6)
            if sugerencias:
                print(f"El punto '{punto}' no es válido. ¿Quizás quisiste decir?: {', '.join(sugerencias)}")
            else:
                print(f"El punto '{punto}' no es válido y no se encontraron sugerencias similares.")
            return False
    
    def datos_fecha_punto(self, fecha: str, punto: str) -> dict:
        """
        Args:
            fecha: str = Fecha en formato YYYY-MM-DD
            punto: str = Punto de medida. Debe ser un punto de medida válido. No es sensible a mayúsculas o minúsculas.
        Returns:
            dict: Diccionario con los datos de gas natural solicitados

        Datos entregados:
        
        - id: Identificador único de la medición.
        - Fecha (YYYY-MM-DD): Fecha de la medición.
        - Punto: Punto de la medición.
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
        - created_at: fecha de ingreso del dato a la db
        """

        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            if fecha_dt > datetime.now():
                raise ValueError(f"La fecha ingresada no puede ser posterior a la fecha actual. Fecha actual: {datetime.now().strftime('%Y-%m-%d')}")
        except ValueError:
            raise ValueError(f"La fecha ingresada no es válida. Formato esperado: YYYY-MM-DD. Fecha ingresada: {fecha}")
        if self._validar_punto(punto):
            try:
                params = [
                    ('fecha', f'eq.{fecha}'),
                    ('punto', f'eq.{punto.upper()}'),
                    ('select', 'hv,n2,co2,metano,etano,propano,i_butano,n_butano,i_pentane,n_pentano,hexano,neopentano,gravedad_especifica,densidad,indice_wobbe,total')
                ]
                response = requests.get(self.data_url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()[0]
            except requests.exceptions.RequestException as e:
                print(f"Error al obtener datos de gas natural: {e}")
                return None
        else:
            return None

    def datos_rango_fechas_punto(self, fecha_inicio: str, fecha_fin: str, punto: str) -> list[dict]:
        """
        Args:
            fecha_inicio: str = Fecha de inicio en formato YYYY-MM-DD
            fecha_fin: str = Fecha de fin en formato YYYY-MM-DD
            punto: str = Punto de medida. Debe ser un punto de medida válido. No es sensible a mayúsculas o minúsculas.
        Returns:
            list[dict]: Lista de diccionarios con los datos de gas natural solicitados

        Datos entregados:
        - id: Identificador único de la medición.
        - Fecha (YYYY-MM-DD): Fecha de la medición.
        - Punto: Punto de la medición.
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
        - created_at: fecha de ingreso del dato a la db
        """
        
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
            fecha_inicio_min = datetime.strptime("2019-07-01", "%Y-%m-%d")
            fecha_actual = datetime.now()

            if fecha_inicio_dt < fecha_inicio_min:
                raise ValueError("La fecha de inicio no puede ser anterior a 2019-07-01. Fecha ingresada: {}".format(fecha_inicio))
            if fecha_fin_dt > fecha_actual:
                raise ValueError("La fecha de fin no puede ser posterior a la fecha actual. Fecha ingresada: {}. Fecha actual: {}".format(fecha_fin, fecha_actual.strftime('%Y-%m-%d')))
        except ValueError:
            raise ValueError("Formato de fecha incorrecto. Se espera YYYY-MM-DD para ambas fechas. Recibido: fecha_inicio={}, fecha_fin={}".format(fecha_inicio, fecha_fin))

        if self._validar_punto(punto):
            try:
                params = [
                    ('fecha', f'gte.{fecha_inicio}'),
                    ('fecha', f'lte.{fecha_fin}'),
                    ('punto', f'eq.{punto.upper()}'),
                    ('select', 'fecha,hv,n2,co2,metano,etano,propano,i_butano,n_butano,i_pentane,n_pentano,hexano,neopentano,gravedad_especifica,densidad,indice_wobbe,total')
                ]
                response = requests.get(self.data_url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error al obtener datos de gas natural: {e}")
                return None