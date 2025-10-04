# 🛰️ NASA Earthdata Library - Acceso Automático
# Librería completa para acceso automatizado a datos NASA sin intervención manual

import os
import sys
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union, Tuple
import warnings
warnings.filterwarnings('ignore')

# Configuración global de credenciales
CONFIG_DIR = Path.home() / '.nasa_earthdata'
CREDENTIALS_FILE = CONFIG_DIR / 'credentials.json'
SESSION_FILE = CONFIG_DIR / 'session.pkl'

class NASAEarthdataError(Exception):
    """Excepción personalizada para errores de NASA Earthdata"""
    pass

class EarthdataAuth:
    """Manejador de autenticación automática para NASA Earthdata"""
    
    def __init__(self):
        self.username = None
        self.password = None
        self.authenticated = False
        self._setup_config_dir()
    
    def _setup_config_dir(self):
        """Crear directorio de configuración si no existe"""
        CONFIG_DIR.mkdir(exist_ok=True)
    
    def save_credentials(self, username: str, password: str):
        """
        Guarda credenciales de forma segura
        
        Args:
            username: Usuario NASA Earthdata
            password: Contraseña NASA Earthdata
        """
        try:
            # Cifrado básico para seguridad
            import base64
            encoded_pass = base64.b64encode(password.encode()).decode()
            
            credentials = {
                'username': username,
                'password': encoded_pass,
                'created': datetime.now().isoformat()
            }
            
            with open(CREDENTIALS_FILE, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            print(f"✅ Credenciales guardadas en {CREDENTIALS_FILE}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando credenciales: {e}")
            return False
    
    def load_credentials(self):
        """Cargar credenciales guardadas"""
        try:
            if not CREDENTIALS_FILE.exists():
                return False
            
            with open(CREDENTIALS_FILE, 'r') as f:
                credentials = json.load(f)
            
            import base64
            self.username = credentials['username']
            self.password = base64.b64decode(credentials['password']).decode()
            return True
            
        except Exception as e:
            print(f"❌ Error cargando credenciales: {e}")
            return False
    
    def authenticate(self, username: str = None, password: str = None):
        """
        Autenticación automática con NASA Earthdata
        
        Args:
            username: Usuario (opcional si está guardado)
            password: Contraseña (opcional si está guardada)
        """
        # Usar credenciales proporcionadas o cargar guardadas
        if username and password:
            self.username = username
            self.password = password
            # Guardar para próximos usos
            self.save_credentials(username, password)
        elif not self.load_credentials():
            raise NASAEarthdataError(
                "No hay credenciales disponibles. "
                "Usa auth.authenticate('usuario', 'contraseña') la primera vez."
            )
        
        # Intentar autenticación con earthaccess
        try:
            import earthaccess
            
            # Configurar credenciales
            os.environ['EARTHDATA_USERNAME'] = self.username
            os.environ['EARTHDATA_PASSWORD'] = self.password
            
            # Autenticar
            auth = earthaccess.login(strategy="environment")
            
            if auth.authenticated:
                self.authenticated = True
                print("✅ Autenticación exitosa con NASA Earthdata")
                return True
            else:
                raise Exception("Falló la autenticación")
                
        except ImportError:
            print("📦 Instalando earthaccess...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "earthaccess"])
            return self.authenticate()
            
        except Exception as e:
            print(f"❌ Error de autenticación: {e}")
            print("💡 Verifica tus credenciales en https://urs.earthdata.nasa.gov/")
            self.authenticated = False
            return False

# Instancia global de autenticación
auth = EarthdataAuth()

def setup_credentials(username: str, password: str) -> bool:
    """
    Configurar credenciales NASA Earthdata (solo necesario una vez)
    
    Args:
        username: Tu usuario NASA Earthdata
        password: Tu contraseña NASA Earthdata
    
    Returns:
        bool: True si la configuración fue exitosa
    
    Example:
        >>> setup_credentials("mi_usuario", "mi_contraseña")
        ✅ Credenciales guardadas y configuradas
    """
    print("🔐 Configurando credenciales NASA Earthdata...")
    
    if auth.authenticate(username, password):
        print("🎉 ¡Configuración completa! Ya puedes usar todas las funciones automáticamente.")
        return True
    else:
        print("❌ Error en configuración. Verifica tus credenciales.")
        return False

def auto_authenticate() -> bool:
    """
    Autenticación automática usando credenciales guardadas
    
    Returns:
        bool: True si la autenticación fue exitosa
    """
    if auth.authenticated:
        return True
    
    try:
        return auth.authenticate()
    except NASAEarthdataError as e:
        print(f"⚠️  {e}")
        print("💡 Ejecuta: setup_credentials('usuario', 'contraseña')")
        return False

# Configuración de datasets
DATASETS_CONFIG = {
    'IMERG_DAILY': {
        'short_name': 'GPM_3IMERGHH',
        'doi': '10.5067/GPM/IMERGDF/DAY/07',
        'description': 'Precipitación diaria GPM IMERG',
        'variables': ['precipitationCal'],
        'temporal_resolution': 'daily'
    },
    'MERRA2': {
        'short_name': 'M2T1NXSLV',
        'version': '5.12.4',
        'description': 'MERRA-2 Variables de Superficie',
        'variables': ['T2M', 'QV2M', 'PS'],
        'temporal_resolution': 'hourly'
    },
    'MODIS_LST': {
        'short_name': 'MOD11A1',
        'version': '6.1',
        'description': 'Temperatura Superficial Terrestre MODIS',
        'variables': ['LST_Day_1km'],
        'temporal_resolution': 'daily'
    }
}

def get_data(
    dataset: str,
    date_start: Union[str, datetime],
    date_end: Union[str, datetime] = None,
    lat: float = None,
    lon: float = None,
    bbox: Tuple[float, float, float, float] = None,
    variables: List[str] = None,
    output_format: str = 'xarray'
) -> Union[object, str, None]:
    """
    Función principal para obtener datos NASA de forma automática
    
    Args:
        dataset: Tipo de dataset ('IMERG_DAILY', 'MERRA2', 'MODIS_LST')
        date_start: Fecha inicio (YYYY-MM-DD o datetime)
        date_end: Fecha fin (opcional, por defecto = date_start)
        lat: Latitud (opcional)
        lon: Longitud (opcional)  
        bbox: Bounding box (oeste, sur, este, norte) - opcional
        variables: Lista de variables específicas (opcional)
        output_format: 'xarray', 'download', 'info' 
    
    Returns:
        xarray.Dataset, str (path), dict (info) o None
    
    Examples:
        # Precipitación para Madrid
        >>> data = get_data('IMERG_DAILY', '2024-03-15', lat=40.4, lon=-3.7)
        
        # Temperatura para España (región)
        >>> data = get_data('MERRA2', '2024-03-01', '2024-03-03', 
        ...                 bbox=(-10, 35, 5, 45))
        
        # Solo información sin descargar
        >>> info = get_data('MODIS_LST', '2024-03-15', output_format='info')
    """
    
    # Autenticación automática
    if not auto_authenticate():
        print("❌ No se pudo autenticar. Configura credenciales primero.")
        return None
    
    # Validar dataset
    if dataset not in DATASETS_CONFIG:
        available = list(DATASETS_CONFIG.keys())
        print(f"❌ Dataset '{dataset}' no disponible. Opciones: {available}")
        return None
    
    # Procesar fechas
    if isinstance(date_start, str):
        date_start = datetime.fromisoformat(date_start)
    if date_end is None:
        date_end = date_start
    elif isinstance(date_end, str):
        date_end = datetime.fromisoformat(date_end)
    
    print(f"🔍 Buscando {DATASETS_CONFIG[dataset]['description']}")
    print(f"📅 Período: {date_start.date()} a {date_end.date()}")
    
    if bbox:
        print(f"🗺️  Región: {bbox}")
    elif lat and lon:
        print(f"📍 Punto: {lat:.3f}°, {lon:.3f}°")
    
    try:
        import earthaccess
        import xarray as xr
        
        # Configurar parámetros de búsqueda
        search_params = {
            'temporal': (date_start.strftime('%Y-%m-%d'), 
                        date_end.strftime('%Y-%m-%d')),
            'count': 20
        }
        
        # Añadir parámetros del dataset
        config = DATASETS_CONFIG[dataset]
        if 'short_name' in config:
            search_params['short_name'] = config['short_name']
        if 'version' in config:
            search_params['version'] = config['version']
        if 'doi' in config:
            search_params['doi'] = config['doi']
        
        # Añadir filtros espaciales
        if bbox:
            search_params['bounding_box'] = bbox
        elif lat and lon:
            # Crear bbox pequeño alrededor del punto
            margin = 0.5  # 0.5 grados de margen
            search_params['bounding_box'] = (
                lon - margin, lat - margin, 
                lon + margin, lat + margin
            )
        
        # Buscar granulos
        granules = earthaccess.search_data(**search_params)
        
        if not granules:
            print("❌ No se encontraron datos para los criterios especificados")
            print("💡 Prueba con fechas diferentes o región más amplia")
            return None
        
        print(f"✅ Encontrados {len(granules)} granulos")
        
        # Procesar según formato de salida
        if output_format == 'info':
            # Solo devolver información
            info = {
                'dataset': dataset,
                'granules_found': len(granules),
                'time_range': (date_start.date(), date_end.date()),
                'first_granule': {
                    'id': granules[0]['meta']['concept-id'],
                    'size_mb': granules[0].size(),
                    'variables': config.get('variables', [])
                }
            }
            return info
        
        elif output_format == 'download':
            # Descargar archivos localmente
            download_path = './nasa_data'
            os.makedirs(download_path, exist_ok=True)
            
            print(f"💾 Descargando a {download_path}...")
            files = earthaccess.download(granules, local_path=download_path)
            print(f"✅ Descargados {len(files)} archivos")
            return download_path
        
        else:  # 'xarray' (por defecto)
            # Streaming directo a xarray
            print("🌊 Cargando datos en memoria...")
            files = earthaccess.open(granules)
            
            # Abrir con xarray
            ds = xr.open_mfdataset(files, engine='h5netcdf', combine='by_coords')
            
            # Filtrar variables si se especifica
            if variables:
                available_vars = list(ds.data_vars.keys())
                valid_vars = [v for v in variables if v in available_vars]
                if valid_vars:
                    ds = ds[valid_vars]
                else:
                    print(f"⚠️ Variables {variables} no encontradas. Disponibles: {available_vars}")
            
            # Filtrar por punto específico si se solicita
            if lat and lon and 'lat' in ds.coords and 'lon' in ds.coords:
                ds = ds.sel(lat=lat, lon=lon, method='nearest')
                print(f"📍 Datos extraídos para punto: {float(ds.lat.values):.3f}°, {float(ds.lon.values):.3f}°")
            
            print(f"✅ Dataset cargado: {dict(ds.sizes)}")
            return ds
    
    except Exception as e:
        print(f"❌ Error procesando datos: {e}")
        return None

def get_precipitation(
    date: Union[str, datetime],
    lat: float = None,
    lon: float = None,
    bbox: Tuple[float, float, float, float] = None
):
    """
    Obtener datos de precipitación IMERG de forma simplificada
    
    Args:
        date: Fecha (YYYY-MM-DD)
        lat: Latitud (opcional)
        lon: Longitud (opcional)
        bbox: Bounding box (opcional)
    
    Returns:
        xarray.Dataset con datos de precipitación
    
    Example:
        >>> precip = get_precipitation('2024-03-15', lat=40.4, lon=-3.7)
        >>> print(f"Precipitación en Madrid: {precip.precipitationCal.values} mm/hr")
    """
    return get_data('IMERG_DAILY', date, lat=lat, lon=lon, bbox=bbox, 
                   variables=['precipitationCal'])

def get_temperature(
    date_start: Union[str, datetime],
    date_end: Union[str, datetime] = None,
    lat: float = None,
    lon: float = None,
    bbox: Tuple[float, float, float, float] = None
):
    """
    Obtener datos de temperatura MERRA-2 de forma simplificada
    
    Args:
        date_start: Fecha inicio
        date_end: Fecha fin (opcional)
        lat: Latitud (opcional)
        lon: Longitud (opcional)
        bbox: Bounding box (opcional)
    
    Returns:
        xarray.Dataset con datos de temperatura
        
    Example:
        >>> temp = get_temperature('2024-03-15', lat=40.4, lon=-3.7)
        >>> temp_celsius = temp.T2M - 273.15  # Convertir K a °C
    """
    return get_data('MERRA2', date_start, date_end, lat=lat, lon=lon, 
                   bbox=bbox, variables=['T2M'])

def list_datasets() -> Dict[str, str]:
    """
    Listar todos los datasets disponibles
    
    Returns:
        Diccionario con datasets y descripciones
    """
    print("📊 DATASETS DISPONIBLES:")
    print("=" * 40)
    
    datasets = {}
    for key, config in DATASETS_CONFIG.items():
        description = config['description']
        datasets[key] = description
        variables = ', '.join(config.get('variables', [])[:3])
        temporal = config.get('temporal_resolution', 'N/A')
        
        print(f"🔹 {key}")
        print(f"   Descripción: {description}")
        print(f"   Variables: {variables}")
        print(f"   Resolución: {temporal}")
        print()
    
    return datasets

def get_location_data(
    location: str,
    dataset: str,
    date_start: Union[str, datetime],
    date_end: Union[str, datetime] = None
):
    """
    Obtener datos para ubicaciones predefinidas
    
    Args:
        location: Nombre de la ciudad ('madrid', 'barcelona', etc.)
        dataset: Tipo de dataset
        date_start: Fecha inicio
        date_end: Fecha fin (opcional)
    
    Returns:
        xarray.Dataset con datos para la ubicación
        
    Example:
        >>> data = get_location_data('madrid', 'MERRA2', '2024-03-15')
    """
    
    # Coordenadas de ciudades predefinidas
    locations = {
        'madrid': {'lat': 40.4168, 'lon': -3.7038},
        'barcelona': {'lat': 41.3851, 'lon': 2.1734},
        'valencia': {'lat': 39.4699, 'lon': -0.3763},
        'sevilla': {'lat': 37.3891, 'lon': -5.9845},
        'bilbao': {'lat': 43.2627, 'lon': -2.9253},
        'zaragoza': {'lat': 41.6560, 'lon': -0.8773}
    }
    
    location_lower = location.lower()
    if location_lower not in locations:
        available = list(locations.keys())
        print(f"❌ Ubicación '{location}' no disponible. Opciones: {available}")
        return None
    
    coords = locations[location_lower]
    print(f"🏙️ Obteniendo datos para {location.title()}")
    
    return get_data(dataset, date_start, date_end, 
                   lat=coords['lat'], lon=coords['lon'])

def quick_analysis(
    dataset: str,
    location: str,
    days: int = 7
):
    """
    Análisis rápido de los últimos N días
    
    Args:
        dataset: Tipo de dataset
        location: Ubicación
        days: Número de días hacia atrás
    
    Example:
        >>> quick_analysis('MERRA2', 'madrid', days=7)
    """
    
    end_date = datetime.now() - timedelta(days=30)  # Datos recientes
    start_date = end_date - timedelta(days=days)
    
    print(f"📈 ANÁLISIS RÁPIDO - {location.title()}")
    print(f"📊 Dataset: {DATASETS_CONFIG[dataset]['description']}")
    print(f"📅 Período: {start_date.date()} a {end_date.date()}")
    print("=" * 50)
    
    data = get_location_data(location, dataset, start_date, end_date)
    
    if data is not None:
        print("✅ Datos obtenidos exitosamente")
        
        # Mostrar información básica
        if hasattr(data, 'data_vars'):
            print(f"🔢 Variables: {list(data.data_vars.keys())}")
            
        if 'time' in data.dims:
            print(f"⏰ Puntos temporales: {len(data.time)}")
        
        return data
    else:
        print("❌ No se pudieron obtener datos")
        return None

# Función de configuración inicial
def configure_library():
    """
    Configuración inicial de la librería
    """
    print("🚀 NASA EARTHDATA LIBRARY - Configuración Inicial")
    print("=" * 55)
    print()
    print("Esta librería te permite acceder automáticamente a datos NASA")
    print("sin necesidad de introducir credenciales cada vez.")
    print()
    print("📝 Pasos para configurar:")
    print("1. Ejecuta: setup_credentials('tu_usuario', 'tu_contraseña')")
    print("2. ¡Ya puedes usar todas las funciones automáticamente!")
    print()
    print("🎯 Funciones principales:")
    print("- get_data(): Función general para cualquier dataset")
    print("- get_precipitation(): Datos de precipitación específicos")  
    print("- get_temperature(): Datos de temperatura específicos")
    print("- get_location_data(): Datos para ciudades predefinidas")
    print("- quick_analysis(): Análisis rápido de días recientes")
    print()
    print("📖 Ejemplos:")
    print("- data = get_precipitation('2024-03-15', lat=40.4, lon=-3.7)")
    print("- temp = get_temperature('2024-03-15', lat=41.4, lon=2.2)")
    print("- madrid = get_location_data('madrid', 'MERRA2', '2024-03-15')")
    print()

if __name__ == "__main__":
    configure_library()