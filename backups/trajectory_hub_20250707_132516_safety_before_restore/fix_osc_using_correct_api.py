# === fix_osc_using_correct_api.py ===
# 🔧 Fix: Usar la API correcta de pythonosc
# ⚡ Sin imports incorrectos

import os
import re

def fix_osc_api():
    bridge_file = "trajectory_hub/core/spat_osc_bridge.py"
    
    with open(bridge_file, 'r') as f:
        content = f.read()
    
    print("🔧 ARREGLANDO API OSC\n")
    
    # 1. Quitar import incorrecto
    content = content.replace("from pythonosc.osc_message import OSCMessage\n", "")
    
    # 2. Arreglar create_group con API correcta
    pattern = r'def create_group\([^)]*\):[^}]+?(?=\n    def|\nclass|\Z)'
    
    new_create_group = '''def create_group(self, group_id: str, group_name: str):
        """Crear un grupo/macro en Spat."""
        try:
            group_name = str(group_name)
            
            print(f"📡 Creando grupo '{group_name}'")
            
            # Usar el método send() de OSCTarget directamente
            for target in self.targets:
                if hasattr(target, 'send'):
                    # Construir mensaje manualmente
                    from pythonosc import osc_message_builder
                    msg = osc_message_builder.OscMessageBuilder(address="/group/new")
                    msg.add_arg(group_name)
                    msg = msg.build()
                    target.client.send(msg)
                else:
                    # Método alternativo
                    if self.client:
                        self.client.send_message("/group/new", [group_name])
                
            print(f"   ✅ Grupo '{group_name}' creado")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")'''
    
    content = re.sub(pattern, new_create_group, content, flags=re.DOTALL)
    
    # 3. Arreglar add_source_to_group
    pattern2 = r'def add_source_to_group\([^)]*\):[^}]+?(?=\n    def|\nclass|\Z)'
    
    new_add_source = '''def add_source_to_group(self, source_id: int, group_name: str):
        """Añadir fuente a grupo en Spat."""
        try:
            source_id = int(source_id)
            group_name = str(group_name)
            
            print(f"📡 Fuente {source_id} → '{group_name}'")
            
            for target in self.targets:
                if hasattr(target, 'client') and target.client:
                    from pythonosc import osc_message_builder
                    msg = osc_message_builder.OscMessageBuilder(
                        address=f"/source/{source_id}/group"
                    )
                    msg.add_arg(group_name)
                    msg = msg.build()
                    target.client.send(msg)
                elif self.client:
                    self.client.send_message(
                        f"/source/{source_id}/group", 
                        [group_name]
                    )
                
            print(f"   ✅ Fuente {source_id} añadida")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")'''
    
    content = re.sub(pattern2, new_add_source, content, flags=re.DOTALL)
    
    # Guardar
    with open(bridge_file, 'w') as f:
        f.write(content)
    
    print("✅ API OSC corregida")
    
    # Test simple sin engine
    with open("test_osc_simple.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
from pythonosc import udp_client
from pythonosc import osc_message_builder

print("🧪 TEST OSC SIMPLE Y DIRECTO\\n")

# Cliente OSC directo
client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

print("1. Enviando /group/new...")
client.send_message("/group/new", ["TestGroup"])
print("   ✅ Enviado")

print("\\n2. Enviando fuentes al grupo...")
for i in range(1, 4):
    client.send_message(f"/source/{i}/group", ["TestGroup"])
    print(f"   ✅ Fuente {i} → TestGroup")

print("\\n✅ VERIFICA EN SPAT OSC MONITOR")
print("   Si ves los mensajes, el problema está en el bridge")
print("   Si NO ves nada, verifica:")
print("   - Puerto 9000 correcto")
print("   - Spat está recibiendo OSC")
''')

if __name__ == "__main__":
    fix_osc_api()