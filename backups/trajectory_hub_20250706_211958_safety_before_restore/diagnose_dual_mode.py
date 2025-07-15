#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO: Por qué no funciona el modo dual
"""

import os
import json
import sys

sys.path.insert(0, 'trajectory_hub')

print("=" * 80)
print("🔍 DIAGNÓSTICO MODO DUAL")
print("=" * 80)

# 1. Verificar configuración
print("\n1️⃣ VERIFICANDO CONFIGURACIÓN...")

config_path = "trajectory_hub/config/parallel_config.json"
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print(f"✅ Archivo config existe")
    print(f"   CONCENTRATION_DUAL_MODE: {config.get('CONCENTRATION_DUAL_MODE', 'NO EXISTE')}")
    print(f"   PARALLEL_MODE: {config.get('PARALLEL_MODE', 'NO EXISTE')}")
else:
    print(f"❌ No existe: {config_path}")

# 2. Verificar compatibility_v2
print("\n2️⃣ VERIFICANDO COMPATIBILITY_V2...")

try:
    from trajectory_hub.core.compatibility_v2 import compat_v2 as compat
    
    print("✅ Import exitoso")
    print(f"   Config path en compat: {compat.config_path}")
    
    # Verificar config cargada
    print(f"   Config actual: {compat.config}")
    
    # Probar métodos
    print(f"   is_concentration_dual_mode(): {compat.is_concentration_dual_mode()}")
    
    # Intentar activar manualmente
    print("\n   Activando modo dual manualmente...")
    compat.config['CONCENTRATION_DUAL_MODE'] = True
    print(f"   is_concentration_dual_mode() ahora: {compat.is_concentration_dual_mode()}")
    
    # Recargar config
    print("\n   Recargando config desde archivo...")
    compat.reload_config()
    print(f"   Después de reload: {compat.is_concentration_dual_mode()}")
    print(f"   Config después de reload: {compat.config}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# 3. Verificar modificación en motion_components
print("\n3️⃣ VERIFICANDO MODIFICACIÓN EN motion_components.py...")

motion_file = "trajectory_hub/core/motion_components.py"

with open(motion_file, 'r') as f:
    lines = f.readlines()

# Buscar el código modificado
found_dual_check = False
line_num = -1

for i, line in enumerate(lines):
    if 'compat.is_concentration_dual_mode()' in line:
        found_dual_check = True
        line_num = i + 1
        break

if found_dual_check:
    print(f"✅ Check de modo dual encontrado en línea {line_num}")
    
    # Mostrar contexto
    print("\nContexto del código:")
    start = max(0, line_num - 6)
    end = min(len(lines), line_num + 10)
    
    for i in range(start, end):
        marker = ">>>" if i == line_num - 1 else "   "
        print(f"{marker} {i+1:4d}: {lines[i]}", end='')
else:
    print("❌ No se encontró el check de modo dual")

# 4. Verificar que está en el lugar correcto
print("\n4️⃣ VERIFICANDO UBICACIÓN DEL CHECK...")

# Buscar la línea de lerp original
lerp_line = -1
for i, line in enumerate(lines):
    if 'state.position = self._lerp(state.position, target, concentration_strength)' in line:
        # Verificar que NO es la que está dentro del else
        if i > 0 and 'else:' not in lines[i-1] and 'else:' not in lines[i-2]:
            lerp_line = i + 1
            print(f"⚠️ Encontrada línea lerp SIN protección en línea {lerp_line}")
            print("   Esta línea debería estar dentro del else del modo dual")
            break

# 5. Test directo
print("\n5️⃣ TEST DIRECTO DE COMPATIBILIDAD...")

try:
    # Crear nueva instancia para test limpio
    from trajectory_hub.core.compatibility_v2 import CompatibilityManagerV2
    
    test_compat = CompatibilityManagerV2()
    
    print(f"   Nueva instancia creada")
    print(f"   Config path: {test_compat.config_path}")
    
    # Intentar varias formas de activar
    test_compat.config = {"CONCENTRATION_DUAL_MODE": True}
    print(f"   Seteado directamente: {test_compat.is_concentration_dual_mode()}")
    
except Exception as e:
    print(f"❌ Error en test: {e}")

# 6. Propuesta de solución
print("\n" + "=" * 80)
print("💡 DIAGNÓSTICO Y SOLUCIÓN")
print("=" * 80)

if not found_dual_check:
    print("❌ El código de modo dual no está en el archivo")
    print("   SOLUCIÓN: Volver a ejecutar la modificación")
elif lerp_line > 0:
    print("❌ Hay una línea lerp sin protección del modo dual")
    print("   SOLUCIÓN: El if debe envolver TODA la lógica de interpolación")
else:
    print("⚠️ El código parece estar bien, pero el modo dual no se activa")
    print("   POSIBLES CAUSAS:")
    print("   1. La config no se está cargando correctamente")
    print("   2. Hay múltiples instancias de compat")
    print("   3. El path del config es incorrecto")

print("\n📝 SIGUIENTE PASO:")
print("   Si el código no está bien ubicado, ejecutar:")
print("   python fix_dual_mode_location.py")
print("=" * 80)