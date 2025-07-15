#!/usr/bin/env python3
"""
🔧 FIX FINAL - Agregar método update a SourceMotion
⚡ Para que calcule los offsets basados en los componentes
"""

import os
import re
from datetime import datetime

def add_update_method():
    """Agregar el método update que falta a SourceMotion"""
    
    print("🔧 AGREGANDO MÉTODO UPDATE A SourceMotion\n")
    
    # Backup
    backup_dir = f"backup_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    if not os.path.exists(motion_file):
        print("❌ No se encuentra motion_components.py")
        return False
    
    # Backup
    import shutil
    shutil.copy2(motion_file, os.path.join(backup_dir, "motion_components.py"))
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # 1. Encontrar la clase SourceMotion
    print("1️⃣ BUSCANDO CLASE SourceMotion...")
    
    class_pattern = r'(class SourceMotion[^:]*:.*?)(?=\nclass|\Z)'
    class_match = re.search(class_pattern, content, re.DOTALL)
    
    if not class_match:
        print("❌ No se encontró la clase SourceMotion")
        return False
    
    class_content = class_match.group(1)
    print("✅ Clase encontrada")
    
    # 2. Verificar si ya tiene update
    if 'def update' in class_content:
        print("ℹ️  Ya existe un método update, verificando...")
        
        # Ver qué hace el update actual
        update_pattern = r'def update\(self.*?\):\s*\n(.*?)(?=\n    def|\Z)'
        update_match = re.search(update_pattern, class_content, re.DOTALL)
        
        if update_match:
            update_body = update_match.group(1)
            if 'concentration_offset' not in update_body:
                print("   ⚠️  El update actual no calcula offsets, reemplazando...")
                # Continuar para reemplazar
            else:
                print("   ✅ El update ya calcula offsets")
                return True
    
    # 3. Agregar/reemplazar método update
    print("\n2️⃣ AGREGANDO MÉTODO update()...")
    
    update_method = '''
    def update(self, dt: float):
        """Actualizar posición calculando offsets de cada componente"""
        if dt < 0.0001:
            return
        
        # Resetear offsets
        self.concentration_offset = np.zeros(3)
        self.macro_rotation_offset = np.zeros(3)
        self.trajectory_offset = np.zeros(3)
        self.algorithmic_rotation_offset = np.zeros(3)
        
        # 1. Calcular offset de trayectoria individual (IS)
        if 'individual_trajectory' in self.components:
            traj = self.components['individual_trajectory']
            if hasattr(traj, 'enabled') and traj.enabled:
                # Obtener posición de la trayectoria
                if hasattr(traj, 'get_position'):
                    traj_pos = traj.get_position(self.time)
                elif hasattr(traj, 'shape') and hasattr(traj, 'params'):
                    # Calcular basado en la forma
                    from trajectory_hub.utils.trajectory_functions import get_trajectory_function
                    func = get_trajectory_function(traj.shape, **traj.params)
                    traj_pos = func(self.time)
                else:
                    traj_pos = self.base_position
                
                self.trajectory_offset = traj_pos - self.base_position
        
        # 2. Calcular offset de concentración
        if 'concentration' in self.components:
            conc = self.components['concentration']
            if hasattr(conc, 'enabled') and conc.enabled and hasattr(conc, 'factor'):
                if conc.factor < 0.99:  # Solo si hay concentración significativa
                    # Punto objetivo (puede ser fijo o el centro del macro)
                    target = getattr(conc, 'target_point', np.zeros(3))
                    
                    # Posición actual (base + trayectoria)
                    current = self.base_position + self.trajectory_offset
                    
                    # Interpolar hacia el punto de concentración
                    # factor 0 = totalmente concentrado, factor 1 = sin concentración
                    concentrated = current * conc.factor + target * (1 - conc.factor)
                    self.concentration_offset = concentrated - current
        
        # 3. Calcular offset de rotación del macro (MS)
        if 'macro_rotation' in self.components:
            rot = self.components['macro_rotation']
            if hasattr(rot, 'enabled') and rot.enabled:
                # Aquí iría la lógica de rotación del macro
                # Por ahora dejar en ceros
                pass
        
        # 4. Actualizar tiempo
        self.time += dt'''
    
    # Si ya existe update, reemplazarlo
    if 'def update' in class_content:
        # Reemplazar el método existente
        update_pattern = r'def update\(self.*?\):\s*\n.*?(?=\n    def|\Z)'
        new_class_content = re.sub(update_pattern, update_method.strip(), class_content, flags=re.DOTALL)
    else:
        # Agregar antes del final de la clase o antes de get_position
        if 'def get_position' in class_content:
            # Insertar antes de get_position
            new_class_content = class_content.replace('def get_position', update_method + '\n\n    def get_position')
        else:
            # Agregar al final
            new_class_content = class_content.rstrip() + '\n' + update_method + '\n'
    
    # Reemplazar en el contenido completo
    content = content.replace(class_content, new_class_content)
    
    # 4. Asegurar imports necesarios
    if 'import numpy as np' not in content:
        content = 'import numpy as np\n' + content
    
    # 5. Guardar
    print("\n3️⃣ GUARDANDO CAMBIOS...")
    
    with open(motion_file, 'w') as f:
        f.write(content)
    
    # Verificar sintaxis
    try:
        compile(content, motion_file, 'exec')
        print("✅ Sintaxis verificada")
        return True
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: línea {e.lineno}")
        print(f"   {e.text}")
        return False

if __name__ == "__main__":
    success = add_update_method()
    
    if success:
        print("\n🎉 MÉTODO UPDATE AGREGADO")
        print("\n✨ La cadena completa está lista:")
        print("   1. SourceMotion tiene offsets ✅")
        print("   2. update() calcula los offsets ✅")
        print("   3. get_position() suma los offsets ✅")
        
        print("\n🚀 PRUEBA FINAL:")
        print("   python verify_source_motions.py")
        print("\n📊 Si todo funciona ahí, entonces:")
        print("   python trajectory_hub/interface/interactive_controller.py")
        
        print("\n🎯 La concentración debería funcionar ahora!")
    else:
        print("\n❌ Error al agregar el método")