# === diagnose_line11.py ===
# 🔍 Diagnóstico rápido línea 11

with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("📋 Líneas 1-20:")
for i, line in enumerate(lines[:20], 1):
    marker = ">>>" if i == 11 else "   "
    print(f"{marker} {i:2d}: {repr(line[:60])}")