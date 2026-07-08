# ngcolombia

Módulo para consultar composición química y algunas propiedades del gas natural en la red colombiana desde 2019-07-01 hasta un día antes de la fecha actual en America/Bogotá. Los datos se actualizan diariamente a las 12:10 a.m. (UTC-5). 

El módulo automatiza el acceso a los datos. Estos son de acceso público.

Los datos son generados por TGI (Grupo de Energía de Bogotá).
Enlace a los datos publicados e información técnica:

[https://beo.tgi.com.co/estadisticas/poder-calorifico-del-gas/](https://beo.tgi.com.co/estadisticas/poder-calorifico-del-gas/)

## Instalación

```bash
pip install ngcolombia
```

## Requisitos

- Python >= 3.8

## Uso rápido

```python
from ngcolombia import reporte_cromatografias

# 1. Obtener la lista de puntos disponibles
puntos = reporte_cromatografias.obtener_puntos()
print(puntos)

# 2. Obtener datos de un punto para una fecha específica
datos = reporte_cromatografias.fecha_punto(fecha='2024-01-15', punto='Sebastopol')
print(datos)

# 3. Obtener datos de un punto para un rango de fechas
datos = reporte_cromatografias.rango_fechas_punto(
    fecha_inicio='2024-01-01',
    fecha_fin='2024-01-31',
    punto='Zarzal'
)
print(datos)

# 4. Obtener la composición en formato GRI-3
composicion = reporte_cromatografias.composicion_gri3(fecha='2024-01-15', punto='Sebastopol')
print(composicion)

# 5. Obtener propiedades en unidades ISO
propiedades = reporte_cromatografias.propiedades_iso(fecha='2024-01-15', punto='Sebastopol')
print(propiedades)
```

## API

### `reporte_cromatografias`

Objeto ya configurado para consultar los datos de gas natural. Se importa directamente desde el paquete y está listo para usarse.

### Métodos


| Método                                               | Descripción                                                                     |
| ---------------------------------------------------- | ------------------------------------------------------------------------------- |
| `obtener_puntos()`                                   | Retorna la lista de puntos de medida disponibles.                               |
| `fecha_punto(fecha, punto)`                          | Obtiene los datos de un punto para una fecha específica (formato `YYYY-MM-DD`). |
| `rango_fechas_punto(fecha_inicio, fecha_fin, punto)` | Obtiene los datos de un punto para un rango de fechas.                          |
| `composicion_gri3(fecha, punto)`                     | Transforma la composición del gas al formato GRI-3.                             |
| `propiedades_iso(fecha, punto)`                      | Calcula propiedades del gas en unidades ISO.                                    |


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

## Comportamiento

- Las fechas deben tener formato `YYYY-MM-DD`, no pueden ser futuras y el rango disponible inicia en `2019-07-01`.
- Los nombres de punto no distinguen mayúsculas de minúsculas.
- Si el punto ingresado no es válido, el módulo imprime sugerencias automáticas.
- Algunos puntos pueden no tener datos para todas las fechas disponibles.
- Las consultas se cachean localmente en `~/.ngcolombia_cache.db`; las consultas repetidas no vuelven a descargar los datos. Los datos de la fecha actual no se cachean.

## Autor

**Ricardo Nájera**  
[ricardo.najera@udea.edu.co](mailto:ricardo.najera@udea.edu.co)