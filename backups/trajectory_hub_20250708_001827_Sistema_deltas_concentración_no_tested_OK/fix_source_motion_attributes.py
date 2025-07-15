#!/usr/bin/env python3
"""
🔧 Fix: Añade atributos faltantes a SourceMotion
⚡ Error: SourceMotion no tiene active_components
🎯 Solución: Verificar y añadir estructura correcta
"""

def fix_source_motion():
    """Arregla SourceMotion para que tenga la estructura correcta"""
    print("🔧 Arreglando SourceMotion...\n")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar la clase SourceMotion
    import re
    source_motion_match = re.search(
        r'(class SourceMotion.*?)((?:\n(?!class).*)*)',
        content,
        re.DOTALL
    )
    
    if source_motion_match:
        class_content = source_motion_match.group(0)
        
        # Verificar si tiene __init__
        if '__init__' not in class_content:
            print("❌ SourceMotion no tiene __init__")
            # Añadir __init__ básico
            init_code = '''
    def __init__(self, source_id: int):
        self.source_id = source_id
        self.state = MotionState()
        self.active_components = []  # Lista de componentes activos
        
    def add_component(self, component):
        """Añade un componente de movimiento"""
        if component not in self.active_components:
            self.active_components.append(component)
'''
            # Insertar después de la definición de clase
            class_def_end = class_content.find(':')
            new_class = class_content[:class_def_end+1] + init_code + class_content[class_def_end+1:]
            content = content.replace(class_content, new_class)
            
        else:
            # Verificar si tiene active_components
            if 'self.active_components' not in class_content:
                print("⚠️ SourceMotion tiene __init__ pero no active_components")
                
                # Buscar __init__ y añadir active_components
                init_pattern = r'(def __init__\(.*?\):.*?)((?:\n\s{8}.*)*?)(\n\s{4}def|\n\s{0,4}\n|$)'
                
                def add_active_components(match):
                    init_body = match.group(2)
                    if 'self.active_components' not in init_body:
                        new_line = '\n        self.active_components = []  # Lista de componentes activos'
                        return match.group(1) + init_body + new_line + match.group(3)
                    return match.group(0)
                
                class_content_new = re.sub(init_pattern, add_active_components, class_content, flags=re.DOTALL)
                content = content.replace(class_content, class_content_new)
        
        # Verificar si tiene add_component
        if 'def add_component' not in class_content:
            print("⚠️ SourceMotion no tiene add_component")
            # Añadir al final de la clase
            add_component_code = '''
    def add_component(self, component):
        """Añade un componente de movimiento"""
        if not hasattr(self, 'active_components'):
            self.active_components = []
        if component not in self.active_components:
            self.active_components.append(component)
'''
            # Buscar el final de la clase
            next_class = content.find('\nclass', content.find('class SourceMotion') + 1)
            if next_class == -1:
                next_class = content.find('\n@dataclass', content.find('class SourceMotion') + 1)
            
            if next_class != -1:
                content = content[:next_class] + add_component_code + content[next_class:]
            else:
                content += add_component_code
    
    # Guardar cambios
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print("✅ SourceMotion actualizado")

def verify_fix():
    """Verifica que el fix funcionó"""
    print("\n🧪 Verificando...")
    
    try:
        from trajectory_hub.core.motion_components import SourceMotion
        
        # Crear instancia de prueba
        sm = SourceMotion(0)
        
        # Verificar atributos
        if hasattr(sm, 'active_components'):
            print("✅ SourceMotion tiene active_components")
        else:
            print("❌ SourceMotion NO tiene active_components")
            
        if hasattr(sm, 'add_component'):
            print("✅ SourceMotion tiene add_component")
        else:
            print("❌ SourceMotion NO tiene add_component")
            
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_debug_script():
    """Crea script para debug detallado"""
    debug_code = '''#!/usr/bin/env python3
"""Debug detallado del sistema"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core.motion_components import SourceMotion, ConcentrationComponent

print("🔍 DEBUG DE SOURCEMOTION\\n")

# Crear SourceMotion
sm = SourceMotion(0)

print(f"Atributos de SourceMotion:")
for attr in dir(sm):
    if not attr.startswith('_'):
        print(f"  - {attr}")

print(f"\\nactive_components: {getattr(sm, 'active_components', 'NO EXISTE')}")

# Test add_component
if hasattr(sm, 'add_component'):
    cc = ConcentrationComponent()
    sm.add_component(cc)
    print(f"\\nDespués de add_component:")
    print(f"  active_components: {sm.active_components}")
'''
    
    with open("debug_source_motion.py", 'w') as f:
        f.write(debug_code)
    
    print("\n✅ Script de debug creado: debug_source_motion.py")

if __name__ == "__main__":
    print("🔧 FIX DE SOURCEMOTION ATTRIBUTES")
    print("=" * 60)
    
    fix_source_motion()
    
    if verify_fix():
        create_debug_script()
        print("\n✅ FIX COMPLETADO")
        print("\n📋 Ejecuta:")
        print("1. python debug_source_motion.py  # Para verificar")
        print("2. python test_delta_working.py   # Para test completo")
    else:
        print("\n❌ El fix necesita revisión manual")