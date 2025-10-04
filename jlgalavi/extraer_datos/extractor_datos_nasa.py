#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de Datos NASA - CSV Directo
Extrae y guarda datos NASA directamente en CSV sin cargar en memoria RAM
"""

import os
import csv
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

# Añadir directorio padre para importar la librería NASA
sys.path.append(str(Path(__file__).parent.parent))

try:
    from nasa_earthdata_lib import auto_authenticate, DATASETS_CONFIG
    print("✅ Librería NASA cargada")
except ImportError as e:
    print(f"❌ Error importando librería NASA: {e}")
    print("💡 Asegúrate de que nasa_earthdata_lib.py esté disponible")
    exit(1)

class ExtractorDatosNASA:
    """
    Extractor eficiente de datos NASA directamente a CSV
    """
    
    def __init__(self, archivo_salida: str = "datos_nasa.csv"):
        """
        Inicializa el extractor
        
        Args:
            archivo_salida: Nombre del archivo CSV de salida
        """
        self.archivo_salida = archivo_salida
        self.datos_extraidos = 0
        self.csv_file = None
        self.csv_writer = None
        
        # Crear directorio si no existe
        Path(archivo_salida).parent.mkdir(parents=True, exist_ok=True)
        
    def inicializar_csv(self, headers: List[str]):
        """
        Inicializa el archivo CSV con cabeceras
        
        Args:
            headers: Lista de cabeceras para el CSV
        """
        self.csv_file = open(self.archivo_salida, 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(headers)
        print(f"✅ Archivo CSV inicializado: {self.archivo_salida}")
        
    def escribir_fila(self, datos: List):
        """
        Escribe una fila de datos al CSV
        
        Args:
            datos: Lista con los datos de la fila
        """
        if self.csv_writer:
            self.csv_writer.writerow(datos)
            self.datos_extraidos += 1
            
    def cerrar_csv(self):
        """
        Cierra el archivo CSV
        """
        if self.csv_file:
            self.csv_file.close()
            print(f"✅ Archivo CSV cerrado. Total datos extraídos: {self.datos_extraidos}")
            
    def extraer_temperatura_streaming(
        self, 
        dataset: str = 'MERRA2',
        fecha_inicio: str = None,
        fecha_fin: str = None,
        ubicaciones: List[Dict] = None,
        intervalo_horas: int = 6
    ):
        """
        Extrae datos de temperatura de forma streaming (sin cargar todo en RAM)
        
        Args:
            dataset: Tipo de dataset NASA
            fecha_inicio: Fecha inicio (YYYY-MM-DD)
            fecha_fin: Fecha fin (YYYY-MM-DD)
            ubicaciones: Lista de ubicaciones [{'nombre': 'madrid', 'lat': 40.4, 'lon': -3.7}]
            intervalo_horas: Intervalo de horas para extraer datos
        """
        
        print(f"🛰️ EXTRACCIÓN STREAMING DE DATOS NASA")
        print(f"📊 Dataset: {dataset}")
        print(f"📅 Período: {fecha_inicio} a {fecha_fin}")
        print("-" * 50)
        
        # Verificar autenticación
        if not auto_authenticate():
            print("❌ No se pudo autenticar con NASA")
            return False
            
        # Ubicaciones por defecto si no se proporcionan
        if ubicaciones is None:
            ubicaciones = [
                {'nombre': 'madrid', 'lat': 40.4168, 'lon': -3.7038},
                {'nombre': 'barcelona', 'lat': 41.3851, 'lon': 2.1734},
                {'nombre': 'valencia', 'lat': 39.4699, 'lon': -0.3763},
                {'nombre': 'sevilla', 'lat': 37.3891, 'lon': -5.9845}
            ]
            
        # Fechas por defecto (últimos 30 días disponibles)
        if not fecha_inicio:
            fecha_fin_dt = datetime.now() - timedelta(days=60)
            fecha_inicio_dt = fecha_fin_dt - timedelta(days=30)
            fecha_inicio = fecha_inicio_dt.strftime('%Y-%m-%d')
            fecha_fin = fecha_fin_dt.strftime('%Y-%m-%d')
            
        print(f"📍 Ubicaciones: {[ub['nombre'] for ub in ubicaciones]}")
        
        # Inicializar CSV con cabeceras
        headers = [
            'fecha', 'hora', 'ubicacion', 'latitud', 'longitud', 
            'temperatura_celsius', 'temperatura_kelvin', 'fuente_dato'
        ]
        self.inicializar_csv(headers)
        
        try:
            import earthaccess
            import xarray as xr
            
            # Procesar cada ubicación por separado (streaming)
            for ubicacion in ubicaciones:
                nombre = ubicacion['nombre']
                lat = ubicacion['lat']
                lon = ubicacion['lon']
                
                print(f"\n🔍 Procesando {nombre.title()}...")
                
                # Configurar parámetros de búsqueda
                search_params = {
                    'temporal': (fecha_inicio, fecha_fin),
                    'bounding_box': (lon - 0.5, lat - 0.5, lon + 0.5, lat + 0.5),
                    'count': 50  # Limitar número de granulos
                }
                
                # Añadir configuración del dataset
                config = DATASETS_CONFIG[dataset]
                if 'short_name' in config:
                    search_params['short_name'] = config['short_name']
                if 'version' in config:
                    search_params['version'] = config['version']
                
                # Buscar granulos
                granules = earthaccess.search_data(**search_params)
                
                if not granules:
                    print(f"   ❌ No se encontraron datos para {nombre}")
                    continue
                    
                print(f"   ✅ Encontrados {len(granules)} granulos para {nombre}")
                
                # Procesar granulos de forma streaming
                for i, granule in enumerate(granules):
                    try:
                        print(f"   📊 Procesando granulo {i+1}/{len(granules)} para {nombre}...")
                        
                        # Abrir granulo individual (minimizar uso RAM)
                        files = earthaccess.open([granule])
                        
                        if not files:
                            continue
                            
                        # Cargar solo el granulo actual
                        ds = xr.open_dataset(files[0], engine='h5netcdf')
                        
                        # Filtrar por ubicación específica
                        if 'lat' in ds.coords and 'lon' in ds.coords:
                            ds_punto = ds.sel(lat=lat, lon=lon, method='nearest')
                            
                            # Extraer datos de temperatura
                            if 'T2M' in ds_punto.data_vars:
                                # Procesar cada timestamp
                                for time_idx in range(len(ds_punto.time)):
                                    # Extraer valores específicos
                                    timestamp = ds_punto.time.isel(time=time_idx).values
                                    temp_kelvin = float(ds_punto.T2M.isel(time=time_idx).values)
                                    temp_celsius = temp_kelvin - 273.15
                                    
                                    # Convertir timestamp a fecha y hora
                                    dt = datetime.fromisoformat(str(timestamp)[:19])
                                    fecha = dt.strftime('%Y-%m-%d')
                                    hora = dt.strftime('%H:%M:%S')
                                    
                                    # Coordenadas reales del punto más cercano
                                    lat_real = float(ds_punto.lat.values)
                                    lon_real = float(ds_punto.lon.values)
                                    
                                    # Escribir fila al CSV inmediatamente
                                    fila_datos = [
                                        fecha, hora, nombre, lat_real, lon_real,
                                        round(temp_celsius, 2), round(temp_kelvin, 2),
                                        f"{dataset}_{granule['meta']['concept-id'][:8]}"
                                    ]
                                    
                                    self.escribir_fila(fila_datos)
                                    
                                    # Progreso cada 100 registros
                                    if self.datos_extraidos % 100 == 0:
                                        print(f"   📈 {self.datos_extraidos} registros extraídos...")
                        
                        # Liberar memoria del dataset
                        ds.close()
                        
                    except Exception as e:
                        print(f"   ⚠️ Error procesando granulo {i+1}: {str(e)[:50]}")
                        continue
                        
                print(f"   ✅ {nombre.title()} completado")
                
        except Exception as e:
            print(f"❌ Error en extracción: {e}")
            return False
        finally:
            # Cerrar CSV siempre
            self.cerrar_csv()
            
        return True

def extraer_datos_rapido(
    archivo_salida: str = "extraer_datos/datos_temperatura.csv",
    dias_historicos: int = 15,
    ciudades: List[str] = None
):
    """
    Función rápida para extraer datos de temperatura
    
    Args:
        archivo_salida: Archivo CSV de salida
        dias_historicos: Días hacia atrás para extraer
        ciudades: Lista de ciudades ['madrid', 'barcelona', ...]
    
    Returns:
        bool: True si la extracción fue exitosa
    """
    
    print("🚀 EXTRACCIÓN RÁPIDA DE DATOS TEMPERATURA NASA")
    print("=" * 50)
    
    # Ciudades por defecto
    if ciudades is None:
        ciudades = ['madrid', 'barcelona', 'valencia', 'sevilla']
    
    # Mapear ciudades a coordenadas
    coordenadas_ciudades = {
        'madrid': {'lat': 40.4168, 'lon': -3.7038},
        'barcelona': {'lat': 41.3851, 'lon': 2.1734},
        'valencia': {'lat': 39.4699, 'lon': -0.3763},
        'sevilla': {'lat': 37.3891, 'lon': -5.9845},
        'bilbao': {'lat': 43.2627, 'lon': -2.9253},
        'zaragoza': {'lat': 41.6560, 'lon': -0.8773}
    }
    
    # Convertir ciudades a ubicaciones
    ubicaciones = []
    for ciudad in ciudades:
        if ciudad.lower() in coordenadas_ciudades:
            coords = coordenadas_ciudades[ciudad.lower()]
            ubicaciones.append({
                'nombre': ciudad.lower(),
                'lat': coords['lat'],
                'lon': coords['lon']
            })
    
    # Calcular fechas
    fecha_fin = datetime.now() - timedelta(days=60)  # Datos disponibles
    fecha_inicio = fecha_fin - timedelta(days=dias_historicos)
    
    # Crear extractor
    extractor = ExtractorDatosNASA(archivo_salida)
    
    # Extraer datos
    exito = extractor.extraer_temperatura_streaming(
        dataset='MERRA2',
        fecha_inicio=fecha_inicio.strftime('%Y-%m-%d'),
        fecha_fin=fecha_fin.strftime('%Y-%m-%d'),
        ubicaciones=ubicaciones
    )
    
    if exito:
        print(f"\n🎉 ¡Extracción completada exitosamente!")
        print(f"📁 Archivo generado: {archivo_salida}")
        print(f"📊 Registros extraídos: {extractor.datos_extraidos}")
        
        # Mostrar ejemplo de datos
        if os.path.exists(archivo_salida):
            print(f"\n📋 MUESTRA DEL ARCHIVO CSV:")
            print("-" * 40)
            with open(archivo_salida, 'r', encoding='utf-8') as f:
                for i, linea in enumerate(f):
                    if i < 5:  # Mostrar primeras 5 líneas
                        print(f"  {linea.strip()}")
                    else:
                        break
    else:
        print("❌ Error en la extracción de datos")
    
    return exito

def mostrar_formato_datos():
    """
    Muestra el formato esperado de los datos extraídos
    """
    print("📊 FORMATO DE DATOS EXTRAÍDOS:")
    print("=" * 40)
    print()
    print("🗂️ Estructura del CSV:")
    print("  • fecha: YYYY-MM-DD")
    print("  • hora: HH:MM:SS") 
    print("  • ubicacion: nombre de la ciudad")
    print("  • latitud: coordenada latitud")
    print("  • longitud: coordenada longitud")
    print("  • temperatura_celsius: temperatura en °C")
    print("  • temperatura_kelvin: temperatura en K")
    print("  • fuente_dato: identificador del granulo NASA")
    print()
    print("📝 Ejemplo de cadena generada:")
    print("  'Temperatura día 2025-08-05 a la hora 12:00:00'")
    print("  'de la latitud 40.417 y longitud -3.704 : 26.85°C'")
    print()
    print("💾 Ventajas del streaming:")
    print("  ✅ No carga todos los datos en RAM")
    print("  ✅ Procesa archivo por archivo")
    print("  ✅ Escribe directamente al CSV")
    print("  ✅ Libera memoria continuamente")

def main():
    """
    Programa principal
    """
    mostrar_formato_datos()
    
    print(f"\n🚀 INICIANDO EXTRACCIÓN DE DATOS NASA...")
    
    # Ejemplo de extracción rápida
    exito = extraer_datos_rapido(
        archivo_salida="extraer_datos/temperatura_madrid_bcn.csv",
        dias_historicos=10,
        ciudades=['madrid', 'barcelona']
    )
    
    if exito:
        print(f"\n✅ ¡Proceso completado!")
        print(f"💡 Usa los datos CSV para entrenar modelos de probabilidad")
    else:
        print(f"\n❌ Error en el proceso")

if __name__ == "__main__":
    main()