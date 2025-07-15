#!/usr/bin/env python3
"""
🔧 ACTIVAR MODO DUAL EN CONFIGURACIÓN
"""

import json
import os

print("=" * 80)
print("🔧 ACTIVANDO MODO DUAL")
print("=" * 80)

config_path = "trajectory_hub/config/parallel_config.json"

# 1. Leer configuración actual
print("\n1️⃣ LEYENDO CONFIGURACIÓN ACTUAL...")

with open(config_path, 'r') as f:
    config = json.load(f)

print("Valores actuales:")
for key in ['CONCENTRATION_DUAL_MODE', 'PARALLEL_MODE', 'LOG_DELTAS']:
    print(f"   {key}: {config.get(key, 'NO EXISTE')}")

# 2. Activar modo dual
print("\n2️⃣ ACTIVANDO MODO DUAL...")

config['CONCENTRATION_DUAL_MODE'] = True
config['LOG_DELTAS'] = True  # Para debug

# Guardar
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("✅ Configuración actualizada")

# 3. Verificar
print("\n3️⃣ VERIFICANDO...")

# Recargar y verificar
with open(config_path, 'r') as f:
    new_config = json.load(f)

print("Nuevos valores:")
for key in ['CONCENTRATION_DUAL_MODE', 'PARALLEL_MODE', 'LOG_DELTAS']:
    print(f"   {key}: {new_config.get(key, 'NO EXISTE')}")

# 4. Test rápido
print("\n4️⃣ TEST RÁPIDO...")

import sys
sys.path.insert(0, 'trajectory_hub')

try:
    from trajectory_hub.core.compatibility_v2 import compat_v2 as compat
    
    # Forzar recarga
    compat.reload_config()
    
    print(f"✅ compat.is_concentration_dual_mode(): {compat.is_concentration_dual_mode()}")
    
    if compat.is_concentration_dual_mode():
        print("\n✅ ¡MODO DUAL ACTIVADO CORRECTAMENTE!")
    else:
        print("\n❌ Algo no funciona, verificar manualmente")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("PRÓXIMO PASO: python test_phase1_real_structure.py")
print("=" * 80)