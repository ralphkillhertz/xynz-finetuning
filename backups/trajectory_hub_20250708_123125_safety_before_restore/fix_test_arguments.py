# === fix_test_arguments.py ===
# 🔧 Fix: Corregir argumentos en el test
# ⚡ Impacto: BAJO - Solo afecta al test

import os

def fix_test():
    """Corrige los argumentos del test"""
    
    print("🔧 CORRIGIENDO ARGUMENTOS DEL TEST\n")
    
    # Leer el test
    with open("test_macro_rotation_fixed.py", 'r') as f:
        content = f.read()
    
    # Reemplazar max_sources por n_sources
    content = content.replace("max_sources=8", "n_sources=8")
    
    # Guardar
    with open("test_macro_rotation_fixed.py", 'w') as f:
        f.write(content)
    
    print("✅ Test corregido: max_sources → n_sources")
    
    # También crear una versión simplificada del test
    simple_test = '''# === test_rotation_simple.py ===
# 🧪 Test simplificado de rotación MS

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

print("\\n🔄 TEST SIMPLE: Rotación MS\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(n_sources=4)
print("✅ Engine creado")

# Crear macro
macro_id = engine.create_macro("test", 4)
print(f"✅ Macro creado: {macro_id}")

# Posiciones en cuadrado
positions = [[2,0,0], [-2,0,0], [0,2,0], [0,-2,0]]
for i, sid in enumerate(list(engine._macros[macro_id].source_ids)[:4]):
    engine._positions[sid] = np.array(positions[i])
    if sid in engine.motion_states:
        engine.motion_states[sid].position = engine._positions[sid].copy()

print("\\n📍 Inicial:")
for sid in list(engine._macros[macro_id].source_ids)[:4]:
    p = engine._positions[sid]
    print(f"   Fuente {sid}: {p}")

# Configurar rotación
print("\\n🎯 Configurando rotación en Y...")
engine.set_macro_rotation(macro_id, 0, 1.0, 0)  # 1 rad/s en Y

# Simular 30 frames
print("\\n⏱️ Simulando...")
for i in range(30):
    engine.update()

print("\\n📍 Final:")
moved = False
for sid in list(engine._macros[macro_id].source_ids)[:4]:
    p = engine._positions[sid]
    print(f"   Fuente {sid}: {p}")
    if not np.allclose(p, positions[sid % 4]):
        moved = True

if moved:
    print("\\n✅ ¡ROTACIÓN MS FUNCIONANDO!")
else:
    print("\\n❌ Sin movimiento")
'''
    
    with open("test_rotation_simple.py", "w") as f:
        f.write(simple_test)
    
    print("✅ Test simple creado")

if __name__ == "__main__":
    fix_test()
    print("\n🚀 Ejecutando test simple...")
    os.system("python test_rotation_simple.py")