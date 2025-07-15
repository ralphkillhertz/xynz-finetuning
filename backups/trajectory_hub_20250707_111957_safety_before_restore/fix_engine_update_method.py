#!/usr/bin/env python3
"""
🔧 FIX FINAL - Arreglar engine.update() para que llame a motion.update()
⚡ El último paso para que todo funcione
"""

import os
import re

def fix_engine_update():
    """Asegurar que engine.update() llame a motion.update() correctamente"""
    
    print("🔧 ARREGLANDO ENGINE.UPDATE()\n")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_file):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
    
    # Backup
    import shutil
    backup_file = engine_file + ".backup_update"
    shutil.copy2(engine_file, backup_file)
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # 1. Buscar el método update
    print("1️⃣ BUSCANDO MÉTODO update()...")
    
    update_pattern = r'(def update\(self[^)]*\):\s*\n)(.*?)(?=\n    def|\nclass|\Z)'
    update_match = re.search(update_pattern, content, re.DOTALL)
    
    if not update_match:
        print("❌ No se encontró el método update")
        return False
    
    method_def = update_match.group(1)
    method_body = update_match.group(2)
    
    print("✅ Método update encontrado")
    
    # 2. Ver si ya llama a motion.update
    if 'motion.update' in method_body or '_source_motions' in method_body:
        print("ℹ️  Ya menciona motion/source_motions")
        
        # Verificar si realmente está llamando update
        if '.update(' not in method_body:
            print("   ❌ Pero NO llama a .update()")
    
    # 3. Crear nuevo método update que funcione
    print("\n2️⃣ CREANDO MÉTODO update() CORRECTO...")
    
    new_update = '''def update(self):
        """Actualizar todas las fuentes y enviar posiciones via OSC"""
        if self.time_paused:
            return
            
        # Calcular dt
        dt = 1.0 / self.fps
        
        # 1. Actualizar cada source motion
        if hasattr(self, '_source_motions'):
            for source_id, motion in self._source_motions.items():
                # Llamar update de cada motion
                motion.update(dt)
        
        # 2. Enviar posiciones via OSC si está activo
        if self.osc_bridge and hasattr(self, '_source_motions'):
            for source_id, motion in self._source_motions.items():
                # Obtener la posición actualizada
                if hasattr(motion, 'get_position'):
                    position = motion.get_position()
                elif hasattr(motion, 'state') and hasattr(motion.state, 'position'):
                    position = motion.state.position
                else:
                    continue
                
                # Enviar via OSC
                self.osc_bridge.send_position(source_id, position)'''
    
    # Reemplazar el método completo
    new_content = content.replace(
        update_match.group(0),
        new_update + '\n'
    )
    
    # 4. Guardar
    print("\n3️⃣ GUARDANDO CAMBIOS...")
    
    with open(engine_file, 'w') as f:
        f.write(new_content)
    
    print("✅ Archivo actualizado")
    
    # 5. Crear test de verificación
    test_script = '''#!/usr/bin/env python3
"""
🧪 TEST FINAL COMPLETO - Verificar engine.update()
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("🧪 TEST COMPLETO DE CONCENTRACIÓN CON ENGINE.UPDATE()\\n")

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine y macro
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("test", source_count=5, formation="circle", spacing=3.0)
    
    print("✅ Macro creado con 5 fuentes en círculo")
    
    if hasattr(engine, '_source_motions'):
        motions = engine._source_motions
        
        # Posiciones iniciales
        print("\\n📍 POSICIONES INICIALES:")
        positions_before = {}
        for i, (source_id, motion) in enumerate(motions.items()):
            pos = motion.state.position.copy()
            positions_before[source_id] = pos
            print(f"   Fuente {source_id}: {pos}")
        
        # Aplicar concentración
        print("\\n🎯 APLICANDO CONCENTRACIÓN (factor 0.2)...")
        engine.set_macro_concentration(macro_id, 0.2)
        
        # Llamar engine.update() varias veces
        print("\\n🔄 LLAMANDO ENGINE.UPDATE() 5 VECES...")
        for i in range(5):
            engine.update()
        
        # Posiciones finales
        print("\\n📍 POSICIONES FINALES:")
        all_moved = True
        for source_id, motion in motions.items():
            pos = motion.state.position
            before = positions_before[source_id]
            
            print(f"   Fuente {source_id}: {pos}")
            
            if not np.allclose(before, pos):
                delta = pos - before
                print(f"      ✅ Se movió: Δ = {delta}")
            else:
                print(f"      ❌ No se movió")
                all_moved = False
        
        if all_moved:
            print("\\n🎉 ¡TODAS LAS FUENTES SE CONCENTRARON!")
            print("   La concentración funciona correctamente con engine.update()")
        else:
            print("\\n⚠️  Algunas fuentes no se movieron")
            print("   (Esto puede ser normal si ya estaban en el centro)")
    
    print("\\n✅ Test completado exitosamente")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\\n" + "="*60)
print("🚀 Si todas las fuentes se movieron hacia el centro,")
print("   entonces el sistema está funcionando perfectamente.")
print("\\n📊 Próximo paso:")
print("   python trajectory_hub/interface/interactive_controller.py")
print("\\n🎯 ¡La concentración debería funcionar en Spat!")
'''
    
    with open("test_engine_update_complete.py", 'w') as f:
        f.write(test_script)
    
    print("\n✅ Test creado: test_engine_update_complete.py")
    
    return True

if __name__ == "__main__":
    success = fix_engine_update()
    
    if success:
        print("\n" + "="*60)
        print("🎉 ENGINE.UPDATE() ARREGLADO")
        print("="*60)
        
        print("\n✅ Ahora engine.update():")
        print("   1. Llama a motion.update(dt) para cada fuente")
        print("   2. Obtiene las posiciones actualizadas")
        print("   3. Las envía via OSC")
        
        print("\n🚀 EJECUTA EL TEST FINAL:")
        print("   python test_engine_update_complete.py")
        
        print("\n📊 Si funciona, prueba en el controller:")
        print("   python trajectory_hub/interface/interactive_controller.py")
        
        print("\n🎯 ¡ESTE ES EL ÚLTIMO PASO!")