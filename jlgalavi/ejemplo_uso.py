# 🌡️ EJEMPLOS RÁPIDOS DE USO

from temperatura_muy_simple import temperatura_simple

# Ejemplo 1: Temperatura simple
print("="*40)
print("🌡️ TEMPERATURAS DE CIUDADES ESPAÑOLAS")
print("="*40)

ciudades = ["madrid", "barcelona", "valencia", "sevilla"]
temperaturas = {}

for ciudad in ciudades:
    temp = temperatura_simple(ciudad)
    if temp:
        temperaturas[ciudad] = temp
    print()  # Línea en blanco

# Mostrar resumen
print("📊 RESUMEN:")
print("-"*20)
for ciudad, temp in temperaturas.items():
    print(f"🏙️ {ciudad.title()}: {temp}°C")

# Encontrar la más caliente y más fría
if temperaturas:
    max_temp = max(temperaturas.values())
    min_temp = min(temperaturas.values())
    
    ciudad_caliente = [c for c, t in temperaturas.items() if t == max_temp][0]
    ciudad_fria = [c for c, t in temperaturas.items() if t == min_temp][0]
    
    print(f"\n🔥 Más caliente: {ciudad_caliente.title()} ({max_temp}°C)")
    print(f"❄️ Más fría: {ciudad_fria.title()} ({min_temp}°C)")
    print(f"📏 Diferencia: {max_temp - min_temp:.1f}°C")