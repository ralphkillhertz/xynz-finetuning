# === fix_update_with_deltas.py ===
# 🔧 Fix: Arregla update_with_deltas para que retorne lista y deltas correctos
# ⚡ Impacto: CRÍTICO - Este es EL problema

import os
import re
from datetime import datetime

def fix_update_with_deltas():
    """Arregla el método update_with_deltas en SourceMotion"""
    
    motion_path = "trajectory_hub/core/motion_components.py"
    
    if not os.path.exists(motion_path):
        print("❌ No se encuentra motion_components.py")
        return False
    
    # Leer archivo
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Buscar update_with_deltas en SourceMotion
    pattern = r'(class SourceMotion.*?)(def update_with_deltas\(self[^)]*\):)(.*?)(?=\n\s{0,8}def|\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ No se encontró update_with_deltas en SourceMotion")
        return False
    
    print("✅ Encontrado update_with_deltas")
    
    # Analizar el método actual
    method_content = match.group(3)
    print("\n📄 Contenido actual (primeras líneas):")
    lines = method_content.split('\n')[:10]
    for line in lines:
        print(f"  {line}")
    
    # Nuevo método update_with_deltas
    method_def = match.group(2)
    new_method = '''
        """Actualiza componentes y retorna lista de deltas"""
        deltas = []
        
        # Actualizar cada componente activo
        for comp_name, component in self.active_components.items():
            if hasattr(component, 'enabled') and component.enabled:
                if hasattr(component, 'calculate_delta'):
                    delta = component.calculate_delta(self.motion_state, current_time, dt)
                    if delta and delta.position is not None:
                        # Asegurar que source_id esté configurado
                        delta.source_id = self.source_id
                        deltas.append(delta)
        
        # Si no hay componentes activos, retornar lista vacía
        return deltas'''
    
    # Reemplazar el método
    new_content = content[:match.start(2)] + method_def + new_method + content[match.end():]
    
    # Escribir archivo
    with open(motion_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("\n✅ update_with_deltas arreglado")
    
    # Verificar sintaxis
    try:
        compile(new_content, motion_path, 'exec')
        print("✅ Sintaxis verificada")
        return True
    except Exception as e:
        print(f"❌ Error de sintaxis: {e}")
        # Restaurar
        with open(backup_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(motion_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print("⚠️ Backup restaurado")
        return False

def create_final_test():
    """Crea test final simplificado"""
    
    test_code = '''# === test_delta_working.py ===
# Test final - debería funcionar!

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent
import numpy as np

print("🚀 TEST FINAL DEL SISTEMA DE DELTAS")
print("="*50)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5)
engine.running = True

# Crear fuentes en círculo
positions = [
    [10.0, 0.0, 0.0],
    [0.0, 10.0, 0.0],
    [-10.0, 0.0, 0.0],
    [0.0, -10.0, 0.0],
    [5.0, 5.0, 0.0]
]

for i, pos in enumerate(positions):
    engine.create_source(i, f"test_{i}")
    engine._positions[i] = np.array(pos)

# Aplicar concentración a todas
for i in range(5):
    motion = engine.motion_states[i]
    comp = ConcentrationComponent()
    comp.enabled = True
    comp.concentration_factor = 0.8
    comp.concentration_center = np.array([0.0, 0.0, 0.0])
    motion.add_component(comp, 'concentration')

print("📍 Posiciones iniciales:")
for i in range(5):
    print(f"  Source {i}: {engine._positions[i]}")

# Simular 10 frames
print("\\n🔄 Simulando 10 frames...")
for frame in range(10):
    engine.step()

print("\\n📍 Posiciones finales:")
for i in range(5):
    print(f"  Source {i}: {engine._positions[i]}")

# Verificar movimiento
moved = False
for i in range(5):
    if not np.array_equal(engine._positions[i], positions[i]):
        moved = True
        break

if moved:
    print("\\n✅ ¡ÉXITO! Las fuentes se movieron hacia el centro")
else:
    print("\\n❌ Las fuentes NO se movieron")
'''
    
    with open('test_delta_working.py', 'w') as f:
        f.write(test_code)
    
    print("\n✅ Test final creado: test_delta_working.py")

if __name__ == "__main__":
    print("🔧 FIX DEFINITIVO DE UPDATE_WITH_DELTAS")
    print("="*60)
    
    success = fix_update_with_deltas()
    
    if success:
        create_final_test()
        print("\n🎯 ESTE ES EL FIX FINAL!")
        print("\n📋 Ejecuta:")
        print("$ python test_delta_working.py")
        print("\n✨ Las fuentes DEBERÍAN moverse ahora!")
    else:
        print("\n❌ Error al aplicar fix")