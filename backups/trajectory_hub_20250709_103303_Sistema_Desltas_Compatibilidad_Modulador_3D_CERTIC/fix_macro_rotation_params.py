# === fix_macro_rotation_params.py ===
import fileinput

# Fix MacroRotation update method parameter order
fixed = False
for line in fileinput.input('trajectory_hub/core/motion_components.py', inplace=True):
    if "def update(self, current_time, dt, state):" in line and not fixed:
        # Check if this is inside MacroRotation (looking at indentation)
        if line.startswith("    def update"):  # 4 spaces = method inside class
            line = line.replace(
                "def update(self, current_time, dt, state):",
                "def update(self, state, current_time, dt):"
            )
            fixed = True
    print(line, end='')

if fixed:
    print("✅ Orden de parámetros en MacroRotation.update() corregido!")
else:
    print("❌ No se encontró la línea exacta")