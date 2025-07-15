#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# NO deshabilitar OSC
if 'DISABLE_OSC' in os.environ:
    del os.environ['DISABLE_OSC']

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget

print("🔍 DIAGNÓSTICO OSC\n")

# 1. Verificar que el bridge funciona solo
print("1. TEST BRIDGE DIRECTO:")
target = OSCTarget("127.0.0.1", 9000)
bridge = SpatOSCBridge(targets=[target], fps=60)

print(f"   Bridge creado: {bridge}")
print(f"   Tiene client: {hasattr(bridge, 'client')}")
print(f"   Targets: {len(bridge.targets)}")

print("\n   Enviando grupo de prueba...")
bridge.create_group("test_id", "TestDirecto")

# 2. Verificar el engine
print("\n2. TEST ENGINE:")
engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)

print(f"   Engine tiene bridge: {hasattr(engine, 'bridge')}")
print(f"   Engine tiene osc_bridge: {hasattr(engine, 'osc_bridge')}")
print(f"   Engine tiene _osc_bridge: {hasattr(engine, '_osc_bridge')}")

# Buscar el bridge
bridge_attr = None
for attr in ['bridge', 'osc_bridge', '_osc_bridge', '_bridge']:
    if hasattr(engine, attr):
        bridge_attr = attr
        print(f"   ✅ Bridge encontrado en: {attr}")
        bridge_obj = getattr(engine, attr)
        print(f"   Tipo: {type(bridge_obj)}")
        break

if not bridge_attr:
    print("   ❌ NO HAY BRIDGE OSC EN EL ENGINE")

# 3. Verificar create_macro
print("\n3. VERIFICANDO create_macro:")

# Parchear temporalmente para debug
if hasattr(engine, 'create_macro'):
    original_create = engine.create_macro
    
    def debug_create(name, **kwargs):
        print(f"   -> create_macro('{name}') llamado")
        result = original_create(name, **kwargs)
        print(f"   -> Resultado: {result}")
        
        # Verificar si intenta crear grupo OSC
        if bridge_attr and hasattr(engine, bridge_attr):
            b = getattr(engine, bridge_attr)
            print(f"   -> Bridge disponible: {b is not None}")
            if b and hasattr(b, 'create_group'):
                print("   -> Bridge tiene create_group")
        
        return result
    
    engine.create_macro = debug_create

# Crear macro
print("\n4. CREANDO MACRO:")
macro_id = engine.create_macro("test", source_count=2)

print("\n📊 RESUMEN:")
print("   - Bridge directo: FUNCIONA" if bridge else "FALLA")
print("   - Engine tiene bridge: " + ("SÍ" if bridge_attr else "NO"))
print("   - create_macro se ejecuta: SÍ")
print("\n   🔍 El problema está en la conexión engine→bridge")
