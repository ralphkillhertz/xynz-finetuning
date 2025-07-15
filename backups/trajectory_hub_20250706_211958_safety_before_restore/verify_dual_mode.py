#!/usr/bin/env python3
"""
🔍 VERIFICAR LÓGICA DEL MODO DUAL
"""

import sys
sys.path.insert(0, 'trajectory_hub')

from trajectory_hub.core.compatibility_v2 import compat_v2 as compat
import json

print("=" * 80)
print("🔍 VERIFICACIÓN DE LÓGICA DUAL MODE")
print("=" * 80)

# 1. Estado actual
print("\n1️⃣ ESTADO ACTUAL:")
print(f"   is_concentration_dual_mode(): {compat.is_concentration_dual_mode()}")
print(f"   Config: {compat.config.get('CONCENTRATION_DUAL_MODE')}")

# 2. Test de cambio dinámico
print("\n2️⃣ TEST DE CAMBIO DINÁMICO:")

# Desactivar
print("\n   Desactivando modo dual...")
config_path = "trajectory_hub/config/parallel_config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

config['CONCENTRATION_DUAL_MODE'] = False

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

# Recargar
compat.reload_config()
print(f"   Después de desactivar: {compat.is_concentration_dual_mode()}")

# Test rápido
print("\n3️⃣ TEST RÁPIDO DE CONCENTRATION:")

from trajectory_hub.core.motion_components import ConcentrationComponent, MotionState
import numpy as np

concentration = ConcentrationComponent()
concentration.enabled = True
concentration.factor = 0.0
concentration.target_point = np.array([0.0, 0.0, 0.0])

state = MotionState()
state.position = np.array([10.0, 0.0, 0.0])
state.source_id = 99

print(f"\n   Modo dual desactivado: {compat.is_concentration_dual_mode()}")
print(f"   Posición inicial: {state.position}")

# Clear deltas
compat.clear_deltas()

# Update
new_state = concentration.update(state, 0.0, 0.016)

print(f"   Posición después: {new_state.position}")
print(f"   ¿Se movió?: {not np.allclose(state.position, new_state.position)}")
print(f"   ¿Hay deltas?: {compat.get_accumulated_delta(99) is not None}")

# 4. Activar y probar de nuevo
print("\n4️⃣ ACTIVANDO Y PROBANDO:")

config['CONCENTRATION_DUAL_MODE'] = True
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

compat.reload_config()
print(f"\n   Modo dual activado: {compat.is_concentration_dual_mode()}")

state2 = MotionState()
state2.position = np.array([10.0, 0.0, 0.0])
state2.source_id = 100

compat.clear_deltas()

new_state2 = concentration.update(state2, 0.0, 0.016)

print(f"   Posición después: {new_state2.position}")
print(f"   ¿Se movió?: {not np.allclose(state2.position, new_state2.position)}")
print(f"   ¿Hay deltas?: {compat.get_accumulated_delta(100) is not None}")

print("\n" + "=" * 80)
print("DIAGNÓSTICO:")

if compat.get_accumulated_delta(99) is not None:
    print("❌ El modo dual está SIEMPRE activo")
    print("   Posible causa: compat es singleton y mantiene estado")
else:
    print("✅ Los modos funcionan correctamente")

print("=" * 80)