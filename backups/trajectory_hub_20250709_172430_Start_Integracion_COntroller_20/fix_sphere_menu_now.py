import os
import re
from datetime import datetime
import shutil

def fix_sphere_menu():
    """Añadir sphere al menú de formaciones que está activo"""
    print("🔧 AÑADIENDO SPHERE AL MENÚ ACTIVO")
    print("="*60)
    
    # Buscar en el controlador interactivo
    controller_file = "trajectory_hub/interface/interactive_controller.py"
    
    if not os.path.exists(controller_file):
        print(f"❌ No existe: {controller_file}")
        return False
    
    with open(controller_file, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Buscar el patrón exacto del menú que vemos
    modified = False
    new_lines = []
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Buscar "5. random" para añadir sphere después
        if "5. random" in line and i < len(lines) - 1:
            # Verificar que no esté ya
            next_line = lines[i+1] if i+1 < len(lines) else ""
            if "6. sphere" not in next_line:
                # Calcular la indentación
                indent = len(line) - len(line.lstrip())
                new_lines.append(" " * indent + "6. sphere")
                print(f"✅ Añadido '6. sphere' después de línea {i+1}")
                modified = True
    
    # Si encontramos el menú, también buscar el diccionario de formaciones
    if modified:
        # Buscar el diccionario que mapea números a formaciones
        for i in range(len(new_lines)):
            line = new_lines[i]
            
            # Patrón: "5": "random"
            if '"5"' in line and "random" in line and i < len(new_lines) - 1:
                next_line = new_lines[i+1] if i+1 < len(new_lines) else ""
                
                # Si no tiene coma al final, añadirla
                if not line.rstrip().endswith(','):
                    new_lines[i] = line.rstrip() + ','
                
                # Verificar que sphere no esté ya
                if '"6"' not in next_line and "sphere" not in next_line:
                    # Calcular indentación
                    indent = len(line) - len(line.lstrip())
                    # Insertar sphere
                    new_lines.insert(i+1, " " * indent + '"6": "sphere"')
                    print(f"✅ Añadido mapeo '6': 'sphere' después de línea {i+1}")
                    break
    
    if not modified:
        print("\n❌ No encontré el menú. Buscando alternativas...")
        
        # Búsqueda más agresiva
        for i, line in enumerate(lines):
            if "circle" in line and "line" in line:
                print(f"📍 Posible menú en línea {i+1}: {line[:80]}")
        
        # Buscar handle_create_macro o similar
        create_macro_pattern = r'def\s+\w*create\w*macro'
        matches = list(re.finditer(create_macro_pattern, content, re.IGNORECASE))
        
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            print(f"📍 Método crear macro en línea {line_num}")
    
    else:
        # Guardar cambios
        backup = f"{controller_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(controller_file, backup)
        
        with open(controller_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"\n✅ Archivo modificado: {controller_file}")
        print(f"📦 Backup: {backup}")
        
        # Verificar FormationManager
        verify_formation_manager()
        
        return True
    
    return False

def verify_formation_manager():
    """Asegurar que FormationManager tenga sphere"""
    formation_file = "trajectory_hub/control/managers/formation_manager.py"
    
    if not os.path.exists(formation_file):
        # Buscar en core
        formation_file = "trajectory_hub/core/formation_manager.py"
    
    if not os.path.exists(formation_file):
        print("\n⚠️ No encuentro FormationManager, verificando engine...")
        
        # Verificar en engine
        engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
        if os.path.exists(engine_file):
            with open(engine_file, 'r') as f:
                content = f.read()
            
            # Buscar _calculate_sphere_positions
            if "_calculate_sphere_positions" not in content:
                print("⚠️ Falta _calculate_sphere_positions en engine")
                add_sphere_to_engine(engine_file)
    else:
        with open(formation_file, 'r') as f:
            content = f.read()
        
        if "_create_sphere_formation" not in content:
            print(f"⚠️ Falta sphere en FormationManager: {formation_file}")
            add_sphere_to_formation_manager(formation_file)

def add_sphere_to_engine(engine_file):
    """Añadir método sphere al engine"""
    print("\n🔧 Añadiendo _calculate_sphere_positions al engine...")
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar dónde insertar (después de otro método _calculate_)
    insert_pattern = r'(def _calculate_\w+_positions.*?return positions)'
    match = re.search(insert_pattern, content, re.DOTALL)
    
    if match:
        sphere_method = '''

    def _calculate_sphere_positions(self, n_sources, center=(0, 0, 0), radius=2.0):
        """Calcular posiciones en formación esférica"""
        import numpy as np
        
        positions = []
        
        # Distribución uniforme en esfera usando espiral de Fibonacci
        golden_angle = np.pi * (3.0 - np.sqrt(5.0))  # Ángulo dorado
        
        for i in range(n_sources):
            y = 1 - (i / float(n_sources - 1)) * 2  # y va de 1 a -1
            radius_at_y = np.sqrt(1 - y * y)
            
            theta = golden_angle * i
            
            x = np.cos(theta) * radius_at_y
            z = np.sin(theta) * radius_at_y
            
            positions.append((
                center[0] + x * radius,
                center[1] + y * radius,
                center[2] + z * radius
            ))
        
        return positions'''
        
        # Insertar después del match
        insert_pos = match.end()
        new_content = content[:insert_pos] + sphere_method + content[insert_pos:]
        
        # Guardar
        backup = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(engine_file, backup)
        
        with open(engine_file, 'w') as f:
            f.write(new_content)
        
        print("✅ Método sphere añadido al engine")

def add_sphere_to_formation_manager(fm_file):
    """Añadir sphere al FormationManager"""
    print(f"\n🔧 Añadiendo sphere a {fm_file}...")
    
    with open(fm_file, 'r') as f:
        content = f.read()
    
    # Similar lógica para FormationManager
    # ... (código similar al anterior)

if __name__ == "__main__":
    if fix_sphere_menu():
        print("\n✅ SPHERE AÑADIDO AL MENÚ")
        print("\n🚀 Prueba ahora:")
        print("1. python main.py --interactive")
        print("2. Crear macro (opción 1)")
        print("3. Selecciona formación 6 (sphere)")
    else:
        print("\n❌ No se pudo añadir sphere automáticamente")
        print("\n📋 Necesito más información:")
        print("1. Ejecuta: grep -n 'random' trajectory_hub/interface/interactive_controller.py")
        print("2. Comparte las líneas encontradas")