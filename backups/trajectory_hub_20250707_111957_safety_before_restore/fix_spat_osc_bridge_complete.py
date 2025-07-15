#!/usr/bin/env python3
"""
🔧 FIX COMPLETO: SpatOSCBridge para macros
"""

import os

print("""
================================================================================
🔧 FIX COMPLETO SPATOSCBRIDGE
================================================================================
""")

# Buscar el archivo SpatOSCBridge
bridge_file = "trajectory_hub/core/spat_osc_bridge.py"

print("📋 VERIFICANDO spat_osc_bridge.py...")

if not os.path.exists(bridge_file):
    print(f"❌ No se encuentra {bridge_file}")
    exit(1)

# Leer el archivo actual
with open(bridge_file, 'r') as f:
    lines = f.readlines()

# Backup
import datetime
backup_name = bridge_file + f".backup_complete_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_name, 'w') as f:
    f.writelines(lines)
print(f"✅ Backup: {backup_name}")

# Buscar dónde está create_group
create_group_line = -1
for i, line in enumerate(lines):
    if 'def create_group' in line:
        create_group_line = i
        print(f"✅ create_group encontrado en línea {i+1}")
        break

# Si existe create_group, verificar si está bien implementado
if create_group_line >= 0:
    # Buscar el final del método
    indent = len(lines[create_group_line]) - len(lines[create_group_line].lstrip())
    end_line = create_group_line + 1
    
    for i in range(create_group_line + 1, len(lines)):
        if lines[i].strip() and (len(lines[i]) - len(lines[i].lstrip())) <= indent:
            end_line = i
            break
    
    # Reemplazar create_group con versión corregida
    print("🔧 ACTUALIZANDO create_group...")
    
    new_create_group = f'''    def create_group(self, group_id: str, group_name: str):
        """
        Crear un grupo/macro en Spat.
        """
        try:
            # Convertir valores a tipos correctos
            group_name_str = str(group_name)
            
            # Enviar mensaje de creación de grupo
            for target in self.targets:
                self.client.send_message("/group/new", [group_name_str], target.host, target.port)
            
            print(f"   ✅ Grupo '{group_name_str}' creado via OSC")
            
        except Exception as e:
            print(f"   ❌ Error creando grupo: {e}")
    
'''
    
    # Eliminar método antiguo
    del lines[create_group_line:end_line]
    
    # Insertar nuevo método
    lines.insert(create_group_line, new_create_group)

# Buscar si existe add_source_to_group
add_source_line = -1
for i, line in enumerate(lines):
    if 'def add_source_to_group' in line:
        add_source_line = i
        break

if add_source_line < 0:
    print("🔧 AÑADIENDO add_source_to_group...")
    
    # Buscar dónde insertar (después de create_group)
    insert_line = create_group_line + 15  # Aproximadamente después de create_group
    
    add_source_method = '''    def add_source_to_group(self, source_id: int, group_name: str):
        """
        Añadir una fuente a un grupo en Spat.
        """
        try:
            # Convertir a tipos correctos
            source_id_int = int(source_id)
            group_name_str = str(group_name)
            
            # Enviar mensaje para añadir fuente al grupo
            for target in self.targets:
                self.client.send_message(
                    f"/source/{source_id_int}/group", 
                    [group_name_str], 
                    target.host, 
                    target.port
                )
            
        except Exception as e:
            print(f"   ❌ Error añadiendo fuente {source_id} al grupo: {e}")
    
'''
    
    lines.insert(insert_line, add_source_method)
    print("✅ add_source_to_group añadido")

# Guardar archivo actualizado
with open(bridge_file, 'w') as f:
    f.writelines(lines)

print("\n✅ spat_osc_bridge.py actualizado completamente")

# Test de verificación
print("\n" + "="*80)
print("🧪 TEST DE VERIFICACIÓN")
print("="*80 + "\n")

test_code = '''
import sys
import os

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

try:
    from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget
    
    print("✅ Importación exitosa")
    
    # Crear bridge de prueba
    target = OSCTarget("127.0.0.1", 9000)
    bridge = SpatOSCBridge(targets=[target], fps=60)
    
    # Verificar métodos
    print("\\nMétodos disponibles:")
    if hasattr(bridge, 'create_group'):
        print("  ✅ create_group existe")
    else:
        print("  ❌ create_group NO existe")
        
    if hasattr(bridge, 'add_source_to_group'):
        print("  ✅ add_source_to_group existe")
    else:
        print("  ❌ add_source_to_group NO existe")
    
    # Test de creación de grupo
    print("\\n🧪 Test de creación de grupo...")
    bridge.create_group("test_id", "TestGroup")
    
    print("\\n🧪 Test de añadir fuente a grupo...")
    bridge.add_source_to_group(1, "TestGroup")
    
    print("\\n✅ Tests completados sin errores")
    
except Exception as e:
    print(f"\\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''

exec(test_code)

print("""

================================================================================
📋 SIGUIENTE PASO
================================================================================

Ejecuta el controlador interactivo:

python trajectory_hub/interface/interactive_controller.py

Los macros deberían crearse correctamente en Spat ahora.

Si aún hay problemas, verifica en el OSC Monitor de Spat:
- /group/new ["NombreGrupo"]
- /source/X/group ["NombreGrupo"]

================================================================================
""")