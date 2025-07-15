#!/usr/bin/env python3
"""
🔧 Implementación CORRECTA de arquitectura de deltas
⚡ Esta vez asegurándonos de que funcione
"""

import os
import re
import shutil
from datetime import datetime
import numpy as np

def implement_delta_architecture_correctly():
    """Implementar arquitectura de deltas que FUNCIONE"""
    
    print("🚀 IMPLEMENTACIÓN CORRECTA DE ARQUITECTURA DE DELTAS\n")
    
    # Backup
    backup_dir = f"backup_delta_correct_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # 1. Encontrar y modificar SourceMotion o equivalente
    print("1️⃣ Buscando clase SourceMotion...")
    
    motion_file = None
    # Buscar en múltiples ubicaciones posibles
    possible_files = [
        "trajectory_hub/core/motion_components.py",
        "trajectory_hub/core/source_motion.py",
        "trajectory_hub/motion/source_motion.py"
    ]
    
    for pf in possible_files:
        if os.path.exists(pf):
            with open(pf, 'r') as f:
                if 'class SourceMotion' in f.read():
                    motion_file = pf
                    break
    
    if not motion_file:
        # Buscar globalmente
        import glob
        for f in glob.glob("**/*.py", recursive=True):
            if os.path.exists(f):
                with open(f, 'r') as file:
                    if 'class SourceMotion' in file.read():
                        motion_file = f
                        break
    
    if not motion_file:
        print("❌ No se encontró SourceMotion")
        return False
    
    print(f"   ✅ Encontrado: {motion_file}")
    shutil.copy2(motion_file, os.path.join(backup_dir, os.path.basename(motion_file)))
    
    # Leer contenido
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # 2. Reemplazar el método update con arquitectura de deltas
    print("\n2️⃣ Implementando arquitectura de deltas en update()...")
    
    new_update_method = '''    def update(self, dt: float):
        """Actualizar posición usando arquitectura de DELTAS (suma)"""
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
                self.trajectory_offset = traj.get_position(self.time) - self.base_position
        
        # 2. Calcular offset de concentración
        if 'concentration' in self.components:
            conc = self.components['concentration']
            if conc.enabled and conc.factor < 0.99:
                target = conc.target_point
                current = self.get_position()
                # Interpolar hacia el punto de concentración
                concentrated = current * conc.factor + target * (1 - conc.factor)
                self.concentration_offset = concentrated - current
        
        # 3. Calcular offset de rotación del macro (MS)
        if 'macro_rotation' in self.components:
            rot = self.components['macro_rotation']
            if rot.enabled:
                # Aplicar rotación alrededor del centro del macro
                angle = rot.angle
                center = rot.center
                current = self.get_position()
                
                # Rotar alrededor del centro
                relative = current - center
                cos_a, sin_a = np.cos(angle), np.sin(angle)
                
                if rot.axis == 'yaw':  # Rotación en Z
                    rotated = np.array([
                        relative[0] * cos_a - relative[1] * sin_a,
                        relative[0] * sin_a + relative[1] * cos_a,
                        relative[2]
                    ])
                elif rot.axis == 'pitch':  # Rotación en Y
                    rotated = np.array([
                        relative[0] * cos_a + relative[2] * sin_a,
                        relative[1],
                        -relative[0] * sin_a + relative[2] * cos_a
                    ])
                else:  # roll - Rotación en X
                    rotated = np.array([
                        relative[0],
                        relative[1] * cos_a - relative[2] * sin_a,
                        relative[1] * sin_a + relative[2] * cos_a
                    ])
                
                self.macro_rotation_offset = (rotated + center) - current
        
        # 4. Calcular offset de rotación algorítmica
        if 'algorithmic_rotation' in self.components:
            algo_rot = self.components['algorithmic_rotation']
            if algo_rot.enabled:
                # Aplicar patrón de rotación
                self.algorithmic_rotation_offset = algo_rot.get_offset(self.time)
        
        # Actualizar tiempo
        self.time += dt
    
    def get_position(self) -> np.ndarray:
        """Obtener posición final sumando TODOS los componentes"""
        return (self.base_position + 
                self.trajectory_offset + 
                self.concentration_offset + 
                self.macro_rotation_offset +
                self.algorithmic_rotation_offset)
    
    def _combine_components(self) -> np.ndarray:
        """Combinar todos los offsets (método auxiliar)"""
        return (self.trajectory_offset + 
                self.concentration_offset + 
                self.macro_rotation_offset +
                self.algorithmic_rotation_offset)'''
    
    # Reemplazar el método update existente
    update_pattern = r'def update\(self.*?\n(?=\n    def|\nclass|\Z)'
    content = re.sub(update_pattern, new_update_method, content, flags=re.DOTALL)
    
    # También necesitamos reemplazar get_position si existe
    get_pos_pattern = r'def get_position\(self.*?\n(?=\n    def|\nclass|\Z)'
    if re.search(get_pos_pattern, content, re.DOTALL):
        # Ya agregado en new_update_method
        pass
    else:
        # Agregar get_position al final de la clase
        class_end = content.rfind('\n\nclass')
        if class_end == -1:
            class_end = len(content)
        
        get_position_method = '''
    def get_position(self) -> np.ndarray:
        """Obtener posición final sumando TODOS los componentes"""
        if not hasattr(self, 'trajectory_offset'):
            self.trajectory_offset = np.zeros(3)
        if not hasattr(self, 'concentration_offset'):
            self.concentration_offset = np.zeros(3)
        if not hasattr(self, 'macro_rotation_offset'):
            self.macro_rotation_offset = np.zeros(3)
        if not hasattr(self, 'algorithmic_rotation_offset'):
            self.algorithmic_rotation_offset = np.zeros(3)
            
        return (self.base_position + 
                self.trajectory_offset + 
                self.concentration_offset + 
                self.macro_rotation_offset +
                self.algorithmic_rotation_offset)'''
        
        content = content[:class_end] + get_position_method + content[class_end:]
    
    # Asegurar que los offsets existen como atributos
    if "__init__" in content:
        init_pattern = r'def __init__\(self.*?\):\s*\n'
        init_match = re.search(init_pattern, content)
        if init_match:
            # Buscar dónde insertar
            init_end = init_match.end()
            # Buscar la primera línea que no sea un comentario después del init
            lines_after = content[init_end:].split('\n')
            insert_line = 0
            
            for i, line in enumerate(lines_after):
                if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""'):
                    insert_line = i
                    break
            
            # Calcular posición de inserción
            insert_pos = init_end + sum(len(line) + 1 for line in lines_after[:insert_line])
            
            # Agregar inicialización de offsets
            offset_init = """        # Offsets para arquitectura de deltas
        self.concentration_offset = np.zeros(3)
        self.macro_rotation_offset = np.zeros(3)
        self.trajectory_offset = np.zeros(3)
        self.algorithmic_rotation_offset = np.zeros(3)
        """
            
            content = content[:insert_pos] + offset_init + content[insert_pos:]
    
    # Guardar cambios
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print("   ✅ Arquitectura de deltas implementada")
    
    # 3. Asegurar que enhanced_trajectory_engine.py llama a update correctamente
    print("\n3️⃣ Verificando enhanced_trajectory_engine.py...")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    if os.path.exists(engine_file):
        shutil.copy2(engine_file, os.path.join(backup_dir, "enhanced_trajectory_engine.py"))
        
        with open(engine_file, 'r') as f:
            engine_content = f.read()
        
        # Verificar que apply_concentration existe y funciona
        if 'def apply_concentration' not in engine_content:
            print("   ⚠️  Agregando apply_concentration...")
            
            apply_conc = '''
    def apply_concentration(self):
        """Aplicar concentración a todos los macros"""
        # La concentración ahora se maneja en SourceMotion.update()
        # Solo necesitamos asegurar que los parámetros estén configurados
        pass'''
            
            # Insertar antes de update
            engine_content = engine_content.replace("    def update(self", apply_conc + "\n\n    def update(self")
        
        # Asegurar que update() no tenga parámetros extra
        update_sig_pattern = r'def update\(self.*?\):'
        update_match = re.search(update_sig_pattern, engine_content)
        if update_match:
            current_sig = update_match.group(0)
            if current_sig != "def update(self):":
                print("   ⚠️  Corrigiendo firma de update()...")
                engine_content = engine_content.replace(current_sig, "def update(self):")
        
        with open(engine_file, 'w') as f:
            f.write(engine_content)
        
        print("   ✅ Engine verificado")
    
    print(f"\n✅ Implementación completada")
    print(f"📁 Backup en: {backup_dir}")
    
    print("\n🎯 CAMBIOS REALIZADOS:")
    print("   1. SourceMotion ahora usa arquitectura de deltas")
    print("   2. get_position() suma todos los offsets")
    print("   3. Cada componente contribuye independientemente")
    
    print("\n🚀 PRÓXIMO PASO:")
    print("   python trajectory_hub/interface/interactive_controller.py")
    
    return True

if __name__ == "__main__":
    implement_delta_architecture_correctly()