#!/usr/bin/env python3
"""
🔧 Fix: Crea/arregla SourceMotion completamente
⚡ Problema: SourceMotion mal formateado o incompleto
🎯 Solución: Verificar y crear correctamente
"""

import re

def find_source_motion():
    """Busca SourceMotion en el archivo"""
    print("🔍 Buscando SourceMotion...")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar cualquier mención de SourceMotion
    if 'class SourceMotion' in content:
        print("✅ SourceMotion encontrado")
        
        # Extraer la clase completa
        match = re.search(r'class SourceMotion.*?(?=\nclass|\n@dataclass|\Z)', content, re.DOTALL)
        if match:
            print("\n📋 Contenido actual de SourceMotion:")
            print("-" * 40)
            print(match.group(0)[:500] + "..." if len(match.group(0)) > 500 else match.group(0))
            print("-" * 40)
        
        return True
    else:
        print("❌ SourceMotion NO encontrado")
        return False

def create_complete_source_motion():
    """Crea SourceMotion completo desde cero"""
    print("\n✨ Creando SourceMotion completo...")
    
    source_motion_code = '''
class SourceMotion:
    """Gestiona el movimiento y componentes de una fuente"""
    
    def __init__(self, source_id: int):
        self.source_id = source_id
        self.state = MotionState()
        self.active_components = []
        self.position = np.zeros(3)
        self.orientation = np.zeros(3)
        
    def add_component(self, component):
        """Añade un componente de movimiento"""
        if component not in self.active_components:
            self.active_components.append(component)
            
    def remove_component(self, component):
        """Elimina un componente"""
        if component in self.active_components:
            self.active_components.remove(component)
            
    def update(self, current_time: float, dt: float) -> MotionState:
        """Actualiza todos los componentes y retorna el estado"""
        for component in self.active_components:
            self.state = component.update(self.state, current_time, dt)
        return self.state
        
    def update_with_deltas(self, current_time: float, dt: float) -> 'MotionDelta':
        """Versión con deltas - retorna cambio incremental"""
        deltas = []
        
        for component in self.active_components:
            if hasattr(component, 'calculate_delta'):
                delta = component.calculate_delta(self.state, current_time, dt)
                deltas.append(delta)
            else:
                # Fallback para componentes sin calculate_delta
                old_pos = self.state.position.copy()
                new_state = component.update(self.state, current_time, dt)
                delta = MotionDelta(
                    position=new_state.position - old_pos,
                    source=component.__class__.__name__
                )
                deltas.append(delta)
                self.state = new_state
        
        # Componer deltas
        if not deltas:
            return MotionDelta()
            
        total_weight = sum(d.weight for d in deltas)
        if total_weight == 0:
            total_weight = 1.0
            
        result = MotionDelta()
        for delta in deltas:
            w = delta.weight / total_weight
            result.position += delta.position * w
            result.orientation += delta.orientation * w
            
        # Actualizar estado interno
        self.state.position += result.position
        self.state.orientation += result.orientation
        
        return result
'''
    
    return source_motion_code

def fix_or_create_source_motion():
    """Arregla o crea SourceMotion según sea necesario"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    if 'class SourceMotion' in content:
        print("\n🔧 Reemplazando SourceMotion existente...")
        
        # Eliminar la clase existente
        pattern = r'class SourceMotion.*?(?=\nclass|\n@dataclass|\Z)'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        
    else:
        print("\n➕ Añadiendo SourceMotion nuevo...")
    
    # Buscar dónde insertar (después de MotionDelta si existe)
    if 'class MotionDelta' in content:
        # Insertar después de MotionDelta
        insert_pattern = r'(class MotionDelta.*?(?=\nclass|\n@dataclass|\Z))'
        replacement = r'\1' + '\n' + create_complete_source_motion()
        content = re.sub(insert_pattern, replacement, content, flags=re.DOTALL)
    else:
        # Insertar al final del archivo
        content += '\n\n' + create_complete_source_motion()
    
    # Guardar
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print("✅ SourceMotion actualizado/creado")

def test_source_motion():
    """Prueba que SourceMotion funciona"""
    print("\n🧪 Probando SourceMotion...")
    
    test_code = '''
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core.motion_components import SourceMotion, ConcentrationComponent, MotionDelta

# Test 1: Crear instancia
print("Test 1: Creación")
sm = SourceMotion(0)
print(f"  ✅ SourceMotion creado con id={sm.source_id}")

# Test 2: Verificar atributos
print("\\nTest 2: Atributos")
attrs = ['state', 'active_components', 'add_component', 'update_with_deltas']
for attr in attrs:
    has_it = hasattr(sm, attr)
    print(f"  {'✅' if has_it else '❌'} {attr}: {'Sí' if has_it else 'No'}")

# Test 3: Añadir componente
print("\\nTest 3: Añadir componente")
cc = ConcentrationComponent()
sm.add_component(cc)
print(f"  ✅ Componentes activos: {len(sm.active_components)}")

# Test 4: update_with_deltas
print("\\nTest 4: Sistema de deltas")
try:
    delta = sm.update_with_deltas(0.0, 0.1)
    print(f"  ✅ Delta generado: {type(delta).__name__}")
except Exception as e:
    print(f"  ❌ Error: {e}")
'''
    
    # Ejecutar test
    try:
        exec(test_code)
        return True
    except Exception as e:
        print(f"\n❌ Error en test: {e}")
        return False

if __name__ == "__main__":
    print("🔧 FIX COMPLETO DE SOURCEMOTION")
    print("=" * 60)
    
    # 1. Buscar estado actual
    find_source_motion()
    
    # 2. Arreglar o crear
    fix_or_create_source_motion()
    
    # 3. Probar
    if test_source_motion():
        print("\n✅ SOURCEMOTION ARREGLADO COMPLETAMENTE")
        print("\n📋 Ahora ejecuta:")
        print("$ python test_delta_working.py")
    else:
        print("\n⚠️ Puede necesitar ajustes adicionales")