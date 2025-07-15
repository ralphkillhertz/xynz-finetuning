#!/usr/bin/env python3
"""
🔧 FIX: Mensajes OSC para macros en Spat
"""

import os
import sys

print("""
================================================================================
🔧 FIX MENSAJES OSC PARA MACROS
================================================================================
""")

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

# 1. Verificar y arreglar SpatOSCBridge
bridge_file = "trajectory_hub/core/spat_osc_bridge.py"

print("1️⃣ VERIFICANDO SpatOSCBridge...")

if os.path.exists(bridge_file):
    with open(bridge_file, 'r') as f:
        bridge_content = f.read()
    
    # Backup
    import datetime
    backup_name = bridge_file + f".backup_macro_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_name, 'w', encoding='utf-8') as f:
        f.write(bridge_content)
    print(f"   📋 Backup: {backup_name}")
    
    # Verificar si existe create_group
    if 'def create_group' not in bridge_content:
        print("   ⚠️ No existe create_group, añadiendo...")
        
        # Buscar dónde insertar (después de __init__ o send_position)
        import re
        
        # Buscar el final de algún método para insertar después
        insert_point = bridge_content.find('def send_position')
        if insert_point > 0:
            # Buscar el final del método
            next_def = bridge_content.find('\n    def ', insert_point + 1)
            if next_def == -1:
                next_def = bridge_content.find('\nclass', insert_point + 1)
            if next_def == -1:
                next_def = len(bridge_content)
            
            # Insertar nuevo método
            group_methods = '''
    def create_group(self, group_id: str, group_name: str):
        """
        Crear un grupo/macro en Spat.
        
        Parameters
        ----------
        group_id : str
            ID único del grupo
        group_name : str
            Nombre para mostrar en Spat
        """
        try:
            # Formato correcto para Spat: /group/new con nombre como string
            self.send_message("/group/new", [str(group_name)])
            
            # También enviar info del grupo
            self.send_message(f"/group/{group_name}/name", [str(group_name)])
            
            print(f"   ✅ Grupo '{group_name}' creado via OSC")
            
        except Exception as e:
            print(f"   ❌ Error creando grupo: {e}")
    
    def add_source_to_group(self, source_id: int, group_name: str):
        """
        Añadir una fuente a un grupo en Spat.
        
        Parameters
        ----------
        source_id : int
            ID de la fuente
        group_name : str
            Nombre del grupo
        """
        try:
            # Formato para Spat: /source/[id]/group [nombre_grupo]
            self.send_message(f"/source/{source_id}/group", [str(group_name)])
            
        except Exception as e:
            print(f"   ❌ Error añadiendo fuente {source_id} al grupo: {e}")
'''
            
            bridge_content = bridge_content[:next_def] + group_methods + bridge_content[next_def:]
            print("   ✅ Métodos de grupo añadidos")
    else:
        print("   ✅ create_group ya existe")
        
        # Verificar que el formato sea correcto
        if 'can only concatenate str' in bridge_content:
            print("   ⚠️ Arreglando conversión de tipos...")
            bridge_content = bridge_content.replace(
                'self.send_message(address, values)',
                'self.send_message(address, [str(v) if not isinstance(v, (int, float)) else v for v in values] if isinstance(values, list) else values)'
            )
    
    # Guardar cambios
    with open(bridge_file, 'w', encoding='utf-8') as f:
        f.write(bridge_content)
    print("   ✅ SpatOSCBridge actualizado")

else:
    print(f"   ❌ No se encuentra {bridge_file}")

# 2. Actualizar create_macro para enviar OSC
print("\n2️⃣ ACTUALIZANDO create_macro EN ENGINE...")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(engine_file, 'r') as f:
    engine_content = f.read()

# Buscar create_macro
import re
create_macro_match = re.search(r'(def create_macro\(.*?\):.*?)(?=\n    def|\nclass|\Z)', engine_content, re.DOTALL)

if create_macro_match:
    create_macro_content = create_macro_match.group(0)
    
    # Verificar si ya envía OSC
    if 'osc_bridge' not in create_macro_content and 'create_group' not in create_macro_content:
        print("   ⚠️ create_macro no envía OSC, añadiendo...")
        
        # Buscar el return statement
        return_match = re.search(r'(return\s+macro_id)', create_macro_content)
        
        if return_match:
            # Insertar código OSC antes del return
            osc_code = '''
        # Enviar creación del macro a Spat via OSC
        if hasattr(self, 'osc_bridge') and self.osc_bridge:
            try:
                # Crear el grupo en Spat
                self.osc_bridge.create_group(macro_id, name)
                
                # Añadir cada fuente al grupo
                for sid in macro.source_ids:
                    self.osc_bridge.add_source_to_group(sid, name)
                    
            except Exception as e:
                print(f"Error enviando macro a Spat: {e}")
        
        '''
            
            # Insertar antes del return
            new_create_macro = create_macro_content.replace(
                return_match.group(0),
                osc_code + return_match.group(0)
            )
            
            engine_content = engine_content.replace(create_macro_content, new_create_macro)
            print("   ✅ Código OSC añadido a create_macro")
    else:
        print("   ✅ create_macro ya envía OSC")

# Guardar
with open(engine_file, 'w', encoding='utf-8') as f:
    f.write(engine_content)

# 3. Test completo
print("\n3️⃣ TEST COMPLETO DE MACROS CON OSC...")

test_code = '''
import os
import sys
import time
import numpy as np

# No deshabilitar OSC
if 'DISABLE_OSC' in os.environ:
    del os.environ['DISABLE_OSC']

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget
    
    print("\\n🎯 CREANDO ENGINE CON OSC...")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=16, fps=60)
    
    # Crear OSC bridge
    target = OSCTarget("127.0.0.1", 9000)
    bridge = SpatOSCBridge(targets=[target], fps=60)
    engine.osc_bridge = bridge
    
    print(f"   ✅ OSC configurado: {target.host}:{target.port}")
    
    # Crear varios macros
    print("\\n📦 CREANDO MACROS...")
    
    macros = []
    formations = ["Line", "Circle", "Grid"]
    
    for i, formation in enumerate(formations):
        print(f"\\n   Creando macro {formation}...")
        
        # Crear macro
        macro_id = engine.create_macro(
            name=f"Test_{formation}",
            source_count=4,
            formation=formation.lower(),
            spacing=2.0,
            position=np.array([i*5.0, 0.0, 0.0])  # Separar macros
        )
        
        macros.append(macro_id)
        print(f"   ✅ Macro creado: {macro_id}")
        
        # Pequeña pausa para que Spat procese
        time.sleep(0.1)
    
    # Aplicar concentración a un macro
    print("\\n🎯 APLICANDO CONCENTRACIÓN...")
    engine.set_macro_concentration(macros[0], 0.6)
    print(f"   ✅ Concentración aplicada a {macros[0]}")
    
    # Ejecutar simulación
    print("\\n🔄 EJECUTANDO SIMULACIÓN...")
    print("   (Los macros deberían aparecer en Spat)\\n")
    
    for frame in range(60):  # 1 segundo
        engine.step()
        
        if frame == 0:
            print("   Frame 1: Enviando posiciones iniciales...")
        elif frame == 30:
            print("   Frame 30: Concentración en progreso...")
        elif frame == 59:
            print("   Frame 60: Completado")
        
        time.sleep(1.0/60.0)
    
    print("\\n✅ TEST COMPLETADO")
    print("\\n📊 VERIFICA EN SPAT:")
    print("   1. Deberías ver 3 grupos: Test_Line, Test_Circle, Test_Grid")
    print("   2. Cada grupo debería tener 4 fuentes")
    print("   3. Test_Line debería mostrar concentración")
    print("   4. El monitor OSC debería mostrar:")
    print("      - /group/new mensajes")
    print("      - /source/X/group mensajes")
    print("      - /source/X/xyz mensajes continuos")
    
except Exception as e:
    print(f"\\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
'''

exec(test_code)

print("""

================================================================================
📋 RESUMEN Y SIGUIENTES PASOS
================================================================================

Si los macros AÚN no aparecen en Spat:

1. VERIFICA EL FORMATO OSC EN SPAT:
   - Algunos Spat esperan: /source/group/new [nombre]
   - Otros esperan: /group/new [nombre]
   - Revisa la documentación de tu versión

2. USA EL MONITOR OSC:
   - View > OSC Monitor en Spat
   - Verifica qué mensajes llegan
   - Busca errores en el formato

3. PRUEBA MANUAL:
   from pythonosc import udp_client
   client = udp_client.SimpleUDPClient('127.0.0.1', 9000)
   client.send_message('/group/new', ['TestGroup'])
   client.send_message('/source/1/group', ['TestGroup'])

4. USA EL CONTROLADOR INTERACTIVO:
   python trajectory_hub/interface/interactive_controller.py
   
   Debería crear los macros automáticamente.

================================================================================
""")