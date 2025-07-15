# === find_real_error.py ===
# 🔧 Fix: Encontrar el VERDADERO error - no es MacroRotation!
# ⚡ CAMBIO DE ESTRATEGIA

import os

print("🔍 BÚSQUEDA DEL ERROR REAL")
print("="*50)

# Crear un test que capture EXACTAMENTE dónde está el error
test_code = '''
import numpy as np
import sys
import traceback
sys.path.append('.')

from trajectory_hub import EnhancedTrajectoryEngine

# Crear engine y setup
engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
sids = []
for i in range(4):
    sid = engine.create_source(f"test_{i}")
    sids.append(sid)

engine.create_macro("test_macro", sids)
engine.set_macro_rotation("test_macro", speed_x=0.0, speed_y=1.0, speed_z=0.0)

# Monkey patch update_with_deltas para debug
original_update_with_deltas = engine.motion_states[0].update_with_deltas

def debug_update_with_deltas(current_time, dt):
    print(f"\\n🔍 DEBUG update_with_deltas:")
    print(f"   current_time: {current_time}, dt: {dt}")
    print(f"   active_components type: {type(engine.motion_states[0].active_components)}")
    print(f"   active_components: {engine.motion_states[0].active_components}")
    
    # Revisar cada componente
    for name, component in engine.motion_states[0].active_components.items():
        print(f"\\n   Componente '{name}':")
        print(f"      Tipo: {type(component)}")
        if hasattr(component, 'enabled'):
            print(f"      enabled: {component.enabled} (tipo: {type(component.enabled)})")
        if hasattr(component, 'speed_x'):
            print(f"      speed_x: {component.speed_x} (tipo: {type(component.speed_x)})")
        if hasattr(component, 'speed_y'):
            print(f"      speed_y: {component.speed_y} (tipo: {type(component.speed_y)})")
    
    try:
        return original_update_with_deltas(current_time, dt)
    except Exception as e:
        print(f"\\n❌ ERROR EN update_with_deltas: {e}")
        traceback.print_exc()
        raise

# Aplicar el monkey patch
engine.motion_states[0].update_with_deltas = debug_update_with_deltas

# Intentar update
print("\\n🚀 Ejecutando engine.update()...")
try:
    engine.update()
    print("✅ Update exitoso")
except Exception as e:
    print(f"\\n❌ ERROR FINAL: {e}")
    print("\\nTRACEBACK COMPLETO:")
    traceback.print_exc()
'''

with open("debug_real_error.py", "w") as f:
    f.write(test_code)

print("\n🧪 Ejecutando debug profundo...")
os.system("python debug_real_error.py")

# Ahora buscar el problema real
print("\n" + "="*50)
print("🔍 Buscando el problema en update_with_deltas...")

# Revisar update_with_deltas en motion_components.py
with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar update_with_deltas
for i, line in enumerate(lines):
    if 'def update_with_deltas' in line and 'SourceMotion' in ''.join(lines[max(0,i-50):i]):
        print(f"\n📍 Encontrado update_with_deltas en línea {i+1}")
        # Mostrar las próximas 20 líneas
        for j in range(i, min(i+20, len(lines))):
            print(f"{j+1:4d}: {lines[j].rstrip()}")
        
        # Buscar comparaciones problemáticas
        for j in range(i, min(i+30, len(lines))):
            if 'if ' in lines[j] and 'component' in lines[j]:
                print(f"\n⚠️ Posible problema en línea {j+1}: {lines[j].strip()}")

os.remove("debug_real_error.py")

print("\n" + "="*50)
print("💡 El error NO está en MacroRotation, está en el flujo de update!")
print("   Necesitamos corregir update_with_deltas o el manejo de componentes")

# Buscar TODAS las comparaciones con 'if' en el archivo
print("\n🔍 Buscando TODAS las comparaciones problemáticas...")
problem_lines = []
for i, line in enumerate(lines):
    if 'if ' in line and ('component' in line or 'enabled' in line or 'active' in line):
        # Verificar que no sea un comentario
        if not line.strip().startswith('#'):
            problem_lines.append((i+1, line.strip()))

print(f"\n📊 Encontradas {len(problem_lines)} líneas con comparaciones potencialmente problemáticas")
for line_num, line in problem_lines[:10]:  # Mostrar solo las primeras 10
    print(f"   Línea {line_num}: {line}")