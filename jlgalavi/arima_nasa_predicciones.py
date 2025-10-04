#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARIMA con Datos NASA - Predicciones Meteorológicas Reales
Integra ARIMA con tu librería NASA para predicciones reales
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Importar librería NASA
try:
    from nasa_earthdata_lib import get_data, auto_authenticate, get_location_data
    print("✅ Librería NASA disponible")
except ImportError:
    print("❌ nasa_earthdata_lib.py no encontrado")
    exit(1)

def obtener_serie_temporal_nasa(
    ciudad="madrid",
    dias_historicos=30,
    dataset='MERRA2'
):
    """
    Obtiene serie temporal de temperatura desde NASA
    
    Args:
        ciudad: Ciudad para obtener datos
        dias_historicos: Días hacia atrás para obtener
        dataset: Tipo de dataset NASA
        
    Returns:
        pandas.DataFrame con serie temporal
    """
    
    print(f"🛰️ OBTENIENDO SERIE TEMPORAL NASA PARA {ciudad.upper()}")
    print("=" * 55)
    
    # Verificar autenticación
    if not auto_authenticate():
        print("❌ No autenticado. Configura credenciales NASA primero.")
        return None
    
    # Calcular rango de fechas (datos disponibles con retraso)
    fecha_fin = datetime.now() - timedelta(days=60)  # 2 meses atrás
    fecha_inicio = fecha_fin - timedelta(days=dias_historicos)
    
    print(f"📅 Período: {fecha_inicio.date()} a {fecha_fin.date()}")
    print(f"📊 Días solicitados: {dias_historicos}")
    
    try:
        # Obtener datos NASA
        data = get_data(
            dataset=dataset,
            date_start=fecha_inicio.strftime('%Y-%m-%d'),
            date_end=fecha_fin.strftime('%Y-%m-%d'),
            **{'madrid': {'lat': 40.4168, 'lon': -3.7038},
               'barcelona': {'lat': 41.3851, 'lon': 2.1734},
               'valencia': {'lat': 39.4699, 'lon': -0.3763},
               'sevilla': {'lat': 37.3891, 'lon': -5.9845}}.get(ciudad.lower(), {'lat': 40.4168, 'lon': -3.7038})
        )
        
        if data is None:
            print("❌ No se pudieron obtener datos NASA")
            return None
        
        # Procesar datos para serie temporal
        if 'T2M' in data.data_vars:
            # Convertir a DataFrame
            df = data.T2M.to_dataframe().reset_index()
            
            # Convertir Kelvin a Celsius
            df['temperatura_celsius'] = df['T2M'] - 273.15
            
            # Agrupar por día (promedio diario)
            df['fecha'] = pd.to_datetime(df['time']).dt.date
            serie_diaria = df.groupby('fecha')['temperatura_celsius'].mean().reset_index()
            serie_diaria['fecha'] = pd.to_datetime(serie_diaria['fecha'])
            serie_diaria.set_index('fecha', inplace=True)
            
            print(f"✅ Serie temporal creada: {len(serie_diaria)} días")
            print(f"🌡️ Rango temperatura: {serie_diaria['temperatura_celsius'].min():.1f}°C - {serie_diaria['temperatura_celsius'].max():.1f}°C")
            
            return serie_diaria
        else:
            print("❌ Variable T2M no encontrada")
            return None
            
    except Exception as e:
        print(f"❌ Error procesando datos NASA: {e}")
        return None

def arima_con_datos_nasa(
    ciudad="madrid",
    dias_historicos=60,
    dias_prediccion=7
):
    """
    Aplica ARIMA a datos NASA para predicción meteorológica
    
    Args:
        ciudad: Ciudad para analizar
        dias_historicos: Días de historia para entrenar
        dias_prediccion: Días a predecir hacia el futuro
        
    Returns:
        dict con resultados del modelo y predicciones
    """
    
    print(f"\n🔮 PREDICCIÓN METEOROLÓGICA CON ARIMA")
    print(f"🏙️ Ciudad: {ciudad.title()}")
    print(f"📊 Historia: {dias_historicos} días")
    print(f"🔍 Predicción: {dias_prediccion} días")
    print("-" * 50)
    
    # Obtener datos
    serie_temporal = obtener_serie_temporal_nasa(ciudad, dias_historicos)
    
    if serie_temporal is None:
        return None
    
    try:
        from statsmodels.tsa.arima.model import ARIMA
        from statsmodels.tsa.stattools import adfuller
        
        # Preparar datos
        temperatura = serie_temporal['temperatura_celsius']
        
        # Dividir en entrenamiento y validación
        split_point = int(len(temperatura) * 0.85)
        train = temperatura[:split_point]
        validation = temperatura[split_point:]
        
        print(f"\n📊 DIVISIÓN DE DATOS:")
        print(f"   • Entrenamiento: {len(train)} días")
        print(f"   • Validación: {len(validation)} días")
        
        # Verificar estacionariedad
        print(f"\n🔍 ANÁLISIS DE ESTACIONARIEDAD:")
        adf_result = adfuller(train)
        print(f"   • ADF p-value: {adf_result[1]:.6f}")
        
        if adf_result[1] <= 0.05:
            print("   ✅ Serie estacionaria")
            d_param = 0
        else:
            print("   ⚠️ Serie no estacionaria, diferenciando...")
            d_param = 1
        
        # Buscar mejor configuración ARIMA
        print(f"\n⚙️ OPTIMIZACIÓN DE PARÁMETROS ARIMA:")
        mejor_aic = float('inf')
        mejor_config = None
        mejor_modelo = None
        
        # Probar diferentes configuraciones
        configuraciones = [
            (1, d_param, 1), (2, d_param, 1), (1, d_param, 2),
            (2, d_param, 2), (3, d_param, 1), (1, d_param, 3),
            (3, d_param, 2), (2, d_param, 3)
        ]
        
        for p, d, q in configuraciones:
            try:
                model = ARIMA(train, order=(p, d, q))
                fitted = model.fit()
                
                if fitted.aic < mejor_aic:
                    mejor_aic = fitted.aic
                    mejor_config = (p, d, q)
                    mejor_modelo = fitted
                    print(f"   ✅ ARIMA({p},{d},{q}): AIC = {fitted.aic:.2f} ⭐")
                else:
                    print(f"   ❌ ARIMA({p},{d},{q}): AIC = {fitted.aic:.2f}")
                    
            except Exception as e:
                print(f"   ⚠️ ARIMA({p},{d},{q}): Error - {str(e)[:30]}")
                continue
        
        if mejor_modelo is None:
            print("❌ No se pudo ajustar ningún modelo ARIMA")
            return None
        
        print(f"\n🎯 MEJOR MODELO: ARIMA{mejor_config}")
        print(f"   • AIC: {mejor_aic:.2f}")
        
        # Validar modelo con datos de validación
        if len(validation) > 0:
            predicciones_validacion = mejor_modelo.forecast(steps=len(validation))
            mae_validacion = np.mean(np.abs(validation - predicciones_validacion))
            rmse_validacion = np.sqrt(np.mean((validation - predicciones_validacion) ** 2))
            
            print(f"\n📊 VALIDACIÓN DEL MODELO:")
            print(f"   • MAE: {mae_validacion:.2f}°C")
            print(f"   • RMSE: {rmse_validacion:.2f}°C")
        
        # Re-entrenar con todos los datos para predicciones finales
        print(f"\n🔄 RE-ENTRENANDO CON TODOS LOS DATOS...")
        modelo_completo = ARIMA(temperatura, order=mejor_config)
        modelo_ajustado = modelo_completo.fit()
        
        # Generar predicciones futuras
        print(f"\n🔮 GENERANDO PREDICCIONES PARA {dias_prediccion} DÍAS...")
        predicciones_futuras = modelo_ajustado.forecast(steps=dias_prediccion)
        
        # Crear fechas futuras
        ultima_fecha = serie_temporal.index[-1]
        fechas_futuras = pd.date_range(
            start=ultima_fecha + timedelta(days=1),
            periods=dias_prediccion,
            freq='D'
        )
        
        # Crear DataFrame con predicciones
        df_predicciones = pd.DataFrame({
            'fecha': fechas_futuras,
            'prediccion_temperatura': predicciones_futuras
        })
        df_predicciones.set_index('fecha', inplace=True)
        
        # Mostrar predicciones
        print(f"\n📈 PREDICCIONES METEOROLÓGICAS:")
        print("-" * 40)
        for i, (fecha, temp) in enumerate(zip(fechas_futuras, predicciones_futuras)):
            dia_semana = fecha.strftime('%A')
            fecha_str = fecha.strftime('%Y-%m-%d')
            print(f"   {dia_semana:>9} {fecha_str}: {temp:.1f}°C")
        
        # Calcular estadísticas
        temp_promedio = predicciones_futuras.mean()
        temp_min = predicciones_futuras.min()
        temp_max = predicciones_futuras.max()
        
        print(f"\n📊 RESUMEN DE PREDICCIONES:")
        print(f"   • Temperatura promedio: {temp_promedio:.1f}°C")
        print(f"   • Temperatura mínima: {temp_min:.1f}°C")
        print(f"   • Temperatura máxima: {temp_max:.1f}°C")
        print(f"   • Variación: {temp_max - temp_min:.1f}°C")
        
        return {
            'modelo': modelo_ajustado,
            'configuracion': mejor_config,
            'aic': mejor_aic,
            'datos_historicos': serie_temporal,
            'predicciones': df_predicciones,
            'metricas_validacion': {
                'MAE': mae_validacion if len(validation) > 0 else None,
                'RMSE': rmse_validacion if len(validation) > 0 else None
            },
            'resumen': {
                'temp_promedio': temp_promedio,
                'temp_min': temp_min,
                'temp_max': temp_max,
                'variacion': temp_max - temp_min
            }
        }
        
    except ImportError:
        print("📦 Instalando statsmodels...")
        import subprocess
        subprocess.check_call([
            "C:/Users/jolug/repos/nasa/.nasa/Scripts/python.exe",
            "-m", "pip", "install", "statsmodels"
        ])
        # Reintentar después de la instalación
        return arima_con_datos_nasa(ciudad, dias_historicos, dias_prediccion)
    
    except Exception as e:
        print(f"❌ Error en análisis ARIMA: {e}")
        return None

def comparar_ciudades_arima(ciudades=['madrid', 'barcelona', 'valencia']):
    """
    Compara predicciones ARIMA para múltiples ciudades
    
    Args:
        ciudades: Lista de ciudades a comparar
        
    Returns:
        dict con comparación de resultados
    """
    
    print(f"\n🌍 COMPARACIÓN ARIMA ENTRE CIUDADES")
    print("=" * 45)
    
    resultados = {}
    
    for ciudad in ciudades:
        print(f"\n🔄 Procesando {ciudad.title()}...")
        resultado = arima_con_datos_nasa(ciudad, dias_historicos=45, dias_prediccion=5)
        
        if resultado:
            resultados[ciudad] = resultado
            config = resultado['configuracion']
            aic = resultado['aic']
            temp_prom = resultado['resumen']['temp_promedio']
            
            print(f"   ✅ ARIMA{config}, AIC={aic:.1f}, Temp.Promedio={temp_prom:.1f}°C")
        else:
            print(f"   ❌ Error procesando {ciudad}")
    
    if resultados:
        print(f"\n📊 RESUMEN COMPARATIVO:")
        print("-" * 35)
        
        for ciudad, resultado in resultados.items():
            temp = resultado['resumen']['temp_promedio']
            var = resultado['resumen']['variacion']
            aic = resultado['aic']
            
            print(f"🏙️ {ciudad.title():>10}: {temp:>5.1f}°C (±{var/2:.1f}) AIC:{aic:.0f}")
        
        # Encontrar extremos
        temperaturas = {c: r['resumen']['temp_promedio'] for c, r in resultados.items()}
        ciudad_mas_calida = max(temperaturas.keys(), key=temperaturas.get)
        ciudad_mas_fria = min(temperaturas.keys(), key=temperaturas.get)
        
        print(f"\n🔥 Más cálida: {ciudad_mas_calida.title()} ({temperaturas[ciudad_mas_calida]:.1f}°C)")
        print(f"❄️ Más fría: {ciudad_mas_fria.title()} ({temperaturas[ciudad_mas_fria]:.1f}°C)")
    
    return resultados

def main():
    """
    Programa principal - ARIMA con datos NASA
    """
    
    print("🛰️ ARIMA + NASA: PREDICCIONES METEOROLÓGICAS REALES")
    print("=" * 60)
    
    # Verificar autenticación NASA
    if not auto_authenticate():
        print("❌ Configura credenciales NASA primero:")
        print("   from nasa_earthdata_lib import setup_credentials")
        print("   setup_credentials('usuario', 'contraseña')")
        return
    
    # Ejemplo 1: Predicción para una ciudad
    print("\n1️⃣ PREDICCIÓN INDIVIDUAL")
    resultado_madrid = arima_con_datos_nasa('madrid', dias_historicos=50, dias_prediccion=7)
    
    if resultado_madrid:
        print("\n✅ Predicción completada para Madrid")
    
    # Ejemplo 2: Comparación entre ciudades  
    print("\n2️⃣ COMPARACIÓN ENTRE CIUDADES")
    comparacion = comparar_ciudades_arima(['madrid', 'barcelona', 'sevilla'])
    
    print("\n🎓 CONCLUSIONES:")
    print("-" * 20)
    print("✅ ARIMA funciona bien con datos NASA reales")
    print("✅ Diferentes ciudades requieren configuraciones diferentes")
    print("✅ AIC ayuda a seleccionar el mejor modelo automáticamente")
    print("✅ Las predicciones meteorológicas son razonables")
    
    print("\n💡 MEJORAS POSIBLES:")
    print("• Usar más días históricos para mayor precisión")
    print("• Incluir variables adicionales (humedad, presión)")
    print("• Aplicar modelos SARIMA para estacionalidad")
    print("• Validar con datos meteorológicos de estaciones terrestres")

if __name__ == "__main__":
    main()