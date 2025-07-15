
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
    print("\n1️⃣ Verificando add_target...")
    
    # Buscar definición
    add_target_match = re.search(r'def add_target\(self, source_id, x, y\):', content)
    
    if add_target_match:
        print("❌ add_target solo acepta (x, y)")
        print("✅ Actualizando para aceptar (x, y, z)...")
        
        # Cambiar firma
        old_sig = 'def add_target(self, source_id, x, y):'
        new_sig = 'def add_target(self, source_id, x, y, z=0):'
        content = content.replace(old_sig, new_sig)
        
        # Actualizar el cuerpo para usar z
        # Buscar dónde se crea el target
        target_creation = re.search(r'self\.targets\[source_id\] = .*', content)
        if target_creation:
            old_line = target_creation.group(0)
            if 'TrajectoryTarget' in old_line:
                # Actualizar para incluir z
                new_line = old_line.replace('x, y)', 'x, y, z)')
                content = content.replace(old_line, new_line)
    
    # 2. Actualizar llamadas a add_target
    print("\n2️⃣ Actualizando llamadas a add_target...")
    
    # En create_macro
    create_macro_pattern = r'self\.add_target\([^,]+, position\[0\], position\[1\]\)'
    new_call = 'self.add_target(source_id, position[0], position[1], position[2] if len(position) > 2 else 0)'
    
    content = re.sub(create_macro_pattern, new_call, content)
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("\n✅ Coordenada Z habilitada")
    
    # Verificar TrajectoryTarget
    print("\n3️⃣ Verificando TrajectoryTarget...")
    
    # Buscar la clase
    if 'class TrajectoryTarget' in content:
        print("✅ TrajectoryTarget encontrado")
        
        # Ver si acepta z
        init_match = re.search(r'class TrajectoryTarget.*?def __init__\(.*?\):', content, re.DOTALL)
        if init_match and ', z' not in init_match.group(0):
            print("⚠️ TrajectoryTarget podría necesitar actualización para z")

if __name__ == "__main__":
    fix_z_coordinate()
    print("\n🚀 Prueba ahora creando un macro con sphere")
