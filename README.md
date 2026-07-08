# ngcolombia

Módulo para consultar composición química y algunas propiedades del gas natural en la red colombiana desde 2019-07-01 hasta la fecha actual. Los datos se actualizan diariamente a las 6:00 a.m. (UTC-5).

El módulo automatiza el acceso a los datos. Estos son de acceso público.

Los datos son generados por TGI (Grupo de Energía de Bogotá).
Enlace a los datos publicados e información técnica:

https://beo.tgi.com.co/estadisticas/poder-calorifico-del-gas/

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
```

## API

### `reporte_cromatografias`

Objeto ya configurado para consultar los datos de gas natural. Se importa directamente desde el paquete, sin necesidad de API key.

### Métodos

| Método | Descripción |
|--------|-------------|
| `obtener_puntos()` | Retorna la lista de puntos de medida disponibles. |
| `fecha_punto(fecha, punto)` | Obtiene los datos de un punto para una fecha específica (formato YYYY-MM-DD). |
| `rango_fechas_punto(fecha_inicio, fecha_fin, punto)` | Obtiene los datos de un punto para un rango de fechas. |

**Nota:** Algunos puntos pueden no tener datos para todas las fechas disponibles. El módulo ofrece sugerencias automáticas si el punto ingresado no es válido.

Las consultas se cachean localmente en `~/.ngcolombia_cache.db`; las consultas repetidas no vuelven a llamar a la API. Los datos de la fecha actual no se cachean.

## Autor

**Ricardo Nájera**  
ricardo.najera@udea.edu.co
