# === quick_fix_modulator.py ===
import fileinput

fixed = False
for line in fileinput.input('trajectory_hub/core/enhanced_trajectory_engine.py', inplace=True):
    if "modulator.update(current_time, dt, state)" in line and not fixed:
        line = line.replace(
            "modulator.update(current_time, dt, state)",
            "modulator.update(state, current_time, dt)"
        )
        fixed = True
    print(line, end='')

if fixed:
    print("✅ Orden de parámetros del modulador corregido!")
else:
    print("❌ No se encontró la línea")