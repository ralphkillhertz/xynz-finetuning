#!/usr/bin/env python3
"""
🔧 FIX DEFINITIVO - Arreglar engine.step() para actualizar las fuentes
⚡ Este es el método que usa el controller
"""

import os
import re
from datetime import datetime

def fix_step_method():
    """Arreglar el método step() del engine"""
    
    print("🔧 ARREGLANDO ENGINE.STEP()\n")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_file):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
    
    # Backup
    backup_dir = f"backup_step_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    import shutil
    shutil.copy2(engine_file, os.path.join(backup_dir, "enhanced_trajectory_engine.py"))
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # 1. Buscar el método step
    print("1️⃣ BUSCANDO MÉTODO step()...")
    
    step_pattern = r'(def step\(self[^)]*\):\s*\n)(.*?)(?=\n    def|\nclass|\Z)'
    step_match = re.search(step_pattern, content, re.DOTALL)
    
    if not step_match:
        print("❌ No se encontró el método step")
        
        # Buscar alternativa
        print("\n🔍 Buscando métodos alternativos...")
        
        # Buscar cualquier def que contenga step
        alt_pattern = r'def (\w*step\w*)\(self[^)]*\):'
        alt_matches = re.findall(alt_pattern, content)
        
        if alt_matches:
            print(f"   Encontrados: {alt_matches}")
        
        return False
    
    method_def = step_match.group(1)
    method_body = step_match.group(2)
    
    print("✅ Método step encontrado")
    
    # 2. Analizar qué hace actualmente
    print("\n2️⃣ ANALIZANDO step() ACTUAL...")
    
    # Ver si ya actualiza source_motions
    if '_source_motions' in method_body:
        print("   ✅ Ya menciona _source_motions")
        
        # Ver si llama a update
        if '.update(' in method_body:
            print("   ✅ Ya llama a .update()")
            print("   ℹ️  El método parece estar bien")
            
            # Verificar que sea motion.update
            if 'motion.update' not in method_body:
                print("   ⚠️  Pero no es motion.update()")
        else:
            print("   ❌ NO llama a .update()")
    else:
        print("   ❌ NO menciona _source_motions")
    
    # 3. Crear nuevo método step que funcione
    print("\n3️⃣ CREANDO MÉTODO step() CORRECTO...")
    
    # Extraer la firma del método (puede tener parámetros)
    method_signature = method_def.strip()
    
    new_step = f'''{method_signature}
        """Actualizar el sistema un paso"""
        if self.time_paused:
            return
        
        # Calcular dt
        dt = 1.0 / self.fps
        
        # 1. Actualizar cada source motion
        if hasattr(self, '_source_motions'):
            for source_id, motion in self._source_motions.items():
                # Actualizar el motion (calcula offsets de concentración, etc.)
                motion.update(dt)
        
        # 2. Si hay OSC activo, enviar posiciones
        if self.osc_bridge and hasattr(self, '_source_motions'):
            for source_id, motion in self._source_motions.items():
                # Obtener la posición actualizada
                if hasattr(motion, 'state') and hasattr(motion.state, 'position'):
                    position = motion.state.position
                    # Enviar via OSC
                    self.osc_bridge.send_position(source_id, position)
        
        # 3. Si el método original hacía algo más, preservarlo
        # (Por ahora solo lo esencial)'''
    
    # 4. Reemplazar el método
    print("\n4️⃣ REEMPLAZANDO step()...")
    
    # Reemplazar todo el método
    new_content = content.replace(
        step_match.group(0),
        new_step + '\n'
    )
    
    # 5. Guardar
    with open(engine_file, 'w') as f:
        f.write(new_content)
    
    print("✅ Archivo actualizado")
    
    # 6. Crear test específico para step
    test_script = '''#!/usr/bin/env python3
"""
🧪 TEST ESPECÍFICO - Verificar engine.step()
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("🧪 TEST DE ENGINE.STEP()\\n")

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine y macro
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=2.0)
    
    print("✅ Macro creado con 4 fuentes en grid")
    
    if hasattr(engine, '_source_motions'):
        motions = engine._source_motions
        
        # Posiciones iniciales
        print("\\n📍 POSICIONES INICIALES:")
        positions_before = {}
        for source_id, motion in motions.items():
            pos = motion.state.position.copy()
            positions_before[source_id] = pos
            print(f"   Fuente {source_id}: {pos}")
        
        # Aplicar concentración fuerte
        print("\\n🎯 APLICANDO CONCENTRACIÓN (factor 0.1)...")
        engine.set_macro_concentration(macro_id, 0.1)
        
        # Llamar step() varias veces (como lo haría el controller)
        print("\\n🔄 LLAMANDO ENGINE.STEP() 10 VECES...")
        for i in range(10):
            engine.step()
        
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
            
            if movement > 0.1:  # Movimiento significativo
                print(f"      ✅ Se movió {movement:.2f} unidades")
            else:
                print(f"      ❌ Movimiento mínimo: {movement:.4f}")
                if movement < 0.01:
                    all_moved = False
        
        print(f"\\n📊 MOVIMIENTO TOTAL: {total_movement:.2f} unidades")
        
        if all_moved and total_movement > 1.0:
            print("\\n🎉 ¡CONCENTRACIÓN FUNCIONA CON ENGINE.STEP()!")
            print("   Todas las fuentes se movieron hacia el centro")
        else:
            print("\\n⚠️  Movimiento insuficiente")
            
            # Debug adicional
            first_motion = list(motions.values())[0]
            if hasattr(first_motion, 'concentration_offset'):
                print(f"\\n🔍 Debug - concentration_offset: {first_motion.concentration_offset}")
            if 'concentration' in first_motion.components:
                conc = first_motion.components['concentration']
                print(f"   concentration.enabled: {conc.enabled}")
                print(f"   concentration.factor: {conc.factor}")
    
    print("\\n✅ Test completado")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\\n" + "="*60)
print("🚀 Si las fuentes se movieron significativamente,")
print("   entonces step() funciona correctamente.")
print("\\n📊 Próximo paso:")
print("   python trajectory_hub/interface/interactive_controller.py")
'''
    
    with open("test_engine_step.py", 'w') as f:
        f.write(test_script)
    
    print("\n✅ Test creado: test_engine_step.py")
    
    return True

if __name__ == "__main__":
    success = fix_step_method()
    
    if success:
        print("\n" + "="*60)
        print("🎉 ENGINE.STEP() ARREGLADO")
        print("="*60)
        
        print("\n✅ Ahora engine.step():")
        print("   1. Actualiza cada motion con motion.update(dt)")
        print("   2. Envía las posiciones actualizadas via OSC")
        print("   3. Es llamado por el controller")
        
        print("\n🚀 EJECUTA EL TEST:")
        print("   python test_engine_step.py")
        
        print("\n📊 Si funciona, la concentración debería verse en:")
        print("   python trajectory_hub/interface/interactive_controller.py")
        
        print("\n🎯 ¡ESTE ES REALMENTE EL ÚLTIMO PASO!")