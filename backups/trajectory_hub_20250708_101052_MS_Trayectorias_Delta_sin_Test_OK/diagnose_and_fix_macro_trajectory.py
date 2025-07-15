# === diagnose_and_fix_macro_trajectory.py ===
# 🔍 Diagnosticar por qué no funciona MacroTrajectory
# ⚡ Aplicar fixes necesarios

import re

print("🔍 DIAGNÓSTICO: MacroTrajectory no funciona\n")

# 1. Verificar cómo se almacenan los macros
engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
with open(engine_path, 'r') as f:
    content = f.read()

# Buscar referencias a macros
print("1️⃣ ANALIZANDO ALMACENAMIENTO DE MACROS:")
if "self.macros = {}" in content:
    print("✅ Usa self.macros (sin guión bajo)")
    macro_attr = "macros"
elif "self._macros = {}" in content:
    print("✅ Usa self._macros (con guión bajo)")
    macro_attr = "_macros"
else:
    print("❌ No encontrado")
    macro_attr = None

# 2. Ver cómo create_macro asigna el trajectory_component
print("\n2️⃣ ANALIZANDO create_macro:")
create_macro_match = re.search(r'def create_macro\(.*?\):.*?(?=\n    def|\Z)', content, re.DOTALL)
if create_macro_match:
    method = create_macro_match.group(0)
    if "trajectory_component" in method:
        print("✅ create_macro configura trajectory_component")
        # Ver qué tipo de componente crea
        comp_match = re.search(r'trajectory_component\s*=\s*(\w+)\(', method)
        if comp_match:
            print(f"  Crea: {comp_match.group(1)}")
    else:
        print("❌ create_macro NO configura trajectory_component")

# 3. Verificar que engine.update() procese componentes de macro
print("\n3️⃣ VERIFICANDO engine.update():")
update_match = re.search(r'def update\(.*?\):.*?(?=\n    def|\Z)', content, re.DOTALL)
if update_match:
    update_method = update_match.group(0)
    if "calculate_delta" in update_method:
        print("✅ update() llama a calculate_delta")
    else:
        print("❌ update() NO llama a calculate_delta")
        
    if "macro_trajectory" in update_method:
        print("✅ update() procesa macro_trajectory")
    else:
        print("❌ update() NO menciona macro_trajectory")

# 4. Crear test de debug detallado
test_code = f'''# === test_macro_debug_detailed.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
import math

print("🔍 DEBUG DETALLADO: MacroTrajectory\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro
print("1️⃣ Creando macro...")
engine.create_macro("test", [0, 1, 2])

# Verificar que el macro existe
print("\\n2️⃣ Verificando macro:")
if hasattr(engine, '{macro_attr}'):
    macros = getattr(engine, '{macro_attr}')
    print(f"  Macros disponibles: {{list(macros.keys())}}")
    
    if "test" in macros:
        macro = macros["test"]
        print(f"  ✅ Macro 'test' existe")
        print(f"  source_ids: {{macro.source_ids}}")
        
        # Verificar trajectory_component
        if hasattr(macro, 'trajectory_component'):
            tc = macro.trajectory_component
            print(f"  trajectory_component: {{tc}}")
            if tc:
                print(f"    - Tipo: {{type(tc).__name__}}")
                print(f"    - enabled: {{tc.enabled if hasattr(tc, 'enabled') else 'N/A'}}")
        else:
            print("  ❌ NO tiene trajectory_component")
else:
    print("  ❌ No se encontró atributo de macros")

# Función de trayectoria simple
def simple_trajectory(t):
    return np.array([t, 0.0, 0.0])  # Movimiento lineal en X

# Configurar trayectoria
print("\\n3️⃣ Configurando trayectoria...")
try:
    engine.set_macro_trajectory("test", simple_trajectory)
    print("  ✅ set_macro_trajectory ejecutado")
except Exception as e:
    print(f"  ❌ Error: {{e}}")

# Verificar componentes en motion_states
print("\\n4️⃣ Verificando motion_states:")
for sid in [0, 1, 2]:
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        components = list(motion.active_components.keys())
        print(f"  Fuente {{sid}}: {{components}}")
        
        # Verificar macro_trajectory
        if 'macro_trajectory' in motion.active_components:
            mt = motion.active_components['macro_trajectory']
            print(f"    - MacroTrajectory.enabled: {{mt.enabled}}")
            print(f"    - MacroTrajectory.trajectory_func: {{mt.trajectory_func is not None}}")
            
            # Test calculate_delta directamente
            if hasattr(mt, 'calculate_delta'):
                print("    - tiene calculate_delta ✅")
                
                # Llamar directamente
                delta = mt.calculate_delta(motion, 0.0, 1/60)
                if delta:
                    print(f"    - Delta calculado: {{delta.position}}")
                else:
                    print("    - Delta es None")
            else:
                print("    - NO tiene calculate_delta ❌")

# Test un solo frame
print("\\n5️⃣ Test de un frame:")
pos_before = engine._positions[0].copy()
print(f"  Antes: {{pos_before}}")

engine.update()

pos_after = engine._positions[0].copy()
print(f"  Después: {{pos_after}}")
print(f"  Movimiento: {{np.linalg.norm(pos_after - pos_before):.6f}}")

# Debug adicional
print("\\n6️⃣ Debug del engine:")
print(f"  motion_states keys: {{list(engine.motion_states.keys())}}")
print(f"  _positions shape: {{engine._positions.shape}}")
'''

with open("test_macro_debug_detailed.py", "w") as f:
    f.write(test_code)

print("\n✅ Test de debug creado")

# 5. Crear fix si es necesario
if macro_attr == "_macros":
    fix_code = '''# === fix_macro_attribute.py ===
import os

print("🔧 Arreglando referencia a macros...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    content = f.read()

# En set_macro_trajectory, cambiar self._macros por self.macros
content = content.replace(
    "if macro_id not in self._macros:",
    "if macro_id not in self.macros:"
)
content = content.replace(
    "macro = self._macros[macro_id]",
    "macro = self.macros[macro_id]"
)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Referencias arregladas")
'''
    
    with open("fix_macro_attribute.py", "w") as f:
        f.write(fix_code)
    
    print("\n🔧 Fix creado: fix_macro_attribute.py")
    print("   Ejecuta primero el fix, luego el test")

print("\n🚀 Ejecuta: python test_macro_debug_detailed.py")