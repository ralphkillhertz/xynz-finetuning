#!/usr/bin/env python3
"""
🔧 FIX: Restaurar comunicación OSC con Spat
"""

import os
import sys

print("""
================================================================================
🔧 FIX COMUNICACIÓN OSC CON SPAT
================================================================================
""")

# 1. Verificar que OSC no esté deshabilitado
print("1️⃣ VERIFICANDO VARIABLE DE ENTORNO OSC...")
if 'DISABLE_OSC' in os.environ:
    print(f"   ⚠️ DISABLE_OSC = {os.environ['DISABLE_OSC']}")
    del os.environ['DISABLE_OSC']
    print("   ✅ Variable DISABLE_OSC eliminada")
else:
    print("   ✅ OSC no está deshabilitado")

# 2. Verificar configuración OSC
print("\n2️⃣ VERIFICANDO CONFIGURACIÓN OSC...")

try:
    # Path setup
    current_dir = os.getcwd()
    if 'trajectory_hub' in current_dir:
        parent_dir = os.path.dirname(current_dir)
        sys.path.insert(0, parent_dir)
    
    from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget
    print("   ✅ SpatOSCBridge importado correctamente")
    
    # Verificar target por defecto
    default_target = OSCTarget("127.0.0.1", 9001)  # Puerto por defecto de Spat
    print(f"   📡 Target OSC: {default_target.host}:{default_target.port}")
    
except Exception as e:
    print(f"   ❌ Error importando OSC: {e}")

# 3. Modificar step() para enviar OSC
print("\n3️⃣ MODIFICANDO step() PARA ENVIAR OSC...")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
import datetime
backup_name = engine_file + f".backup_osc_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_name, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"   📋 Backup: {backup_name}")

# Buscar el método step
import re
step_match = re.search(r'(def step\(self.*?\):.*?)(?=\n    def|\nclass|\Z)', content, re.DOTALL)

if step_match:
    step_content = step_match.group(0)
    
    # Verificar si ya envía OSC
    if 'osc_bridge' not in step_content:
        print("   ⚠️ step() no envía OSC, añadiendo...")
        
        # Buscar el return statement
        return_match = re.search(r'(return\s*{[^}]+})', step_content)
        
        if return_match:
            # Insertar código OSC antes del return
            osc_code = '''
        # Enviar posiciones via OSC si está activo
        if hasattr(self, 'osc_bridge') and self.osc_bridge:
            try:
                # Preparar datos para enviar
                active_sources = []
                active_positions = []
                active_orientations = []
                
                for sid in range(self.max_sources):
                    if sid in self._source_motions:
                        active_sources.append(sid)
                        active_positions.append(self._positions[sid])
                        active_orientations.append(self._orientations[sid])
                
                if active_sources:
                    # Enviar batch de posiciones
                    import numpy as np
                    positions_array = np.array(active_positions)
                    orientations_array = np.array(active_orientations)
                    
                    self.osc_bridge.send_batch_positions(
                        active_sources,
                        positions_array,
                        orientations_array
                    )
            except Exception as e:
                # No fallar si hay error OSC
                pass
        
        '''
            
            # Insertar antes del return
            new_step = step_content.replace(
                return_match.group(0),
                osc_code + return_match.group(0)
            )
            
            content = content.replace(step_content, new_step)
            print("   ✅ Código OSC añadido a step()")
    else:
        print("   ✅ step() ya tiene código OSC")

# Guardar
with open(engine_file, 'w', encoding='utf-8') as f:
    f.write(content)

# 4. Test de comunicación OSC
print("\n4️⃣ TEST DE COMUNICACIÓN OSC...")

test_code = '''
import os
import sys
import time

# NO deshabilitar OSC
if 'DISABLE_OSC' in os.environ:
    del os.environ['DISABLE_OSC']

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget
    
    print("\\n🔧 CREANDO ENGINE CON OSC...")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # Crear OSC bridge
    print("\\n📡 CONFIGURANDO OSC BRIDGE...")
    target = OSCTarget("127.0.0.1", 9000)  # Puerto de Spat
    bridge = SpatOSCBridge(targets=[target], fps=60)
    
    # Asignar bridge al engine
    engine.osc_bridge = bridge
    
    print(f"   Target: {target.host}:{target.port}")
    print(f"   Bridge activo: {bridge is not None}")
    
    # Crear macro
    print("\\n🎯 CREANDO MACRO...")
    macro_id = engine.create_macro("TestOSC", source_count=4, formation="grid")
    
    print(f"   Macro creado: {macro_id}")
    print(f"   Fuentes: {engine._macros[macro_id].source_ids}")
    
    # Enviar mensajes OSC de creación
    print("\\n📤 ENVIANDO MENSAJES OSC DE CREACIÓN...")
    
    # Crear grupo en Spat
    if hasattr(bridge, 'create_group'):
        bridge.create_group(macro_id, "TestOSC")
        print("   ✅ Grupo creado via OSC")
    
    # Enviar posiciones iniciales
    for sid in engine._macros[macro_id].source_ids:
        if sid < engine.max_sources:
            pos = engine._positions[sid]
            bridge.send_position(sid, pos)
            print(f"   ✅ Posición F{sid} enviada: {pos}")
    
    # Ejecutar algunos frames
    print("\\n🔄 EJECUTANDO FRAMES CON OSC...")
    
    for frame in range(10):
        engine.step()
        time.sleep(0.05)  # 50ms entre frames
        
        if frame == 0:
            print("   Frame 1: OSC enviando...")
        elif frame == 9:
            print("   Frame 10: OSC completado")
    
    print("\\n✅ TEST COMPLETADO")
    print("\\n💡 VERIFICA EN SPAT:")
    print("   1. Las fuentes deberían aparecer")
    print("   2. El grupo 'TestOSC' debería existir")
    print("   3. Los mensajes OSC deberían verse en el monitor")
    
except Exception as e:
    print(f"\\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
'''

exec(test_code)

print("""

================================================================================
📋 ACCIONES ADICIONALES
================================================================================

Si aún no hay comunicación OSC:

1. VERIFICA SPAT REVOLUTION:
   - Puerto OSC Input: 9000 (por defecto)
   - OSC habilitado en preferencias
   - Monitor OSC abierto para ver mensajes

2. VERIFICA FIREWALL:
   - Permite comunicación en puerto 9000
   - Localhost (127.0.0.1) no bloqueado

3. PRUEBA MANUAL OSC:
   python -c "from pythonosc import udp_client; client = udp_client.SimpleUDPClient('127.0.0.1', 9000); client.send_message('/source/1/xyz', [1.0, 2.0, 0.0])"

4. USA EL CONTROLADOR:
   python trajectory_hub/interface/interactive_controller.py
   
   El controlador debería:
   - Inicializar OSC automáticamente
   - Crear macros en Spat
   - Enviar posiciones continuamente

================================================================================
""")