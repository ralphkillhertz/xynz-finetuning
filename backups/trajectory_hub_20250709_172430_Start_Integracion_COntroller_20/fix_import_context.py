import os
from datetime import datetime
import shutil

def fix_import_context():
    """Arreglar el import viendo el contexto completo"""
    print("🔧 FIX DE CONTEXTO DE IMPORT")
    print("="*60)
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Backup
    backup = f"{engine_file}.backup_context_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(engine_file, backup)
    
    # Leer archivo
    with open(engine_file, 'r') as f:
        lines = f.readlines()
    
    # Mostrar contexto alrededor de línea 21
    print("\n📄 CONTEXTO ALREDEDOR DE LÍNEA 21:")
    for i in range(15, min(30, len(lines))):
        if i < len(lines):
            marker = ">>>" if i == 20 else "   "
            print(f"{marker} L{i+1}: {lines[i].rstrip()}")
    
    # Buscar el problema
    print("\n🔍 Analizando problema...")
    
    # El problema es que el import se insertó dentro de otro statement
    # Necesitamos encontrar dónde están los imports y ponerlo ahí
    
    import_section_start = None
    import_section_end = None
    
    for i, line in enumerate(lines):
        if i < 50:  # Solo en las primeras 50 líneas
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                if import_section_start is None:
                    import_section_start = i
                import_section_end = i
    
    print(f"\n✅ Sección de imports: líneas {import_section_start+1} a {import_section_end+1}")
    
    # Eliminar el import mal colocado (línea 21)
    if 20 < len(lines) and 'FormationManager' in lines[20]:
        print("\n🗑️ Eliminando import mal colocado en línea 21")
        lines.pop(20)
    
    # Verificar si ya existe el import en algún lugar
    formation_import_exists = False
    for i, line in enumerate(lines):
        if 'from trajectory_hub.control.managers.formation_manager import FormationManager' in line:
            formation_import_exists = True
            print(f"\n✅ Import ya existe en línea {i+1}")
            break
    
    # Si no existe, añadirlo después de la sección de imports
    if not formation_import_exists and import_section_end is not None:
        print(f"\n✅ Añadiendo import después de línea {import_section_end+1}")
        lines.insert(import_section_end + 1, 'from trajectory_hub.control.managers.formation_manager import FormationManager\n')
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo corregido")

def restore_working_version():
    """Restaurar una versión que funcione definitivamente"""
    print("\n🔄 RESTAURACIÓN A VERSIÓN FUNCIONAL")
    print("="*60)
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Buscar el backup que funcionó antes
    working_backup = "trajectory_hub/core/enhanced_trajectory_engine.py.backup_macro_fix_20250708_093056"
    
    if os.path.exists(working_backup):
        print(f"✅ Restaurando desde: {working_backup}")
        shutil.copy(working_backup, engine_file)
        
        # NO añadir el import de FormationManager todavía
        # Primero asegurémonos de que funciona
        
        print("\n🧪 Verificando que funciona...")
        try:
            # Cambiar al directorio correcto
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            import trajectory_hub
            print("✅ Import funciona!")
            
            # Ahora sí, añadir sphere de forma diferente
            add_sphere_without_formation_manager()
            
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ No se encuentra el backup funcional")

def add_sphere_without_formation_manager():
    """Añadir sphere sin usar FormationManager (temporal)"""
    print("\n🔧 AÑADIENDO SPHERE SIN FORMATION MANAGER")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar dónde están los casos de formation
    import re
    
    # Buscar el último elif formation
    formation_cases = list(re.finditer(r'elif formation == "[^"]+":', content))
    
    if formation_cases:
        last_case = formation_cases[-1]
        
        # Buscar el final de ese caso
        lines_after = content[last_case.end():].split('\n')
        indent = len(last_case.group(0)) - len(last_case.group(0).lstrip())
        
        # Encontrar dónde termina
        end_offset = 0
        for i, line in enumerate(lines_after[1:], 1):
            if line.strip() and len(line) - len(line.lstrip()) <= indent:
                end_offset = sum(len(l) + 1 for l in lines_after[:i])
                break
        
        insert_pos = last_case.end() + end_offset
        
        # Código sphere 3D sin FormationManager
        sphere_code = f'''
        elif formation == "sphere":
            # Sphere 3D temporal sin FormationManager
            import numpy as np
            positions = []
            n = self.config['n_sources']
            
            # Distribución uniforme en esfera
            golden_angle = np.pi * (3.0 - np.sqrt(5.0))
            
            for i in range(n):
                y = 1 - (i / float(n - 1)) * 2 if n > 1 else 0
                radius_at_y = np.sqrt(1 - y * y)
                theta = golden_angle * i
                
                x = np.cos(theta) * radius_at_y * 2.0  # radio 2
                z = np.sin(theta) * radius_at_y * 2.0
                y_scaled = y * 2.0
                
                positions.append((x, y_scaled, z))
            
            print(f"🌐 Sphere 3D: {{n}} posiciones calculadas")
'''
        
        content = content[:insert_pos] + sphere_code + content[insert_pos:]
        
        # Guardar
        with open(engine_file, 'w') as f:
            f.write(content)
        
        print("✅ Sphere añadido sin FormationManager")

if __name__ == "__main__":
    # Primero intentar arreglar el contexto
    fix_import_context()
    
    # Verificar si funciona
    try:
        import trajectory_hub
        print("\n✅ Sistema funcionando!")
    except:
        print("\n❌ Sigue sin funcionar, restaurando versión funcional...")
        restore_working_version()
    
    print("\n🚀 Intenta ejecutar:")
    print("cd trajectory_hub")
    print("python -m trajectory_hub.interface.interactive_controller")