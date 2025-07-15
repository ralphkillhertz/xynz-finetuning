# === fix_create_source_complete.py ===
# 🔧 Fix: Elimina TODOS los accesos problemáticos a components
# ⚡ Impacto: CRÍTICO - Permite crear fuentes sin errores

import os
import re
from datetime import datetime

def fix_create_source():
    """Arregla create_source eliminando todos los accesos a components"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Buscar el método create_source completo
    pattern = r'(def create_source\(self.*?\n)(.*?)(\n\s{0,4}def|\n\s{0,4}async def|\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ No se encuentra create_source")
        return False
    
    method_content = match.group(2)
    original_method = method_content
    
    # Eliminar TODOS los accesos a motion.components
    # Patrón para encontrar líneas con motion.components
    lines = method_content.split('\n')
    new_lines = []
    
    for line in lines:
        if 'motion.components[' in line:
            # Comentar la línea problemática
            indent = len(line) - len(line.lstrip())
            commented = ' ' * indent + '# ' + line.strip() + ' # DESHABILITADO - components no existe'
            new_lines.append(commented)
            print(f"  ✅ Comentada línea: {line.strip()}")
        else:
            new_lines.append(line)
    
    new_method = '\n'.join(new_lines)
    
    # Si no hubo cambios, buscar otro patrón
    if new_method == original_method:
        print("⚠️ No se encontraron accesos directos, buscando otros patrones...")
        
        # Buscar if 'key' in motion.components
        pattern2 = r"if\s+['\"].*?['\"]\s+in\s+motion\.components.*?:.*?(?:\n\s+.*?)*"
        new_method = re.sub(pattern2, 
                           lambda m: '# ' + m.group(0).replace('\n', '\n# '), 
                           new_method)
    
    # Reemplazar en el contenido
    new_content = content[:match.start(2)] + new_method + content[match.end(2):]
    
    # Escribir archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ create_source actualizado")
    
    # Verificar sintaxis
    try:
        compile(new_content, engine_path, 'exec')
        print("✅ Sintaxis verificada")
        return True
    except Exception as e:
        print(f"❌ Error de sintaxis: {e}")
        # Restaurar backup
        with open(backup_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print("⚠️ Backup restaurado")
        return False

def add_macro_class():
    """Añade la clase Macro si no existe"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'class Macro' in content:
        print("✅ Clase Macro ya existe")
        return True
    
    # Añadir clase Macro simple al final del archivo
    macro_class = '''

class Macro:
    """Grupo de fuentes con comportamiento colectivo"""
    
    def __init__(self, name: str, source_ids: List[int]):
        self.name = name
        self.source_ids = source_ids
        self.formation = "circle"
        self.behavior = "flock"
        self.trajectory_type = None
        self.trajectory_params = {}
        self.active = True
        self.center = np.zeros(3)
        self.created_at = time.time()
'''
    
    # Añadir imports necesarios si no están
    if 'from typing import List' not in content:
        # Buscar otros imports from typing
        if 'from typing import' in content:
            content = content.replace('from typing import', 'from typing import List,', 1)
        else:
            # Añadir al principio después de otros imports
            import_pos = content.rfind('import')
            if import_pos > -1:
                import_end = content.find('\n', import_pos)
                content = content[:import_end] + '\nfrom typing import List' + content[import_end:]
    
    # Añadir la clase
    content += macro_class
    
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Clase Macro añadida")
    return True

if __name__ == "__main__":
    print("🔧 FIX COMPLETO DE CREATE_SOURCE")
    print("="*60)
    
    # Fix 1: Arreglar create_source
    success1 = fix_create_source()
    
    # Fix 2: Añadir Macro si no existe
    success2 = add_macro_class()
    
    if success1 and success2:
        print("\n✅ Todos los fixes aplicados")
        print("\n📋 Intenta de nuevo:")
        print("$ python test_delta_concentration_final.py")
        print("\nSi falla, prueba el test mínimo:")
        print("$ python test_delta_minimal.py")
    else:
        print("\n❌ Algunos fixes fallaron")