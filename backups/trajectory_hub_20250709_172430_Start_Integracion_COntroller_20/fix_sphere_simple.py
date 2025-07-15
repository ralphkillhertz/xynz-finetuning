import os
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
        print("\n❌ Engine solo pasa X,Y")
        content = content.replace(
            'send_source_position(source_id, pos[0], pos[1])',
            'send_source_position(source_id, pos[0], pos[1], pos[2] if len(pos) > 2 else 0)'
        )
        
        backup = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(engine_file, backup)
        
        with open(engine_file, 'w') as f:
            f.write(content)
        
        print("✅ Engine actualizado para pasar Z")

print("\n✅ FIX COMPLETADO")
print("🚀 Prueba sphere ahora")
