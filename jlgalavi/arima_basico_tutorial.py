#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARIMA para Predicciones Meteorológicas - Código Educativo
Aprende ARIMA paso a paso con ejemplos simples
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def explicar_arima():
    """
    Explicación sencilla de qué es ARIMA
    """
    print("📚 ¿QUÉ ES ARIMA?")
    print("=" * 50)
    print()
    print("ARIMA = AutoRegressive Integrated Moving Average")
    print()
    print("🔹 AR (p) - AutoRegresivo:")
    print("   ➤ Usa valores pasados para predecir el futuro")
    print("   ➤ Ejemplo: Temp[hoy] = a×Temp[ayer] + b×Temp[antier]")
    print()
    print("🔹 I (d) - Integrado (Diferenciación):")
    print("   ➤ Elimina tendencias para hacer datos estacionarios")
    print("   ➤ Ejemplo: Usar diferencias en lugar de valores absolutos")
    print()
    print("🔹 MA (q) - Media Móvil:")
    print("   ➤ Usa errores pasados para corregir predicciones")
    print("   ➤ Ejemplo: Corregir usando errores de predicciones anteriores")
    print()
    print("📊 ARIMA(p,d,q) - Tres números clave:")
    print("   • p = cuántos valores pasados usar")
    print("   • d = cuántas veces diferenciar")
    print("   • q = cuántos errores pasados considerar")
    print()

def generar_datos_temperatura_sintetica(dias=100):
    """
    Genera datos sintéticos de temperatura para aprender ARIMA
    
    Args:
        dias: Número de días de datos
        
    Returns:
        pandas.DataFrame con fechas y temperaturas
    """
    print("🌡️ Generando datos sintéticos de temperatura...")
    
    # Crear fechas
    fechas = pd.date_range(start='2024-01-01', periods=dias, freq='D')
    
    # Componentes de la temperatura
    # 1. Tendencia estacional (ciclo anual)
    tendencia_anual = 10 * np.sin(2 * np.pi * np.arange(dias) / 365.25) + 15
    
    # 2. Variación semanal (más frío en invierno)
    variacion_semanal = 3 * np.sin(2 * np.pi * np.arange(dias) / 7)
    
    # 3. Tendencia a largo plazo (calentamiento gradual)
    tendencia_largo_plazo = 0.01 * np.arange(dias)
    
    # 4. Ruido aleatorio
    ruido = np.random.normal(0, 2, dias)
    
    # 5. Componente autoregresiva (temperatura depende del día anterior)
    temperatura = np.zeros(dias)
    temperatura[0] = tendencia_anual[0] + ruido[0]
    
    for i in range(1, dias):
        # Temperatura base
        temp_base = (tendencia_anual[i] + 
                    variacion_semanal[i] + 
                    tendencia_largo_plazo[i])
        
        # Componente autoregresiva (70% del día anterior + 30% base)
        temperatura[i] = (0.7 * temperatura[i-1] + 
                         0.3 * temp_base + 
                         ruido[i])
    
    # Crear DataFrame
    df = pd.DataFrame({
        'fecha': fechas,
        'temperatura': temperatura
    })
    df.set_index('fecha', inplace=True)
    
    print(f"✅ Generados {dias} días de datos sintéticos")
    return df

def arima_basico_ejemplo():
    """
    Ejemplo básico de ARIMA con explicación paso a paso
    """
    print("\n🚀 EJEMPLO BÁSICO DE ARIMA")
    print("=" * 40)
    
    # Generar datos
    datos = generar_datos_temperatura_sintetica(120)
    
    # Dividir en entrenamiento y prueba
    split_point = int(len(datos) * 0.8)
    train = datos[:split_point]
    test = datos[split_point:]
    
    print(f"📊 Datos de entrenamiento: {len(train)} días")
    print(f"🔍 Datos de prueba: {len(test)} días")
    
    try:
        # Instalar statsmodels si no está disponible
        from statsmodels.tsa.arima.model import ARIMA
        from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
        from statsmodels.tsa.stattools import adfuller
        
    except ImportError:
        print("📦 Instalando statsmodels...")
        import subprocess
        subprocess.check_call([
            "C:/Users/jolug/repos/nasa/.nasa/Scripts/python.exe", 
            "-m", "pip", "install", "statsmodels"
        ])
        from statsmodels.tsa.arima.model import ARIMA
        from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
        from statsmodels.tsa.stattools import adfuller
    
    # Paso 1: Verificar estacionariedad
    print("\n📈 PASO 1: Verificando estacionariedad...")
    result = adfuller(train['temperatura'])
    
    print(f"   • ADF Statistic: {result[0]:.6f}")
    print(f"   • p-value: {result[1]:.6f}")
    
    if result[1] <= 0.05:
        print("   ✅ Serie es estacionaria (p-value ≤ 0.05)")
        d_param = 0
    else:
        print("   ⚠️ Serie NO es estacionaria, aplicando diferenciación...")
        # Aplicar diferenciación
        train_diff = train['temperatura'].diff().dropna()
        result_diff = adfuller(train_diff)
        print(f"   • ADF después de diferenciación: {result_diff[1]:.6f}")
        d_param = 1
    
    # Paso 2: Configurar ARIMA simple
    print(f"\n⚙️ PASO 2: Configurando ARIMA(2,{d_param},2)...")
    print("   • p=2: Usar 2 valores pasados")
    print(f"   • d={d_param}: {'Sin' if d_param==0 else 'Con'} diferenciación")
    print("   • q=2: Considerar 2 errores pasados")
    
    # Entrenar modelo
    model = ARIMA(train['temperatura'], order=(2, d_param, 2))
    fitted_model = model.fit()
    
    print("\n📊 RESULTADOS DEL ENTRENAMIENTO:")
    print(f"   • AIC: {fitted_model.aic:.2f} (menor es mejor)")
    print(f"   • BIC: {fitted_model.bic:.2f} (menor es mejor)")
    
    # Paso 3: Hacer predicciones
    print("\n🔮 PASO 3: Generando predicciones...")
    
    # Predicciones para el periodo de prueba
    predictions = fitted_model.forecast(steps=len(test))
    
    # Calcular errores
    mae = np.mean(np.abs(test['temperatura'] - predictions))
    rmse = np.sqrt(np.mean((test['temperatura'] - predictions) ** 2))
    
    print(f"   • MAE (Error Absoluto Medio): {mae:.2f}°C")
    print(f"   • RMSE (Error Cuadrático Medio): {rmse:.2f}°C")
    
    # Crear DataFrame con resultados
    resultados = pd.DataFrame({
        'real': test['temperatura'],
        'prediccion': predictions,
        'error': test['temperatura'] - predictions
    })
    
    print("\n📈 MUESTRA DE PREDICCIONES:")
    print("-" * 45)
    for i in range(min(5, len(resultados))):
        fecha = test.index[i].strftime('%Y-%m-%d')
        real = resultados['real'].iloc[i]
        pred = resultados['prediccion'].iloc[i]
        error = resultados['error'].iloc[i]
        print(f"{fecha}: Real {real:.1f}°C, Predicción {pred:.1f}°C, Error {error:+.1f}°C")
    
    return {
        'modelo': fitted_model,
        'predicciones': resultados,
        'datos_entrenamiento': train,
        'datos_prueba': test,
        'metricas': {'MAE': mae, 'RMSE': rmse}
    }

def encontrar_mejor_arima(serie_temporal, max_p=3, max_d=2, max_q=3):
    """
    Encuentra los mejores parámetros ARIMA automáticamente
    
    Args:
        serie_temporal: Serie de tiempo pandas
        max_p: Máximo valor de p a probar
        max_d: Máximo valor de d a probar  
        max_q: Máximo valor de q a probar
        
    Returns:
        tuple: (mejor_orden, mejor_aic, modelo_ajustado)
    """
    print("\n🔍 BUSCANDO MEJOR CONFIGURACIÓN ARIMA...")
    print("-" * 45)
    
    try:
        from statsmodels.tsa.arima.model import ARIMA
        
        mejor_aic = float('inf')
        mejor_orden = None
        mejor_modelo = None
        
        combinaciones_probadas = 0
        total_combinaciones = (max_p + 1) * (max_d + 1) * (max_q + 1)
        
        for p in range(max_p + 1):
            for d in range(max_d + 1):
                for q in range(max_q + 1):
                    try:
                        combinaciones_probadas += 1
                        print(f"Probando ARIMA({p},{d},{q}) [{combinaciones_probadas}/{total_combinaciones}]", end=" ")
                        
                        model = ARIMA(serie_temporal, order=(p, d, q))
                        fitted = model.fit()
                        
                        if fitted.aic < mejor_aic:
                            mejor_aic = fitted.aic
                            mejor_orden = (p, d, q)
                            mejor_modelo = fitted
                            print("✅ ¡Mejor hasta ahora!")
                        else:
                            print("❌")
                            
                    except Exception as e:
                        print("⚠️ Error")
                        continue
        
        if mejor_modelo:
            print(f"\n🎯 MEJOR CONFIGURACIÓN ENCONTRADA:")
            print(f"   • ARIMA{mejor_orden}")
            print(f"   • AIC: {mejor_aic:.2f}")
            return mejor_orden, mejor_aic, mejor_modelo
        else:
            print("❌ No se pudo encontrar una configuración válida")
            return None, None, None
            
    except ImportError:
        print("❌ statsmodels no disponible")
        return None, None, None

def main():
    """
    Función principal - Tutorial completo de ARIMA
    """
    print("🌡️ ARIMA PARA PREDICCIONES METEOROLÓGICAS")
    print("=" * 50)
    
    # Explicación teórica
    explicar_arima()
    
    # Ejemplo básico
    resultado_basico = arima_basico_ejemplo()
    
    if resultado_basico:
        print("\n🎯 EJEMPLO BÁSICO COMPLETADO")
        
        # Buscar mejor configuración
        datos_entrenamiento = resultado_basico['datos_entrenamiento']
        mejor_orden, mejor_aic, mejor_modelo = encontrar_mejor_arima(
            datos_entrenamiento['temperatura']
        )
        
        if mejor_modelo:
            print(f"\n🏆 COMPARACIÓN DE MODELOS:")
            print(f"   • Modelo básico ARIMA(2,0,2): AIC = {resultado_basico['modelo'].aic:.2f}")
            print(f"   • Mejor modelo ARIMA{mejor_orden}: AIC = {mejor_aic:.2f}")
            
            diferencia = resultado_basico['modelo'].aic - mejor_aic
            if diferencia > 0:
                print(f"   ✅ Mejora de {diferencia:.2f} puntos AIC")
            else:
                print(f"   ℹ️ Modelo básico ya era bueno")
    
    print("\n📚 CONCEPTOS CLAVE APRENDIDOS:")
    print("-" * 35)
    print("✅ ARIMA combina AR + I + MA para predicciones")
    print("✅ Parámetros (p,d,q) se pueden optimizar automáticamente")
    print("✅ AIC ayuda a seleccionar el mejor modelo")
    print("✅ Estacionariedad es importante para ARIMA")
    print("✅ MAE y RMSE miden la calidad de predicciones")
    
    print("\n🎓 PRÓXIMOS PASOS:")
    print("• Usar datos reales NASA con get_data()")
    print("• Aplicar ARIMA a series temporales más largas")
    print("• Combinar con datos de múltiples ubicaciones")
    print("• Añadir variables exógenas (ARIMAX)")

if __name__ == "__main__":
    main()