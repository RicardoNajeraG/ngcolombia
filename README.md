

<p align="center">
  <img src="https://private-user-images.githubusercontent.com/55412834/643171994-bc6c152a-b366-47bb-bb11-eeda2e101e4c.webp?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODgwNDU2OTAsIm5iZiI6MTc4ODA0NTM5MCwicGF0aCI6Ii81NTQxMjgzNC82NDMxNzE5OTQtYmM2YzE1MmEtYjM2Ni00N2JiLWJiMTEtZWVkYTJlMTAxZTRjLndlYnA_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODI5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgyOVQyMzE2MzBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1iMGU0NzQ4ZWZlNmUwMDRhMTlhYzVlMTY0NGVlMWY3ODhhMmMzOTFlZDc1NWY0NTRlM2I0NjU2NDhkNTYyMWE2JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZ3ZWJwIn0.64YqV_5dt5_37VmWsA_HPtvGnm8xH4ktMWpwzZDwXBw" alt="ngcolombia banner" width="720">
</p>

-----------------

<h1 align="center">ngcolombia</h1>
<p align="center">
  Composición química, poder calorífico e índice de Wobbe del gas natural en la red colombiana, desde Python.
</p>

|          |                                                                                                                                                                                                    |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Paquete  | [![PyPI - Version](https://img.shields.io/pypi/v/ngcolombia.svg)](https://pypi.org/project/ngcolombia/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/ngcolombia.svg)](https://pypi.org/project/ngcolombia/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ngcolombia.svg)](https://pypi.org/project/ngcolombia/) |
| Build    | [![Publish to PyPI](https://github.com/RicardoNajeraG/ngcolombia/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/RicardoNajeraG/ngcolombia/actions/workflows/pypi-publish.yml) |
| Meta     | [![License](https://img.shields.io/github/license/RicardoNajeraG/ngcolombia.svg)](https://github.com/RicardoNajeraG/ngcolombia/blob/main/LICENSE) [![Last Commit](https://img.shields.io/github/last-commit/RicardoNajeraG/ngcolombia.svg)](https://github.com/RicardoNajeraG/ngcolombia/commits/main) [![Repo Stars](https://img.shields.io/github/stars/RicardoNajeraG/ngcolombia.svg?style=social)](https://github.com/RicardoNajeraG/ngcolombia) |

## ¿Qué es `ngcolombia`?

`ngcolombia` es una librería de Python que automatiza la consulta de la **cromatografía del gas natural** (composición química, poder calorífico HHV, gravedad específica e índice de Wobbe) en los puntos de medición de la red colombiana, con datos históricos desde el **2019-07-01**, publicados diariamente por **TGI (Grupo de Energía de Bogotá)**.

En lugar de consultar manualmente los reportes desde el portal de TGI, `ngcolombia` te entrega esos datos directamente como estructuras de Python listas para usar en análisis, facturación energética, modelos de balance de gas o reportes regulatorios (CREG).

Ideal para ingenieros de gas, analistas del sector energético, desarrolladores de software para el sector de hidrocarburos, e investigadores del gas natural y de sus usos y aplicaciones en Colombia.

## Tabla de contenido

- [Características](#características)
- [Instalación](#instalación)
- [API](#api)
- [Uso rápido](#uso-rápido)
- [Casos de uso](#casos-de-uso)
- [Comportamiento](#comportamiento)
- [Preguntas frecuentes](#preguntas-frecuentes)
- [Fuente de los datos](#fuente-de-los-datos)
- [Uso responsable de los datos](#uso-responsable-de-los-datos)
- [Licencia](#licencia)
- [Código de conducta](#código-de-conducta)
- [Autor](#autor)

## Características

- Consulta la composición química, el **poder calorífico superior (HHV)**, la **gravedad específica** y el **índice de Wobbe** del gas natural por fecha y punto de medición en la red.
- Convierte la composición al formato estándar **GRI-3**.
- Entrega propiedades en **unidades ISO** (kWh/m³, kg/m³).
- Cachea localmente las consultas de forma persistente (Linux: `~/.local/share/ngcolombia/ngcolombia_cache.db`; macOS: `~/Library/Application Support/ngcolombia/ngcolombia_cache.db`; Windows: `%LOCALAPPDATA%\ngcolombia\ngcolombia_cache.db`). La ruta se puede cambiar con la variable de entorno `NGCOLOMBIA_CACHE`.
- Sin necesidad de consulta manual del portal de TGI.

## Instalación

```bash
pip install ngcolombia
```

**Requisitos:** Python >= 3.8

## API

### `reporte_cromatografias`

Objeto ya configurado para consultar los datos de gas natural. Se importa directamente desde el paquete y está listo para usarse.

### Métodos

| Método                                               | Descripción                                                                     |
| ----------------------------------------------------- | --------------------------------------------------------------------------------- |
| `obtener_puntos()`                                   | Retorna la lista de puntos de medida disponibles.                               |
| `fecha_punto(fecha, punto)`                          | Obtiene los datos de un punto para una fecha específica (formato `YYYY-MM-DD`). |
| `rango_fechas_punto(fecha_inicio, fecha_fin, punto)` | Obtiene los datos de un punto para un rango de fechas.                          |
| `composicion_gri3(fecha, punto)`                     | Transforma la composición del gas al formato GRI-3.                             |
| `propiedades_iso(fecha, punto)`                      | Calcula propiedades del gas en unidades ISO.                                    |
| `limpiar_cache()`                                    | Vacía la caché local (puntos, mediciones y ausencias).                          |

### Datos entregados por `fecha_punto` y `rango_fechas_punto`

- `fecha` (YYYY-MM-DD): Fecha de la medición.
- `hv`: Poder calorífico superior (HHV) [kBTU/ft³]
- `n2`: N2 [%]
- `co2`: CO2 [%]
- `metano`: Metano [%]
- `etano`: Etano [%]
- `propano`: Propano [%]
- `i_butano`: I-Butano [%]
- `n_butano`: N-Butano [%]
- `i_pentane`: I-Pentano [%]
- `n_pentano`: N-Pentano [%]
- `hexano`: Hexano [%]
- `neopentano`: Neopentano [%]
- `gravedad_especifica`: Gravedad específica (SG)
- `densidad`: Densidad (ρ) [lb/ft³]
- `indice_wobbe`: Índice de Wobbe respecto al HHV [kBTU/ft³]
- `total`: Suma de los porcentajes en la composición presentada

### Datos entregados por `composicion_gri3`

- `N2`: Nitrógeno [%]
- `CO2`: Dióxido de carbono [%]
- `CH4`: Metano [%]
- `C2H6`: Etano [%]
- `C3H8`: Hidrocarburos pesados agrupados (propano, butanos, pentanos, hexano y neopentano) [%]

### Datos entregados por `propiedades_iso`

- `HHV_kWh_m3`: Poder calorífico superior [kWh/m³]
- `SG`: Gravedad específica
- `ρ_kg_m3`: Densidad [kg/m³]
- `indice_wobbe_kWh_m3`: Índice de Wobbe [kWh/m³]

## Uso rápido

```python
from ngcolombia import reporte_cromatografias

puntos = reporte_cromatografias.obtener_puntos()
print(len(puntos))
print(puntos[:8])
```

```text
501
['ACACIAS LLANOGAS', 'ACACIAS MADIGAS', 'ACORDIONERO_PS', 'AGUACHICA', 'AGUACHICA II', 'AGUACLARA', 'AGUAZUL', 'AGUSTIN CODAZZI']
```

```python
datos = reporte_cromatografias.fecha_punto(fecha="2026-08-24", punto="BALLENA")
print(datos)
```

```text
{'fecha': '2026-08-24', 'hv': 0.99603, 'n2': 1.4182, 'co2': 0.2781, 'metano': 97.9544, 'etano': 0.2374, 'propano': 0.0541, 'i_butano': 0.0223, 'n_butano': 0.0084, 'i_pentane': 0.0083, 'n_pentano': 0.002, 'hexano': 0.0168, 'neopentano': 0.0, 'gravedad_especifica': 0.5661, 'densidad': 0.04309, 'indice_wobbe': 1.32381, 'total': 100.0}
```

```python
datos = reporte_cromatografias.rango_fechas_punto(
    fecha_inicio="2026-08-24",
    fecha_fin="2026-08-26",
    punto="BALLENA",
)
print(datos)
```

```text
[{'fecha': '2026-08-24', 'hv': 0.99603, 'n2': 1.4182, 'co2': 0.2781, 'metano': 97.9544, 'etano': 0.2374, 'propano': 0.0541, 'i_butano': 0.0223, 'n_butano': 0.0084, 'i_pentane': 0.0083, 'n_pentano': 0.002, 'hexano': 0.0168, 'neopentano': 0.0, 'gravedad_especifica': 0.5661, 'densidad': 0.04309, 'indice_wobbe': 1.32381, 'total': 100.0}, {'fecha': '2026-08-25', 'hv': 0.99603, 'n2': 1.4182, 'co2': 0.2781, 'metano': 97.9544, 'etano': 0.2374, 'propano': 0.0541, 'i_butano': 0.0223, 'n_butano': 0.0084, 'i_pentane': 0.0083, 'n_pentano': 0.002, 'hexano': 0.0168, 'neopentano': 0.0, 'gravedad_especifica': 0.5661, 'densidad': 0.04309, 'indice_wobbe': 1.32381, 'total': 100.0}, {'fecha': '2026-08-26', 'hv': 0.99603, 'n2': 1.4182, 'co2': 0.2781, 'metano': 97.9544, 'etano': 0.2374, 'propano': 0.0541, 'i_butano': 0.0223, 'n_butano': 0.0084, 'i_pentane': 0.0083, 'n_pentano': 0.002, 'hexano': 0.0168, 'neopentano': 0.0, 'gravedad_especifica': 0.5661, 'densidad': 0.04309, 'indice_wobbe': 1.32381, 'total': 100.0}]
```

```python
composicion = reporte_cromatografias.composicion_gri3(fecha="2026-08-24", punto="BALLENA")
print(composicion)
```

```text
{'N2': 1.4182, 'CO2': 0.2781, 'CH4': 97.9544, 'C2H6': 0.2374, 'C3H8': 0.1119}
```

```python
propiedades = reporte_cromatografias.propiedades_iso(fecha="2026-08-24", punto="BALLENA")
print(propiedades)
```

```text
{'HHV_kWh_m3': 10.308617889881194, 'SG': 0.5661, 'ρ_kg_m3': 0.69021562, 'indice_wobbe_kWh_m3': 13.701044595849146}
```

## Casos de uso

- **Facturación y balance de gas:** obtener el poder calorífico diario de un punto para calcular energía entregada (m³ → kWh).
- **Potencia de equipos térmicos:** estimar la potencia de calderas, hornos o quemadores a partir del consumo de gas natural y el poder calorífico (HHV) del punto de entrega.
- **Cumplimiento regulatorio:** generar reportes históricos de calidad del gas para la CREG u otros entes de control.
- **Modelos de simulación de redes:** alimentar modelos hidráulicos o térmicos con composición GRI-3 real.
- **Investigación académica:** alimentar modelos con la composición real del gas natural en Colombia.

## Comportamiento

- Las fechas deben tener formato `YYYY-MM-DD`, no pueden ser futuras respecto al día actual en America/Bogotá y el rango disponible inicia en `2019-07-01`.
- Los nombres de punto no distinguen mayúsculas de minúsculas.
- Si el punto ingresado no es válido, el módulo imprime sugerencias automáticas.
- Algunos puntos pueden no tener datos para todas las fechas disponibles.
- Las consultas se cachean de forma persistente; los datos del día actual (America/Bogotá) no se cachean.
- Los rangos reutilizan los días ya cacheados y solo descargan las fechas que faltan. Los días históricos sin datos se recuerdan para no volver a consultarlos.
- Los errores de red o del servidor lanzan `ValueError`.
- `limpiar_cache()` vacía la caché local.

## Preguntas frecuentes

**¿Qué es el índice de Wobbe?**
Es una medida de la intercambiabilidad de gases combustibles: indica si dos gases con distinta composición producirán una combustión equivalente en el mismo quemador sin necesidad de reajustarlo.

**¿De dónde vienen los datos?**
De los reportes públicos de cromatografía publicados diariamente por TGI (Grupo de Energía de Bogotá) en su portal BEO.

**¿Cada cuánto se actualizan?**
Diariamente a las 12:10 a.m. (hora America/Bogotá).

**¿Necesito una API key?**
No, los datos son de acceso público.

## Fuente de los datos

Los datos son generados por **TGI (Grupo de Energía de Bogotá)** y son de acceso público:
<https://beo.tgi.com.co/estadisticas/poder-calorifico-del-gas/>

## Uso responsable de los datos

Los datos que entrega `ngcolombia` proceden de los reportes públicos de TGI. Esta librería no está afiliada a TGI, al Grupo de Energía de Bogotá ni a la CREG, y no constituye una fuente oficial. Si vas a usarlos para facturación, balance de gas, cumplimiento regulatorio o decisiones de operación, verifica los valores contra el [portal de TGI](https://beo.tgi.com.co/estadisticas/poder-calorifico-del-gas/) y contra la normativa vigente. No presentes estos resultados como publicación o certificación de TGI. Usa el caché local para consultas repetidas y evita descargas innecesarias del origen.

## Licencia

[MIT](https://github.com/RicardoNajeraG/ngcolombia/blob/main/LICENSE)

## Código de conducta

La participación en este proyecto se rige por el [Código de Conducta](CODE_OF_CONDUCT.md). Al abrir un issue, enviar un pull request o comentar, se espera que lo respetes. Los reportes se reciben en [ricardo.najera@udea.edu.co](mailto:ricardo.najera@udea.edu.co).

## Autor

**Ricardo Nájera Giraldo**
📧 ricardo.najera@udea.edu.co
