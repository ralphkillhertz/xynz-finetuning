#!/usr/bin/env python3
"""
🔧 FIX: Arreglar cálculo de concentración
⚡ Los offsets están en 0 porque no se calculan correctamente
"""

import os
import sys
import re

print("""
================================================================================
🔧 ARREGLANDO CÁLCULO DE CONCENTRACIÓN
================================================================================
""")

# 1. Buscar enhanced_trajectory_engine.py
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

if not os.path.exists(engine_file):
    print(f"❌ No se encuentra {engine_file}")
    sys.exit(1)

# 2. Leer el archivo
with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 3. Buscar set_macro_concentration
concentration_pattern = r'def set_macro_concentration\(self.*?\):(.*?)(?=\n    def|\n\s*$|\nclass)'
match = re.search(concentration_pattern, content, re.DOTALL)

if match:
    print("✅ Método set_macro_concentration encontrado")
    method_content = match.group(0)
    
    # Verificar si calcula offsets
    if 'concentration_offset' in method_content:
        print("✅ concentration_offset se menciona")
    else:
        print("❌ concentration_offset NO se menciona")
    
    print("\n🔨 REEMPLAZANDO método set_macro_concentration...")
    
    # Método corregido
    new_method = '''def set_macro_concentration(self, macro_id: str, concentration_factor: float):
        """
        Establece el factor de concentración para un macro.
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        concentration_factor : float
            Factor de concentración (0=sin cambio, 1=máxima concentración)
        """
        if macro_id not in self._macros:
            print(f"⚠️ Macro {macro_id} no encontrado")
            return
            
        macro = self._macros[macro_id]
        macro.concentration_factor = concentration_factor
        
        if not macro.source_ids:
            print("⚠️ Macro sin fuentes")
            return
        
        # Calcular centro del macro
        positions = []
        for sid in macro.source_ids:
            if sid in self._source_motions:
                motion = self._source_motions[sid]
                # Obtener posición base (sin offsets)
                positions.append(motion.state.position.copy())
            elif sid < len(self._positions):
                positions.append(self._positions[sid].copy())
        
        if not positions:
            print("⚠️ No se encontraron posiciones")
            return
            
        import numpy as np
        center = np.mean(positions, axis=0)
        
        print(f"\\n🎯 Aplicando concentración {concentration_factor} al macro {macro_id}")
        print(f"   Centro: {center}")
        print(f"   Fuentes: {len(positions)}")
        
        # Aplicar offset a cada fuente
        for i, sid in enumerate(macro.source_ids):
            if sid in self._source_motions:
                motion = self._source_motions[sid]
                
                # Vector desde la fuente hacia el centro
                direction = center - positions[i]
                distance = np.linalg.norm(direction)
                
                if distance > 0.001:  # Evitar división por cero
                    # Normalizar y aplicar factor
                    direction_normalized = direction / distance
                    offset_magnitude = distance * concentration_factor
                    
                    # Establecer el offset
                    motion.concentration_offset = direction_normalized * offset_magnitude
                    
                    print(f"   Fuente {sid}: offset magnitud = {offset_magnitude:.4f}")
                else:
                    motion.concentration_offset = np.zeros(3)
                    print(f"   Fuente {sid}: ya está en el centro")'''
    
    # Reemplazar
    content = re.sub(concentration_pattern, new_method, content, count=1)
    
else:
    print("❌ No se encontró set_macro_concentration")
    print("\n🔨 CREANDO método set_macro_concentration...")
    
    # Buscar donde insertar (después de create_macro)
    create_macro_match = re.search(r'(def create_macro\(self.*?\n(?:.*?\n)*?)(\n    def|\n\s*$|\nclass)', content, re.DOTALL)
    
    if create_macro_match:
        new_method = '''
    def set_macro_concentration(self, macro_id: str, concentration_factor: float):
        """
        Establece el factor de concentración para un macro.
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        concentration_factor : float
            Factor de concentración (0=sin cambio, 1=máxima concentración)
        """
        if macro_id not in self._macros:
            print(f"⚠️ Macro {macro_id} no encontrado")
            return
            
        macro = self._macros[macro_id]
        macro.concentration_factor = concentration_factor
        
        if not macro.source_ids:
            print("⚠️ Macro sin fuentes")
            return
        
        # Calcular centro del macro
        positions = []
        for sid in macro.source_ids:
            if sid in self._source_motions:
                motion = self._source_motions[sid]
                # Obtener posición base (sin offsets)
                positions.append(motion.state.position.copy())
            elif sid < len(self._positions):
                positions.append(self._positions[sid].copy())
        
        if not positions:
            print("⚠️ No se encontraron posiciones")
            return
            
        import numpy as np
        center = np.mean(positions, axis=0)
        
        print(f"\\n🎯 Aplicando concentración {concentration_factor} al macro {macro_id}")
        print(f"   Centro: {center}")
        print(f"   Fuentes: {len(positions)}")
        
        # Aplicar offset a cada fuente
        for i, sid in enumerate(macro.source_ids):
            if sid in self._source_motions:
                motion = self._source_motions[sid]
                
                # Vector desde la fuente hacia el centro
                direction = center - positions[i]
                distance = np.linalg.norm(direction)
                
                if distance > 0.001:  # Evitar división por cero
                    # Normalizar y aplicar factor
                    direction_normalized = direction / distance
                    offset_magnitude = distance * concentration_factor
                    
                    # Establecer el offset
                    motion.concentration_offset = direction_normalized * offset_magnitude
                    
                    print(f"   Fuente {sid}: offset magnitud = {offset_magnitude:.4f}")
                else:
                    motion.concentration_offset = np.zeros(3)
                    print(f"   Fuente {sid}: ya está en el centro")
'''
        
        # Insertar
        insert_pos = create_macro_match.end(1)
        content = content[:insert_pos] + new_method + content[insert_pos:]

# 4. Guardar
import datetime
backup_name = engine_file + f".backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_name, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\n📋 Backup: {backup_name}")

with open(engine_file, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"✅ Archivo actualizado: {engine_file}")

# 5. Arreglar get_position en SourceMotion
motion_file = "trajectory_hub/core/motion_components.py"
print(f"\n🔧 Arreglando get_position en {motion_file}...")

with open(motion_file, 'r', encoding='utf-8') as f:
    motion_content = f.read()

# Buscar get_position existente
get_pos_pattern = r'def get_position\(self.*?\):(.*?)(?=\n    def|\n\s*$|\nclass)'
get_pos_match = re.search(get_pos_pattern, motion_content, re.DOTALL)

if get_pos_match:
    print("✅ get_position encontrado, actualizando...")
    
    # Reemplazar con versión correcta
    new_get_position = '''def get_position(self) -> np.ndarray:
        """Obtener posición actual con offsets aplicados"""
        base_pos = self.state.position.copy()
        
        # Sumar todos los offsets
        if hasattr(self, 'concentration_offset') and self.concentration_offset is not None:
            base_pos = base_pos + self.concentration_offset
        if hasattr(self, 'distribution_offset') and self.distribution_offset is not None:
            base_pos = base_pos + self.distribution_offset
        if hasattr(self, 'trajectory_offset') and self.trajectory_offset is not None:
            base_pos = base_pos + self.trajectory_offset
            
        return base_pos'''
    
    motion_content = re.sub(get_pos_pattern, new_get_position, motion_content, count=1)
else:
    print("❌ get_position no encontrado")

# Guardar motion_components
with open(motion_file, 'w', encoding='utf-8') as f:
    f.write(motion_content)
print(f"✅ {motion_file} actualizado")

# 6. Test final
test_code = '''#!/usr/bin/env python3
"""
🧪 TEST FINAL: Concentración completa
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

print("\\n🧪 TEST FINAL DE CONCENTRACIÓN\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Crear macro con fuentes dispersas
macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=4.0)

# Guardar posiciones iniciales
initial_pos = {}
for sid in range(4):
    if sid in engine._source_motions:
        pos = engine._source_motions[sid].state.position.copy()
        initial_pos[sid] = pos
        print(f"📍 Fuente {sid} inicial: {pos}")

# Aplicar concentración
print("\\n🎯 Aplicando concentración factor=0.5...")
engine.set_macro_concentration(macro_id, 0.5)

# Verificar offsets
print("\\n🔍 Verificando offsets calculados:")
for sid in range(4):
    if sid in engine._source_motions:
        motion = engine._source_motions[sid]
        offset = motion.concentration_offset
        mag = np.linalg.norm(offset)
        print(f"   Fuente {sid}: offset={offset}, magnitud={mag:.4f}")

# Ejecutar simulación
print("\\n🔄 Ejecutando 60 frames...")
for i in range(60):
    engine.step()
    
    # Mostrar progreso cada 20 frames
    if (i + 1) % 20 == 0:
        print(f"   Frame {i+1}")
        # Verificar una posición
        if 0 in engine._source_motions:
            pos = engine._positions[0]
            print(f"      Fuente 0 está en: {pos}")

# Resultados finales
print("\\n📊 RESULTADOS FINALES:")
total_movement = 0
for sid in initial_pos:
    if sid in engine._source_motions:
        final_pos = engine._positions[sid]
        movement = np.linalg.norm(final_pos - initial_pos[sid])
        total_movement += movement
        print(f"   Fuente {sid}: movió {movement:.4f} unidades")

avg_movement = total_movement / len(initial_pos) if initial_pos else 0

if avg_movement > 0.1:
    print(f"\\n✅ ¡ÉXITO! Movimiento promedio: {avg_movement:.4f}")
    print("🎉 LA CONCENTRACIÓN FUNCIONA CORRECTAMENTE")
    print("\\n🚀 Ahora prueba con el controlador interactivo:")
    print("   python trajectory_hub/interface/interactive_controller.py")
else:
    print(f"\\n❌ No hubo movimiento suficiente: {avg_movement:.4f}")

print("\\n" + "="*60)
'''

with open("test_concentration_final.py", 'w', encoding='utf-8') as f:
    f.write(test_code)

print(f"\n✅ Test creado: test_concentration_final.py")

print("""
================================================================================
✅ FIXES APLICADOS
================================================================================

🔧 Lo que arreglamos:
   1. set_macro_concentration ahora CALCULA los offsets correctamente
   2. get_position() suma los offsets a la posición base
   3. Los offsets se aplican con la magnitud correcta

🚀 EJECUTA EL TEST FINAL:
   python test_concentration_final.py

🎯 Este test muestra:
   - Los offsets calculados
   - El progreso frame a frame
   - El movimiento total de cada fuente

💡 Si funciona, verás las fuentes moverse hacia el centro
================================================================================
""")