# 🔧 Fix: Error de sintaxis en logger.info
# ⚡ Línea 132: cadena no cerrada

print("🔧 Arreglando error de sintaxis...")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
with open(engine_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar la línea problemática
for i, line in enumerate(lines):
    if 'logger.info("Inicializan' in line and '")' not in line:
        print(f"❌ Error encontrado en línea {i+1}: {line.strip()}")
        
        # Corregir la línea
        lines[i] = '        logger.info("Inicializando OSC bridge...")\n'
        print(f"✅ Corregido a: {lines[i].strip()}")
        break

# Guardar
with open(engine_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ Error de sintaxis corregido")
print("\n🚀 Ejecuta el test de nuevo:")
print("   python test_osc_debug.py")