# === fix_test_and_rotation.py ===
# 🔧 Fix: Corregir test para usar sets y completar set_individual_rotation
# ⚡ Solución para errores del test completo

import os

def fix_test_for_sets():
    """Arreglar test para manejar source_ids como set"""
    
    with open('test_delta_final_fixed.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open('test_delta_final_fixed.py.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Reemplazar accesos por índice con conversión a lista
    content = content.replace('macro.source_ids[0]', 'list(macro.source_ids)[0]')
    content = content.replace('macro.source_ids[:4]', 'list(macro.source_ids)[:4]')
    content = content.replace('macro.source_ids[:3]', 'list(macro.source_ids)[:3]')
    
    # Guardar
    with open('test_delta_final_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Test actualizado para manejar sets")

def fix_set_individual_rotation_complete():
    """Completar la implementación de set_individual_rotation"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar set_individual_rotation
    for i, line in enumerate(lines):
        if 'def set_individual_rotation' in line and 'speed_x' not in line:
            print(f"🔍 Encontrado set_individual_rotation sin parámetros en línea {i+1}")
            
            # Buscar el final del método actual
            j = i + 1
            indent = '        '
            while j < len(lines) and (lines[j].startswith(indent) or not lines[j].strip()):
                j += 1
            
            # Reemplazar método completo
            new_method = '''    def set_individual_rotation(self, source_id: int, speed_x=0.0, speed_y=0.0, speed_z=0.0, center=None):
        """Configurar rotación algorítmica individual con deltas"""
        if source_id not in self.motion_states:
            print(f"⚠️ Fuente {source_id} no existe")
            return
        
        motion = self.motion_states[source_id]
        
        # Importar aquí para evitar imports circulares
        from trajectory_hub.core.motion_components import IndividualRotation
        
        # Crear componente de rotación
        rotation = IndividualRotation()
        rotation.speed_x = float(speed_x)
        rotation.speed_y = float(speed_y)
        rotation.speed_z = float(speed_z)
        rotation.center = center if center is not None else np.zeros(3)
        rotation.enabled = True
        
        # Añadir a componentes activos
        motion.active_components["individual_rotation"] = rotation
        
        print(f"✅ Rotación individual configurada para fuente {source_id}")
        print(f"   Velocidades: X={speed_x:.2f}, Y={speed_y:.2f}, Z={speed_z:.2f} rad/s")
    
'''
            # Reemplazar
            lines[i:j] = [new_method]
            
            # Guardar
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print("✅ set_individual_rotation actualizado con parámetros completos")
            return

def create_quick_test():
    """Test rápido para verificar fixes"""
    
    test_code = '''# === test_quick.py ===
# 🚀 Test rápido post-fixes

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST RÁPIDO")
print("=" * 40)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Test 1: Macro con sets
print("\\n1️⃣ Test macro y sets")
macro = engine.create_macro("test", 3)
print(f"   source_ids tipo: {type(macro.source_ids)}")
print(f"   source_ids: {macro.source_ids}")
sids_list = list(macro.source_ids)
print(f"   Como lista: {sids_list}")
print(f"   Primer elemento: {sids_list[0]}")

# Test 2: Rotación individual
print("\\n2️⃣ Test rotación individual")
try:
    engine.set_individual_rotation(5, speed_x=0.0, speed_y=1.0, speed_z=0.0)
    print("   ✅ Parámetros aceptados")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\\n✅ Test completado")
'''
    
    with open('test_quick.py', 'w', encoding='utf-8') as f:
        f.write(test_code)

if __name__ == "__main__":
    print("🔧 FIXING TEST AND ROTATION ISSUES")
    print("=" * 60)
    
    print("\n1️⃣ Arreglando test para manejar sets...")
    fix_test_for_sets()
    
    print("\n2️⃣ Completando set_individual_rotation...")
    fix_set_individual_rotation_complete()
    
    print("\n3️⃣ Creando test rápido...")
    create_quick_test()
    
    print("\n✅ FIXES APLICADOS")
    print("\n📋 Ejecutar: python test_quick.py")
    print("📋 Si pasa, ejecutar: python test_delta_final_fixed.py")