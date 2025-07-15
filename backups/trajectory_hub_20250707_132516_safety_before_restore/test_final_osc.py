#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# NO deshabilitar OSC
if 'DISABLE_OSC' in os.environ:
    del os.environ['DISABLE_OSC']

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🧪 TEST FINAL OSC\n")

print("1. Creando engine...")
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

print(f"\n2. Verificando OSC:")
print(f"   osc_bridge existe: {engine.osc_bridge is not None}")
if engine.osc_bridge:
    print(f"   Tipo: {type(engine.osc_bridge)}")

print("\n3. Creando macro 'DemoGroup'...")
macro_id = engine.create_macro("DemoGroup", source_count=3)

print("\n4. Moviendo fuentes...")
engine.set_macro_concentration(macro_id, 0.5)

for i in range(5):
    engine.step()
    print(f"   Frame {i+1}")

print("\n✅ VERIFICA EN SPAT OSC MONITOR:")
print("   - /group/new ['DemoGroup']")
print("   - /source/0/group ['DemoGroup']")
print("   - /source/1/group ['DemoGroup']")
print("   - /source/2/group ['DemoGroup']")
print("   - /source/0/xyz [x, y, z] (actualizándose)")
