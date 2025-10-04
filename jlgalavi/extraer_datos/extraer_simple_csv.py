#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor Simple NASA -> CSV
Código muy simple para extraer y guardar datos NASA directamente en CSV
"""

import csv
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Importar librería NASA
sys.path.append(str(Path(__file__).parent.parent))
from nasa_earthdata_lib import get_data, auto_authenticate

def extraer_temperatura_simple_csv(
    archivo_csv="datos_temperatura_simple.csv",
    ciudad="madrid",
    dias=5
):
    """
    Extrae temperatura NASA y guarda directamente en CSV
    
    Args:
        archivo_csv: Nombre del archivo CSV a crear
        ciudad: Ciudad para extraer datos
        dias: Número de días hacia atrás
    
    Returns:
        bool: True si fue exitoso
    """
    
    print(f"📊 EXTRAYENDO DATOS PARA {ciudad.upper()}")
    print(f"💾 Guardando en: {archivo_csv}")
    print("-" * 40)
    
    # Verificar autenticación
    if not auto_authenticate():
        print("❌ Error de autenticación NASA")
        return False
    
    # Coordenadas de ciudades
    coordenadas = {
        'madrid': {'lat': 40.4168, 'lon': -3.7038},
        'barcelona': {'lat': 41.3851, 'lon': 2.1734},
        'valencia': {'lat': 39.4699, 'lon': -0.3763},
        'sevilla': {'lat': 37.3891, 'lon': -5.9845}
    }
    
    if ciudad.lower() not in coordenadas:
        print(f"❌ Ciudad {ciudad} no disponible")
        return False
    
    coords = coordenadas[ciudad.lower()]
    
    # Calcular fechas (datos disponibles hace 60 días)
    fecha_fin = datetime.now() - timedelta(days=60)
    fecha_inicio = fecha_fin - timedelta(days=dias)
    
    print(f"📅 Fechas: {fecha_inicio.date()} a {fecha_fin.date()}")
    
    try:
        # Crear directorio si no existe
        Path(archivo_csv).parent.mkdir(parents=True, exist_ok=True)
        
        # Obtener datos NASA
        data = get_data(
            dataset='MERRA2',
            date_start=fecha_inicio.strftime('%Y-%m-%d'),
            date_end=fecha_fin.strftime('%Y-%m-%d'),
            lat=coords['lat'],
            lon=coords['lon']
        )
        
        if data is None:
            print("❌ No se pudieron obtener datos NASA")
            return False
        
        # Crear archivo CSV
        with open(archivo_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escribir cabecera
            writer.writerow([
                'fecha', 'hora', 'ciudad', 'latitud', 'longitud', 
                'temperatura_celsius', 'descripcion_completa'
            ])
            
            registros = 0
            
            # Procesar cada timestamp
            for i in range(len(data.time)):
                # Extraer valores
                timestamp = data.time.isel(time=i).values
                temp_kelvin = float(data.T2M.isel(time=i).values)
                temp_celsius = temp_kelvin - 273.15
                
                # Convertir timestamp
                dt = datetime.fromisoformat(str(timestamp)[:19])
                fecha = dt.strftime('%Y-%m-%d')
                hora = dt.strftime('%H:%M:%S')
                
                # Coordenadas reales
                lat_real = float(data.lat.values)
                lon_real = float(data.lon.values)
                
                # Crear descripción completa (como pediste)
                descripcion = (
                    f"Temperatura día {fecha} a la hora {hora} "
                    f"de la latitud {lat_real:.3f} y longitud {lon_real:.3f} : "
                    f"{temp_celsius:.2f}°C"
                )
                
                # Escribir fila
                writer.writerow([
                    fecha, hora, ciudad, lat_real, lon_real, 
                    round(temp_celsius, 2), descripcion
                ])
                
                registros += 1
                
                # Mostrar progreso
                if registros % 50 == 0:
                    print(f"   📊 {registros} registros procesados...")
            
            print(f"✅ {registros} registros guardados en {archivo_csv}")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def extraer_multiples_ciudades_csv(
    archivo_csv="datos_multiples_ciudades.csv",
    ciudades=['madrid', 'barcelona', 'valencia'],
    dias=3
):
    """
    Extrae datos de múltiples ciudades en un solo CSV
    
    Args:
        archivo_csv: Archivo CSV de salida
        ciudades: Lista de ciudades
        dias: Días de datos a extraer
    """
    
    print(f"🌍 EXTRACCIÓN MÚLTIPLES CIUDADES")
    print(f"🏙️ Ciudades: {', '.join(ciudades)}")
    print(f"💾 Archivo: {archivo_csv}")
    print("-" * 50)
    
    # Crear directorio si no existe
    Path(archivo_csv).parent.mkdir(parents=True, exist_ok=True)
    
    # Crear CSV con cabecera
    with open(archivo_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'ciudad', 'fecha', 'hora', 'latitud', 'longitud', 
            'temperatura_celsius', 'temperatura_kelvin', 'descripcion'
        ])
    
    total_registros = 0
    
    # Procesar cada ciudad
    for ciudad in ciudades:
        print(f"\n🔍 Procesando {ciudad.title()}...")
        
        # Extraer datos temporalmente
        archivo_temp = f"temp_{ciudad}.csv"
        
        if extraer_temperatura_simple_csv(archivo_temp, ciudad, dias):
            # Leer archivo temporal y añadir al archivo principal
            with open(archivo_temp, 'r', encoding='utf-8') as temp_file:
                reader = csv.reader(temp_file)
                next(reader)  # Saltar cabecera
                
                with open(archivo_csv, 'a', newline='', encoding='utf-8') as main_file:
                    writer = csv.writer(main_file)
                    
                    for fila in reader:
                        # Reorganizar datos para el archivo principal
                        fecha, hora, ciudad_nombre, lat, lon, temp_c, descripcion = fila
                        temp_k = float(temp_c) + 273.15
                        
                        writer.writerow([
                            ciudad_nombre, fecha, hora, lat, lon, 
                            temp_c, round(temp_k, 2), descripcion
                        ])
                        total_registros += 1
            
            # Eliminar archivo temporal
            Path(archivo_temp).unlink(missing_ok=True)
    
    print(f"\n🎉 ¡Extracción completada!")
    print(f"📊 Total registros: {total_registros}")
    print(f"📁 Archivo final: {archivo_csv}")
    
    # Mostrar muestra de datos
    print(f"\n📋 MUESTRA DE DATOS:")
    print("-" * 30)
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        for i, linea in enumerate(f):
            if i < 3:  # Primeras 3 líneas
                print(f"  {linea.strip()}")
    
    return total_registros > 0

def leer_csv_ejemplo(archivo_csv):
    """
    Lee y muestra contenido del CSV generado
    
    Args:
        archivo_csv: Archivo a leer
    """
    
    if not Path(archivo_csv).exists():
        print(f"❌ Archivo {archivo_csv} no encontrado")
        return
    
    print(f"📖 LEYENDO ARCHIVO: {archivo_csv}")
    print("=" * 50)
    
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Leer cabecera
        headers = next(reader)
        print(f"📊 Cabeceras: {', '.join(headers)}")
        print()
        
        # Leer primeras filas
        contador = 0
        for fila in reader:
            contador += 1
            if contador <= 5:
                print(f"Fila {contador}: {fila}")
            else:
                break
        
        print(f"\n📈 Mostrando {min(contador, 5)} de {contador} registros totales")

def main():
    """
    Programa principal - ejemplos de uso
    """
    
    print("🛰️ EXTRACTOR SIMPLE NASA -> CSV")
    print("=" * 40)
    
    # Ejemplo 1: Una ciudad
    print("\n1️⃣ EXTRACCIÓN CIUDAD INDIVIDUAL")
    exito1 = extraer_temperatura_simple_csv(
        archivo_csv="madrid_temperatura.csv",
        ciudad="madrid",
        dias=3
    )
    
    if exito1:
        leer_csv_ejemplo("madrid_temperatura.csv")
    
    # Ejemplo 2: Múltiples ciudades
    print("\n\n2️⃣ EXTRACCIÓN MÚLTIPLES CIUDADES")
    exito2 = extraer_multiples_ciudades_csv(
        archivo_csv="espana_temperatura.csv",
        ciudades=['madrid', 'barcelona', 'valencia'],
        dias=2
    )
    
    if exito2:
        leer_csv_ejemplo("espana_temperatura.csv")
    
    print(f"\n🎓 RESUMEN:")
    print(f"✅ Los datos están guardados en archivos CSV")
    print(f"✅ Listos para análisis de probabilidades")
    print(f"✅ Sin carga en memoria RAM - procesamiento directo")

if __name__ == "__main__":
    main()