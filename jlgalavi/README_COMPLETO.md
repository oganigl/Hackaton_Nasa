# 🛰️ NASA Earthdata - Sistema Automatizado

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![NASA](https://img.shields.io/badge/NASA-Earthdata-red.svg)](https://earthdata.nasa.gov/)
[![Automation](https://img.shields.io/badge/Status-Automated-green.svg)](https://github.com)

**Sistema completo y automatizado para acceso a datos NASA sin intervención manual**

## 🚀 Características Principales

- ✅ **Configuración única** - Credenciales NASA guardadas de forma segura
- 🤖 **Totalmente automatizado** - Sin necesidad de entrada manual después de la configuración
- 🌍 **Múltiples datasets** - GPM, MERRA-2, MODIS, GOES y más
- 📊 **Análisis integrado** - Funciones built-in para visualización y estadísticas
- 🗺️ **Geolocalización inteligente** - Búsqueda por nombre de ciudad o coordenadas
- 📈 **Exportación flexible** - Múltiples formatos de salida

## 📁 Estructura del Proyecto

```
Hackaton_Nasa/
├── 🧠 nasa_earthdata_lib.py      # Librería principal automatizada
├── 📚 ejemplos_nasa_lib.py       # Ejemplos completos de uso
├── 📓 nasa_earthdata_access.ipynb # Tutorial interactivo Jupyter
├── 🔧 tesp_api_earthdata.py      # Código original mejorado
├── 📋 GUIA_USO.md               # Guía de uso detallada
├── 🔍 CONFIGURACION_NASA.md     # Troubleshooting
└── 📖 README_COMPLETO.md        # Este archivo
```

## 🏗️ Instalación Rápida

### 1. Preparar el entorno
```bash
# Crear entorno virtual (recomendado)
python -m venv nasa
cd nasa
Scripts\activate  # Windows
# source bin/activate  # Linux/Mac

# Instalar dependencias
pip install earthaccess xarray requests cartopy matplotlib pandas
```

### 2. Configuración única de credenciales
```python
from nasa_earthdata_lib import setup_credentials

# ¡Solo UNA VEZ!
success = setup_credentials("tu_usuario_nasa", "tu_contraseña_nasa")
print("✅ Credenciales configuradas" if success else "❌ Error en configuración")
```

## 🎯 Uso Inmediato

### Precipitación en cualquier lugar
```python
from nasa_earthdata_lib import get_precipitation

# Madrid - 15 marzo 2024
data = get_precipitation(date='2024-03-15', lat=40.4168, lon=-3.7038)
print(f"Precipitación: {data.precipitationCal.values} mm/hr")
```

### Temperatura de una región
```python
from nasa_earthdata_lib import get_temperature

# España completa - última semana
data = get_temperature(
    date_start='2024-03-15',
    date_end='2024-03-22',
    bbox=(-10, 35, 5, 45)  # (oeste, sur, este, norte)
)
temp_celsius = data.T2M - 273.15
print(f"Temperatura media: {temp_celsius.mean().values:.1f}°C")
```

### Análisis por ciudad
```python
from nasa_earthdata_lib import get_location_data

# Barcelona - datos MERRA-2
data = get_location_data(
    location='barcelona',
    dataset='MERRA2',
    date_start='2024-03-15'
)
```

### Análisis automático
```python
from nasa_earthdata_lib import quick_analysis

# Madrid - últimos 7 días con gráficos automáticos
results = quick_analysis(
    dataset='MERRA2', 
    location='madrid', 
    days=7
)
```

## 📊 Datasets Disponibles

| Dataset | Descripción | Variables Principales |
|---------|-------------|----------------------|
| **GPM_IMERG** | Precipitación global 30min | `precipitationCal` |
| **MERRA2** | Reanálisis atmosférico | `T2M`, `U10M`, `V10M`, `QV2M` |
| **MODIS_AQUA** | Observaciones oceánicas | `chlor_a`, `sst` |
| **GOES16** | Datos meteorológicos | `Rad`, `DQF` |

## 🔧 Funciones Principales

### Configuración
- `setup_credentials(user, password)` - Configuración única
- `verify_auth()` - Verificar autenticación
- `list_datasets()` - Listar datasets disponibles

### Obtención de datos
- `get_data(**params)` - Función universal
- `get_precipitation(date, lat, lon)` - Precipitación puntual
- `get_temperature(date_start, bbox)` - Temperatura regional
- `get_location_data(location, dataset)` - Por nombre de ciudad

### Análisis
- `quick_analysis(dataset, location, days)` - Análisis automático
- Funciones de plotting integradas
- Exportación a múltiples formatos

## 🌍 Ejemplos por Región

### España
```python
# Precipitación en Madrid
madrid_lluvia = get_precipitation('2024-03-15', 40.4168, -3.7038)

# Temperatura de toda España
espana_temp = get_temperature(
    date_start='2024-03-15',
    bbox=(-10, 35, 5, 45)
)
```

### América Latina
```python
# Ciudad de México
cdmx_data = get_location_data('mexico city', 'MERRA2', '2024-03-15')

# Región amazónica
amazon_temp = get_temperature(
    date_start='2024-03-15',
    bbox=(-75, -10, -45, 5)
)
```

## 📈 Análisis Avanzado

### Serie temporal completa
```python
from nasa_earthdata_lib import get_data
import matplotlib.pyplot as plt

# Temperatura Madrid - último mes
data = get_data(
    dataset='MERRA2',
    date_start='2024-02-15',
    date_end='2024-03-15',
    lat=40.4, lon=-3.7,
    variables=['T2M']
)

# Conversión y plotting
temp_celsius = data.T2M - 273.15
temp_celsius.plot(x='time')
plt.title('Temperatura Madrid - Último Mes')
plt.ylabel('Temperatura (°C)')
plt.show()
```

### Análisis espacial
```python
# Precipitación peninsular
precip_data = get_data(
    dataset='GPM_IMERG',
    date='2024-03-15',
    bbox=(-10, 35, 5, 45),
    variables=['precipitationCal']
)

# Mapa de precipitación
precip_data.precipitationCal.plot(x='lon', y='lat')
plt.title('Precipitación Península Ibérica')
plt.show()
```

## 🔐 Seguridad y Credenciales

### Métodos de autenticación soportados
1. **Automático** - Credenciales cifradas localmente
2. **Variables de entorno** - `EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD`
3. **Archivo .netrc** - Estándar NASA
4. **Interactivo** - Prompt manual como respaldo

### Ubicaciones de credenciales
```
Windows: %USERPROFILE%\.nasa_credentials
Linux/Mac: ~/.nasa_credentials
```

## 📚 Recursos Adicionales

### Notebooks incluidos
- `nasa_earthdata_access.ipynb` - Tutorial completo paso a paso
- Secciones: Autenticación, Búsqueda, Descarga, Análisis, Visualización

### Documentación
- `GUIA_USO.md` - Guía práctica
- `CONFIGURACION_NASA.md` - Solución de problemas
- Comentarios extensivos en todo el código

## 🆘 Solución de Problemas

### Error de autenticación
```python
from nasa_earthdata_lib import verify_auth, setup_credentials

# Verificar estado
if not verify_auth():
    # Reconfigurar
    setup_credentials("usuario", "contraseña")
```

### Dataset no encontrado
```python
from nasa_earthdata_lib import list_datasets

# Ver datasets disponibles
datasets = list_datasets()
print("Datasets disponibles:", datasets)
```

### Región sin datos
```python
# Probar diferentes fechas/regiones
data = get_data(
    dataset='MERRA2',  # Dataset alternativo
    date_start='2024-03-10',  # Fecha anterior
    bbox=(-8, 36, 3, 44),     # Región más pequeña
    max_retries=3
)
```

## 🎯 Casos de Uso Típicos

### 1. Monitoreo meteorológico
```python
# Alerta de precipitación
precipitacion = get_precipitation('2024-03-15', 40.4, -3.7)
if precipitacion.precipitationCal.values > 5:  # > 5mm/hr
    print("⚠️ Alerta: Lluvia intensa detectada")
```

### 2. Análisis climático
```python
# Trend de temperatura
data_historica = get_temperature(
    date_start='2024-01-01',
    date_end='2024-03-15',
    bbox=(40, 40, 41, 41)  # Madrid área
)
trend = data_historica.T2M.polyfit(dim='time', deg=1)
print(f"Tendencia: {trend.polyfit_coefficients[0].values:.3f} K/día")
```

### 3. Agricultura de precisión
```python
# Condiciones para cultivos
madrid_conditions = quick_analysis('MERRA2', 'madrid', days=7)
# Automáticamente genera reportes de temperatura, humedad, viento
```

## 🔄 Actualizaciones y Mantenimiento

### Auto-actualización de datasets
- La librería busca automáticamente nuevos datasets disponibles
- Configuración automática de parámetros por dataset

### Logs y debugging
```python
import logging
logging.basicConfig(level=logging.INFO)

# Ver información detallada de descargas
data = get_data(..., verbose=True)
```

## 🤝 Contribución

### Estructura modular
- `EarthdataAuth` - Gestión de autenticación
- `DatasetConfig` - Configuraciones por dataset
- `LocationSearch` - Geolocalización
- Funciones wrapper para facilidad de uso

### Extensión fácil
```python
# Añadir nuevo dataset
DATASET_CONFIGS['NUEVO_DATASET'] = {
    'collection': 'C1234567-GES_DISC',
    'variables': ['nueva_variable'],
    'processing': lambda x: x.sel(time='2024-03-15')
}
```

## 📞 Soporte

### Problemas comunes
1. **Credenciales inválidas** → Verificar en [URS NASA](https://urs.earthdata.nasa.gov/)
2. **Aplicaciones no autorizadas** → Autorizar GES DISC DATA ARCHIVE
3. **Timeouts** → Reducir región o usar `max_retries`

### Contacto
- 📧 Issues en el repositorio
- 📚 Documentación NASA: [earthdata.nasa.gov](https://earthdata.nasa.gov/)
- 🛠️ Tutorial oficial earthaccess: [NASA GES DISC](https://disc.gsfc.nasa.gov/)

---

## 🏆 Logros del Sistema

✅ **Eliminación completa** de entrada manual de credenciales  
✅ **Automatización total** del flujo de autenticación NASA  
✅ **API simplificada** para casos de uso comunes  
✅ **Integración** con herramientas científicas estándar  
✅ **Documentación completa** con ejemplos prácticos  
✅ **Compatibilidad** con múltiples métodos de autenticación  

**🎯 Resultado:** Acceso inmediato a datos NASA con una sola línea de código tras configuración inicial única.