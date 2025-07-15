import os
import re

def find_z_loss():
    """Encontrar dónde se pierde la coordenada Z"""
    print("🔍 BUSCANDO DÓNDE SE PIERDE LA COORDENADA Z")
    print("="*60)
    
    # 1. Ver cómo CommandProcessor llama a FormationManager
    print("\n1️⃣ COMMAND PROCESSOR → FORMATION MANAGER")
    
    cp_file = "trajectory_hub/control/processors/command_processor.py"
    
    if os.path.exists(cp_file):
        with open(cp_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar uso de FormationManager
        for i, line in enumerate(lines):
            if 'FormationManager' in line and 'import' not in line:
                print(f"L{i+1}: {line.strip()}")
                
                # Si es instanciación, buscar usos cerca
                if '=' in line and 'FormationManager' in line:
                    var_name = line.split('=')[0].strip()
                    print(f"\nVariable: {var_name}")
                    
                    # Buscar usos de esta variable
                    for j in range(i+1, min(len(lines), i+100)):
                        if var_name in lines[j] and 'calculate_formation' in lines[j]:
                            print(f"L{j+1}: {lines[j].strip()}")
                            
                            # Ver qué hace con el resultado
                            for k in range(j+1, min(len(lines), j+10)):
                                if 'positions' in lines[k] or 'formation' in lines[k]:
                                    print(f"L{k+1}: {lines[k].strip()}")
    
    # 2. Ver cómo se pasan las posiciones al engine
    print("\n\n2️⃣ POSITIONS → ENGINE")
    
    # Buscar en engine cómo recibe positions
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        with open(engine_file, 'r') as f:
            content = f.read()
        
        # Buscar create_macro
        create_match = re.search(r'def create_macro\(.*?\):', content)
        if create_match:
            print(f"\n✅ Encontrado: {create_match.group(0)}")
            
            # Ver los parámetros
            params = create_match.group(0)
            if 'positions' in params:
                print("   ✅ create_macro recibe positions")
            elif 'formation' in params:
                print("   ⚠️ create_macro recibe formation (no positions)")
        
        # Buscar cómo procesa positions/formation
        if 'elif formation == "sphere"' in content:
            print("\n⚠️ ENGINE tiene su propio manejo de sphere!")
            
            # Buscar ese código
            sphere_match = re.search(r'elif formation == "sphere".*?(?=elif|else:|$)', content, re.DOTALL)
            if sphere_match:
                print("\n📍 Código sphere en engine:")
                code = sphere_match.group(0)
                print(code[:300] + "..." if len(code) > 300 else code)
        
        # Buscar add_target
        add_target_match = re.search(r'def add_target\(.*?\):', content)
        if add_target_match:
            print(f"\n✅ add_target: {add_target_match.group(0)}")
            
            # Ver si acepta z
            if ', z' in add_target_match.group(0):
                print("   ✅ add_target acepta Z")
            else:
                print("   ❌ add_target NO acepta Z - ESTE ES EL PROBLEMA!")
    
    # 3. Buscar el flujo real
    print("\n\n3️⃣ FLUJO REAL DE CREACIÓN")
    
    # En CLI interface
    cli_file = "trajectory_hub/control/interfaces/cli_interface.py"
    
    if os.path.exists(cli_file):
        with open(cli_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar dónde se maneja la selección de formation
        for i, line in enumerate(lines):
            if 'formation_idx' in line and 'get_choice' in line:
                print(f"\nCLI L{i+1}: {line.strip()}")
                
                # Ver qué hace después
                for j in range(i+1, min(len(lines), i+20)):
                    if 'formation' in lines[j] and ('=' in lines[j] or 'command' in lines[j]):
                        print(f"CLI L{j+1}: {lines[j].strip()}")
                    
                    if 'execute' in lines[j] or 'handle' in lines[j]:
                        print(f"CLI L{j+1}: {lines[j].strip()}")
                        break

def create_fix_script():
    """Crear script para arreglar el problema"""
    
    fix_content = '''
# === fix_z_coordinate.py ===
import os
import re
from datetime import datetime
import shutil

def fix_z_coordinate():
    """Arreglar para que se use la coordenada Z"""
    print("🔧 ARREGLANDO USO DE COORDENADA Z")
    print("="*60)
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Backup
    backup = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(engine_file, backup)
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # 1. Verificar firma de add_target
    print("\\n1️⃣ Verificando add_target...")
    
    # Buscar definición
    add_target_match = re.search(r'def add_target\\(self, source_id, x, y\\):', content)
    
    if add_target_match:
        print("❌ add_target solo acepta (x, y)")
        print("✅ Actualizando para aceptar (x, y, z)...")
        
        # Cambiar firma
        old_sig = 'def add_target(self, source_id, x, y):'
        new_sig = 'def add_target(self, source_id, x, y, z=0):'
        content = content.replace(old_sig, new_sig)
        
        # Actualizar el cuerpo para usar z
        # Buscar dónde se crea el target
        target_creation = re.search(r'self\\.targets\\[source_id\\] = .*', content)
        if target_creation:
            old_line = target_creation.group(0)
            if 'TrajectoryTarget' in old_line:
                # Actualizar para incluir z
                new_line = old_line.replace('x, y)', 'x, y, z)')
                content = content.replace(old_line, new_line)
    
    # 2. Actualizar llamadas a add_target
    print("\\n2️⃣ Actualizando llamadas a add_target...")
    
    # En create_macro
    create_macro_pattern = r'self\\.add_target\\([^,]+, position\\[0\\], position\\[1\\]\\)'
    new_call = 'self.add_target(source_id, position[0], position[1], position[2] if len(position) > 2 else 0)'
    
    content = re.sub(create_macro_pattern, new_call, content)
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("\\n✅ Coordenada Z habilitada")
    
    # Verificar TrajectoryTarget
    print("\\n3️⃣ Verificando TrajectoryTarget...")
    
    # Buscar la clase
    if 'class TrajectoryTarget' in content:
        print("✅ TrajectoryTarget encontrado")
        
        # Ver si acepta z
        init_match = re.search(r'class TrajectoryTarget.*?def __init__\\(.*?\\):', content, re.DOTALL)
        if init_match and ', z' not in init_match.group(0):
            print("⚠️ TrajectoryTarget podría necesitar actualización para z")

if __name__ == "__main__":
    fix_z_coordinate()
    print("\\n🚀 Prueba ahora creando un macro con sphere")
'''
    
    with open("fix_z_coordinate.py", 'w') as f:
        f.write(fix_content)
    
    print("\n✅ Script creado: fix_z_coordinate.py")

if __name__ == "__main__":
    find_z_loss()
    create_fix_script()
    
    print("\n\n💡 SOLUCIÓN:")
    print("Si add_target no acepta Z, ejecuta:")
    print("python fix_z_coordinate.py")