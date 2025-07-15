#!/usr/bin/env python3
"""
🔧 FIX FINAL: Reemplazo directo y robusto
"""

import os
import sys

print("""
================================================================================
🔧 FIX FINAL DE CONCENTRACIÓN
================================================================================
""")

# 1. Verificar contenido actual de set_macro_concentration
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

print("📋 VERIFICANDO CONTENIDO ACTUAL...")

with open(engine_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar línea por línea
in_method = False
method_start = -1
method_end = -1
indent_level = 0

for i, line in enumerate(lines):
    if 'def set_macro_concentration' in line:
        in_method = True
        method_start = i
        indent_level = len(line) - len(line.lstrip())
        print(f"✅ Encontrado set_macro_concentration en línea {i+1}")
        
    elif in_method:
        # Detectar fin del método
        current_indent = len(line) - len(line.lstrip())
        
        # Si encontramos otra función al mismo nivel o clase
        if line.strip() and current_indent <= indent_level and ('def ' in line or 'class ' in line):
            method_end = i
            break
            
# Si no encontramos el final, usar el final del archivo
if method_start >= 0 and method_end == -1:
    method_end = len(lines)

if method_start >= 0:
    print(f"📍 Método encontrado: líneas {method_start+1} a {method_end}")
    
    # Mostrar contenido actual
    print("\n📄 CONTENIDO ACTUAL:")
    print("".join(lines[method_start:method_start+5]))
    print("...")
    
    # REEMPLAZAR con implementación correcta
    new_method = '''    def set_macro_concentration(self, macro_id: str, concentration_factor: float):
        """
        Establece el factor de concentración para un macro.
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        concentration_factor : float
            Factor de concentración (0=sin cambio, 1=máxima concentración)
        """
        import numpy as np
        
        if macro_id not in self._macros:
            return
            
        macro = self._macros[macro_id]
        macro.concentration_factor = concentration_factor
        
        if not macro.source_ids:
            return
        
        # Calcular centro del macro
        positions = []
        for sid in macro.source_ids:
            if sid in self._source_motions:
                motion = self._source_motions[sid]
                positions.append(motion.state.position.copy())
        
        if not positions:
            return
            
        center = np.mean(positions, axis=0)
        
        # Aplicar offset a cada fuente
        for i, sid in enumerate(macro.source_ids):
            if sid in self._source_motions:
                motion = self._source_motions[sid]
                
                # Vector desde la fuente hacia el centro
                direction = center - positions[i]
                
                # Aplicar factor
                motion.concentration_offset = direction * concentration_factor
'''
    
    # Reemplazar líneas
    new_lines = lines[:method_start] + [new_method + '\n'] + lines[method_end:]
    
    # Guardar backup
    import datetime
    backup_name = engine_file + f".backup_final_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_name, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"\n📋 Backup: {backup_name}")
    
    # Guardar cambios
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"✅ set_macro_concentration actualizado")
    
else:
    print("❌ No se encontró set_macro_concentration")

# 2. Arreglar get_position en SourceMotion
print("\n🔧 ARREGLANDO get_position()...")

motion_file = "trajectory_hub/core/motion_components.py"
with open(motion_file, 'r', encoding='utf-8') as f:
    motion_lines = f.readlines()

# Buscar SourceMotion
in_sourcemotion = False
class_start = -1
get_position_exists = False

for i, line in enumerate(motion_lines):
    if 'class SourceMotion' in line:
        in_sourcemotion = True
        class_start = i
        print(f"✅ SourceMotion encontrado en línea {i+1}")
        
    elif in_sourcemotion and 'def get_position' in line:
        get_position_exists = True
        print("✅ get_position ya existe")
        break
        
    elif in_sourcemotion and 'class ' in line and class_start > 0:
        # Fin de SourceMotion
        break

if not get_position_exists and class_start >= 0:
    print("❌ get_position no existe, añadiendo...")
    
    # Buscar dónde insertar (después del último método)
    last_method_line = class_start
    in_class = False
    
    for i in range(class_start, len(motion_lines)):
        line = motion_lines[i]
        
        if i == class_start:
            in_class = True
            continue
            
        if in_class:
            # Si encontramos otra clase, parar
            if line.strip().startswith('class '):
                break
                
            # Si es un método, actualizar última posición
            if line.strip().startswith('def '):
                last_method_line = i
                
    # Buscar el final del último método
    indent = 4  # Asumiendo 4 espacios
    insert_line = last_method_line + 1
    
    for i in range(last_method_line + 1, len(motion_lines)):
        line = motion_lines[i]
        if line.strip() and not line.startswith(' ' * 8):  # Fin del método
            insert_line = i
            break
    
    # Insertar get_position
    new_get_position = '''
    def get_position(self):
        """Obtener posición actual con offsets aplicados"""
        import numpy as np
        pos = self.state.position.copy()
        
        if hasattr(self, 'concentration_offset'):
            pos = pos + self.concentration_offset
        if hasattr(self, 'distribution_offset'):
            pos = pos + self.distribution_offset
        if hasattr(self, 'trajectory_offset'):
            pos = pos + self.trajectory_offset
            
        return pos
    
    def get_orientation(self):
        """Obtener orientación actual"""
        return self.state.orientation
    
    def get_aperture(self):
        """Obtener apertura actual"""
        return self.state.aperture
'''
    
    motion_lines.insert(insert_line, new_get_position)
    
    # Guardar
    with open(motion_file, 'w', encoding='utf-8') as f:
        f.writelines(motion_lines)
    print("✅ get_position añadido a SourceMotion")

# 3. Test final integrado
test_code = '''#!/usr/bin/env python3
"""
🧪 TEST INTEGRADO FINAL
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

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("\\n🧪 TEST FINAL INTEGRADO\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Crear macro
macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=5.0)

# Guardar posiciones iniciales
print("📍 POSICIONES INICIALES:")
initial_positions = {}
for sid in range(4):
    if sid in engine._source_motions:
        pos = engine._source_motions[sid].state.position.copy()
        initial_positions[sid] = pos
        print(f"   Fuente {sid}: {pos}")

# Calcular centro esperado
center = np.mean(list(initial_positions.values()), axis=0)
print(f"\\n📍 Centro del macro: {center}")

# Aplicar concentración
factor = 0.3
print(f"\\n🎯 Aplicando concentración factor={factor}...")
engine.set_macro_concentration(macro_id, factor)

# Verificar offsets
print("\\n🔍 OFFSETS APLICADOS:")
has_offsets = False
for sid in range(4):
    if sid in engine._source_motions:
        motion = engine._source_motions[sid]
        offset = motion.concentration_offset
        mag = np.linalg.norm(offset)
        if mag > 0:
            has_offsets = True
        print(f"   Fuente {sid}: offset={offset}, magnitud={mag:.4f}")

if not has_offsets:
    print("\\n❌ ERROR: Los offsets siguen en cero")
    sys.exit(1)

# Ejecutar simulación
print("\\n🔄 EJECUTANDO 100 FRAMES...")
for i in range(100):
    engine.step()
    
    if (i + 1) % 25 == 0:
        # Mostrar progreso
        pos0 = engine._positions[0] if hasattr(engine, '_positions') else engine._source_motions[0].get_position()
        print(f"   Frame {i+1}: Fuente 0 en {pos0}")

# Calcular resultados
print("\\n📊 RESULTADOS FINALES:")
total_movement = 0
final_positions = {}

for sid in initial_positions:
    # Obtener posición final
    if hasattr(engine._source_motions[sid], 'get_position'):
        final_pos = engine._source_motions[sid].get_position()
    else:
        final_pos = engine._positions[sid]
    
    final_positions[sid] = final_pos
    movement = np.linalg.norm(final_pos - initial_positions[sid])
    total_movement += movement
    
    print(f"   Fuente {sid}:")
    print(f"      Inicial: {initial_positions[sid]}")
    print(f"      Final:   {final_pos}")
    print(f"      Movimiento: {movement:.4f}")

# Verificar concentración
initial_dispersion = np.std(list(initial_positions.values()))
final_dispersion = np.std(list(final_positions.values()))

print(f"\\n📊 ANÁLISIS DE CONCENTRACIÓN:")
print(f"   Dispersión inicial: {initial_dispersion:.4f}")
print(f"   Dispersión final:   {final_dispersion:.4f}")
print(f"   Reducción:          {(1 - final_dispersion/initial_dispersion)*100:.1f}%")

if total_movement > 0.1:
    print(f"\\n✅ ¡ÉXITO! Las fuentes se movieron")
    if final_dispersion < initial_dispersion:
        print("✅ ¡LA CONCENTRACIÓN FUNCIONA!")
        print("\\n🚀 Ahora prueba el controlador interactivo:")
        print("   python trajectory_hub/interface/interactive_controller.py")
else:
    print(f"\\n❌ Las fuentes no se movieron lo suficiente")

print("\\n" + "="*60)
'''

with open("test_integrated_final.py", 'w', encoding='utf-8') as f:
    f.write(test_code)

print(f"\n✅ Test creado: test_integrated_final.py")

print("""
================================================================================
✅ FIX FINAL APLICADO
================================================================================

🔧 Cambios realizados:
   1. Reemplazo completo de set_macro_concentration (sin regex)
   2. Añadido get_position() a SourceMotion si faltaba
   3. Test integrado que verifica todo el flujo

🚀 EJECUTA:
   python test_integrated_final.py

💡 Este test verificará:
   - Que los offsets se calculan (> 0)
   - Que las fuentes se mueven
   - Que la dispersión se reduce

🎯 Si funciona, la concentración estará lista para Spat!
================================================================================
""")