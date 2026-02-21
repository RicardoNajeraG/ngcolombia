# ngcolombia

Módulo para consultar composición química y algunas propiedades del gas natural en la red colombiana desde 2019-07-01 hasta la fecha actual. Los datos se actualizan diariamente a las 6:00 a.m. (UTC-5).

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
- API key (obtener en: ricardo.najera@udea.edu.co)

## Uso rápido

```python
from ngcolombia import ngDataManager

# Inicializar con tu API key
ngData = ngDataManager(apikey='tu_api_key')

# 1. Obtener la lista de puntos disponibles
puntos = ngData.obtener_puntos()
print(puntos)

# 2. Obtener datos de un punto para una fecha específica
datos = ngData.datos_fecha_punto(fecha='2024-01-15', punto='Sebastopol')
print(datos)

# 3. Obtener datos de un punto para un rango de fechas
datos = ngData.datos_rango_fechas_punto(
    fecha_inicio='2024-01-01',
    fecha_fin='2024-01-31',
    punto='Zarzal'
)
print(datos)
```

## API

### `ngDataManager(apikey: str)`

Clase principal para gestionar la conexión y obtención de datos de gas natural.

**Parámetros:**
- `apikey` (str): API key requerida. Contactar a ricardo.najera@udea.edu.co para obtenerla.

### Métodos

| Método | Descripción |
|--------|-------------|
| `obtener_puntos()` | Retorna la lista de puntos de medida disponibles. |
| `datos_fecha_punto(fecha, punto)` | Obtiene los datos de un punto para una fecha específica (formato YYYY-MM-DD). |
| `datos_rango_fechas_punto(fecha_inicio, fecha_fin, punto)` | Obtiene los datos de un punto para un rango de fechas. |

**Nota:** Algunos puntos pueden no tener datos para todas las fechas disponibles. El módulo ofrece sugerencias automáticas si el punto ingresado no es válido.

## Autor

**Ricardo Nájera**  
ricardo.najera@udea.edu.co
