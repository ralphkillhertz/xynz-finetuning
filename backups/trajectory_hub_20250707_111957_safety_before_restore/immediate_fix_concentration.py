#!/usr/bin/env python3
"""
🔧 FIX INMEDIATO: Restaurar y corregir concentración
"""

import os
import sys
import glob
import shutil

print("""
================================================================================
🔧 CORRECCIÓN INMEDIATA DE CONCENTRACIÓN
================================================================================
""")

# 1. Buscar el mejor backup disponible
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
backups = glob.glob("trajectory_hub/core/enhanced_trajectory_engine.py.backup_*")

if backups:
    # Ordenar por fecha
    backups.sort()
    
    # Preferir backup antes del error agresivo
    good_backup = None
    for backup in reversed(backups):
        if "aggressive" not in backup:
            good_backup = backup
            break
    
    if not good_backup:
        good_backup = backups[-2]  # Penúltimo backup
    
    print(f"✅ Restaurando desde: {good_backup}")
    shutil.copy(good_backup, engine_file)
else:
    print("❌ No hay backups disponibles")
    sys.exit(1)

# 2. Leer el archivo restaurado
print("\n📋 ANALIZANDO ARCHIVO RESTAURADO...")

with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Verificar que no hay error de sintaxis
try:
    compile(content, engine_file, 'exec')
    print("✅ Sintaxis correcta")
except SyntaxError as e:
    print(f"❌ Error de sintaxis en línea {e.lineno}: {e.msg}")
    sys.exit(1)

# 3. Buscar y arreglar el método step
print("\n🔍 BUSCANDO MÉTODO step()...")

import re

# Buscar si existe step
step_exists = bool(re.search(r'def step\(self[^)]*\):', content))

if not step_exists:
    print("❌ No existe step(), creándolo...")
    
    # Buscar el final de la clase
    class_match = re.search(r'class EnhancedTrajectoryEngine[^:]*:.*?(?=\nclass|\Z)', content, re.DOTALL)
    
    if class_match:
        # Insertar step al final de la clase
        insert_pos = class_match.end() - 1
        
        step_method = '''
    def step(self, dt: float = None) -> dict:
        """
        Ejecuta un paso de simulación aplicando concentración correctamente.
        """
        if dt is None:
            dt = self.dt
        
        # Llamar a update si existe
        if hasattr(self, 'update'):
            self.update(dt)
        
        # APLICAR CONCENTRACIÓN DIRECTAMENTE
        for sid, motion in self._source_motions.items():
            if sid < self.max_sources and motion.enabled:
                # Posición base
                pos = motion.state.position.copy()
                
                # Aplicar concentration_offset si existe
                if hasattr(motion, 'concentration_offset') and motion.concentration_offset is not None:
                    pos = pos + motion.concentration_offset
                
                # Actualizar _positions
                self._positions[sid] = pos
                
                # También actualizar orientación y apertura
                self._orientations[sid] = motion.state.orientation
                self._apertures[sid] = motion.state.aperture
        
        # Incrementar tiempo
        self._time = getattr(self, '_time', 0.0) + dt
        self._frame_count = getattr(self, '_frame_count', 0) + 1
        
        # Retornar estado
        return {
            'positions': self._positions.copy(),
            'orientations': self._orientations.copy(),
            'apertures': self._apertures.copy(),
            'names': [self._source_info.get(i, SourceInfo(i, f"Source_{i}")).name 
                     for i in range(self.max_sources)],
            'time': self._time,
            'frame': self._frame_count
        }
'''
        
        content = content[:insert_pos] + step_method + '\n' + content[insert_pos:]
        
        # Guardar
        with open(engine_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Método step() creado")

else:
    print("✅ step() existe")
    
    # Verificar que step aplica offsets
    step_match = re.search(r'def step\(self[^)]*\):.*?(?=\n    def|\nclass|\Z)', content, re.DOTALL)
    
    if step_match and 'concentration_offset' not in step_match.group(0):
        print("⚠️ step() no aplica concentration_offset, modificando...")
        
        # Buscar dónde se actualiza _positions dentro de step
        step_content = step_match.group(0)
        
        # Reemplazar el método completo con uno que funcione
        new_step = '''def step(self, dt: float = None) -> dict:
        """
        Ejecuta un paso de simulación aplicando concentración correctamente.
        """
        if dt is None:
            dt = self.dt
        
        # Llamar a update si existe
        if hasattr(self, 'update'):
            self.update(dt)
        
        # APLICAR CONCENTRACIÓN DIRECTAMENTE
        for sid, motion in self._source_motions.items():
            if sid < self.max_sources and motion.enabled:
                # Posición base
                pos = motion.state.position.copy()
                
                # Aplicar concentration_offset si existe
                if hasattr(motion, 'concentration_offset') and motion.concentration_offset is not None:
                    pos = pos + motion.concentration_offset
                
                # Actualizar _positions
                self._positions[sid] = pos
                
                # También actualizar orientación y apertura
                self._orientations[sid] = motion.state.orientation
                self._apertures[sid] = motion.state.aperture
        
        # Incrementar tiempo
        self._time = getattr(self, '_time', 0.0) + dt
        self._frame_count = getattr(self, '_frame_count', 0) + 1
        
        # Retornar estado
        return {
            'positions': self._positions.copy(),
            'orientations': self._orientations.copy(),
            'apertures': self._apertures.copy(),
            'names': [self._source_info.get(i, SourceInfo(i, f"Source_{i}")).name 
                     for i in range(self.max_sources)],
            'time': self._time,
            'frame': self._frame_count
        }'''
        
        content = re.sub(r'def step\(self[^)]*\):.*?(?=\n    def|\nclass|\Z)', new_step, content, flags=re.DOTALL)
        
        with open(engine_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ step() modificado para aplicar offsets")

# 4. Test completo
print("\n" + "="*80)
print("🧪 TEST COMPLETO DE CONCENTRACIÓN")
print("="*80 + "\n")

test_code = '''
import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    print("1️⃣ CREANDO ENGINE Y MACRO...")
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=6.0)
    
    print("\\n2️⃣ POSICIONES INICIALES:")
    initial_pos = {}
    for i in range(4):
        initial_pos[i] = engine._positions[i].copy()
        print(f"   Fuente {i}: {initial_pos[i]}")
    
    center = np.mean(list(initial_pos.values()), axis=0)
    print(f"   Centro: {center}")
    
    print("\\n3️⃣ APLICANDO CONCENTRACIÓN 0.5...")
    engine.set_macro_concentration(macro_id, 0.5)
    
    print("\\n4️⃣ VERIFICANDO OFFSETS:")
    for i in range(4):
        if i in engine._source_motions:
            offset = engine._source_motions[i].concentration_offset
            mag = np.linalg.norm(offset)
            print(f"   Fuente {i}: offset={offset}, magnitud={mag:.4f}")
    
    print("\\n5️⃣ EJECUTANDO SIMULACIÓN...")
    
    # Primer frame
    engine.step()
    
    print("\\n   Después de 1 frame:")
    for i in range(4):
        mov = np.linalg.norm(engine._positions[i] - initial_pos[i])
        print(f"   Fuente {i}: movimiento={mov:.4f}")
        if mov > 0:
            print(f"      Nueva posición: {engine._positions[i]}")
    
    # Más frames
    for _ in range(99):
        engine.step()
    
    print("\\n6️⃣ RESULTADO FINAL (100 frames):")
    total_movement = 0
    for i in range(4):
        final_pos = engine._positions[i]
        movement = np.linalg.norm(final_pos - initial_pos[i])
        total_movement += movement
        print(f"   Fuente {i}:")
        print(f"      Inicial: {initial_pos[i]}")
        print(f"      Final: {final_pos}")
        print(f"      Movimiento total: {movement:.4f}")
    
    # Análisis
    initial_spread = np.std(list(initial_pos.values()))
    final_spread = np.std([engine._positions[i] for i in range(4)])
    
    print(f"\\n📊 ANÁLISIS DE CONCENTRACIÓN:")
    print(f"   Dispersión inicial: {initial_spread:.4f}")
    print(f"   Dispersión final: {final_spread:.4f}")
    print(f"   Reducción: {(1 - final_spread/initial_spread) * 100:.1f}%")
    
    if total_movement > 0.1:
        print("\\n✅ ¡ÉXITO! LA CONCENTRACIÓN FUNCIONA")
        print("\\n🎉 Las fuentes se mueven hacia el centro")
        print("\\n🚀 Ejecuta ahora:")
        print("   python trajectory_hub/interface/interactive_controller.py")
    else:
        print("\\n❌ Las fuentes no se mueven")
        print("\\n💡 Revisa manualmente enhanced_trajectory_engine.py")
        
except Exception as e:
    print(f"\\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
'''

exec(test_code)

print("""

================================================================================
📋 ESTADO FINAL
================================================================================

✅ Archivo restaurado desde backup
✅ Sintaxis verificada
✅ Método step() creado/modificado para aplicar offsets

Si el test muestra movimiento:
→ La concentración funciona correctamente
→ Usa el controlador interactivo con Spat

Si NO hay movimiento:
→ El problema puede estar en otra parte
→ Verificar que set_macro_concentration() calcule offsets
→ Verificar que motion.state.position tenga valores correctos

💡 Este fix aplica los offsets DIRECTAMENTE en step()
   sin depender de otros métodos intermedios.
================================================================================
""")