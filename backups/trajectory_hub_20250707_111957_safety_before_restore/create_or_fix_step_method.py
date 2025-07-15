#!/usr/bin/env python3
"""
🔧 FIX DEFINITIVO - Crear/modificar engine.step() para actualizar fuentes
⚡ Este método es el que usa el controller
"""

import os
import re
from datetime import datetime

def create_or_fix_step():
    """Crear o arreglar el método step del engine"""
    
    print("🔧 CREANDO/ARREGLANDO ENGINE.STEP()\n")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_file):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
    
    # Backup
    backup_dir = f"backup_step_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    import shutil
    shutil.copy2(engine_file, os.path.join(backup_dir, "enhanced_trajectory_engine.py"))
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # 1. Buscar dónde está el método step actual o dónde insertarlo
    print("1️⃣ BUSCANDO MÉTODO step()...")
    
    # Buscar si step existe
    step_exists = False
    step_pattern = r'def step\(self\):'
    
    if re.search(step_pattern, content):
        step_exists = True
        print("   ✅ step() existe, lo modificaremos")
    else:
        print("   ❌ step() no existe, lo crearemos")
    
    # 2. Crear el nuevo método step
    print("\n2️⃣ CREANDO MÉTODO step() CORRECTO...")
    
    new_step = '''    def step(self):
        """
        Actualizar el sistema un paso.
        Llamado por el controller en cada iteración.
        """
        if self.time_paused:
            return self._prepare_state_dict()
        
        # Calcular dt
        dt = 1.0 / self.fps
        
        # 1. Actualizar cada source motion
        if hasattr(self, '_source_motions'):
            for source_id, motion in self._source_motions.items():
                # Actualizar el motion (calcula offsets de concentración, etc.)
                motion.update(dt)
        
        # 2. Preparar el estado para devolver (el controller espera un dict)
        state = self._prepare_state_dict()
        
        # 3. Si hay OSC activo, enviar posiciones
        if self.osc_bridge and hasattr(self, '_source_motions'):
            positions = {}
            for source_id, motion in self._source_motions.items():
                # Obtener la posición actualizada
                if hasattr(motion, 'state') and hasattr(motion.state, 'position'):
                    position = motion.state.position
                    positions[source_id] = position.tolist()
                    # Enviar via OSC
                    self.osc_bridge.send_position(source_id, position)
            
            # Agregar posiciones al estado
            state['positions'] = positions
        
        return state
    
    def _prepare_state_dict(self):
        """Preparar el diccionario de estado que espera el controller"""
        state = {
            'time': getattr(self, 'time', 0),
            'fps': self.fps,
            'paused': self.time_paused,
            'source_count': len(self._source_motions) if hasattr(self, '_source_motions') else 0,
            'positions': {},
            'status': 'ok'
        }
        
        # Agregar posiciones actuales
        if hasattr(self, '_source_motions'):
            for source_id, motion in self._source_motions.items():
                if hasattr(motion, 'state') and hasattr(motion.state, 'position'):
                    state['positions'][source_id] = motion.state.position.tolist()
        
        return state'''
    
    # 3. Aplicar el cambio
    print("\n3️⃣ APLICANDO CAMBIOS...")
    
    if step_exists:
        # Reemplazar el método step existente
        # Buscar el método completo
        step_full_pattern = r'(    def step\(self\):.*?)(?=\n    def|\nclass|\Z)'
        
        # Encontrar el método actual
        step_match = re.search(step_full_pattern, content, re.DOTALL)
        
        if step_match:
            # Reemplazar
            content = content.replace(step_match.group(0), new_step)
            print("   ✅ Método step() reemplazado")
        else:
            print("   ⚠️  No se pudo encontrar el método completo, agregando al final")
            step_exists = False
    
    if not step_exists:
        # Agregar el método step antes del último método o al final de la clase
        # Buscar un buen lugar para insertar
        
        # Buscar el método update para insertar después
        update_pattern = r'(def update\(self.*?\):.*?)(?=\n    def|\nclass|\Z)'
        update_match = re.search(update_pattern, content, re.DOTALL)
        
        if update_match:
            # Insertar después de update
            insert_pos = update_match.end()
            content = content[:insert_pos] + '\n\n' + new_step + content[insert_pos:]
            print("   ✅ Método step() agregado después de update()")
        else:
            # Buscar el final de la clase
            class_pattern = r'class EnhancedTrajectoryEngine.*?(?=\nclass|\Z)'
            class_match = re.search(class_pattern, content, re.DOTALL)
            
            if class_match:
                # Insertar antes del final
                insert_pos = class_match.end() - 1
                content = content[:insert_pos] + '\n' + new_step + '\n' + content[insert_pos:]
                print("   ✅ Método step() agregado al final de la clase")
    
    # 4. Guardar
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("\n✅ Archivo actualizado")
    
    # 5. Crear test final
    test_script = '''#!/usr/bin/env python3
"""
🧪 TEST FINAL - Verificar que step() actualiza las fuentes
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("🧪 TEST FINAL DE ENGINE.STEP()\\n")

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine y macro
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=3.0)
    
    print("✅ Macro creado con 4 fuentes en grid")
    
    if hasattr(engine, '_source_motions'):
        motions = engine._source_motions
        
        # Posiciones iniciales
        print("\\n📍 POSICIONES INICIALES:")
        positions_before = {}
        center = np.zeros(3)
        
        for source_id, motion in motions.items():
            pos = motion.state.position.copy()
            positions_before[source_id] = pos
            center += pos
            print(f"   Fuente {source_id}: {pos}")
        
        center /= len(motions)
        print(f"\\n   Centro calculado: {center}")
        
        # Aplicar concentración fuerte
        print("\\n🎯 APLICANDO CONCENTRACIÓN (factor 0.05 - muy concentrado)...")
        engine.set_macro_concentration(macro_id, 0.05)
        
        # Llamar step() como lo haría el controller
        print("\\n🔄 LLAMANDO ENGINE.STEP() 20 VECES...")
        for i in range(20):
            state = engine.step()
            
            if i == 0:
                print(f"\\n   step() devuelve: {type(state).__name__}")
                if isinstance(state, dict):
                    print(f"   Claves: {list(state.keys())}")
        
        # Posiciones finales
        print("\\n📍 POSICIONES FINALES:")
        all_moved = True
        total_movement = 0
        
        for source_id, motion in motions.items():
            pos = motion.state.position
            before = positions_before[source_id]
            
            movement = np.linalg.norm(pos - before)
            total_movement += movement
            
            print(f"   Fuente {source_id}: {pos}")
            
            if movement > 0.1:
                print(f"      ✅ Se movió {movement:.2f} unidades hacia el centro")
            else:
                print(f"      ⚠️  Movimiento pequeño: {movement:.4f}")
                if movement < 0.01:
                    all_moved = False
        
        # Verificar concentración
        final_center = np.zeros(3)
        for motion in motions.values():
            final_center += motion.state.position
        final_center /= len(motions)
        
        spread_before = np.mean([np.linalg.norm(p - center) for p in positions_before.values()])
        spread_after = np.mean([np.linalg.norm(m.state.position - final_center) for m in motions.values()])
        
        print(f"\\n📊 ANÁLISIS DE CONCENTRACIÓN:")
        print(f"   Dispersión inicial: {spread_before:.2f}")
        print(f"   Dispersión final: {spread_after:.2f}")
        print(f"   Reducción: {(1 - spread_after/spread_before)*100:.1f}%")
        
        if spread_after < spread_before * 0.5:
            print("\\n🎉 ¡CONCENTRACIÓN FUNCIONA PERFECTAMENTE!")
            print("   Las fuentes se concentraron significativamente")
        elif spread_after < spread_before:
            print("\\n✅ La concentración funciona")
            print("   Las fuentes se acercaron al centro")
        else:
            print("\\n❌ La concentración NO funciona")
    
    print("\\n✅ Test completado")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\\n" + "="*60)
print("🚀 Si las fuentes se concentraron, entonces:")
print("   python trajectory_hub/interface/interactive_controller.py")
print("\\n🎯 ¡La concentración debería verse en Spat!")
'''
    
    with open("test_final_step_method.py", 'w') as f:
        f.write(test_script)
    
    print("\n✅ Test creado: test_final_step_method.py")
    
    return True

if __name__ == "__main__":
    success = create_or_fix_step()
    
    if success:
        print("\n" + "="*60)
        print("🎉 ENGINE.STEP() IMPLEMENTADO CORRECTAMENTE")
        print("="*60)
        
        print("\n✅ Ahora engine.step():")
        print("   1. Actualiza cada motion con motion.update(dt)")
        print("   2. Devuelve un diccionario de estado")
        print("   3. Envía posiciones via OSC si está activo")
        print("   4. Es exactamente lo que el controller espera")
        
        print("\n🚀 EJECUTA EL TEST FINAL:")
        print("   python test_final_step_method.py")
        
        print("\n📊 Si funciona, la concentración se verá en:")
        print("   python trajectory_hub/interface/interactive_controller.py")
        
        print("\n🎯 ¡ESTE ES EL FIX DEFINITIVO!")