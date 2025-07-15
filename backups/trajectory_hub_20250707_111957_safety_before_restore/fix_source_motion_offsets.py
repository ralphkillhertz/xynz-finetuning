#!/usr/bin/env python3
"""
🔧 FIX DEFINITIVO - Agregar offsets a SourceMotion
⚡ Esta vez a la clase correcta que se está usando
"""

import os
import re
from datetime import datetime

def fix_source_motion_offsets():
    """Agregar los offsets faltantes a SourceMotion"""
    
    print("🔧 AGREGANDO OFFSETS A SourceMotion\n")
    
    # Backup
    backup_dir = f"backup_offsets_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
    
    print("1️⃣ BUSCANDO CLASE SourceMotion...")
    
    # Encontrar la clase SourceMotion
    class_pattern = r'(class SourceMotion[^:]*:.*?)(?=\nclass|\Z)'
    class_match = re.search(class_pattern, content, re.DOTALL)
    
    if not class_match:
        print("❌ No se encontró la clase SourceMotion")
        return False
    
    print("✅ Clase SourceMotion encontrada")
    
    # 2. Verificar si tiene __init__
    class_content = class_match.group(1)
    init_pattern = r'def __init__\(self.*?\):\s*\n(.*?)(?=\n    def|\Z)'
    init_match = re.search(init_pattern, class_content, re.DOTALL)
    
    if init_match:
        print("\n2️⃣ MODIFICANDO __init__...")
        
        init_body = init_match.group(1)
        
        # Verificar si ya tiene offsets
        if 'concentration_offset' in init_body:
            print("   ℹ️  Los offsets ya existen en __init__")
        else:
            print("   ➕ Agregando inicialización de offsets...")
            
            # Encontrar dónde insertar (después de las primeras asignaciones)
            lines = init_body.split('\n')
            insert_index = 0
            
            # Buscar después de self.components o similar
            for i, line in enumerate(lines):
                if 'self.' in line and '=' in line:
                    insert_index = i + 1
            
            # Preparar las líneas de offset
            offset_lines = [
                "        # Offsets para arquitectura de deltas",
                "        self.concentration_offset = np.zeros(3)",
                "        self.macro_rotation_offset = np.zeros(3)",
                "        self.trajectory_offset = np.zeros(3)",
                "        self.algorithmic_rotation_offset = np.zeros(3)",
                ""
            ]
            
            # Insertar
            new_lines = lines[:insert_index] + offset_lines + lines[insert_index:]
            new_init_body = '\n'.join(new_lines)
            
            # Reemplazar en la clase
            new_class_content = class_content.replace(init_body, new_init_body)
            content = content.replace(class_content, new_class_content)
    
    # 3. Verificar/modificar el método update
    print("\n3️⃣ VERIFICANDO MÉTODO update()...")
    
    # Buscar update en la clase actualizada
    class_match = re.search(class_pattern, content, re.DOTALL)
    class_content = class_match.group(1)
    
    update_pattern = r'def update\(self[^)]*\):\s*\n(.*?)(?=\n    def|\Z)'
    update_match = re.search(update_pattern, class_content, re.DOTALL)
    
    if update_match:
        update_method = update_match.group(0)
        update_body = update_match.group(1)
        
        # Verificar si calcula offsets
        if 'concentration_offset' not in update_body:
            print("   ⚠️  update() no calcula offsets, agregando lógica...")
            
            # Nuevo método update con cálculo de offsets
            new_update = '''def update(self, dt: float):
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
            if traj.enabled:
                # Asumiendo que tiene un método para obtener posición
                if hasattr(traj, 'get_position'):
                    self.trajectory_offset = traj.get_position(self.time) - self.base_position
        
        # 2. Calcular offset de concentración
        if 'concentration' in self.components:
            conc = self.components['concentration']
            if conc.enabled and conc.factor < 0.99:
                # El punto de concentración
                target = getattr(conc, 'target_point', np.zeros(3))
                current = self.base_position + self.trajectory_offset
                
                # Interpolar hacia el punto de concentración
                concentrated = current * conc.factor + target * (1 - conc.factor)
                self.concentration_offset = concentrated - current
        
        # 3. Actualizar tiempo
        self.time += dt'''
            
            # Reemplazar el método update
            new_class_content = class_content.replace(update_method, new_update)
            content = content.replace(class_content, new_class_content)
        else:
            print("   ✅ update() ya calcula offsets")
    else:
        print("   ❌ No se encontró método update()")
    
    # 4. Verificar/agregar get_position si es necesario
    print("\n4️⃣ VERIFICANDO get_position()...")
    
    # Actualizar referencia a la clase
    class_match = re.search(class_pattern, content, re.DOTALL)
    class_content = class_match.group(1)
    
    if 'def get_position' not in class_content:
        print("   ➕ Agregando get_position()...")
        
        get_position_method = '''
    def get_position(self) -> np.ndarray:
        """Obtener posición final sumando TODOS los offsets"""
        if not hasattr(self, 'concentration_offset'):
            self.concentration_offset = np.zeros(3)
        if not hasattr(self, 'macro_rotation_offset'):
            self.macro_rotation_offset = np.zeros(3)
        if not hasattr(self, 'trajectory_offset'):
            self.trajectory_offset = np.zeros(3)
        if not hasattr(self, 'algorithmic_rotation_offset'):
            self.algorithmic_rotation_offset = np.zeros(3)
            
        return (self.base_position + 
                self.trajectory_offset + 
                self.concentration_offset + 
                self.macro_rotation_offset +
                self.algorithmic_rotation_offset)'''
        
        # Agregar al final de la clase
        new_class_content = class_content.rstrip() + '\n' + get_position_method + '\n'
        content = content.replace(class_content, new_class_content)
    
    # 5. Guardar cambios
    print("\n5️⃣ GUARDANDO CAMBIOS...")
    
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print("✅ Archivo modificado")
    
    # Verificar sintaxis
    try:
        compile(content, motion_file, 'exec')
        print("✅ Sintaxis verificada")
        return True
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: línea {e.lineno}")
        return False

if __name__ == "__main__":
    success = fix_source_motion_offsets()
    
    if success:
        print("\n🎉 FIX COMPLETADO")
        print("\n🚀 Ahora ejecuta:")
        print("   python verify_source_motions.py")
        print("\nY luego prueba en el controller:")
        print("   python trajectory_hub/interface/interactive_controller.py")
    else:
        print("\n❌ Hubo problemas con el fix")
        print("Revisa el backup en backup_offsets_*")