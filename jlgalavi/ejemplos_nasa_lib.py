#!/usr/bin/env python3
"""
🚀 Ejemplos de Uso - NASA Earthdata Library

Este archivo demuestra cómo usar la librería automatizada para 
acceder a datos NASA sin intervención manual.

Autor: Hackaton NASA - Automatización completa
"""

# Importar la librería
from nasa_earthdata_lib import (
    setup_credentials,
    get_data,
    get_precipitation,
    get_temperature, 
    get_location_data,
    quick_analysis,
    list_datasets
)

def ejemplo_configuracion_inicial():
    """
    🔧 Configuración inicial - Solo necesario UNA VEZ
    """
    print("🔧 CONFIGURACIÓN INICIAL (solo una vez)")
    print("=" * 50)
    
    # Sustituye por tus credenciales reales
    usuario = "jlgalavi"
    contraseña = "d8.sj24/eqfT27#" 
    
    print("⚠️  IMPORTANTE: Sustituye las credenciales por las tuyas reales")
    print(f"   Usuario actual: {usuario}")
    print("   Para configurar ejecuta:")
    print("   setup_credentials('tu_usuario_real', 'tu_contraseña_real')")
    
    # Descomenta la siguiente línea con tus credenciales reales:
    # success = setup_credentials(usuario, contraseña)
    
    print("\n✅ Una vez configurado, ¡nunca más necesitarás introducir credenciales!")

def ejemplo_precipitacion_simple():
    """
    🌧️ Ejemplo 1: Obtener precipitación para Madrid
    """
    print("\n🌧️ EJEMPLO 1: Precipitación en Madrid")
    print("=" * 40)
    
    try:
        # Obtener precipitación para Madrid el 15 de marzo de 2024
        precipitacion = get_precipitation(
            date='2024-03-15',
            lat=40.4168,  # Madrid
            lon=-3.7038
        )
        
        if precipitacion is not None:
            print("✅ Datos de precipitación obtenidos")
            print(f"📊 Dimensiones: {dict(precipitacion.sizes)}")
            
            # Mostrar valor de precipitación
            if 'precipitationCal' in precipitacion.data_vars:
                valor = precipitacion.precipitationCal.values
                print(f"🌧️ Precipitación: {valor} mm/hr")
            
            return precipitacion
        else:
            print("❌ No se pudieron obtener datos de precipitación")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def ejemplo_temperatura_region():
    """
    🌡️ Ejemplo 2: Temperatura para toda España
    """
    print("\n🌡️ EJEMPLO 2: Temperatura en España")
    print("=" * 40)
    
    try:
        # Obtener temperatura para toda España (región)
        temperatura = get_temperature(
            date_start='2024-03-15',
            date_end='2024-03-17',  # 3 días
            bbox=(-10, 35, 5, 45)   # España (oeste, sur, este, norte)
        )
        
        if temperatura is not None:
            print("✅ Datos de temperatura obtenidos")
            print(f"📊 Dimensiones: {dict(temperatura.sizes)}")
            
            # Convertir de Kelvin a Celsius
            if 'T2M' in temperatura.data_vars:
                temp_kelvin = temperatura.T2M
                temp_celsius = temp_kelvin - 273.15
                
                print(f"🌡️ Temperatura media: {float(temp_celsius.mean()):.1f}°C")
                print(f"🔥 Temperatura máxima: {float(temp_celsius.max()):.1f}°C")
                print(f"❄️ Temperatura mínima: {float(temp_celsius.min()):.1f}°C")
            
            return temperatura
        else:
            print("❌ No se pudieron obtener datos de temperatura")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def ejemplo_ciudades_multiples():
    """
    🏙️ Ejemplo 3: Datos para múltiples ciudades
    """
    print("\n🏙️ EJEMPLO 3: Datos para múltiples ciudades")
    print("=" * 45)
    
    ciudades = ['madrid', 'barcelona', 'valencia', 'sevilla']
    resultados = {}
    
    for ciudad in ciudades:
        print(f"\n📍 Obteniendo datos para {ciudad.title()}...")
        
        try:
            data = get_location_data(
                location=ciudad,
                dataset='MERRA2',
                date_start='2024-03-15'
            )
            
            if data is not None:
                resultados[ciudad] = data
                
                # Calcular temperatura si está disponible
                if 'T2M' in data.data_vars:
                    temp_celsius = float(data.T2M.mean()) - 273.15
                    print(f"  🌡️ Temperatura: {temp_celsius:.1f}°C")
                
                print(f"  ✅ Datos obtenidos para {ciudad.title()}")
            else:
                print(f"  ❌ No se pudieron obtener datos para {ciudad}")
                
        except Exception as e:
            print(f"  ❌ Error en {ciudad}: {e}")
    
    print(f"\n📊 Resumen: Datos obtenidos para {len(resultados)} ciudades")
    return resultados

def ejemplo_analisis_rapido():
    """
    📈 Ejemplo 4: Análisis rápido de la última semana
    """
    print("\n📈 EJEMPLO 4: Análisis rápido - Madrid última semana")
    print("=" * 55)
    
    try:
        # Análisis automático de los últimos 7 días
        datos = quick_analysis(
            dataset='MERRA2',
            location='madrid',
            days=7
        )
        
        if datos is not None:
            print("\n📊 Análisis completado:")
            
            # Si hay datos temporales, hacer estadísticas
            if 'time' in datos.dims and 'T2M' in datos.data_vars:
                temp_celsius = datos.T2M - 273.15
                
                print(f"   📈 Serie temporal de {len(datos.time)} puntos")
                print(f"   🌡️ Temp. promedio: {float(temp_celsius.mean()):.1f}°C")
                print(f"   📊 Desv. estándar: {float(temp_celsius.std()):.1f}°C")
                
            return datos
        else:
            print("❌ No se pudo completar el análisis")
            
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
    
    return None

def ejemplo_datos_generales():
    """
    🔧 Ejemplo 5: Uso de la función general get_data()
    """
    print("\n🔧 EJEMPLO 5: Función general get_data()")
    print("=" * 45)
    
    try:
        # Ejemplo con información sin descargar
        info = get_data(
            dataset='IMERG_DAILY',
            date_start='2024-03-15',
            lat=40.4,
            lon=-3.7,
            output_format='info'  # Solo información
        )
        
        if info:
            print("ℹ️ Información del dataset:")
            for key, value in info.items():
                print(f"   {key}: {value}")
        
        # Ejemplo con datos reales
        print("\n🌊 Obteniendo datos reales...")
        datos = get_data(
            dataset='MERRA2',
            date_start='2024-03-15',
            bbox=(-5, 38, 0, 42),  # Región de Madrid ampliada
            variables=['T2M'],     # Solo temperatura
            output_format='xarray'
        )
        
        if datos is not None:
            print("✅ Datos obtenidos con función general")
            print(f"📊 Variables: {list(datos.data_vars.keys())}")
            
        return datos
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def mostrar_datasets_disponibles():
    """
    📋 Mostrar todos los datasets disponibles
    """
    print("\n📋 DATASETS DISPONIBLES")
    print("=" * 30)
    
    datasets = list_datasets()
    
    print("\n💡 Puedes usar cualquiera de estos datasets con:")
    print("   - get_data(dataset='NOMBRE', ...)")
    print("   - get_location_data(location='madrid', dataset='NOMBRE', ...)")

def main():
    """
    🚀 Función principal - Ejecutar todos los ejemplos
    """
    print("🛰️ NASA EARTHDATA LIBRARY - EJEMPLOS DE USO")
    print("=" * 55)
    print("📚 Esta librería automatiza completamente el acceso a datos NASA")
    print("🔐 Solo necesitas configurar credenciales UNA VEZ")
    print()
    
    # Mostrar datasets disponibles
    mostrar_datasets_disponibles()
    
    # Ejemplo de configuración
    ejemplo_configuracion_inicial()
    
    print("\n" + "="*60)
    print("⚠️  PARA EJECUTAR LOS EJEMPLOS SIGUIENTES:")
    print("   1. Configura tus credenciales primero")
    print("   2. Descomenta los ejemplos que quieras probar")
    print("="*60)
    
    # Ejemplos (comentados por defecto para evitar errores sin credenciales)
    
    # # Ejemplo 1: Precipitación simple
    ejemplo_precipitacion_simple()
    
    # # Ejemplo 2: Temperatura regional
    # ejemplo_temperatura_region()
    
    # # Ejemplo 3: Múltiples ciudades
    # ejemplo_ciudades_multiples()
    
    # # Ejemplo 4: Análisis rápido
    # ejemplo_analisis_rapido()
    
    # # Ejemplo 5: Función general
    # ejemplo_datos_generales()
    
    print("\n🎉 ¡Librería lista para usar!")
    print("💡 Descomenta los ejemplos después de configurar credenciales")

if __name__ == "__main__":
    main()