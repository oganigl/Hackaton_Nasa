#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARIMA Simple - Tutorial Paso a Paso
Código sencillo para entender ARIMA sin complicaciones
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def tutorial_arima_simple():
    """
    Tutorial ARIMA paso a paso - MUY SIMPLE
    """
    print("📚 TUTORIAL ARIMA - VERSIÓN SIMPLE")
    print("=" * 40)
    
    print("\n🔍 ¿Qué es ARIMA?")
    print("ARIMA = Modelo para predecir valores futuros basándose en valores pasados")
    print()
    print("📊 ARIMA(p,d,q) tiene 3 números:")
    print("• p = ¿cuántos días anteriores mirar?")
    print("• d = ¿necesita suavizar los datos?") 
    print("• q = ¿usar errores de predicciones pasadas?")
    print()
    
    # Generar datos de temperatura sintéticos
    print("🌡️ Generando datos de temperatura ficticios...")
    dias = 60
    fechas = pd.date_range(start='2024-08-01', periods=dias)
    
    # Temperatura base con patrón
    temperatura_base = 25  # Temperatura promedio
    variacion_estacional = 5 * np.sin(2 * np.pi * np.arange(dias) / 30)  # Ciclo mensual
    ruido = np.random.normal(0, 2, dias)  # Variabilidad aleatoria
    
    # Crear serie con dependencia del día anterior
    temperatura = np.zeros(dias)
    temperatura[0] = temperatura_base + ruido[0]
    
    for i in range(1, dias):
        # Cada día depende 70% del anterior + 30% del patrón base
        temperatura[i] = (0.7 * temperatura[i-1] + 
                         0.3 * (temperatura_base + variacion_estacional[i]) + 
                         ruido[i])
    
    # Crear DataFrame
    df = pd.DataFrame({
        'fecha': fechas,
        'temperatura': temperatura
    })
    
    print(f"✅ {dias} días de datos creados")
    print(f"🌡️ Rango: {temperatura.min():.1f}°C - {temperatura.max():.1f}°C")
    
    # Dividir datos: entrenamiento y prueba
    split = int(dias * 0.8)  # 80% para entrenar, 20% para probar
    train_temp = temperatura[:split]
    test_temp = temperatura[split:]
    
    print(f"\n📊 División de datos:")
    print(f"• Entrenamiento: {len(train_temp)} días")
    print(f"• Prueba: {len(test_temp)} días")
    
    # Modelo ARIMA simple sin librerías externas
    print(f"\n🤖 Modelo simple (sin ARIMA real):")
    print("Simulando predicción con promedio móvil...")
    
    # Predicción simple: promedio de últimos 3 días
    predicciones = []
    for i in range(len(test_temp)):
        if i == 0:
            # Primera predicción: promedio de últimos 3 días de entrenamiento
            pred = np.mean(train_temp[-3:])
        else:
            # Siguientes: combinar datos reales anteriores
            datos_disponibles = list(test_temp[:i]) + list(train_temp[-3:])
            pred = np.mean(datos_disponibles[-3:])
        
        predicciones.append(pred)
    
    # Calcular errores
    errores = test_temp - predicciones
    mae = np.mean(np.abs(errores))  # Error promedio absoluto
    
    print(f"\n📈 Resultados de la predicción:")
    print(f"• Error promedio: {mae:.2f}°C")
    
    # Mostrar algunas predicciones
    print(f"\n🔍 Muestra de predicciones:")
    for i in range(min(5, len(test_temp))):
        real = test_temp[i]
        pred = predicciones[i]
        error = errores[i]
        print(f"  Día {i+1}: Real {real:.1f}°C, Predicho {pred:.1f}°C, Error {error:+.1f}°C")
    
    return {
        'datos_completos': df,
        'entrenamiento': train_temp,
        'prueba': test_temp,
        'predicciones': predicciones,
        'error_mae': mae
    }

def arima_con_statsmodels():
    """
    ARIMA usando la librería statsmodels (si está disponible)
    """
    print(f"\n🔬 ARIMA REAL CON STATSMODELS")
    print("-" * 35)
    
    try:
        # Intentar importar statsmodels
        from statsmodels.tsa.arima.model import ARIMA
        print("✅ statsmodels disponible")
        
        # Usar los mismos datos del tutorial simple
        resultado_simple = tutorial_arima_simple()
        train_data = resultado_simple['entrenamiento']
        test_data = resultado_simple['prueba']
        
        print(f"\n⚙️ Probando diferentes configuraciones ARIMA...")
        
        configuraciones = [(1,0,0), (2,0,0), (1,0,1), (2,0,1), (1,1,1)]
        mejor_aic = float('inf')
        mejor_modelo = None
        mejor_config = None
        
        for p, d, q in configuraciones:
            try:
                modelo = ARIMA(train_data, order=(p, d, q))
                modelo_ajustado = modelo.fit()
                
                aic = modelo_ajustado.aic
                print(f"  ARIMA({p},{d},{q}): AIC = {aic:.2f}")
                
                if aic < mejor_aic:
                    mejor_aic = aic
                    mejor_modelo = modelo_ajustado
                    mejor_config = (p, d, q)
                    
            except Exception as e:
                print(f"  ARIMA({p},{d},{q}): Error")
        
        if mejor_modelo:
            print(f"\n🎯 Mejor modelo: ARIMA{mejor_config} (AIC: {mejor_aic:.2f})")
            
            # Hacer predicciones
            predicciones_arima = mejor_modelo.forecast(steps=len(test_data))
            mae_arima = np.mean(np.abs(test_data - predicciones_arima))
            
            print(f"🎯 Error ARIMA real: {mae_arima:.2f}°C")
            print(f"📊 Error modelo simple: {resultado_simple['error_mae']:.2f}°C")
            
            if mae_arima < resultado_simple['error_mae']:
                mejora = resultado_simple['error_mae'] - mae_arima
                print(f"✅ ARIMA es {mejora:.2f}°C mejor que el modelo simple")
            else:
                print(f"ℹ️ El modelo simple funciona bastante bien")
            
            return {
                'modelo_arima': mejor_modelo,
                'configuracion': mejor_config,
                'predicciones_arima': predicciones_arima,
                'mae_arima': mae_arima,
                'comparacion': resultado_simple
            }
        
    except ImportError:
        print("❌ statsmodels no disponible")
        print("💡 Para instalarlo: pip install statsmodels")
        print("ℹ️ Continuando con modelo simple...")
        return None
    
    except Exception as e:
        print(f"❌ Error con ARIMA real: {e}")
        return None

def ejemplo_nasa_arima():
    """
    Ejemplo de cómo usar ARIMA con datos NASA (conceptual)
    """
    print(f"\n🛰️ EJEMPLO CONCEPTUAL: ARIMA + NASA")
    print("-" * 40)
    
    print("📋 Pasos para usar ARIMA con datos NASA:")
    print()
    print("1️⃣ Obtener datos históricos:")
    print("   from nasa_earthdata_lib import get_location_data")
    print("   data = get_location_data('madrid', 'MERRA2', fecha_inicio)")
    print()
    print("2️⃣ Procesar serie temporal:")
    print("   temperaturas = data.T2M - 273.15  # Kelvin a Celsius")
    print("   serie_diaria = temperaturas.groupby('fecha').mean()")
    print()
    print("3️⃣ Aplicar ARIMA:")
    print("   from statsmodels.tsa.arima.model import ARIMA")
    print("   modelo = ARIMA(serie_diaria, order=(2,0,1))")
    print("   modelo_entrenado = modelo.fit()")
    print()
    print("4️⃣ Hacer predicciones:")
    print("   predicciones = modelo_entrenado.forecast(steps=7)")
    print("   # Predicciones para próximos 7 días")
    print()
    
    # Simular resultado esperado
    print("📊 Resultado esperado:")
    fechas_futuras = pd.date_range(start=datetime.now().date(), periods=7)
    temps_simuladas = np.random.normal(22, 3, 7)  # Temperaturas simuladas
    
    print("🔮 Predicciones meteorológicas:")
    for fecha, temp in zip(fechas_futuras, temps_simuladas):
        dia = fecha.strftime('%Y-%m-%d (%A)')
        print(f"   {dia}: {temp:.1f}°C")

def main():
    """
    Programa principal - Tutorial completo ARIMA
    """
    print("🌡️ ARIMA PARA PREDICCIONES METEOROLÓGICAS")
    print("Aprende ARIMA paso a paso con ejemplos simples")
    print("=" * 55)
    
    # Tutorial básico
    resultado_simple = tutorial_arima_simple()
    
    # ARIMA real si está disponible
    resultado_arima = arima_con_statsmodels()
    
    # Ejemplo conceptual con NASA
    ejemplo_nasa_arima()
    
    print(f"\n🎓 RESUMEN DE APRENDIZAJE:")
    print("=" * 30)
    print("✅ ARIMA predice valores futuros usando valores pasados")
    print("✅ Los parámetros (p,d,q) se pueden optimizar automáticamente")
    print("✅ AIC ayuda a comparar diferentes configuraciones")
    print("✅ Funciona bien con datos de temperatura")
    print("✅ Se puede integrar con datos NASA reales")
    
    print(f"\n🚀 PRÓXIMOS PASOS:")
    print("• Instalar statsmodels para ARIMA real")
    print("• Obtener más días de datos históricos")
    print("• Probar SARIMA para patrones estacionales")
    print("• Validar predicciones con datos reales")
    
    if resultado_arima:
        print(f"\n🎯 Tu modelo ARIMA está funcionando correctamente!")
    else:
        print(f"\n💡 Instala statsmodels para usar ARIMA completo:")
        print("   pip install statsmodels")

if __name__ == "__main__":
    main()