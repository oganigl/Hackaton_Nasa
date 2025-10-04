#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Código simple para obtener temperatura usando NASA Earthdata
Autor: Sistema de asistencia
Fecha: 2025-10-04
"""

from datetime import datetime, timedelta
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Importar la librería NASA local
try:
    from nasa_earthdata_lib import (
        setup_credentials, 
        get_temperature, 
        get_location_data,
        list_datasets,
        quick_analysis,
        auto_authenticate
    )
    print("✅ Librería NASA cargada correctamente")
except ImportError as e:
    print(f"❌ Error importando librería NASA: {e}")
    print("💡 Asegúrate de que nasa_earthdata_lib.py esté en el mismo directorio")
    exit(1)

def obtener_temperatura_nasa(
    ciudad="madrid", 
    fecha=None, 
    configurar_credenciales=False
):
    """
    Obtiene temperatura usando datos NASA MERRA-2
    
    Args:
        ciudad (str): Ciudad ('madrid', 'barcelona', 'valencia', etc.)
        fecha (str): Fecha en formato 'YYYY-MM-DD' (opcional, usa fecha reciente por defecto)
        configurar_credenciales (bool): True para configurar credenciales nuevas
    
    Returns:
        dict: Datos de temperatura NASA o None si hay error
    """
    
    # Configurar credenciales si es primera vez
    if configurar_credenciales:
        print("🔐 CONFIGURACIÓN DE CREDENCIALES NASA")
        print("=" * 40)
        print("Necesitas una cuenta gratuita en NASA Earthdata:")
        print("👉 https://urs.earthdata.nasa.gov/users/new")
        print()
        
        usuario = input("Usuario NASA Earthdata: ").strip()
        contraseña = input("Contraseña: ").strip()
        
        if usuario and contraseña:
            if setup_credentials(usuario, contraseña):
                print("✅ ¡Credenciales configuradas exitosamente!")
            else:
                print("❌ Error configurando credenciales")
                return None
        else:
            print("❌ Usuario y contraseña son obligatorios")
            return None
    
    # Verificar autenticación
    if not auto_authenticate():
        print("❌ No estás autenticado con NASA")
        print("💡 Ejecuta: obtener_temperatura_nasa(configurar_credenciales=True)")
        return None
    
    # Usar fecha por defecto (hace 60 días para asegurar disponibilidad de datos NASA)
    if fecha is None:
        fecha_obj = datetime.now() - timedelta(days=60)
        fecha = fecha_obj.strftime('%Y-%m-%d')
    
    print(f"🌡️  OBTENIENDO TEMPERATURA NASA PARA {ciudad.upper()}")
    print(f"📅 Fecha: {fecha}")
    print("-" * 50)
    
    try:
        # Obtener datos de temperatura usando NASA MERRA-2
        data = get_location_data(ciudad, 'MERRA2', fecha)
        
        if data is None:
            print("❌ No se pudieron obtener datos NASA")
            return None
        
        # Extraer temperatura (T2M está en Kelvin)
        if 'T2M' in data.data_vars:
            temp_kelvin = float(data.T2M.values)
            temp_celsius = temp_kelvin - 273.15
            
            # Crear diccionario con información de temperatura
            resultado = {
                'ciudad': ciudad.title(),
                'fecha': fecha,
                'temperatura_celsius': round(temp_celsius, 2),
                'temperatura_kelvin': round(temp_kelvin, 2),
                'fuente': 'NASA MERRA-2',
                'coordenadas': {
                    'latitud': float(data.lat.values),
                    'longitud': float(data.lon.values)
                },
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Añadir otras variables si están disponibles
            if 'QV2M' in data.data_vars:
                humedad = float(data.QV2M.values)
                resultado['humedad_especifica'] = round(humedad * 1000, 2)  # g/kg
            
            if 'PS' in data.data_vars:
                presion = float(data.PS.values)
                resultado['presion_pascal'] = round(presion, 2)
                resultado['presion_hPa'] = round(presion / 100, 2)
            
            return resultado
            
        else:
            print("❌ Variable de temperatura T2M no encontrada en los datos")
            return None
            
    except Exception as e:
        print(f"❌ Error procesando datos NASA: {e}")
        return None

def mostrar_temperatura(datos_temp):
    """
    Muestra los datos de temperatura de forma bonita
    
    Args:
        datos_temp (dict): Datos de temperatura NASA
    """
    if not datos_temp:
        print("❌ No hay datos de temperatura para mostrar")
        return
    
    print("\n" + "="*60)
    print(f"🛰️  TEMPERATURA NASA - {datos_temp['ciudad'].upper()}")
    print("="*60)
    print(f"📍 Ubicación: {datos_temp['ciudad']}")
    print(f"🗺️  Coordenadas: {datos_temp['coordenadas']['latitud']:.3f}°N, {datos_temp['coordenadas']['longitud']:.3f}°E")
    print(f"📅 Fecha: {datos_temp['fecha']}")
    print(f"🌡️  Temperatura: {datos_temp['temperatura_celsius']}°C ({datos_temp['temperatura_kelvin']}K)")
    
    if 'humedad_especifica' in datos_temp:
        print(f"💧 Humedad específica: {datos_temp['humedad_especifica']} g/kg")
    
    if 'presion_hPa' in datos_temp:
        print(f"🌪️  Presión: {datos_temp['presion_hPa']} hPa")
    
    print(f"🛰️  Fuente: {datos_temp['fuente']}")
    print(f"⏰ Consulta: {datos_temp['timestamp']}")
    print("="*60)

def obtener_analisis_multiple_ciudades(
    ciudades=None, 
    fecha=None
):
    """
    Obtiene temperatura para múltiples ciudades españolas
    
    Args:
        ciudades (list): Lista de ciudades (opcional)
        fecha (str): Fecha en formato 'YYYY-MM-DD' (opcional)
    
    Returns:
        dict: Temperaturas para cada ciudad
    """
    
    if ciudades is None:
        ciudades = ['madrid', 'barcelona', 'valencia', 'sevilla', 'bilbao']
    
    print(f"🗺️  ANÁLISIS DE TEMPERATURA PARA {len(ciudades)} CIUDADES")
    print("=" * 55)
    
    resultados = {}
    
    for ciudad in ciudades:
        print(f"\n🔍 Procesando {ciudad.title()}...")
        temp_data = obtener_temperatura_nasa(ciudad, fecha)
        
        if temp_data:
            resultados[ciudad] = temp_data
            print(f"✅ {ciudad.title()}: {temp_data['temperatura_celsius']}°C")
        else:
            print(f"❌ Error obteniendo datos para {ciudad}")
    
    return resultados

def comparar_temperaturas(resultados):
    """
    Compara temperaturas entre ciudades
    
    Args:
        resultados (dict): Resultados de múltiples ciudades
    """
    if not resultados:
        print("❌ No hay datos para comparar")
        return
    
    print(f"\n📊 COMPARACIÓN DE TEMPERATURAS")
    print("=" * 40)
    
    # Extraer temperaturas
    temperaturas = [(ciudad, data['temperatura_celsius']) 
                   for ciudad, data in resultados.items()]
    
    # Ordenar por temperatura
    temperaturas.sort(key=lambda x: x[1], reverse=True)
    
    print("🌡️  Ranking de temperaturas:")
    for i, (ciudad, temp) in enumerate(temperaturas, 1):
        emoji = "🔥" if i == 1 else "❄️" if i == len(temperaturas) else "🌡️"
        print(f"{emoji} {i}. {ciudad.title()}: {temp}°C")
    
    # Estadísticas
    temps_values = [temp for _, temp in temperaturas]
    print(f"\n📈 Estadísticas:")
    print(f"   • Máxima: {max(temps_values)}°C")
    print(f"   • Mínima: {min(temps_values)}°C")
    print(f"   • Promedio: {np.mean(temps_values):.1f}°C")
    print(f"   • Diferencia: {max(temps_values) - min(temps_values):.1f}°C")

def main():
    """
    Función principal - ejemplos de uso
    """
    print("🛰️  PROGRAMA TEMPERATURA NASA EARTHDATA")
    print("=" * 45)
    
    # Verificar si necesitamos configurar credenciales
    if not auto_authenticate():
        print("\n🔐 PRIMERA VEZ - CONFIGURACIÓN REQUERIDA")
        print("-" * 40)
        print("Para usar datos NASA necesitas configurar credenciales.")
        
        respuesta = input("¿Quieres configurar ahora? (s/n): ").strip().lower()
        if respuesta in ['s', 'si', 'sí', 'yes', 'y']:
            temp_data = obtener_temperatura_nasa(configurar_credenciales=True)
            if temp_data:
                mostrar_temperatura(temp_data)
        else:
            print("💡 Cuando quieras configurar, ejecuta:")
            print("   obtener_temperatura_nasa(configurar_credenciales=True)")
        return
    
    print("\n🎯 EJEMPLOS DE USO:")
    print("-" * 20)
    
    # Ejemplo 1: Temperatura simple
    print("\n1️⃣  Temperatura para Madrid:")
    temp_madrid = obtener_temperatura_nasa('madrid')
    if temp_madrid:
        mostrar_temperatura(temp_madrid)
    
    # Ejemplo 2: Múltiples ciudades
    print("\n2️⃣  Comparación múltiples ciudades:")
    resultados = obtener_analisis_multiple_ciudades(['madrid', 'barcelona', 'valencia'])
    if resultados:
        comparar_temperaturas(resultados)
    
    # Ejemplo 3: Fecha específica
    print("\n3️⃣  Temperatura para fecha específica:")
    fecha_especifica = '2024-08-15'  # Verano
    temp_verano = obtener_temperatura_nasa('sevilla', fecha_especifica)
    if temp_verano:
        mostrar_temperatura(temp_verano)
    
    print("\n🎉 ¡Programa completado!")
    print("💡 Modifica las funciones para tus necesidades específicas")

if __name__ == "__main__":
    main()