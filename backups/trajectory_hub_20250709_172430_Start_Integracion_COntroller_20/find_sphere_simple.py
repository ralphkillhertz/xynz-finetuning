import os

def find_sphere_simple():
    """Buscar el problema de sphere de forma simple"""
    print("🔍 BÚSQUEDA SIMPLE DEL PROBLEMA SPHERE")
    print("="*60)
    
    # 1. Ver qué hace el engine con sphere
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        with open(engine_file, 'r') as f:
            lines = f.readlines()
        
        print("\n1️⃣ BUSCANDO EN ENGINE...")
        
        # Buscar líneas con sphere
        sphere_lines = []
        for i, line in enumerate(lines):
            if 'sphere' in line.lower():
                sphere_lines.append((i+1, line.strip()))
        
        if sphere_lines:
            print(f"\n✅ Encontradas {len(sphere_lines)} líneas con 'sphere':")
            for line_num, text in sphere_lines[:10]:
                print(f"   L{line_num}: {text}")
        else:
            print("❌ No se encontró 'sphere' en engine")
            print("→ Engine no maneja sphere específicamente")
    
    # 2. Ver cómo se envían las posiciones
    print("\n\n2️⃣ BUSCANDO ENVÍO DE POSICIONES...")
    
    # Buscar en spat_osc_bridge
    bridge_file = "trajectory_hub/core/spat_osc_bridge.py"
    
    if os.path.exists(bridge_file):
        with open(bridge_file, 'r') as f:
            bridge_lines = f.readlines()
        
        # Buscar send_source_position
        for i, line in enumerate(bridge_lines):
            if 'def send_source_position' in line:
                print(f"\n✅ send_source_position en línea {i+1}:")
                print(f"   {line.strip()}")
                
                # Ver las siguientes 5 líneas
                for j in range(i+1, min(len(bridge_lines), i+6)):
                    if 'send' in bridge_lines[j] or 'xyz' in bridge_lines[j]:
                        print(f"   L{j+1}: {bridge_lines[j].strip()}")
                break

def create_simple_fix():
    """Crear un fix simple y directo"""
    
    print("\n\n🔧 CREANDO FIX SIMPLE")
    
    fix_content = '''import os
from datetime import datetime
import shutil

print("🔧 FIX SIMPLE SPHERE 3D")
print("="*60)

# 1. Asegurar que OSC envíe Z
bridge_file = "trajectory_hub/core/spat_osc_bridge.py"

if os.path.exists(bridge_file):
    backup = f"{bridge_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(bridge_file, backup)
    
    with open(bridge_file, 'r') as f:
        lines = f.readlines()
    
    modified = False
    
    # Buscar y arreglar send_source_position
    for i, line in enumerate(lines):
        if 'def send_source_position' in line:
            # Verificar si acepta z
            if ', z' not in line:
                print("❌ send_source_position no acepta Z")
                # Cambiar la firma
                lines[i] = line.replace(', y):', ', y, z=0):')
                modified = True
                print("✅ Actualizada firma para aceptar Z")
        
        # Buscar el envío
        if '"/source/{source_id}/xyz"' in line and '[x, y]' in line:
            print("❌ Solo envía [x, y]")
            lines[i] = line.replace('[x, y]', '[x, y, z]')
            modified = True
            print("✅ Actualizado para enviar [x, y, z]")
    
    if modified:
        with open(bridge_file, 'w') as f:
            f.writelines(lines)
        print("✅ OSC Bridge actualizado")

# 2. Asegurar que engine pase Z
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

if os.path.exists(engine_file):
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar llamadas a send_source_position con solo 3 params
    if 'send_source_position(source_id, pos[0], pos[1])' in content:
        print("\\n❌ Engine solo pasa X,Y")
        content = content.replace(
            'send_source_position(source_id, pos[0], pos[1])',
            'send_source_position(source_id, pos[0], pos[1], pos[2] if len(pos) > 2 else 0)'
        )
        
        backup = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(engine_file, backup)
        
        with open(engine_file, 'w') as f:
            f.write(content)
        
        print("✅ Engine actualizado para pasar Z")

print("\\n✅ FIX COMPLETADO")
print("🚀 Prueba sphere ahora")
'''
    
    with open("fix_sphere_simple.py", 'w') as f:
        f.write(fix_content)
    
    print("✅ Fix creado: fix_sphere_simple.py")

if __name__ == "__main__":
    find_sphere_simple()
    create_simple_fix()
    
    print("\n\n🚀 EJECUTA:")
    print("python fix_sphere_simple.py")