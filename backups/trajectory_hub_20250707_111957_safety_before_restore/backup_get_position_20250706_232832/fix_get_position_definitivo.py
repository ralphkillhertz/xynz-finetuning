#!/usr/bin/env python3
"""
🔧 FIX DEFINITIVO - Asegurar que get_position() sume los offsets
⚡ Esta vez encontrando y corrigiendo el método correcto
"""

import os
import re
from datetime import datetime

def find_and_fix_get_position():
    """Encontrar y corregir get_position() para que sume offsets"""
    
    print("🔧 FIX DEFINITIVO - get_position()\n")
    
    # Backup
    backup_dir = f"backup_get_position_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # 1. Buscar todos los archivos que podrían tener get_position
    print("1️⃣ BUSCANDO ARCHIVOS CON get_position()...")
    
    files_to_check = []
    import glob
    
    # Buscar en todo el proyecto
    for pattern in ['**/*.py', 'trajectory_hub/**/*.py']:
        files_to_check.extend(glob.glob(pattern, recursive=True))
    
    files_with_get_position = []
    
    for file in files_to_check:
        if 'backup' in file or '__pycache__' in file:
            continue
            
        try:
            with open(file, 'r') as f:
                content = f.read()
                if 'def get_position' in content and ('Source' in content or 'Motion' in content):
                    files_with_get_position.append(file)
        except:
            pass
    
    print(f"\n📄 Archivos encontrados con get_position:")
    for f in files_with_get_position:
        print(f"   • {f}")
    
    # 2. Modificar cada uno
    modified_files = []
    
    for file in files_with_get_position:
        print(f"\n2️⃣ PROCESANDO: {file}")
        
        # Backup
        import shutil
        backup_name = os.path.join(backup_dir, os.path.basename(file))
        shutil.copy2(file, backup_name)
        
        with open(file, 'r') as f:
            content = f.read()
        
        # Buscar el método get_position
        get_pos_pattern = r'(def get_position\(self[^)]*\)[^:]*:)(.*?)(?=\n    def|\nclass|\Z)'
        matches = list(re.finditer(get_pos_pattern, content, re.DOTALL))
        
        if matches:
            for match in matches:
                method_body = match.group(2)
                
                # Verificar si ya suma offsets
                if '+' in method_body and 'offset' in method_body:
                    print("   ✅ Ya suma offsets")
                    continue
                
                # Verificar si es un método simple que retorna position
                if 'return self.position' in method_body or 'return self._position' in method_body:
                    print("   🔧 Modificando para sumar offsets...")
                    
                    # Nuevo método que suma offsets
                    new_method = match.group(1) + '''
        """Obtener posición sumando todos los offsets"""
        base = getattr(self, 'position', getattr(self, '_position', getattr(self, 'base_position', np.zeros(3))))
        
        # Sumar offsets si existen
        if hasattr(self, 'concentration_offset'):
            base = base + self.concentration_offset
        elif hasattr(self, 'motion') and hasattr(self.motion, 'concentration_offset'):
            base = base + self.motion.concentration_offset
            
        if hasattr(self, 'macro_rotation_offset'):
            base = base + self.macro_rotation_offset
        elif hasattr(self, 'motion') and hasattr(self.motion, 'macro_rotation_offset'):
            base = base + self.motion.macro_rotation_offset
            
        if hasattr(self, 'trajectory_offset'):
            base = base + self.trajectory_offset
        elif hasattr(self, 'motion') and hasattr(self.motion, 'trajectory_offset'):
            base = base + self.motion.trajectory_offset
            
        if hasattr(self, 'algorithmic_rotation_offset'):
            base = base + self.algorithmic_rotation_offset
        elif hasattr(self, 'motion') and hasattr(self.motion, 'algorithmic_rotation_offset'):
            base = base + self.motion.algorithmic_rotation_offset
            
        return base'''
                    
                    # Reemplazar
                    content = content[:match.start()] + new_method + content[match.end():]
                    modified_files.append(file)
                    
                # Si retorna base_position + algo
                elif 'return' in method_body and 'base_position' in method_body:
                    print("   ⚠️  Método más complejo, verificando...")
                    
                    # Si no suma todos los offsets, modificar
                    required_offsets = ['concentration_offset', 'macro_rotation_offset', 
                                       'trajectory_offset', 'algorithmic_rotation_offset']
                    
                    missing = [off for off in required_offsets if off not in method_body]
                    
                    if missing:
                        print(f"   ❌ Faltan offsets: {missing}")
                        # Aquí podríamos hacer una modificación más compleja si es necesario
        
        # Guardar cambios si se modificó
        if file in modified_files:
            with open(file, 'w') as f:
                f.write(content)
            print("   ✅ Archivo modificado")
    
    # 3. Caso especial: SourceMotion en motion_components.py
    print("\n3️⃣ VERIFICANDO SourceMotion en motion_components.py...")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    if os.path.exists(motion_file):
        with open(motion_file, 'r') as f:
            content = f.read()
        
        # Buscar la clase SourceMotion
        class_match = re.search(r'class SourceMotion.*?(?=\nclass|\Z)', content, re.DOTALL)
        
        if class_match:
            class_content = class_match.group(0)
            
            # Verificar si tiene get_position
            if 'def get_position' not in class_content:
                print("   ⚠️  SourceMotion no tiene get_position, agregándolo...")
                
                # Agregar el método
                get_position_method = '''
    def get_position(self) -> np.ndarray:
        """Obtener posición final sumando TODOS los componentes"""
        return (self.base_position + 
                self.trajectory_offset + 
                self.concentration_offset + 
                self.macro_rotation_offset +
                self.algorithmic_rotation_offset)'''
                
                # Insertar antes del final de la clase
                insert_pos = class_match.end() - 1
                content = content[:insert_pos] + get_position_method + '\n' + content[insert_pos:]
                
                with open(motion_file, 'w') as f:
                    f.write(content)
                
                print("   ✅ get_position agregado a SourceMotion")
                modified_files.append(motion_file)
    
    # 4. Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    
    if modified_files:
        print(f"\n✅ Archivos modificados: {len(modified_files)}")
        for f in modified_files:
            print(f"   • {f}")
    else:
        print("\n⚠️  No se encontraron archivos para modificar")
        print("   Puede que el problema esté en otro lugar")
    
    print(f"\n📁 Backup guardado en: {backup_dir}")
    
    # 5. Verificación adicional
    print("\n4️⃣ VERIFICACIÓN ADICIONAL")
    
    # Buscar dónde se crean las fuentes
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    if os.path.exists(engine_file):
        with open(engine_file, 'r') as f:
            engine_content = f.read()
        
        # Buscar create_source
        if 'def create_source' in engine_content:
            create_match = re.search(r'def create_source.*?\n(?:.*?\n)*?return.*?\n', 
                                   engine_content, re.DOTALL)
            if create_match:
                create_method = create_match.group(0)
                print("\n📍 Método create_source encontrado")
                
                # Ver qué tipo de objeto crea
                if 'Source(' in create_method:
                    print("   → Crea objetos Source")
                elif 'TrajectorySource(' in create_method:
                    print("   → Crea objetos TrajectorySource")
                else:
                    print("   → Tipo de objeto no claro")
    
    print("\n🚀 PRÓXIMO PASO:")
    print("   python trajectory_hub/interface/interactive_controller.py")

if __name__ == "__main__":
    find_and_fix_get_position()