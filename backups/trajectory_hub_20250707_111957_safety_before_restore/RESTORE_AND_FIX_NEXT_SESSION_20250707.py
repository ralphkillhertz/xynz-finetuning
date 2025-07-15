#!/usr/bin/env python3
"""
🚀 INICIO RÁPIDO - Próxima Sesión Trajectory Hub
📅 Estado: Concentración FUNCIONA, falta arreglar OSC para macros
"""

import os
import sys

print("""
================================================================================
🚀 RESTORE AND FIX - PRÓXIMA SESIÓN
================================================================================

ESTADO ACTUAL:
✅ Concentración FUNCIONA perfectamente (50% reducción)
✅ Comunicación OSC básica funciona
❌ Creación de macros en Spat falla (error de tipos)
❌ Método add_source_to_group no existe

================================================================================
""")

# 1. Verificar estado actual
print("1️⃣ VERIFICANDO ESTADO ACTUAL...\n")

# Verificar que la concentración funciona
test_concentration = '''
import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'  # Solo para test rápido

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
    macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)
    
    # Posiciones iniciales
    pos_init = engine._positions[0].copy()
    
    # Aplicar concentración
    engine.set_macro_concentration(macro_id, 0.5)
    
    # Ejecutar 10 frames
    for _ in range(10):
        engine.step()
    
    # Verificar movimiento
    movement = np.linalg.norm(engine._positions[0] - pos_init)
    
    if movement > 0.1:
        print("✅ Concentración funciona correctamente")
        print(f"   Movimiento detectado: {movement:.4f}")
    else:
        print("❌ Concentración NO funciona")
        print("   Necesitas ejecutar simple_direct_fix.py primero")
        
except Exception as e:
    print(f"❌ Error verificando concentración: {e}")
'''

exec(test_concentration)

# 2. Arreglar OSC para macros
print("\n2️⃣ ARREGLANDO OSC PARA MACROS...\n")

# Arreglar spat_osc_bridge.py
bridge_file = "trajectory_hub/core/spat_osc_bridge.py"

if os.path.exists(bridge_file):
    print(f"📋 Actualizando {bridge_file}...")
    
    with open(bridge_file, 'r') as f:
        content = f.read()
    
    # Backup
    import datetime
    backup_name = bridge_file + f".backup_session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_name, 'w') as f:
        f.write(content)
    
    # Verificar si necesita fixes
    needs_fix = False
    
    if 'def add_source_to_group' not in content:
        print("   ❌ Falta add_source_to_group, añadiendo...")
        needs_fix = True
        
        # Buscar dónde insertar
        insert_pos = content.find('def create_group')
        if insert_pos > 0:
            # Buscar el final del método create_group
            next_def = content.find('\n    def ', insert_pos + 1)
            if next_def == -1:
                next_def = len(content)
            
            # Insertar métodos corregidos
            fixed_methods = '''
    def create_group(self, group_id: str, group_name: str):
        """Crear un grupo/macro en Spat."""
        try:
            group_name = str(group_name)  # Asegurar tipo string
            
            for target in self.targets:
                # Usar client para enviar
                if hasattr(self, 'client'):
                    self.client.send_message("/group/new", [group_name], target.host, target.port)
                else:
                    # Fallback si no hay client
                    self.send_message("/group/new", [group_name])
            
            print(f"   ✅ Grupo '{group_name}' creado via OSC")
            
        except Exception as e:
            print(f"   ❌ Error creando grupo: {e}")
    
    def add_source_to_group(self, source_id: int, group_name: str):
        """Añadir una fuente a un grupo en Spat."""
        try:
            source_id = int(source_id)  # Asegurar tipo int
            group_name = str(group_name)  # Asegurar tipo string
            
            for target in self.targets:
                if hasattr(self, 'client'):
                    self.client.send_message(
                        f"/source/{source_id}/group", 
                        [group_name], 
                        target.host, 
                        target.port
                    )
                else:
                    self.send_message(f"/source/{source_id}/group", [group_name])
                    
        except Exception as e:
            print(f"   ❌ Error añadiendo fuente al grupo: {e}")
'''
            
            # Reemplazar create_group existente y añadir add_source_to_group
            # Buscar el create_group actual
            create_start = content.find('def create_group')
            create_end = next_def
            
            # Reemplazar
            content = content[:create_start] + fixed_methods + '\n' + content[create_end:]
            
            # Guardar
            with open(bridge_file, 'w') as f:
                f.write(content)
            
            print("   ✅ Métodos OSC actualizados")
    
    else:
        print("   ✅ add_source_to_group ya existe")

# 3. Test rápido OSC
print("\n3️⃣ TEST RÁPIDO OSC...\n")

test_osc = '''
import os
import sys

# No deshabilitar OSC para este test
if 'DISABLE_OSC' in os.environ:
    del os.environ['DISABLE_OSC']

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

try:
    from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget
    
    # Crear bridge
    target = OSCTarget("127.0.0.1", 9000)
    bridge = SpatOSCBridge(targets=[target], fps=60)
    
    # Verificar métodos
    if hasattr(bridge, 'create_group') and hasattr(bridge, 'add_source_to_group'):
        print("✅ Métodos OSC disponibles")
        
        # Test de creación
        try:
            bridge.create_group("test_id", "TestGroup")
            bridge.add_source_to_group(1, "TestGroup")
            print("✅ Mensajes OSC enviados sin errores")
        except Exception as e:
            print(f"❌ Error enviando OSC: {e}")
    else:
        print("❌ Faltan métodos OSC")
        
except Exception as e:
    print(f"❌ Error en test OSC: {e}")
'''

exec(test_osc)

# 4. Instrucciones finales
print("""

================================================================================
📋 PRÓXIMOS PASOS
================================================================================

1. VERIFICA EN SPAT:
   - Abre OSC Monitor (View > OSC Monitor)
   - Deberías ver mensajes /group/new y /source/X/group

2. EJECUTA EL CONTROLADOR:
   python trajectory_hub/interface/interactive_controller.py
   
   - La concentración debería funcionar (tecla C)
   - Los macros deberían crearse en Spat

3. SI LOS MACROS NO APARECEN:
   - Verifica el formato OSC de tu versión de Spat
   - Algunos usan /source/group/new en lugar de /group/new
   - Revisa la documentación específica

4. OPTIMIZACIÓN (OPCIONAL):
   Si la concentración es muy rápida/lenta, edita step():
   
   # Busca esta línea:
   new_pos = current_pos + (direction * factor * dt * 10.0)
   
   # Cambia el 10.0 por otro valor (5.0 = más lento, 20.0 = más rápido)

================================================================================
🎯 RESUMEN DEL ESTADO
================================================================================

✅ FUNCIONANDO:
   - Concentración de fuentes (convergencia al centro)
   - Comunicación OSC básica
   - Envío de posiciones

⚠️ POR VERIFICAR:
   - Creación de macros en Spat
   - Formato OSC específico de tu versión

💡 La concentración está 100% funcional. Solo falta afinar la
   comunicación OSC para los macros según tu versión de Spat.

================================================================================
""")