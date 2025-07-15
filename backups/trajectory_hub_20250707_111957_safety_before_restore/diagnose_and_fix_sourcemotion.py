#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO Y FIX: SourceMotion
"""

import os
import sys
import ast

print("""
================================================================================
🔍 DIAGNOSTICANDO SOURCEMOTION
================================================================================
""")

# 1. Buscar motion_components.py
motion_file = "trajectory_hub/core/motion_components.py"

if not os.path.exists(motion_file):
    print(f"❌ No se encuentra {motion_file}")
    sys.exit(1)

# 2. Analizar la estructura de SourceMotion
with open(motion_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar la clase SourceMotion
import re
class_pattern = r'class SourceMotion.*?(?=\nclass|\Z)'
match = re.search(class_pattern, content, re.DOTALL)

if match:
    print("✅ Clase SourceMotion encontrada")
    
    # Buscar métodos existentes
    class_content = match.group(0)
    methods = re.findall(r'def (\w+)\(self', class_content)
    print(f"\n📋 Métodos encontrados: {methods}")
    
    # Buscar atributos
    if 'concentration_offset' in class_content:
        print("✅ concentration_offset existe")
    
    # Verificar si faltan métodos getter
    needs_getters = False
    if 'get_position' not in methods:
        print("❌ Falta get_position()")
        needs_getters = True
    if 'get_orientation' not in methods:
        print("❌ Falta get_orientation()")
        needs_getters = True
    if 'get_aperture' not in methods:
        print("❌ Falta get_aperture()")
        needs_getters = True
        
    if needs_getters:
        print("\n🔨 AÑADIENDO MÉTODOS GETTER...")
        
        # Buscar donde insertar (antes del final de la clase)
        getter_code = '''
    def get_position(self) -> np.ndarray:
        """Obtener posición actual con offsets aplicados"""
        base_pos = self.state.position
        total_offset = np.zeros(3)
        
        # Aplicar todos los offsets
        if hasattr(self, 'concentration_offset'):
            total_offset += self.concentration_offset
        if hasattr(self, 'distribution_offset'):
            total_offset += self.distribution_offset
        if hasattr(self, 'trajectory_offset'):
            total_offset += self.trajectory_offset
            
        return base_pos + total_offset
    
    def get_orientation(self) -> np.ndarray:
        """Obtener orientación actual"""
        return self.state.orientation
    
    def get_aperture(self) -> float:
        """Obtener apertura actual"""
        return self.state.aperture
'''
        
        # Insertar antes del final de la clase
        # Buscar el último método de la clase
        last_method = re.findall(r'(\n    def \w+.*?)(?=\n(?:class|\s*$))', class_content, re.DOTALL)
        if last_method:
            insert_point = class_content.rfind(last_method[-1]) + len(last_method[-1])
            new_class = class_content[:insert_point] + getter_code + class_content[insert_point:]
            
            # Reemplazar en el contenido completo
            content = content.replace(class_content, new_class)
            
            # Guardar
            import datetime
            backup_name = motion_file + f".backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_name, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n📋 Backup: {backup_name}")
            
            with open(motion_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Archivo actualizado: {motion_file}")
            
else:
    print("❌ No se encontró clase SourceMotion")

# 3. Crear test mejorado
test_code = '''#!/usr/bin/env python3
"""
🧪 TEST MEJORADO: Concentración con getters correctos
"""

import os
import sys
import numpy as np

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    from trajectory_hub.core.motion_components import SourceMotion
    
    print("\\n🧪 TEST DE CONCENTRACIÓN\\n")
    
    # Verificar que SourceMotion tiene los métodos necesarios
    print("📋 Verificando SourceMotion...")
    sm = SourceMotion(0)
    if hasattr(sm, 'get_position'):
        print("   ✅ get_position() existe")
    else:
        print("   ❌ get_position() NO existe")
        
    # Crear engine y macro
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=3.0)
    
    # Obtener posiciones iniciales
    print("\\n📍 POSICIONES INICIALES:")
    initial_positions = {}
    for sid in engine._source_motions:
        if sid < 4:
            motion = engine._source_motions[sid]
            # Intentar diferentes formas de obtener la posición
            if hasattr(motion, 'get_position'):
                pos = motion.get_position()
            elif hasattr(motion, 'state') and hasattr(motion.state, 'position'):
                pos = motion.state.position.copy()
            else:
                pos = engine._positions[sid]
            initial_positions[sid] = pos.copy()
            print(f"   Fuente {sid}: {pos}")
    
    # Calcular centro
    if initial_positions:
        center = np.mean(list(initial_positions.values()), axis=0)
        print(f"\\n📍 Centro del macro: {center}")
    
    # Aplicar concentración
    print("\\n🎯 APLICANDO CONCENTRACIÓN (factor=0.05)...")
    engine.set_macro_concentration(macro_id, 0.05)
    
    # Verificar que se aplicaron offsets
    print("\\n🔍 VERIFICANDO OFFSETS:")
    for sid in initial_positions:
        motion = engine._source_motions[sid]
        if hasattr(motion, 'concentration_offset'):
            offset = motion.concentration_offset
            magnitude = np.linalg.norm(offset)
            print(f"   Fuente {sid}: offset={offset}, magnitud={magnitude:.4f}")
    
    # Simular varios frames
    print("\\n🔄 EJECUTANDO 30 FRAMES...")
    for i in range(30):
        state = engine.step()
        if i % 10 == 0:
            print(f"   Frame {i}")
    
    # Verificar posiciones finales
    print("\\n📍 POSICIONES FINALES:")
    final_positions = {}
    movements = []
    
    for sid in initial_positions:
        # Obtener posición final
        if hasattr(engine._source_motions[sid], 'get_position'):
            pos = engine._source_motions[sid].get_position()
        else:
            pos = engine._positions[sid]
            
        final_positions[sid] = pos
        movement = np.linalg.norm(pos - initial_positions[sid])
        movements.append(movement)
        
        print(f"   Fuente {sid}: {pos}")
        print(f"      Movimiento total: {movement:.4f}")
    
    # Análisis
    print("\\n📊 ANÁLISIS:")
    if movements:
        avg_movement = np.mean(movements)
        print(f"   Movimiento promedio: {avg_movement:.4f}")
        
        # Calcular dispersión
        initial_dispersion = np.std([p for p in initial_positions.values()])
        final_dispersion = np.std([p for p in final_positions.values()])
        
        print(f"   Dispersión inicial: {initial_dispersion:.4f}")
        print(f"   Dispersión final: {final_dispersion:.4f}")
        
        if avg_movement > 0.01:
            print("\\n✅ ¡ÉXITO! Las fuentes se concentraron")
            if final_dispersion < initial_dispersion * 0.9:
                print("✅ La dispersión se redujo significativamente")
        else:
            print("\\n❌ Las fuentes NO se movieron")
            
except Exception as e:
    print(f"\\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\\n" + "="*60)
'''

with open("test_concentration_complete.py", 'w', encoding='utf-8') as f:
    f.write(test_code)

print(f"\n✅ Test creado: test_concentration_complete.py")

print("""
================================================================================
🔧 DIAGNÓSTICO COMPLETADO
================================================================================

🚀 EJECUTA EL TEST:
   python test_concentration_complete.py

💡 Si aún falla, podemos acceder directamente a:
   - motion.state.position (posición base)
   - motion.concentration_offset (offset de concentración)
   - engine._positions[sid] (posición en el array global)

🎯 El test verificará todas las formas posibles de obtener posiciones
================================================================================
""")