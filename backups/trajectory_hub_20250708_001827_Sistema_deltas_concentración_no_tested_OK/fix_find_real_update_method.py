# === fix_find_real_update_method.py ===
# 🔍 Encuentra qué método realmente actualiza el sistema
# ⚡ Debug completo del flujo de actualización

import os
import re
import ast

def find_all_methods():
    """Encuentra TODOS los métodos en EnhancedTrajectoryEngine"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return []
    
    print("🔍 Analizando EnhancedTrajectoryEngine...")
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la clase
    class_pattern = r'class EnhancedTrajectoryEngine[^:]*:(.*?)(?=\nclass|\Z)'
    class_match = re.search(class_pattern, content, re.DOTALL)
    
    if not class_match:
        print("❌ No se encuentra la clase EnhancedTrajectoryEngine")
        return []
    
    # Buscar todos los métodos
    methods = []
    method_pattern = r'def (\w+)\(self[^)]*\):'
    for match in re.finditer(method_pattern, class_match.group(1)):
        methods.append(match.group(1))
    
    print(f"\n📋 Métodos encontrados: {len(methods)}")
    
    # Categorizar
    update_methods = []
    for method in methods:
        keywords = ['update', 'step', 'tick', 'advance', 'process', 'run', 'execute']
        for keyword in keywords:
            if keyword in method.lower():
                update_methods.append(method)
                break
    
    print(f"\n🔄 Métodos relacionados con actualización:")
    for method in update_methods:
        print(f"  - {method}")
    
    return methods, update_methods, content

def check_test_implementation():
    """Verifica cómo el test llama al engine"""
    
    test_path = "test_delta_minimal.py"
    
    if not os.path.exists(test_path):
        print("❌ No existe test_delta_minimal.py")
        return None
    
    print("\n🧪 Analizando test_delta_minimal.py...")
    
    with open(test_path, 'r', encoding='utf-8') as f:
        test_content = f.read()
    
    # Buscar llamadas a engine
    engine_calls = re.findall(r'engine\.(\w+)\(', test_content)
    
    print(f"📋 Llamadas a engine encontradas:")
    for call in set(engine_calls):
        print(f"  - engine.{call}()")
    
    return engine_calls

def create_comprehensive_fix():
    """Crea un fix comprehensivo basado en el análisis"""
    
    # Analizar
    methods, update_methods, content = find_all_methods()
    test_calls = check_test_implementation()
    
    print("\n🔧 Creando fix comprehensivo...")
    
    # Si step está en las llamadas del test pero no existe
    if test_calls and 'step' in test_calls and 'step' not in methods:
        print("⚠️ El test llama a step() pero NO existe!")
        print("🔧 Creando step() que delegue a update()...")
        
        fix_code = '''# === fix_add_step_method.py ===
# Añade método step() que faltaba

import os
from datetime import datetime

def add_step_method():
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Buscar dónde insertar (después de update)
    insert_pos = content.find('def update(')
    if insert_pos > -1:
        # Buscar el final del método update
        next_def = content.find('\\n    def ', insert_pos + 10)
        if next_def > -1:
            insert_pos = next_def
        else:
            insert_pos = len(content)
    else:
        # Después de __init__
        insert_pos = content.find('def __init__')
        next_def = content.find('\\n    def ', insert_pos + 10)
        if next_def > -1:
            insert_pos = next_def
    
    # Método step
    step_method = """
    def step(self) -> None:
        \"\"\"Ejecuta un paso de simulación\"\"\"
        if hasattr(self, 'update'):
            self.update()
        else:
            # Implementación directa si no hay update
            if not self.running:
                return
            
            current_time = time.time()
            dt = 1.0 / self._update_rate
            
            # Sistema de deltas
            all_deltas = []
            
            for source_id, motion in self.motion_states.items():
                if hasattr(motion, 'update_with_deltas'):
                    deltas = motion.update_with_deltas(current_time, dt)
                    if deltas:
                        all_deltas.extend(deltas)
            
            # Aplicar deltas
            for delta in all_deltas:
                if delta.source_id < len(self._positions):
                    if delta.position is not None:
                        self._positions[delta.source_id] += delta.position
"""
    
    # Insertar
    content = content[:insert_pos] + step_method + content[insert_pos:]
    
    # Añadir import time si no existe
    if 'import time' not in content:
        content = 'import time\\n' + content
    
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Método step() añadido")

if __name__ == "__main__":
    add_step_method()
'''
        
        with open('fix_add_step_method.py', 'w') as f:
            f.write(fix_code)
        
        print("\n✅ Script creado: fix_add_step_method.py")
        print("📋 Ejecuta: python fix_add_step_method.py")
    
    elif 'update' in methods:
        print("✅ Existe método update")
        print("🔍 Verificando si update tiene el código de deltas...")
        
        # Verificar si update tiene deltas
        update_pattern = r'def update\(self[^)]*\):(.*?)(?=\n\s{0,4}def|\Z)'
        update_match = re.search(update_pattern, content, re.DOTALL)
        
        if update_match and 'update_with_deltas' not in update_match.group(1):
            print("❌ update NO tiene código de deltas")
            print("📋 Ejecuta: python fix_find_update_method.py")

def create_debug_test():
    """Crea un test con más debug"""
    
    test_code = '''# === test_debug_flow.py ===
# Test con debug detallado del flujo

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent
import numpy as np

print("🔍 TEST DEBUG DETALLADO")
print("="*50)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=3)
engine.running = True

# Verificar métodos disponibles
print("\\n📋 Métodos disponibles en engine:")
methods = [m for m in dir(engine) if not m.startswith('_') and callable(getattr(engine, m))]
update_methods = [m for m in methods if any(k in m.lower() for k in ['update', 'step', 'tick', 'run'])]
print(f"  Métodos de actualización: {update_methods}")

# Crear fuente
engine.create_source(0, "test")
engine._positions[0] = np.array([10.0, 0.0, 0.0])

# Añadir concentración
motion = engine.motion_states[0]
comp = ConcentrationComponent()
comp.enabled = True
comp.concentration_factor = 0.8
comp.concentration_center = np.array([0.0, 0.0, 0.0])
motion.add_component(comp, 'concentration')

print(f"\\n📍 Posición inicial: {engine._positions[0]}")

# Probar diferentes métodos
for method_name in ['step', 'update', 'tick', 'run']:
    if hasattr(engine, method_name):
        print(f"\\n🔄 Llamando engine.{method_name}()...")
        method = getattr(engine, method_name)
        try:
            method()
            print(f"  ✅ {method_name}() ejecutado")
            print(f"  📍 Posición después: {engine._positions[0]}")
            
            if not np.array_equal(engine._positions[0], [10.0, 0.0, 0.0]):
                print(f"  🎯 ¡FUNCIONA con {method_name}()!")
                break
        except Exception as e:
            print(f"  ❌ Error: {e}")
    else:
        print(f"\\n❌ No existe engine.{method_name}()")
'''
    
    with open('test_debug_flow.py', 'w') as f:
        f.write(test_code)
    
    print("\n✅ Test de debug creado: test_debug_flow.py")

if __name__ == "__main__":
    print("🔧 ANÁLISIS COMPLETO DEL SISTEMA")
    print("="*60)
    
    # Análisis
    find_all_methods()
    check_test_implementation()
    
    # Crear fix
    create_comprehensive_fix()
    
    # Crear test debug
    create_debug_test()
    
    print("\n📋 Ejecuta el test de debug para ver qué métodos existen:")
    print("$ python test_debug_flow.py")