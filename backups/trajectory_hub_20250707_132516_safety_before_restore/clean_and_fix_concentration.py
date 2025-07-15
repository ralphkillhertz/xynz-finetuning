# === clean_and_fix_concentration.py ===
# 🔧 Fix: Limpiar TODAS las definiciones y dejar UNA que funcione
# ⚡ Directo al grano

import os

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

# Leer archivo
with open(engine_file, 'r') as f:
    lines = f.readlines()

# Backup
import datetime
backup_name = f"{engine_file}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_name, 'w') as f:
    f.writelines(lines)

print("🧹 LIMPIEZA TOTAL\n")

# 1. Encontrar TODAS las líneas con set_macro_concentration
found_lines = []
for i, line in enumerate(lines):
    if 'def set_macro_concentration' in line:
        found_lines.append((i, line.strip().startswith('#')))
        print(f"   Línea {i+1}: {'[COMENTADA]' if line.strip().startswith('#') else '[ACTIVA]'}")

# 2. Comentar TODAS (incluso las ya comentadas)
print("\n🗑️ Comentando TODAS las definiciones...")
for line_num, is_commented in found_lines:
    # Comentar desde esta línea hasta el siguiente def
    i = line_num
    while i < len(lines):
        if i > line_num and lines[i].strip().startswith('def '):
            break
        if not lines[i].strip().startswith('#'):
            lines[i] = '# ' + lines[i]
        i += 1

# 3. Insertar UNA definición simple que FUNCIONE
print("\n✅ Insertando definición SIMPLE y FUNCIONAL...")

# Buscar dónde insertar (después de create_macro)
insert_pos = -1
for i, line in enumerate(lines):
    if 'def create_macro' in line and not line.strip().startswith('#'):
        # Buscar el siguiente def
        for j in range(i+1, len(lines)):
            if lines[j].strip().startswith('def '):
                insert_pos = j
                break
        break

if insert_pos > 0:
    # Método SIMPLE que FUNCIONA
    method = '''    def set_macro_concentration(self, macro_id: str, factor: float):
        """Set concentration - SIMPLE VERSION."""
        if macro_id in self._macros:
            self._macros[macro_id].concentration_factor = factor
            print(f"SET: {macro_id} concentration = {factor}")
        else:
            print(f"ERROR: Macro {macro_id} not found")

'''
    lines.insert(insert_pos, method)
    print(f"   Insertado en línea {insert_pos + 1}")

# Guardar
with open(engine_file, 'w') as f:
    f.writelines(lines)

print("\n✅ ARCHIVO LIMPIO Y ACTUALIZADO")

# Test
print("\n🧪 TEST:")
exec('''
import sys
sys.path.insert(0, ".")
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

e = EnhancedTrajectoryEngine(max_sources=2, fps=60)
m = e.create_macro("test", source_count=2)
e.set_macro_concentration(m, 0.7)

factor = getattr(e._macros[m], 'concentration_factor', 'NO_EXISTE')
print(f"\\nFactor guardado: {factor}")

if factor == 0.7:
    print("✅ ¡FUNCIONA!")
else:
    print("❌ Sigue sin funcionar")
''')