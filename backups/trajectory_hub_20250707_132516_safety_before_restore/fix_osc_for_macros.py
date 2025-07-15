# === fix_osc_for_macros.py ===
# 🔧 Fix: Arreglar comunicación OSC para macros en Spat
# ⚡ Basado en sesión anterior donde quedó pendiente

import os
import datetime

def fix_osc_bridge():
    bridge_file = "trajectory_hub/core/spat_osc_bridge.py"
    
    with open(bridge_file, 'r') as f:
        content = f.read()
    
    # Backup
    backup_name = f"{bridge_file}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_name, 'w') as f:
        f.write(content)
    
    print("🔧 ARREGLANDO OSC PARA MACROS\n")
    
    # 1. Buscar y arreglar create_group
    if 'def create_group' in content:
        print("✅ create_group encontrado, verificando...")
        
        # Reemplazar el método con versión corregida
        import re
        pattern = r'def create_group\([^)]*\):[^}]+?(?=\n    def|\nclass|\Z)'
        
        new_method = '''def create_group(self, group_id: str, group_name: str):
        """Crear un grupo/macro en Spat."""
        try:
            # CRÍTICO: Asegurar tipos correctos
            group_id = str(group_id)
            group_name = str(group_name)
            
            print(f"🔄 Creando grupo OSC: id='{group_id}', name='{group_name}'")
            
            for target in self.targets:
                if hasattr(self, 'client') and self.client:
                    # Formato correcto para Spat
                    self.client.send_message(
                        "/group/new", 
                        [group_name],  # Solo el nombre
                        target.host, 
                        target.port
                    )
                else:
                    # Fallback
                    self.send_message("/group/new", [group_name])
            
            print(f"   ✅ Mensaje /group/new enviado para '{group_name}'")
            
        except Exception as e:
            print(f"   ❌ Error creando grupo: {e}")
            import traceback
            traceback.print_exc()'''
        
        content = re.sub(pattern, new_method, content, flags=re.DOTALL)
    
    # 2. Añadir add_source_to_group si no existe
    if 'def add_source_to_group' not in content:
        print("\n❌ add_source_to_group NO EXISTE, añadiendo...")
        
        # Buscar dónde insertar (después de create_group)
        insert_pos = content.find('def create_group')
        if insert_pos > 0:
            # Buscar el siguiente def
            next_def = content.find('\n    def ', insert_pos + 1)
            if next_def == -1:
                next_def = len(content)
            
            method_to_add = '''
    def add_source_to_group(self, source_id: int, group_name: str):
        """Añadir una fuente a un grupo en Spat."""
        try:
            # CRÍTICO: Asegurar tipos correctos
            source_id = int(source_id)
            group_name = str(group_name)
            
            print(f"🔄 Añadiendo fuente {source_id} al grupo '{group_name}'")
            
            for target in self.targets:
                if hasattr(self, 'client') and self.client:
                    # Formato para Spat
                    self.client.send_message(
                        f"/source/{source_id}/group",
                        [group_name],
                        target.host,
                        target.port
                    )
                else:
                    self.send_message(f"/source/{source_id}/group", [group_name])
            
            print(f"   ✅ Fuente {source_id} añadida a '{group_name}'")
            
        except Exception as e:
            print(f"   ❌ Error añadiendo fuente al grupo: {e}")
            import traceback
            traceback.print_exc()
'''
            
            content = content[:next_def] + method_to_add + content[next_def:]
    
    # 3. Verificar que send_message existe y funciona
    if 'def send_message' not in content:
        print("\n⚠️ send_message no existe, añadiendo...")
        
        # Añadir al final de la clase
        class_end = content.rfind('\nclass')
        if class_end == -1:
            class_end = len(content)
        
        send_method = '''
    def send_message(self, address: str, values: list = None):
        """Enviar mensaje OSC a todos los targets."""
        if values is None:
            values = []
            
        for target in self.targets:
            try:
                if hasattr(self, 'client') and self.client:
                    self.client.send_message(address, values, target.host, target.port)
                else:
                    print(f"⚠️ No hay cliente OSC para enviar a {target.host}:{target.port}")
            except Exception as e:
                print(f"❌ Error enviando {address}: {e}")
'''
        
        content = content[:class_end] + send_method + '\n' + content[class_end:]
    
    # Guardar
    with open(bridge_file, 'w') as f:
        f.write(content)
    
    print("\n✅ OSC Bridge actualizado:")
    print("   - create_group con tipos corregidos")
    print("   - add_source_to_group añadido")
    print("   - Mensajes de debug mejorados")
    
    # Test rápido
    with open("test_osc_macros.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🧪 TEST OSC PARA MACROS\\n")

# Sin DISABLE_OSC para este test
if 'DISABLE_OSC' in os.environ:
    del os.environ['DISABLE_OSC']

# Crear bridge
print("1. Creando OSC Bridge...")
target = OSCTarget("127.0.0.1", 9000)
bridge = SpatOSCBridge(targets=[target], fps=60)

# Verificar métodos
print("\\n2. Verificando métodos:")
print(f"   create_group existe: {hasattr(bridge, 'create_group')}")
print(f"   add_source_to_group existe: {hasattr(bridge, 'add_source_to_group')}")

# Test de creación
print("\\n3. Test de creación de grupo:")
try:
    bridge.create_group("test_id", "TestGroup")
    print("   ✅ create_group ejecutado sin errores")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\\n4. Test de añadir fuente:")
try:
    bridge.add_source_to_group(1, "TestGroup")
    print("   ✅ add_source_to_group ejecutado sin errores")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\\n5. Test con engine completo:")
engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
macro_id = engine.create_macro("test_macro", source_count=3)

print("\\n📡 VERIFICA EN SPAT:")
print("   - View > OSC Monitor")
print("   - Deberías ver mensajes /group/new")
print("   - Y mensajes /source/X/group")
''')

if __name__ == "__main__":
    fix_osc_bridge()