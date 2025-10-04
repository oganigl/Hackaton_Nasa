# 🛰️ NASA Earthdata - Guía de Uso

## 📖 Descripción

Este script permite descargar datos de NASA Earthdata de forma personalizada, especificando:
- **📅 Fecha**: Formato YYYYMMDD o YYYY-MM-DD
- **📍 Coordenadas**: Latitud y longitud
- **📊 Tipo de dato**: Diferentes datasets disponibles

## 🔧 Configuración Inicial

1. **Instala las dependencias**:
```bash
pip install requests
```

2. **Configura tus credenciales** en el archivo `tesp_api_earthdata.py`:
```python
USER = "tu_usuario_nasa"
PASS = "tu_contraseña_nasa"
```

## 📊 Datasets Disponibles

| Dataset | Descripción | Ejemplo de Uso |
|---------|-------------|----------------|
| `IMERG_DAILY` | Precipitación diaria | Lluvia del último mes |
| `IMERG_MONTHLY` | Precipitación mensual | Tendencias anuales |
| `MODIS_LST` | Temperatura superficial | Islas de calor urbano |

## 🚀 Ejemplos de Uso

### 1. Precipitación en Madrid
```python
from tesp_api_earthdata import earthdata_custom_request

# Datos de precipitación diaria para Madrid
result = earthdata_custom_request(
    dataset='IMERG_DAILY',
    date='2024-03-15',  # 15 de marzo de 2024
    lat=40.4168,        # Latitud de Madrid
    lon=-3.7038,        # Longitud de Madrid
    out_dir='data/madrid'
)
```

### 2. Temperatura Superficial en Barcelona
```python
# Temperatura superficial MODIS para Barcelona
result = earthdata_custom_request(
    dataset='MODIS_LST',
    date='2024-03-15',
    lat=41.3851,        # Latitud de Barcelona
    lon=2.1734,         # Longitud de Barcelona
    out_dir='data/barcelona'
)
```

### 3. Múltiples Descargas
```python
# Lista de ciudades españolas
ciudades = [
    {'name': 'Madrid', 'lat': 40.4168, 'lon': -3.7038},
    {'name': 'Barcelona', 'lat': 41.3851, 'lon': 2.1734},
    {'name': 'Valencia', 'lat': 39.4699, 'lon': -0.3763},
    {'name': 'Sevilla', 'lat': 37.3891, 'lon': -5.9845}
]

# Descargar precipitación para todas las ciudades
fecha = '2024-03-15'
for ciudad in ciudades:
    print(f"\n🏙️ Descargando datos para {ciudad['name']}")
    earthdata_custom_request(
        dataset='IMERG_DAILY',
        date=fecha,
        lat=ciudad['lat'],
        lon=ciudad['lon'],
        out_dir=f"data/{ciudad['name'].lower()}"
    )
```

### 4. Rango de Fechas
```python
from datetime import datetime, timedelta

# Descargar datos de una semana
fecha_inicio = datetime(2024, 3, 10)
for i in range(7):  # 7 días
    fecha = fecha_inicio + timedelta(days=i)
    fecha_str = fecha.strftime('%Y%m%d')
    
    earthdata_custom_request(
        dataset='IMERG_DAILY',
        date=fecha_str,
        lat=40.4168,  # Madrid
        lon=-3.7038,
        out_dir=f'data/madrid_semana/{fecha_str}'
    )
```

## 🔍 Funciones Útiles

### Listar Datasets Disponibles
```python
from tesp_api_earthdata import list_available_datasets

datasets = list_available_datasets()
for dataset_id, description in datasets.items():
    print(f"{dataset_id}: {description}")
```

### Sugerir Fecha Reciente
```python
from tesp_api_earthdata import suggest_recent_date

# Obtener fecha sugerida para diferentes datasets
fecha_imerg = suggest_recent_date('IMERG_DAILY')
fecha_modis = suggest_recent_date('MODIS_LST')

print(f"Fecha sugerida IMERG: {fecha_imerg}")
print(f"Fecha sugerida MODIS: {fecha_modis}")
```

## 🗂️ Estructura de Archivos Descargados

```
data/
├── madrid/
│   └── 3B-Daily.MS.MRG.3IMERG.20240315-S000000-E235959.V07B.nc4
├── barcelona/
│   └── MOD11A1.A2024075.h17v04.061.*.hdf
└── valencia/
    └── 3B-Daily.MS.MRG.3IMERG.20240315-S000000-E235959.V07B.nc4
```

## 📋 Coordenadas de Ciudades Españolas

| Ciudad | Latitud | Longitud |
|--------|---------|----------|
| Madrid | 40.4168 | -3.7038 |
| Barcelona | 41.3851 | 2.1734 |
| Valencia | 39.4699 | -0.3763 |
| Sevilla | 37.3891 | -5.9845 |
| Bilbao | 43.2627 | -2.9253 |
| Zaragoza | 41.6560 | -0.8773 |

## ⚠️ Notas Importantes

1. **Disponibilidad de datos**: No todos los datos están disponibles para todas las fechas
2. **Latencia**: Los datos pueden tener un retraso de varios días
3. **Límites de descarga**: NASA puede tener límites en las descargas masivas
4. **Formatos**: Los archivos descargados están en formato NetCDF (.nc4) o HDF

## 🔧 Solución de Problemas

### Error 404 - Archivo No Encontrado
- Verifica que la fecha esté disponible
- Usa `suggest_recent_date()` para fechas más probables
- Consulta el catálogo de NASA Earthdata online

### Error de Autenticación
- Verifica tus credenciales USER y PASS
- Asegúrate de tener una cuenta activa en https://urs.earthdata.nasa.gov/

### Archivos Grandes
- Los archivos NetCDF pueden ser grandes (>100MB)
- Asegúrate de tener suficiente espacio en disco
- La descarga puede tomar varios minutos