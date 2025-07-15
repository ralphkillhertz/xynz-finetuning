# === quick_fix_update_order.py ===
import fileinput

for line in fileinput.input('trajectory_hub/core/motion_components.py', inplace=True):
    if "component.update(current_time, dt, self.state)" in line:
        line = line.replace(
            "component.update(current_time, dt, self.state)",
            "component.update(self.state, current_time, dt)"
        )
    print(line, end='')

print("✅ Orden de parámetros corregido!")