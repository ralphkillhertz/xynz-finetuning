#!/usr/bin/env python3
"""
🔧 FIX - Encontrar y usar el atributo correcto de posición
⚡ SourceMotion debe tener position o _position en lugar de base_position
"""

import os
import re

def fix_base_position_attribute():
    """Encontrar y corregir el nombre del atributo de posición"""
    
    print("🔧 CORRIGIENDO ATRIBUTO DE POSICIÓN\n")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # 1. Buscar qué atributos de posición tiene SourceMotion
    print("1️⃣ BUSCANDO ATRIBUTOS DE POSICIÓN EN SourceMotion...")
    
    # Buscar la clase SourceMotion y su __init__
    class_pattern = r'class SourceMotion[^:]*:.*?def __init__\(self.*?\):\s*\n(.*?)(?=\n    def|\nclass|\Z)'
    class_match = re.search(class_pattern, content, re.DOTALL)
    
    position_attr = None
    
    if class_match:
        init_body = class_match.group(1)
        
        # Buscar asignaciones relacionadas con position
        position_patterns = [
            r'self\.(position)\s*=',
            r'self\.(_position)\s*=',
            r'self\.(pos)\s*=',
            r'self\.(base_pos)\s*=',
            r'self\.(initial_position)\s*='
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, init_body)
            if match:
                position_attr = match.group(1)
                print(f"   ✅ Encontrado: self.{position_attr}")
                break
        
        if not position_attr:
            # Buscar cualquier cosa con zeros(3) o array
            array_patterns = re.findall(r'self\.(\w+)\s*=\s*(?:np\.)?(?:zeros\(3\)|array\(\[.*?\]\))', init_body)
            if array_patterns:
                # Probablemente el primero sea la posición
                position_attr = array_patterns[0]
                print(f"   📍 Posible atributo: self.{position_attr}")
    
    if not position_attr:
        # Valor por defecto
        position_attr = 'position'
        print(f"   ⚠️  No encontrado, usando default: self.{position_attr}")
    
    # 2. Buscar también cómo se llama en get_position
    print("\n2️⃣ VERIFICANDO get_position()...")
    
    get_pos_pattern = r'def get_position\(self.*?\).*?:\s*\n(.*?)(?=\n    def|\nclass|\Z)'
    get_pos_match = re.search(get_pos_pattern, content, re.DOTALL)
    
    if get_pos_match:
        get_pos_body = get_pos_match.group(1)
        
        # Ver qué usa como base
        base_patterns = re.findall(r'self\.(\w+)\s*\+', get_pos_body)
        if base_patterns and base_patterns[0] != 'base_position':
            position_attr = base_patterns[0]
            print(f"   ✅ get_position usa: self.{position_attr}")
    
    # 3. Actualizar el método update
    print(f"\n3️⃣ ACTUALIZANDO update() para usar self.{position_attr}...")
    
    # Reemplazar base_position con el atributo correcto
    content = content.replace('self.base_position', f'self.{position_attr}')
    
    # También actualizar get_position si es necesario
    if 'self.base_position' in content:
        content = content.replace('self.base_position', f'self.{position_attr}')
    
    # 4. Guardar
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print("✅ Archivo actualizado")
    
    # 5. Crear test específico para verificar
    test_script = f'''#!/usr/bin/env python3
"""
🧪 Test rápido del atributo de posición
"""

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
    
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("test", source_count=1)
    
    # Obtener la primera fuente
    if hasattr(engine, '_source_motions') and engine._source_motions:
        motion = list(engine._source_motions.values())[0]
        
        print("✅ SourceMotion obtenido")
        print(f"   Tipo: {{type(motion).__name__}}")
        
        # Ver qué atributos de posición tiene
        print("\\n📍 Atributos de posición:")
        for attr in ['{position_attr}', 'position', '_position', 'pos', 'base_position']:
            if hasattr(motion, attr):
                value = getattr(motion, attr)
                print(f"   ✅ {{attr}}: {{value}}")
        
        # Test update
        print("\\n🧪 Test update()...")
        try:
            motion.update(0.1)
            print("   ✅ update() ejecutado sin errores")
            
            # Ver offsets
            print("\\n📊 Offsets después de update:")
            print(f"   concentration_offset: {{motion.concentration_offset}}")
            
        except Exception as e:
            print(f"   ❌ Error en update: {{e}}")
        
        # Test get_position
        try:
            pos = motion.get_position()
            print(f"\\n✅ get_position(): {{pos}}")
        except Exception as e:
            print(f"\\n❌ Error en get_position: {{e}}")
            
except Exception as e:
    print(f"❌ Error: {{e}}")
    import traceback
    traceback.print_exc()
'''
    
    with open("test_position_attribute.py", 'w') as f:
        f.write(test_script)
    
    print("\n✅ Script de test creado: test_position_attribute.py")
    
    return position_attr

if __name__ == "__main__":
    attr = fix_base_position_attribute()
    
    print("\n" + "="*60)
    print("🎯 RESUMEN")
    print("="*60)
    
    print(f"\n✅ Atributo de posición actualizado a: self.{attr}")
    
    print("\n🚀 EJECUTA EL TEST:")
    print("   python test_position_attribute.py")
    
    print("\n📊 Si funciona, entonces prueba:")
    print("   python verify_source_motions.py")
    print("\nY finalmente:")
    print("   python trajectory_hub/interface/interactive_controller.py")