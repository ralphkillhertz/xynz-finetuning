#!/usr/bin/env python3
"""
fix_integration_errors.py - Corrige errores de la integración
"""

import os
import re

def fix_enum_import():
    """Corregir el import de Enum en motion_components.py"""
    print("🔧 CORRIGIENDO IMPORT DE ENUM...")
    
    filepath = "trajectory_hub/core/motion_components.py"
    if not os.path.exists(filepath):
        print(f"❌ No se encuentra {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Verificar si Enum ya está importado
    if "from enum import Enum" not in content:
        # Buscar donde agregar el import
        import_numpy = content.find("import numpy as np")
        if import_numpy != -1:
            # Agregar después de numpy
            insert_pos = content.find("\n", import_numpy) + 1
            content = content[:insert_pos] + "from enum import Enum\n" + content[insert_pos:]
        else:
            # Agregar al principio después de docstring
            docstring_end = content.find('"""', 3)
            if docstring_end != -1:
                insert_pos = content.find("\n", docstring_end) + 1
                content = content[:insert_pos] + "\nimport numpy as np\nfrom enum import Enum\n" + content[insert_pos:]
                
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("✅ Import de Enum corregido")
    return True

def fix_update_method():
    """Corregir el método update en enhanced_trajectory_engine.py"""
    print("\n🔧 CORRIGIENDO MÉTODO UPDATE...")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    if not os.path.exists(filepath):
        print(f"❌ No se encuentra {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Buscar donde se llama a motion.update
    pattern = r'motion\.update\(self\._time, self\.dt\)'
    
    # Verificar el orden correcto de parámetros
    # SourceMotion.update espera (current_time, dt)
    # Pero algunos componentes pueden esperar (state, current_time, dt)
    
    # Reemplazar la llamada incorrecta
    if "motion.update(self._time, self.dt)" in content:
        # Ya está correcto
        print("✅ motion.update ya tiene los parámetros correctos")
    else:
        # Buscar variaciones posibles
        variations = [
            "motion.update(self._time)",
            "motion.update()",
            "motion.update(self.dt)"
        ]
        
        for var in variations:
            if var in content:
                content = content.replace(var, "motion.update(self._time, self.dt)")
                print(f"✅ Corregido: {var} → motion.update(self._time, self.dt)")
                
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return True

def verify_motion_component_update():
    """Verificar que MotionComponent tiene el método update correcto"""
    print("\n🔍 VERIFICANDO MotionComponent.update...")
    
    filepath = "trajectory_hub/core/motion_components.py"
    if not os.path.exists(filepath):
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Verificar que MotionComponent tiene update con los parámetros correctos
    if "def update(self, state: MotionState, current_time: float, dt: float)" in content:
        print("✅ MotionComponent.update tiene la firma correcta")
        return True
    elif "def update(self" in content:
        print("⚠️  MotionComponent.update existe pero puede tener parámetros incorrectos")
        # Aquí podríamos corregirlo si es necesario
    else:
        print("❌ MotionComponent no tiene método update")
        
    return False

def create_minimal_test():
    """Crear un test mínimo para verificar"""
    print("\n📝 CREANDO TEST MÍNIMO...")
    
    test_code = '''#!/usr/bin/env python3
"""
test_concentration_minimal.py - Test mínimo del sistema
"""

import sys
import os

# Asegurar que podemos importar trajectory_hub
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("1. Importando módulos...")
try:
    from trajectory_hub.core.motion_components import ConcentrationComponent, ConcentrationMode
    print("   ✅ ConcentrationComponent importado")
except Exception as e:
    print(f"   ❌ Error importando ConcentrationComponent: {e}")
    sys.exit(1)

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    print("   ✅ EnhancedTrajectoryEngine importado")
except Exception as e:
    print(f"   ❌ Error importando EnhancedTrajectoryEngine: {e}")
    sys.exit(1)

print("\\n2. Creando engine...")
try:
    engine = EnhancedTrajectoryEngine()
    print("   ✅ Engine creado")
except Exception as e:
    print(f"   ❌ Error creando engine: {e}")
    sys.exit(1)

print("\\n3. Creando macro...")
try:
    macro_id = engine.create_macro("test", 5, formation="circle")
    print(f"   ✅ Macro creado: {macro_id}")
except Exception as e:
    print(f"   ❌ Error creando macro: {e}")
    sys.exit(1)

print("\\n4. Probando concentración...")
try:
    # Establecer concentración
    result = engine.set_macro_concentration(macro_id, 0.5)
    print(f"   ✅ Concentración establecida: {result}")
    
    # Obtener estado
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   ✅ Estado: factor={state.get('factor', 'N/A')}, enabled={state.get('enabled', False)}")
except Exception as e:
    print(f"   ❌ Error en concentración: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\\n5. Probando update...")
try:
    for i in range(5):
        engine.update()
    print("   ✅ Updates ejecutados sin errores")
except Exception as e:
    print(f"   ❌ Error en update: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\\n✅ TODAS LAS PRUEBAS PASARON")
'''
    
    with open("test_concentration_minimal.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
        
    print("✅ test_concentration_minimal.py creado")
    return True

def main():
    print("="*60)
    print("🔧 CORRECCIÓN DE ERRORES DE INTEGRACIÓN")
    print("="*60)
    
    # Aplicar correcciones
    success = True
    success &= fix_enum_import()
    success &= fix_update_method()
    success &= verify_motion_component_update()
    success &= create_minimal_test()
    
    print("\n" + "="*60)
    
    if success:
        print("✅ CORRECCIONES APLICADAS")
        print("\nPróximos pasos:")
        print("1. Ejecutar: python test_concentration_minimal.py")
        print("2. Si pasa, ejecutar: python test_concentration.py")
        print("3. Usar opción 31 en el controlador")
    else:
        print("❌ Algunas correcciones fallaron")
        print("   Revisa los mensajes anteriores")

if __name__ == "__main__":
    main()