#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Código MUY SIMPLE para obtener temperatura usando NASA
Solo lo esencial - fácil de usar
"""

from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Importar la librería NASA
try:
    from nasa_earthdata_lib import get_location_data, auto_authenticate
    print("✅ Librería NASA lista")
except ImportError:
    print("❌ Error: nasa_earthdata_lib.py no encontrado")
    exit(1)

def temperatura_simple(ciudad="madrid"):
    """
    Obtiene temperatura de forma muy simple
    
    Args:
        ciudad: 'madrid', 'barcelona', 'valencia', etc.
    
    Returns:
        Temperatura en Celsius o None si hay error
    """
    
    # Verificar autenticación
    if not auto_authenticate():
        print("❌ Configura credenciales NASA primero")
        return None
    
    # Fecha hace 2 meses (datos disponibles)
    fecha = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    
    print(f"🌡️ Obteniendo temperatura para {ciudad.title()}...")
    
    try:
        # Obtener datos NASA
        data = get_location_data(ciudad, 'MERRA2', fecha)
        
        if data and 'T2M' in data.data_vars:
            # Tomar el promedio diario si hay múltiples horas
            if 'time' in data.dims and len(data.time) > 1:
                temp_kelvin = float(data.T2M.mean(dim='time').values)
            else:
                temp_kelvin = float(data.T2M.values)
            
            # Convertir Kelvin a Celsius
            temp_celsius = round(temp_kelvin - 273.15, 1)
            
            print(f"🌡️ Temperatura promedio en {ciudad.title()}: {temp_celsius}°C")
            print(f"📅 Fecha: {fecha}")
            print(f"🛰️ Fuente: NASA MERRA-2")
            
            return temp_celsius
        else:
            print("❌ No hay datos disponibles")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🛰️ TEMPERATURA NASA - VERSIÓN SIMPLE")
    print("=" * 35)
    
    # Ejemplo básico
    temp = temperatura_simple("madrid")
    
    # Prueba con otra ciudad
    if temp:
        print("\n" + "-" * 25)
        temperatura_simple("barcelona")