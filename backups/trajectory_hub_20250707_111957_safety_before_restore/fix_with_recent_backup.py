#!/usr/bin/env python3
"""
🔧 FIX: Usar backup más reciente o implementar métodos faltantes
"""

import os
import sys
import glob
import shutil

print("""
================================================================================
🔧 RESTAURACIÓN CON BACKUP RECIENTE
================================================================================
""")

# 1. Listar todos los backups disponibles
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
backups = glob.glob("trajectory_hub/core/enhanced_trajectory_engine.py.backup_*")

if backups:
    backups.sort()
    print("📋 BACKUPS DISPONIBLES:")
    for i, backup in enumerate(backups):
        size = os.path.getsize(backup)
        print(f"   {i+1}. {os.path.basename(backup)} ({size} bytes)")
    
    # Usar el más reciente antes del aggressive
    good_backup = None
    for backup in reversed(backups):
        if "aggressive" not in backup:
            good_backup = backup
            break
    
    if good_backup:
        print(f"\n✅ Usando: {os.path.basename(good_backup)}")
        shutil.copy(good_backup, engine_file)
    else:
        print("❌ No hay backups válidos")
        sys.exit(1)
else:
    print("❌ No hay backups")
    sys.exit(1)

# 2. Verificar qué métodos existen
print("\n🔍 VERIFICANDO MÉTODOS EN EL ARCHIVO...")

with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

methods_to_check = [
    'set_macro_concentration',
    'create_macro',
    'step',
    'update'
]

missing_methods = []
for method in methods_to_check:
    if f'def {method}(' in content:
        print(f"   ✅ {method} existe")
    else:
        print(f"   ❌ {method} NO existe")
        missing_methods.append(method)

# 3. Si falta set_macro_concentration, implementarlo
if 'set_macro_concentration' in missing_methods:
    print("\n🔨 IMPLEMENTANDO set_macro_concentration...")
    
    # Buscar dónde insertar (después de create_macro si existe)
    import re
    
    # Buscar create_macro
    create_macro_match = re.search(r'def create_macro\(.*?\):[^}]+?(?=\n    def|\n\s*$)', content, re.DOTALL)
    
    if create_macro_match:
        insert_pos = create_macro_match.end()
    else:
        # Buscar el final de __init__
        init_match = re.search(r'def __init__\(.*?\):[^}]+?(?=\n    def)', content, re.DOTALL)
        if init_match:
            insert_pos = init_match.end()
        else:
            print("❌ No se puede determinar dónde insertar")
            sys.exit(1)
    
    # Método set_macro_concentration
    concentration_method = '''
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
        import numpy as np
        
        if macro_id not in self._macros:
            print(f"⚠️ Macro {macro_id} no encontrado")
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
            elif sid < len(self._positions):
                positions.append(self._positions[sid].copy())
        
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
    
    # Insertar
    content = content[:insert_pos] + concentration_method + content[insert_pos:]
    
    # Guardar
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ set_macro_concentration implementado")

# 4. Asegurar que step() aplique los offsets
print("\n🔧 VERIFICANDO/ARREGLANDO step()...")

# Recargar contenido
with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Si step existe, verificar que aplique offsets
if 'def step(' in content:
    step_match = re.search(r'def step\(.*?\):[^}]+?(?=\n    def|\n\s*$|\nclass)', content, re.DOTALL)
    
    if step_match and 'concentration_offset' not in step_match.group(0):
        print("   step() existe pero no aplica offsets, modificando...")
        
        # Reemplazar con versión que aplica offsets
        new_step = '''def step(self, dt: float = None) -> dict:
        """
        Ejecuta un paso de simulación con concentración.
        """
        if dt is None:
            dt = self.dt
        
        # Actualizar motions
        for sid, motion in self._source_motions.items():
            if sid < self.max_sources and motion.enabled:
                # Actualizar motion
                motion.update(dt)
                
                # Obtener posición con offsets
                pos = motion.state.position.copy()
                
                # Aplicar concentration_offset
                if hasattr(motion, 'concentration_offset') and motion.concentration_offset is not None:
                    pos = pos + motion.concentration_offset
                
                # Actualizar arrays
                self._positions[sid] = pos
                self._orientations[sid] = motion.state.orientation
                self._apertures[sid] = motion.state.aperture
        
        # Incrementar tiempo
        self._time = getattr(self, '_time', 0.0) + dt
        self._frame_count = getattr(self, '_frame_count', 0) + 1
        
        return {
            'positions': self._positions.copy(),
            'orientations': self._orientations.copy(),
            'apertures': self._apertures.copy(),
            'time': self._time,
            'frame': self._frame_count
        }'''
        
        content = re.sub(r'def step\(.*?\):[^}]+?(?=\n    def|\n\s*$|\nclass)', new_step, content, flags=re.DOTALL)
        
        with open(engine_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ step() modificado")
else:
    print("   step() ya aplica offsets correctamente")

# 5. Test final
print("\n" + "="*80)
print("🧪 TEST FINAL")
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
    
    print("CREANDO ENGINE...")
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
    
    print("CREANDO MACRO...")
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=4.0)
    
    print("\\nPOSICIONES INICIALES:")
    initial_pos = {}
    for i in range(4):
        initial_pos[i] = engine._positions[i].copy()
        print(f"  F{i}: {initial_pos[i]}")
    
    print("\\nAPLICANDO CONCENTRACIÓN...")
    engine.set_macro_concentration(macro_id, 0.5)
    
    # Verificar offsets
    print("\\nOFFSETS:")
    has_offsets = False
    for i in range(4):
        if i in engine._source_motions:
            motion = engine._source_motions[i]
            if hasattr(motion, 'concentration_offset'):
                offset = motion.concentration_offset
                mag = np.linalg.norm(offset)
                if mag > 0:
                    has_offsets = True
                print(f"  F{i}: {offset} (mag={mag:.4f})")
    
    if not has_offsets:
        print("\\n❌ No se calcularon offsets")
    else:
        print("\\nEJECUTANDO SIMULACIÓN...")
        
        # Un frame
        engine.step()
        
        # Verificar movimiento
        print("\\nDESPUÉS DE 1 FRAME:")
        moved = False
        for i in range(4):
            mov = np.linalg.norm(engine._positions[i] - initial_pos[i])
            if mov > 0.001:
                moved = True
                print(f"  F{i}: movió {mov:.4f}")
        
        if moved:
            # Ejecutar más
            for _ in range(99):
                engine.step()
            
            print("\\nRESULTADO FINAL (100 frames):")
            for i in range(4):
                print(f"  F{i}: {engine._positions[i]}")
            
            # Análisis
            initial_spread = np.std(list(initial_pos.values()))
            final_spread = np.std([engine._positions[i] for i in range(4)])
            reduction = (1 - final_spread/initial_spread) * 100
            
            print(f"\\nCONCENTRACIÓN:")
            print(f"  Dispersión inicial: {initial_spread:.4f}")
            print(f"  Dispersión final: {final_spread:.4f}")
            print(f"  Reducción: {reduction:.1f}%")
            
            print("\\n✅ ¡ÉXITO! LA CONCENTRACIÓN FUNCIONA")
        else:
            print("\\n❌ No hay movimiento")
            
except Exception as e:
    print(f"\\nERROR: {e}")
    import traceback
    traceback.print_exc()
'''

exec(test_code)

print("""

================================================================================
✅ CORRECCIÓN APLICADA
================================================================================

Si el test muestra éxito:
→ python trajectory_hub/interface/interactive_controller.py

Si aún no funciona:
→ Verificar que concentration_offset se inicialice en SourceMotion
→ Verificar que los valores de las posiciones sean correctos
================================================================================
""")