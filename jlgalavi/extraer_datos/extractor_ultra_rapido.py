#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor Ultra-Rápido NASA -> CSV
Versión optimizada para extraer datos NASA directamente sin RAM
"""

import csv
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Importar librería NASA
sys.path.append(str(Path(__file__).parent.parent))
from nasa_earthdata_lib import get_data, auto_authenticate

def extraer_datos_ultra_rapido(
    archivo_salida="datos_nasa_rapido.csv",
    ciudades=['madrid'],
    dias=5,
    variables=['temperatura']
):
    """
    Extractor ultra-rápido de datos NASA a CSV
    
    Args:
        archivo_salida: Archivo CSV de salida
        ciudades: Lista de ciudades a procesar
        dias: Días históricos a extraer
        variables: Variables a extraer ['temperatura', 'precipitacion']
    
    Returns:
        tuple: (éxito, número_registros)
    """
    
    print(f"⚡ EXTRACTOR ULTRA-RÁPIDO NASA -> CSV")
    print(f"📁 Archivo: {archivo_salida}")
    print(f"🏙️ Ciudades: {', '.join(ciudades)}")
    print(f"📅 Días: {dias}")
    print("-" * 50)
    
    # Verificar autenticación
    if not auto_authenticate():
        print("❌ Error autenticación NASA")
        return False, 0
    
    # Coordenadas ciudades
    coords = {
        'madrid': (40.4168, -3.7038),
        'barcelona': (41.3851, 2.1734), 
        'valencia': (39.4699, -0.3763),
        'sevilla': (37.3891, -5.9845),
        'bilbao': (43.2627, -2.9253),
        'zaragoza': (41.6560, -0.8773)
    }
    
    # Fechas
    fecha_fin = datetime.now() - timedelta(days=60)
    fecha_inicio = fecha_fin - timedelta(days=dias)
    
    total_registros = 0
    
    try:
        # Crear CSV con cabecera
        Path(archivo_salida).parent.mkdir(parents=True, exist_ok=True)
        
        with open(archivo_salida, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Cabecera dinámica según variables
            headers = ['ciudad', 'fecha', 'hora', 'lat', 'lon']
            
            if 'temperatura' in variables:
                headers.extend(['temp_celsius', 'temp_kelvin'])
            if 'precipitacion' in variables:
                headers.extend(['precipitacion_mm'])
                
            headers.append('descripcion')
            writer.writerow(headers)
            
            # Procesar cada ciudad
            for ciudad in ciudades:
                if ciudad.lower() not in coords:
                    print(f"   ⚠️ {ciudad} no disponible")
                    continue
                    
                lat, lon = coords[ciudad.lower()]
                print(f"\n🔍 {ciudad.title()}...")
                
                # Obtener datos NASA
                data = get_data(
                    dataset='MERRA2',
                    date_start=fecha_inicio.strftime('%Y-%m-%d'),
                    date_end=fecha_fin.strftime('%Y-%m-%d'),
                    lat=lat,
                    lon=lon
                )
                
                if data is None:
                    print(f"   ❌ Sin datos para {ciudad}")
                    continue
                
                # Procesar cada timestamp directamente
                for i in range(len(data.time)):
                    # Extraer timestamp
                    timestamp = data.time.isel(time=i).values
                    dt = datetime.fromisoformat(str(timestamp)[:19])
                    fecha = dt.strftime('%Y-%m-%d')
                    hora = dt.strftime('%H:%M:%S')
                    
                    # Coordenadas reales
                    lat_real = float(data.lat.values)
                    lon_real = float(data.lon.values)
                    
                    # Preparar fila
                    fila = [ciudad, fecha, hora, lat_real, lon_real]
                    
                    # Añadir variables solicitadas
                    descripciones = []
                    
                    if 'temperatura' in variables and 'T2M' in data.data_vars:
                        temp_k = float(data.T2M.isel(time=i).values)
                        temp_c = temp_k - 273.15
                        fila.extend([round(temp_c, 2), round(temp_k, 2)])
                        descripciones.append(
                            f"Temperatura día {fecha} a la hora {hora} "
                            f"de la latitud {lat_real:.3f} y longitud {lon_real:.3f} : {temp_c:.2f}°C"
                        )
                    
                    if 'precipitacion' in variables and 'QV2M' in data.data_vars:
                        precip = float(data.QV2M.isel(time=i).values) * 1000  # g/kg
                        fila.append(round(precip, 3))
                        descripciones.append(
                            f"Humedad específica día {fecha} a la hora {hora} "
                            f"de la latitud {lat_real:.3f} y longitud {lon_real:.3f} : {precip:.3f} g/kg"
                        )
                    
                    # Descripción final
                    descripcion_completa = " | ".join(descripciones)
                    fila.append(descripcion_completa)
                    
                    # Escribir al CSV inmediatamente
                    writer.writerow(fila)
                    total_registros += 1
                    
                    # Progreso cada 24 registros (1 día)
                    if total_registros % 24 == 0:
                        print(f"   📊 {total_registros} registros...")
                
                print(f"   ✅ {ciudad.title()} completado")
        
        print(f"\n🎉 ¡Extracción completada!")
        print(f"📊 Total registros: {total_registros}")
        print(f"📁 Archivo: {archivo_salida}")
        
        return True, total_registros
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, 0

def mostrar_muestra_csv(archivo_csv, lineas=5):
    """
    Muestra una muestra del CSV generado
    
    Args:
        archivo_csv: Archivo a mostrar
        lineas: Número de líneas a mostrar
    """
    
    if not Path(archivo_csv).exists():
        print(f"❌ Archivo {archivo_csv} no encontrado")
        return
    
    print(f"\n📋 MUESTRA DEL ARCHIVO: {archivo_csv}")
    print("-" * 60)
    
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Cabecera
        headers = next(reader)
        print(f"📊 Cabeceras ({len(headers)}): {', '.join(headers[:3])}...")
        print()
        
        # Primeras filas
        for i, fila in enumerate(reader):
            if i < lineas:
                ciudad = fila[0]
                fecha = fila[1]
                temp = fila[5] if len(fila) > 5 else 'N/A'
                print(f"  {i+1}. {ciudad} | {fecha} | {temp}°C")
            else:
                break
    
    # Tamaño del archivo
    size_kb = Path(archivo_csv).stat().st_size / 1024
    print(f"\n📈 Archivo: {size_kb:.1f} KB")

def generar_datos_entrenamiento(
    archivo_salida="datos_entrenamiento_nasa.csv",
    ciudades=['madrid', 'barcelona', 'valencia', 'sevilla'],
    dias_historicos=20
):
    """
    Genera dataset específico para entrenamiento de modelos
    
    Args:
        archivo_salida: Archivo CSV para entrenamiento
        ciudades: Ciudades a incluir
        dias_historicos: Días de historia
    
    Returns:
        bool: Éxito de la operación
    """
    
    print(f"🤖 GENERANDO DATASET DE ENTRENAMIENTO")
    print(f"🎯 Objetivo: Datos para entrenar modelos de probabilidad")
    print("-" * 55)
    
    exito, registros = extraer_datos_ultra_rapido(
        archivo_salida=archivo_salida,
        ciudades=ciudades,
        dias=dias_historicos,
        variables=['temperatura']
    )
    
    if exito:
        mostrar_muestra_csv(archivo_salida)
        
        print(f"\n🎓 DATOS LISTOS PARA ENTRENAMIENTO:")
        print(f"✅ {registros} registros de temperatura")
        print(f"✅ {len(ciudades)} ciudades incluidas")
        print(f"✅ {dias_historicos} días de historia")
        print(f"✅ Formato CSV optimizado para ML/probabilidades")
        
        return True
    else:
        print("❌ Error generando dataset de entrenamiento")
        return False

def main():
    """
    Programa principal
    """
    
    print("🛰️ EXTRACTOR NASA ULTRA-RÁPIDO")
    print("=" * 40)
    
    # Ejemplo 1: Extracción básica
    print("\n1️⃣ EXTRACCIÓN BÁSICA")
    exito1, registros1 = extraer_datos_ultra_rapido(
        archivo_salida="temp_basico.csv",
        ciudades=['madrid'],
        dias=3,
        variables=['temperatura']
    )
    
    if exito1:
        mostrar_muestra_csv("temp_basico.csv")
    
    # Ejemplo 2: Dataset de entrenamiento
    print("\n\n2️⃣ DATASET DE ENTRENAMIENTO")
    exito2 = generar_datos_entrenamiento(
        archivo_salida="dataset_entrenamiento.csv",
        ciudades=['madrid', 'barcelona', 'valencia'],
        dias_historicos=7
    )
    
    print(f"\n🎯 ARCHIVOS GENERADOS:")
    for archivo in ['temp_basico.csv', 'dataset_entrenamiento.csv']:
        if Path(archivo).exists():
            size = Path(archivo).stat().st_size / 1024
            print(f"  📁 {archivo}: {size:.1f} KB")
    
    print(f"\n✅ ¡Listo para calcular probabilidades y entrenar modelos!")

if __name__ == "__main__":
    main()