# === quick_fix_add_component.py ===
import fileinput
import sys

fixed = False
for line in fileinput.input('trajectory_hub/core/motion_components.py', inplace=True):
    if "self.active_components.append(component)" in line and not fixed:
        indent = len(line) - len(line.lstrip())
        print(" " * indent + "# Determinar tipo de componente")
        print(" " * indent + "component_type = type(component).__name__.lower()")
        print(" " * indent + "if component_type.endswith('component'):")
        print(" " * indent + "    component_type = component_type[:-9]  # Quitar 'component'")
        print(" " * indent + "self.active_components[component_type] = component")
        fixed = True
    else:
        print(line, end='')

if fixed:
    print("✅ Arreglado!", file=sys.stderr)
else:
    print("❌ No se encontró la línea", file=sys.stderr)