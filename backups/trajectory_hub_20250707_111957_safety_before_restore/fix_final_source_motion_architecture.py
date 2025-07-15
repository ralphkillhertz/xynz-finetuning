#!/usr/bin/env python3
"""
🔧 FIX FINAL - Adaptar a la arquitectura real de SourceMotion
⚡ Usar state.position y arreglar update()
"""

import os
import re
from datetime import datetime

def fix_source_motion_architecture():
    """Arreglar SourceMotion para que funcione con su arquitectura real"""
    
    print("🔧 FIX FINAL - ARQUITECTURA CORRECTA\n")
    
    # Backup
    backup_dir = f"backup_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    import shutil
    shutil.copy2(motion_file, os.path.join(backup_dir, "motion_components.py"))
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # 1. Encontrar la clase SourceMotion
    print("1️⃣ ACTUALIZANDO SourceMotion...")
    
    class_pattern = r'(class SourceMotion[^:]*:.*?)(?=\nclass|\Z)'
    class_match = re.search(class_pattern, content, re.DOTALL)
    
    if not class_match:
        print("❌ No se encontró SourceMotion")
        return False
    
    class_content = class_match.group(1)
    
    # 2. Reemplazar el método update problemático
    print("\n2️⃣ CORRIGIENDO método update()...")
    
    new_update = '''    def update(self, dt: float):
        """Actualizar posición aplicando offsets a state.position"""
        if dt < 0.0001:
            return
        
        # Resetear offsets
        self.concentration_offset = np.zeros(3)
        self.macro_rotation_offset = np.zeros(3)
        self.trajectory_offset = np.zeros(3)
        self.algorithmic_rotation_offset = np.zeros(3)
        
        # Posición base del state
        base_pos = self.state.position.copy()
        
        # 1. Calcular offset de trayectoria individual (IS)
        if 'individual_trajectory' in self.components:
            traj = self.components['individual_trajectory']
            if hasattr(traj, 'enabled') and traj.enabled:
                # La trayectoria individual puede tener su propia lógica
                # Por ahora solo marcamos que existe
                pass
        
        # 2. Calcular offset de concentración
        if 'concentration' in self.components:
            conc = self.components['concentration']
            if hasattr(conc, 'enabled') and conc.enabled and hasattr(conc, 'factor'):
                if conc.factor < 0.99:  # Solo si hay concentración significativa
                    # Punto objetivo - usar el centro del macro o un punto fijo
                    target = getattr(conc, 'target_point', self.macro_reference)
                    
                    # Interpolar hacia el punto de concentración
                    # factor 0 = totalmente concentrado, factor 1 = sin concentración
                    concentrated = base_pos * conc.factor + target * (1 - conc.factor)
                    self.concentration_offset = concentrated - base_pos
        
        # 3. Actualizar la posición en el state sumando offsets
        self.state.position = (base_pos + 
                              self.concentration_offset + 
                              self.macro_rotation_offset +
                              self.trajectory_offset +
                              self.algorithmic_rotation_offset)'''
    
    # Reemplazar el método update existente
    update_pattern = r'def update\(self.*?\):\s*\n.*?(?=\n    def|\Z)'
    new_class_content = re.sub(update_pattern, new_update, class_content, flags=re.DOTALL)
    
    # 3. Agregar método get_position si no existe
    print("\n3️⃣ AGREGANDO get_position()...")
    
    if 'def get_position' not in new_class_content:
        get_position_method = '''
    def get_position(self):
        """Obtener la posición actual del state"""
        return self.state.position.copy()'''
        
        # Agregar antes del final de la clase
        new_class_content = new_class_content.rstrip() + '\n' + get_position_method + '\n'
    
    # Reemplazar en el contenido completo
    content = content.replace(class_content, new_class_content)
    
    # 4. Guardar
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print("✅ Archivo actualizado")
    
    # 5. Crear test final
    test_script = '''#!/usr/bin/env python3
"""
🧪 TEST FINAL - Verificar que la concentración funciona
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("🧪 TEST FINAL DE CONCENTRACIÓN\\n")

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine y macro
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("test", source_count=3, formation="line", spacing=2.0)
    
    print("✅ Macro creado con 3 fuentes en línea")
    
    if hasattr(engine, '_source_motions'):
        motions = engine._source_motions
        
        # Mostrar posiciones iniciales
        print("\\n📍 POSICIONES INICIALES:")
        positions_before = {}
        for source_id, motion in motions.items():
            pos = motion.state.position.copy()
            positions_before[source_id] = pos
            print(f"   Fuente {source_id}: {pos}")
        
        # Aplicar concentración
        print("\\n🎯 APLICANDO CONCENTRACIÓN (factor 0.1)...")
        engine.set_macro_concentration(macro_id, 0.1)
        
        # Verificar que se creó el componente
        first_motion = list(motions.values())[0]
        if 'concentration' in first_motion.components:
            conc = first_motion.components['concentration']
            print(f"   ✅ Componente creado - factor: {conc.factor}")
        
        # Update manual de cada motion
        print("\\n🔄 UPDATE MANUAL DE CADA FUENTE:")
        for source_id, motion in motions.items():
            print(f"\\n   Fuente {source_id}:")
            print(f"   Antes: {motion.state.position}")
            
            # Update
            motion.update(0.1)
            
            print(f"   Después: {motion.state.position}")
            print(f"   concentration_offset: {motion.concentration_offset}")
            
            # Verificar si cambió
            if not np.allclose(positions_before[source_id], motion.state.position):
                print("   ✅ ¡POSICIÓN CAMBIÓ!")
            else:
                print("   ❌ Posición sin cambios")
        
        # Test con engine.update()
        print("\\n🔄 TEST CON ENGINE.UPDATE():")
        
        # Reset y probar de nuevo
        for motion in motions.values():
            motion.state.position = positions_before[list(motions.keys())[0]].copy()
        
        # Update del engine
        engine.update()
        
        print("\\n📍 POSICIONES DESPUÉS DE ENGINE.UPDATE():")
        for source_id, motion in motions.items():
            print(f"   Fuente {source_id}: {motion.state.position}")
    
    print("\\n✅ Test completado")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\\n" + "="*60)
print("💡 Si las posiciones cambiaron con la concentración,")
print("   entonces el sistema está funcionando correctamente.")
print("   Prueba ahora en el controller interactivo.")
'''
    
    with open("test_final_concentration.py", 'w') as f:
        f.write(test_script)
    
    print("\n✅ Test creado: test_final_concentration.py")
    
    return True

if __name__ == "__main__":
    success = fix_source_motion_architecture()
    
    if success:
        print("\n" + "="*60)
        print("🎉 FIX FINAL COMPLETADO")
        print("="*60)
        
        print("\n✅ Cambios realizados:")
        print("   1. update() ahora modifica state.position")
        print("   2. No necesita self.time")
        print("   3. Calcula concentration_offset correctamente")
        print("   4. get_position() devuelve state.position")
        
        print("\n🚀 EJECUTA EL TEST FINAL:")
        print("   python test_final_concentration.py")
        
        print("\n📊 Si funciona ahí, prueba en:")
        print("   python trajectory_hub/interface/interactive_controller.py")
        
        print("\n🎯 ¡La concentración debería funcionar finalmente!")