# === fix_bridge_to_use_simple_client.py ===
# 🔧 Fix: Hacer que el bridge use el mismo método que funciona
# ⚡ Basado en el test simple que SÍ envía a Spat

import os
import re

def fix_bridge_simple():
    bridge_file = "trajectory_hub/core/spat_osc_bridge.py"
    
    with open(bridge_file, 'r') as f:
        content = f.read()
    
    print("🔧 ACTUALIZANDO BRIDGE PARA USAR MÉTODO SIMPLE\n")
    
    # 1. Asegurar que __init__ crea el client correcto
    init_pattern = r'def __init__\(self,[^)]*\):(.*?)(?=\n    def|\Z)'
    
    def fix_init(match):
        original = match.group(0)
        if 'SimpleUDPClient' not in original:
            # Añadir creación del client
            return original.rstrip() + '''
        
        # Crear cliente UDP simple para cada target
        from pythonosc import udp_client
        if self.targets:
            # Usar el primer target como principal
            target = self.targets[0]
            self.client = udp_client.SimpleUDPClient(target.host, target.port)
            print(f"✅ Cliente OSC creado: {target.host}:{target.port}")
'''
        return original
    
    content = re.sub(init_pattern, fix_init, content, flags=re.DOTALL)
    
    # 2. Simplificar create_group
    pattern = r'def create_group\([^)]*\):[^}]+?(?=\n    def|\nclass|\Z)'
    
    new_create_group = '''def create_group(self, group_id: str, group_name: str):
        """Crear grupo en Spat - MÉTODO SIMPLE."""
        try:
            group_name = str(group_name)
            
            if hasattr(self, 'client') and self.client:
                # Mismo método que funciona en test_osc_simple
                self.client.send_message("/group/new", [group_name])
                print(f"✅ Grupo '{group_name}' creado via OSC")
            else:
                print("❌ No hay cliente OSC")
                
        except Exception as e:
            print(f"❌ Error creando grupo: {e}")'''
    
    content = re.sub(pattern, new_create_group, content, flags=re.DOTALL)
    
    # 3. Simplificar add_source_to_group
    pattern2 = r'def add_source_to_group\([^)]*\):[^}]+?(?=\n    def|\nclass|\Z)'
    
    new_add_source = '''def add_source_to_group(self, source_id: int, group_name: str):
        """Añadir fuente a grupo - MÉTODO SIMPLE."""
        try:
            source_id = int(source_id)
            group_name = str(group_name)
            
            if hasattr(self, 'client') and self.client:
                # Mismo método que funciona
                self.client.send_message(f"/source/{source_id}/group", [group_name])
                print(f"✅ Fuente {source_id} → grupo '{group_name}'")
            else:
                print("❌ No hay cliente OSC")
                
        except Exception as e:
            print(f"❌ Error: {e}")'''
    
    content = re.sub(pattern2, new_add_source, content, flags=re.DOTALL)
    
    # Guardar
    with open(bridge_file, 'w') as f:
        f.write(content)
    
    print("✅ Bridge actualizado para usar SimpleUDPClient")
    
    # Test con el engine completo
    with open("test_engine_with_osc.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# NO deshabilitar OSC
if 'DISABLE_OSC' in os.environ:
    del os.environ['DISABLE_OSC']

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🧪 TEST ENGINE CON OSC\\n")

# Crear engine (esto debe crear grupos en Spat)
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

print("\\nCreando macro con 3 fuentes...")
macro_id = engine.create_macro("demo", source_count=3, formation="triangle")

print("\\nAplicando concentración...")
engine.set_macro_concentration(macro_id, 0.5)

print("\\n🔄 Ejecutando algunos frames...")
for _ in range(5):
    engine.step()

print("\\n✅ VERIFICA EN SPAT:")
print("   1. OSC Monitor debe mostrar /group/new")
print("   2. El grupo 'macro_0_demo' debe existir")
print("   3. Las fuentes 0,1,2 deben estar en el grupo")
print("   4. Las posiciones deben actualizarse")
''')

if __name__ == "__main__":
    fix_bridge_simple()