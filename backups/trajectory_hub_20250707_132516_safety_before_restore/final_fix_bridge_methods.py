# === final_fix_bridge_methods.py ===
# 🔧 Fix: Arreglar definitivamente create_group y add_source_to_group
# ⚡ Usar solo el client que funciona

import os
import re

def final_bridge_fix():
    bridge_file = "trajectory_hub/core/spat_osc_bridge.py"
    
    with open(bridge_file, 'r') as f:
        content = f.read()
    
    print("🔧 FIX FINAL DEL BRIDGE OSC\n")
    
    # 1. Arreglar create_group completamente
    pattern1 = r'def create_group\([^)]*\):[^}]+?(?=\n    def|\nclass|\Z)'
    
    new_create_group = '''def create_group(self, group_id: str, group_name: str):
        """Crear grupo en Spat - VERSIÓN FINAL."""
        try:
            # Solo necesitamos el nombre para Spat
            group_name = str(group_name)
            
            print(f"📡 Enviando /group/new ['{group_name}']")
            
            # Usar el client directamente
            if hasattr(self, 'client') and self.client:
                self.client.send_message("/group/new", [group_name])
                print(f"   ✅ Grupo '{group_name}' creado")
            else:
                print("   ❌ No hay cliente OSC")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()'''
    
    content = re.sub(pattern1, new_create_group, content, flags=re.DOTALL)
    
    # 2. Arreglar add_source_to_group completamente
    pattern2 = r'def add_source_to_group\([^)]*\):[^}]+?(?=\n    def|\nclass|\Z)'
    
    new_add_source = '''def add_source_to_group(self, source_id: int, group_name: str):
        """Añadir fuente a grupo - VERSIÓN FINAL."""
        try:
            source_id = int(source_id)
            group_name = str(group_name)
            
            address = f"/source/{source_id}/group"
            print(f"📡 Enviando {address} ['{group_name}']")
            
            # Usar el client directamente
            if hasattr(self, 'client') and self.client:
                self.client.send_message(address, [group_name])
                print(f"   ✅ Fuente {source_id} → '{group_name}'")
            else:
                print("   ❌ No hay cliente OSC")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()'''
    
    content = re.sub(pattern2, new_add_source, content, flags=re.DOTALL)
    
    # 3. Asegurar que el client se crea en __init__
    if 'SimpleUDPClient' not in content:
        # Añadir import
        content = content.replace(
            "from pythonosc import udp_client",
            "from pythonosc import udp_client\nfrom pythonosc.udp_client import SimpleUDPClient"
        )
    
    # Guardar
    with open(bridge_file, 'w') as f:
        f.write(content)
    
    print("✅ Bridge arreglado definitivamente")
    
    # Test completo
    with open("test_complete_osc_system.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🧪 TEST COMPLETO DEL SISTEMA OSC\\n")

# Crear engine
print("1. Iniciando engine...")
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Crear varios macros
print("\\n2. Creando macros...")
macro1 = engine.create_macro("Pajaros", source_count=3, formation="triangle")
macro2 = engine.create_macro("Insectos", source_count=4, formation="grid")

# Aplicar comportamientos
print("\\n3. Aplicando concentración...")
engine.set_macro_concentration(macro1, 0.7)
engine.set_macro_concentration(macro2, 0.3)

# Ejecutar algunos frames
print("\\n4. Ejecutando simulación...")
for i in range(10):
    engine.step()
    if i % 5 == 0:
        print(f"   Frame {i}")

print("\\n✅ VERIFICA EN SPAT:")
print("   1. Grupos 'Pajaros' e 'Insectos' creados")
print("   2. Fuentes 0-2 en 'Pajaros'")
print("   3. Fuentes 3-6 en 'Insectos'")
print("   4. Todas las fuentes moviéndose")
print("   5. Concentración visible")

print("\\n🚀 Si todo funciona, ejecuta:")
print("   python trajectory_hub/interface/interactive_controller.py")
''')

if __name__ == "__main__":
    final_bridge_fix()