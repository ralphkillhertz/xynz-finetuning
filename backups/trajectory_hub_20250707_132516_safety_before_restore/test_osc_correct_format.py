#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget

print("🧪 TEST OSC FORMATO CORRECTO\n")

# Crear bridge
target = OSCTarget("127.0.0.1", 9000)
bridge = SpatOSCBridge(targets=[target], fps=60)

print("1. Creando grupo 'MiGrupo'...")
bridge.create_group("interno_01", "MiGrupo")

print("\n2. Añadiendo fuentes 1,2,3 al grupo...")
for i in range(1, 4):
    bridge.add_source_to_group(i, "MiGrupo")

print("\n✅ VERIFICA EN SPAT OSC MONITOR:")
print("   Deberías ver:")
print("   - /group/new ['MiGrupo']")
print("   - /source/1/group ['MiGrupo']")
print("   - /source/2/group ['MiGrupo']")
print("   - /source/3/group ['MiGrupo']")
