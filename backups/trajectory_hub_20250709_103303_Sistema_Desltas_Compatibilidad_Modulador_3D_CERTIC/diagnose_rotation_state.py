# === diagnose_rotation_state.py ===
import os

# Check the MacroRotation update method
file_path = "trajectory_hub/core/motion_components.py"

print("🔍 Diagnosticando problema con MacroRotation")
print("=" * 60)

with open(file_path, 'r') as f:
    lines = f.readlines()

# Find MacroRotation class and its update method
in_macro_rotation = False
in_update = False
update_start = -1

for i, line in enumerate(lines):
    if "class MacroRotation" in line:
        in_macro_rotation = True
        print(f"✅ MacroRotation encontrado en línea {i+1}")
    
    if in_macro_rotation and "def update(" in line:
        in_update = True
        update_start = i
        print(f"\n📍 Método update encontrado en línea {i+1}:")
        print(f"   {line.strip()}")
        
        # Mostrar las siguientes 10 líneas
        for j in range(i, min(i+10, len(lines))):
            print(f"   L{j+1}: {lines[j].rstrip()}")
        break

print("\n💡 SOLUCIÓN PROBABLE:")
print("   El método update() de MacroRotation podría tener los parámetros en orden incorrecto")
print("   O podría estar retornando un valor incorrecto en lugar del state")