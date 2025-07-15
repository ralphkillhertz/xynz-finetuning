# 🔧 Fix: Corregir parámetros de SpatOSCBridge
# ⚡ Problema: Parámetros incorrectos en la inicialización

print("🔧 Arreglando parámetros de SpatOSCBridge...")

# Primero veamos qué parámetros acepta SpatOSCBridge
bridge_file = "trajectory_hub/core/spat_osc_bridge.py"
with open(bridge_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar el __init__ de SpatOSCBridge
for i, line in enumerate(lines):
    if "class SpatOSCBridge" in line:
        print(f"Encontrada clase en línea {i+1}")
        # Buscar el __init__
        for j in range(i, min(i+50, len(lines))):
            if "def __init__" in lines[j]:
                print(f"__init__ encontrado en línea {j+1}:")
                # Mostrar los parámetros
                k = j
                while k < len(lines) and "):" not in lines[k]:
                    print(f"  {lines[k].rstrip()}")
                    k += 1
                if k < len(lines):
                    print(f"  {lines[k].rstrip()}")
                break
        break

# Ahora corregir en enhanced_trajectory_engine.py
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar la inicialización incorrecta
old_init = """self.osc_bridge = SpatOSCBridge(
            max_sources=self.max_sources,
            update_rate=self.fps,
            source_prefix="/source"
        )"""

# Nueva inicialización (sin parámetros o con los correctos)
new_init = """self.osc_bridge = SpatOSCBridge()"""

content = content.replace(old_init, new_init)

# Guardar
with open(engine_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Parámetros de SpatOSCBridge corregidos")
print("\n🚀 Prueba de nuevo:")
print("   python -m trajectory_hub.interface.interactive_controller")