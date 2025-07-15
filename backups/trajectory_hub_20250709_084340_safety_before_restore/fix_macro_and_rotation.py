# === fix_macro_and_rotation.py ===
# 🔧 Fix: Corregir create_macro y set_individual_rotation
# ⚡ Solución para errores de API

import os

def fix_create_macro_return():
    """Arreglar create_macro para que retorne el objeto macro"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f'{file_path}.backup_macro_fix', 'w', encoding='utf-8') as f:
        f.write(content)
    
    lines = content.split('\n')
    
    # Buscar create_macro
    in_create_macro = False
    for i, line in enumerate(lines):
        if 'def create_macro' in line:
            in_create_macro = True
            print(f"🔍 Encontrado create_macro en línea {i+1}")
        
        if in_create_macro and 'return' in line:
            if 'return name' in line:
                # Cambiar para retornar el objeto macro
                indent = len(line) - len(line.lstrip())
                lines[i] = ' ' * indent + 'return self.macros[name]'
                print(f"✅ Cambiado 'return name' por 'return self.macros[name]'")
                in_create_macro = False
            elif 'return macro_name' in line:
                lines[i] = line.replace('return macro_name', 'return self.macros[macro_name]')
                print(f"✅ Cambiado 'return macro_name' por 'return self.macros[macro_name]'")
                in_create_macro = False
    
    content = '\n'.join(lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_set_individual_rotation_complete():
    """Arreglar completamente set_individual_rotation"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar la definición actual
    for i, line in enumerate(lines):
        if 'def set_individual_rotation' in line:
            print(f"🔍 Encontrada definición en línea {i+1}")
            
            # Verificar si ya tiene los parámetros correctos
            if 'speed_x' in line:
                print("✅ Ya tiene parámetros correctos")
                return
            
            # Si no, buscar el método completo y reemplazarlo
            j = i
            while j < len(lines) and not (lines[j].strip() and not lines[j].startswith(' ')):
                j += 1
            
            # Reemplazar el método completo
            new_method = '''    def set_individual_rotation(self, source_id: int, speed_x=0.0, speed_y=0.0, speed_z=0.0, center=None):
        """Configurar rotación algorítmica individual"""
        if source_id not in self.motion_states:
            print(f"⚠️ Fuente {source_id} no existe")
            return
        
        motion = self.motion_states[source_id]
        
        # Crear componente de rotación
        from trajectory_hub.core.motion_components import IndividualRotation
        rotation = IndividualRotation()
        rotation.speed_x = speed_x
        rotation.speed_y = speed_y
        rotation.speed_z = speed_z
        rotation.center = center if center is not None else np.array([0.0, 0.0, 0.0])
        
        # Añadir a componentes activos
        motion.active_components["individual_rotation"] = rotation
        
        print(f"✅ Rotación individual configurada para fuente {source_id}")
        print(f"   Velocidades: X={speed_x:.2f}, Y={speed_y:.2f}, Z={speed_z:.2f} rad/s")
    
'''
            
            # Reemplazar
            lines[i:j] = [new_method]
            print("✅ Método set_individual_rotation reemplazado")
            break
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def create_simple_test():
    """Crear test simple para verificar fixes"""
    
    test_code = '''# === test_delta_simple.py ===
# 🎯 Test simple del sistema de deltas
# ⚡ Verificación básica post-fixes

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np

def test_simple():
    print("🚀 TEST SIMPLE SISTEMA DE DELTAS")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=20, fps=60)
    
    # Test 1: create_macro retorna objeto
    print("\\n1️⃣ TEST: create_macro retorna objeto")
    macro = engine.create_macro("test", 3, formation='line', spacing=2.0)
    
    if hasattr(macro, 'source_ids'):
        print(f"✅ Macro es objeto con source_ids: {macro.source_ids}")
    else:
        print(f"❌ Macro no es objeto: {type(macro)}")
        return
    
    # Test 2: set_individual_rotation con parámetros
    print("\\n2️⃣ TEST: set_individual_rotation")
    try:
        sid = 10
        engine.create_source(sid)
        engine.set_individual_rotation(sid, speed_x=0.0, speed_y=1.0, speed_z=0.0)
        print("✅ set_individual_rotation acepta parámetros correctos")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Concentración básica
    print("\\n3️⃣ TEST: Concentración")
    try:
        engine.set_macro_concentration(macro, 0.5)
        
        # Simular algunos frames
        for _ in range(10):
            engine.update()
        
        print("✅ Concentración ejecutada sin errores")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\\n✅ Test completado")

if __name__ == "__main__":
    test_simple()
'''
    
    with open('test_delta_simple.py', 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ test_delta_simple.py creado")

if __name__ == "__main__":
    print("🔧 FIXING MACRO AND ROTATION ISSUES")
    print("=" * 60)
    
    print("\n1️⃣ Arreglando create_macro return...")
    fix_create_macro_return()
    
    print("\n2️⃣ Arreglando set_individual_rotation completo...")
    fix_set_individual_rotation_complete()
    
    print("\n3️⃣ Creando test simple...")
    create_simple_test()
    
    print("\n✅ FIXES APLICADOS")
    print("\n📋 Ejecutar primero: python test_delta_simple.py")
    print("📋 Si pasa, ejecutar: python test_delta_final_fixed.py")