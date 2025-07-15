# === fix_osc_format_correct.py ===
# 🔧 Fix: Formato OSC correcto para Spat
# ⚡ Solo enviar nombre, no ID

import os
import re

def fix_osc_format():
    bridge_file = "trajectory_hub/core/spat_osc_bridge.py"
    
    with open(bridge_file, 'r') as f:
        content = f.read()
    
    print("🔧 ARREGLANDO FORMATO OSC\n")
    
    # 1. Arreglar create_group - NO enviar el ID
    pattern = r'def create_group\([^)]*\):[^}]+?(?=\n    def|\nclass|\Z)'
    
    new_create_group = '''def create_group(self, group_id: str, group_name: str):
        """Crear un grupo/macro en Spat - SOLO envía el nombre."""
        try:
            # Solo necesitamos el nombre para Spat
            group_name = str(group_name)
            
            print(f"📡 Creando grupo '{group_name}' (id interno: {group_id})")
            
            for target in self.targets:
                # IMPORTANTE: Solo enviar el nombre, NO el ID
                msg = OSCMessage("/group/new", [group_name])
                target.send(msg)
                
            print(f"   ✅ /group/new ['{group_name}'] enviado")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")'''
    
    content = re.sub(pattern, new_create_group, content, flags=re.DOTALL)
    
    # 2. Arreglar add_source_to_group
    pattern2 = r'def add_source_to_group\([^)]*\):[^}]+?(?=\n    def|\nclass|\Z)'
    
    new_add_source = '''def add_source_to_group(self, source_id: int, group_name: str):
        """Añadir fuente a grupo en Spat."""
        try:
            source_id = int(source_id)
            group_name = str(group_name)
            
            print(f"📡 Añadiendo fuente {source_id} a '{group_name}'")
            
            for target in self.targets:
                msg = OSCMessage(f"/source/{source_id}/group", [group_name])
                target.send(msg)
                
            print(f"   ✅ /source/{source_id}/group ['{group_name}'] enviado")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")'''
    
    content = re.sub(pattern2, new_add_source, content, flags=re.DOTALL)
    
    # 3. Verificar imports necesarios
    if 'from pythonosc.osc_message import OSCMessage' not in content:
        # Añadir import al principio
        import_line = "from pythonosc.osc_message import OSCMessage\n"
        content = content.replace("import numpy as np", f"import numpy as np\n{import_line}")
    
    # Guardar
    with open(bridge_file, 'w') as f:
        f.write(content)
    
    print("✅ Formato OSC corregido")
    print("   - Solo envía nombre del grupo, no ID")
    print("   - Usa OSCMessage directamente")
    
    # Test actualizado
    with open("test_osc_correct_format.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget

print("🧪 TEST OSC FORMATO CORRECTO\\n")

# Crear bridge
target = OSCTarget("127.0.0.1", 9000)
bridge = SpatOSCBridge(targets=[target], fps=60)

print("1. Creando grupo 'MiGrupo'...")
bridge.create_group("interno_01", "MiGrupo")

print("\\n2. Añadiendo fuentes 1,2,3 al grupo...")
for i in range(1, 4):
    bridge.add_source_to_group(i, "MiGrupo")

print("\\n✅ VERIFICA EN SPAT OSC MONITOR:")
print("   Deberías ver:")
print("   - /group/new ['MiGrupo']")
print("   - /source/1/group ['MiGrupo']")
print("   - /source/2/group ['MiGrupo']")
print("   - /source/3/group ['MiGrupo']")
''')

if __name__ == "__main__":
    fix_osc_format()