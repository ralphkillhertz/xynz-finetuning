# === fix_verify_step_implementation.py ===
# 🔍 Verifica qué están haciendo step() y update()
# ⚡ Añade debug para ver el flujo real

import os
import re
from datetime import datetime

def verify_and_fix_step():
    """Verifica y arregla la implementación de step()"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Buscar step()
    step_pattern = r'def step\(self[^)]*\):(.*?)(?=\n\s{0,4}def|\n\s{0,4}async def|\nclass|\Z)'
    step_match = re.search(step_pattern, content, re.DOTALL)
    
    if step_match:
        step_content = step_match.group(1)
        print("\n📄 Contenido actual de step():")
        lines = step_content.split('\n')[:15]
        for i, line in enumerate(lines):
            print(f"  {i}: {line}")
        
        # Verificar si tiene código de deltas
        has_deltas = 'update_with_deltas' in step_content
        calls_update = 'self.update()' in step_content
        
        print(f"\n📊 Análisis de step():")
        print(f"  - Procesa deltas: {'✅' if has_deltas else '❌'}")
        print(f"  - Llama a update(): {'✅' if calls_update else '❌'}")
        
        if not has_deltas and calls_update:
            print("\n⚠️ step() solo llama a update(), verificando update()...")
            
            # Verificar update()
            update_pattern = r'def update\(self[^)]*\):(.*?)(?=\n\s{0,4}def|\n\s{0,4}async def|\nclass|\Z)'
            update_match = re.search(update_pattern, content, re.DOTALL)
            
            if update_match:
                update_content = update_match.group(1)
                update_has_deltas = 'update_with_deltas' in update_content
                print(f"  - update() procesa deltas: {'✅' if update_has_deltas else '❌'}")
                
                if not update_has_deltas:
                    print("\n❌ Ni step() ni update() procesan deltas!")
                    return False
    
    # Crear test detallado
    test_code = '''# === test_step_detailed.py ===
# Test con máximo debug

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent, SourceMotion
import numpy as np

print("🔍 TEST DETALLADO DE STEP")
print("="*50)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=3)
engine.running = True

# Crear fuente
engine.create_source(0, "test")
engine._positions[0] = np.array([10.0, 0.0, 0.0])

# Verificar motion_states
print(f"\\n📋 motion_states: {list(engine.motion_states.keys())}")
motion = engine.motion_states[0]
print(f"  - Tipo de motion: {type(motion).__name__}")
print(f"  - Tiene update_with_deltas: {hasattr(motion, 'update_with_deltas')}")

# Añadir concentración
comp = ConcentrationComponent()
comp.enabled = True
comp.concentration_factor = 0.8
comp.concentration_center = np.array([0.0, 0.0, 0.0])

if hasattr(motion, 'add_component'):
    motion.add_component(comp, 'concentration')
    print("  ✅ Concentración añadida con add_component")
elif hasattr(motion, 'components'):
    motion.components['concentration'] = comp
    print("  ✅ Concentración añadida a components dict")
else:
    print("  ❌ No se puede añadir concentración")

# Test manual de update_with_deltas
print("\\n🧪 Test manual de update_with_deltas:")
if hasattr(motion, 'update_with_deltas'):
    deltas = motion.update_with_deltas(0.0, 0.1)
    print(f"  - Deltas retornados: {deltas}")
    if deltas:
        for delta in deltas:
            print(f"    Delta: source_id={delta.source_id}, position={delta.position}")

# Ahora step()
print(f"\\n📍 Posición antes de step: {engine._positions[0]}")
engine.step()
print(f"📍 Posición después de step: {engine._positions[0]}")

# Si no se movió, aplicar delta manualmente
if np.array_equal(engine._positions[0], [10.0, 0.0, 0.0]):
    print("\\n🔧 Aplicando delta manualmente:")
    if deltas and len(deltas) > 0:
        delta = deltas[0]
        engine._positions[0] += delta.position
        print(f"  ✅ Nueva posición: {engine._positions[0]}")
'''
    
    with open('test_step_detailed.py', 'w') as f:
        f.write(test_code)
    
    print("\n✅ Test detallado creado: test_step_detailed.py")
    return True

if __name__ == "__main__":
    print("🔧 VERIFICACIÓN DE STEP() Y UPDATE()")
    print("="*60)
    
    verify_and_fix_step()
    
    print("\n📋 Ejecuta el test detallado:")
    print("$ python test_step_detailed.py")
    print("\nEsto mostrará exactamente qué está fallando.")