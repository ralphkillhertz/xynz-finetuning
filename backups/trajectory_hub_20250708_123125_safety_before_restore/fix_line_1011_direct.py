# === fix_line_1011_direct.py ===
# 🔧 Fix: Arreglar línea 1011 directamente
# ⚡ DIRECT FIX

import os

# Leer archivo
with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"📋 Total líneas: {len(lines)}")

# Mostrar contexto alrededor de línea 1011
if len(lines) > 1010:
    print("\n📋 Contexto líneas 1008-1013:")
    for i in range(max(0, 1007), min(len(lines), 1013)):
        marker = ">>>" if i == 1010 else "   "
        print(f"{marker} {i+1:4d}: {repr(lines[i][:70])}")
    
    # Corregir si la línea 1011 es un docstring mal indentado
    if '"""' in lines[1010]:
        # Asegurar que tenga 8 espacios (para método dentro de clase)
        lines[1010] = '        """Actualiza y retorna lista de deltas de todos los componentes activos"""\n'
        print("\n✅ Línea 1011 corregida")
    
    # También verificar la línea anterior (1010)
    if 'def update_with_deltas' in lines[1009]:
        # Asegurar que el def tenga 4 espacios
        if not lines[1009].startswith('    def'):
            lines[1009] = '    def update_with_deltas(self, current_time: float, dt: float) -> List[MotionDelta]:\n'
            print("✅ Línea 1010 también corregida")

# Guardar
with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ Archivo actualizado")
print("🚀 Ejecutando test...")
os.system("python test_rotation_ms_final.py")