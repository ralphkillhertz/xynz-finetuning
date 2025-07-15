#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🧪 TEST OSC PARA MACROS\n")

# Sin DISABLE_OSC para este test
if 'DISABLE_OSC' in os.environ:
    del os.environ['DISABLE_OSC']

# Crear bridge
print("1. Creando OSC Bridge...")
target = OSCTarget("127.0.0.1", 9000)
bridge = SpatOSCBridge(targets=[target], fps=60)

# Verificar métodos
print("\n2. Verificando métodos:")
print(f"   create_group existe: {hasattr(bridge, 'create_group')}")
print(f"   add_source_to_group existe: {hasattr(bridge, 'add_source_to_group')}")

# Test de creación
print("\n3. Test de creación de grupo:")
try:
    bridge.create_group("test_id", "TestGroup")
    print("   ✅ create_group ejecutado sin errores")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n4. Test de añadir fuente:")
try:
    bridge.add_source_to_group(1, "TestGroup")
    print("   ✅ add_source_to_group ejecutado sin errores")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n5. Test con engine completo:")
engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
macro_id = engine.create_macro("test_macro", source_count=3)

print("\n📡 VERIFICA EN SPAT:")
print("   - View > OSC Monitor")
print("   - Deberías ver mensajes /group/new")
print("   - Y mensajes /source/X/group")
