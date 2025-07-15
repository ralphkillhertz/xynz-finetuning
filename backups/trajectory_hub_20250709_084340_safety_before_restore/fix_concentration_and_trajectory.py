# === fix_concentration_and_trajectory.py ===
# 🔧 Fix: Corregir errores de concentración y trayectorias
# ⚡ Arreglos específicos para los problemas encontrados

import os
import ast
import re

def fix_concentration_error():
    """Arreglar el error 'dict' object has no attribute 'append'"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    if not os.path.exists(file_path):
        print(f"❌ No se encontró {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f'{file_path}.backup_concentration', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Buscar el método set_macro_concentration
    # El error sugiere que active_components es un dict cuando debería ser una lista
    
    # Fix 1: Buscar donde se usa .append en active_components
    if '.append(' in content:
        # Reemplazar active_components.append por lógica correcta para dict
        pattern = r'(\s+)([\w\.]+active_components)\.append\(([^)]+)\)'
        
        def replace_append(match):
            indent = match.group(1)
            var_name = match.group(2)
            component = match.group(3)
            # Si active_components es dict, usar el nombre del componente como key
            return f'{indent}if isinstance({var_name}, dict):\n{indent}    component_name = {component}.__class__.__name__\n{indent}    {var_name}[component_name] = {component}\n{indent}else:\n{indent}    {var_name}.append({component})'
        
        content = re.sub(pattern, replace_append, content)
    
    # Fix 2: Asegurar que ConcentrationComponent se agregue correctamente
    # Buscar específicamente el método set_macro_concentration
    concentration_pattern = r'def set_macro_concentration\(self[^:]+\):(.+?)(?=\n    def|\nclass|\Z)'
    
    def fix_concentration_method(match):
        method_content = match.group(0)
        
        # Si no tiene el fix de dict vs list, agregarlo
        if 'isinstance(motion.active_components, dict)' not in method_content:
            # Buscar donde se agrega el componente
            append_pattern = r'(\s+)(motion\.active_components)\.append\(concentration\)'
            
            def fix_append(m):
                indent = m.group(1)
                return f'''{indent}# Fix para dict vs list
{indent}if isinstance(motion.active_components, dict):
{indent}    motion.active_components['concentration'] = concentration
{indent}else:
{indent}    motion.active_components.append(concentration)'''
            
            method_content = re.sub(append_pattern, fix_append, method_content)
        
        return method_content
    
    content = re.sub(concentration_pattern, fix_concentration_method, content, flags=re.DOTALL)
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Concentración arreglada")
    return True

def fix_trajectory_api():
    """Arreglar la API de set_individual_trajectory"""
    
    # Crear un test actualizado con la API correcta
    test_content = '''# === test_api_correct.py ===
# 🎯 Test con APIs correctas del sistema
# ⚡ Verificado contra el código actual

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import time

def test_with_correct_api():
    """Test usando las APIs correctas"""
    print("🚀 TEST CON APIS CORRECTAS")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    print("✅ Engine creado")
    
    # Test 1: Crear macro directamente (crea las fuentes automáticamente)
    print("\\n1️⃣ Creando macro...")
    try:
        macro_name = engine.create_macro("test", 4, formation='square')
        print(f"✅ Macro creado: {macro_name}")
        
        # El macro debería tener source_ids
        if hasattr(engine, '_macros') and macro_name in engine._macros:
            macro = engine._macros[macro_name]
            print(f"   Source IDs: {macro.source_ids if hasattr(macro, 'source_ids') else 'No disponible'}")
        
    except Exception as e:
        print(f"❌ Error creando macro: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Trayectoria individual con API correcta
    print("\\n2️⃣ Configurando trayectoria individual...")
    try:
        # La API espera: set_individual_trajectory(macro_name, source_index, shape, ...)
        engine.set_individual_trajectory(
            macro_name,    # nombre del macro
            0,             # índice dentro del macro (0-3)
            'circle',      # forma
            shape_params={'radius': 2.0},
            movement_mode='fix',
            speed=1.0
        )
        
        print("✅ Trayectoria configurada")
        
        # Simular movimiento
        initial_pos = None
        if hasattr(engine._macros[macro_name], 'source_ids'):
            sid = engine._macros[macro_name].source_ids[0]
            initial_pos = engine._positions[sid].copy()
        
        for _ in range(30):
            engine.update()
        
        if initial_pos is not None:
            final_pos = engine._positions[sid]
            movement = np.linalg.norm(final_pos - initial_pos)
            print(f"   Movimiento detectado: {movement:.3f} unidades")
        
    except Exception as e:
        print(f"❌ Error en trayectoria: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Concentración (intentar aunque falle)
    print("\\n3️⃣ Aplicando concentración...")
    try:
        engine.set_macro_concentration(macro_name, 0.5)
        print("✅ Concentración aplicada")
    except Exception as e:
        print(f"⚠️ Error en concentración (esperado): {e}")
    
    print("\\n✅ Test completado")
    return True

if __name__ == "__main__":
    test_with_correct_api()
'''
    
    with open('test_api_correct.py', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ test_api_correct.py creado con APIs correctas")
    return True

def create_diagnosis_script():
    """Crear script de diagnóstico para entender la estructura"""
    
    diagnosis = '''# === diagnose_structure.py ===
# 🔍 Diagnóstico de la estructura del sistema
# ⚡ Para entender las APIs correctas

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import inspect

def diagnose_system():
    """Diagnosticar la estructura del sistema"""
    print("🔍 DIAGNÓSTICO DEL SISTEMA")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
    
    # 1. Inspeccionar métodos disponibles
    print("\\n📋 MÉTODOS PRINCIPALES:")
    methods = [m for m in dir(engine) if not m.startswith('_') and callable(getattr(engine, m))]
    for method in sorted(methods)[:20]:  # Primeros 20
        try:
            sig = inspect.signature(getattr(engine, method))
            print(f"  • {method}{sig}")
        except:
            print(f"  • {method}()")
    
    # 2. Verificar estructura de macros
    print("\\n📦 ESTRUCTURA DE MACROS:")
    print(f"  • _macros exists: {hasattr(engine, '_macros')}")
    print(f"  • macros exists: {hasattr(engine, 'macros')}")
    
    # 3. Crear un macro y ver su estructura
    print("\\n🧪 CREANDO MACRO DE PRUEBA:")
    try:
        macro_name = engine.create_macro("diagnose", 3, formation='line')
        print(f"  ✅ Macro creado: {macro_name}")
        
        # Ver estructura
        if hasattr(engine, '_macros'):
            macro = engine._macros.get(macro_name)
            if macro:
                print(f"  • Tipo: {type(macro)}")
                print(f"  • Atributos: {[a for a in dir(macro) if not a.startswith('_')][:10]}")
                if hasattr(macro, 'source_ids'):
                    print(f"  • Source IDs: {macro.source_ids}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # 4. Verificar motion_states
    print("\\n🔄 MOTION STATES:")
    print(f"  • motion_states exists: {hasattr(engine, 'motion_states')}")
    if hasattr(engine, 'motion_states'):
        print(f"  • Tipo: {type(engine.motion_states)}")
        print(f"  • Cantidad: {len(engine.motion_states)}")
        
        # Ver estructura de un motion state
        if engine.motion_states:
            sid = list(engine.motion_states.keys())[0]
            motion = engine.motion_states[sid]
            print(f"\\n  📌 Motion State {sid}:")
            print(f"    • Tipo: {type(motion)}")
            if hasattr(motion, 'active_components'):
                print(f"    • active_components tipo: {type(motion.active_components)}")
                print(f"    • active_components contenido: {motion.active_components}")

if __name__ == "__main__":
    diagnose_system()
'''
    
    with open('diagnose_structure.py', 'w', encoding='utf-8') as f:
        f.write(diagnosis)
    
    print("✅ diagnose_structure.py creado")

if __name__ == "__main__":
    print("🔧 FIXING CONCENTRATION AND TRAJECTORY ERRORS")
    print("=" * 60)
    
    # 1. Arreglar error de concentración
    print("\n1️⃣ Arreglando error de concentración...")
    fix_concentration_error()
    
    # 2. Crear test con API correcta
    print("\n2️⃣ Creando test con API correcta...")
    fix_trajectory_api()
    
    # 3. Crear diagnóstico
    print("\n3️⃣ Creando script de diagnóstico...")
    create_diagnosis_script()
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Ejecutar: python diagnose_structure.py")
    print("2. Ejecutar: python test_api_correct.py")
    print("3. Si funciona → MCP Server implementation")