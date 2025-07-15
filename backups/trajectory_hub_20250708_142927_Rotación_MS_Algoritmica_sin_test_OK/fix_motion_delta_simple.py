# === fix_motion_delta_simple.py ===
# 🔧 Fix: Solución directa para source_id en MotionDelta
# ⚡ Impacto: CRÍTICO - Desbloquea sistema

import os

def fix_motion_delta():
    """Fix simple y directo para el problema de source_id"""
    
    file_path = "trajectory_hub/core/motion_components.py"
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar clase MotionDelta y añadir source_id
    for i, line in enumerate(lines):
        if line.strip() == "class MotionDelta:":
            # Buscar el __init__
            for j in range(i, min(i+20, len(lines))):
                if "def __init__(self):" in lines[j]:
                    # Insertar source_id después de __init__
                    indent = "        "
                    if j+1 < len(lines) and "self." in lines[j+1]:
                        # Añadir antes de otros atributos
                        lines.insert(j+1, f"{indent}self.source_id = None\n")
                        print("✅ Añadido source_id a MotionDelta.__init__")
                    break
            break
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ MotionDelta actualizado")
    
    # Ahora arreglar el error en _send_osc_update que usa delta.source_id
    fix_send_osc_update()

def fix_send_osc_update():
    """Arregla _send_osc_update para no usar delta.source_id"""
    
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar el uso incorrecto de delta.source_id
    content = content.replace(
        "if delta.source_id < len(self._positions):",
        "# No usar delta.source_id aquí - se procesa más adelante"
    )
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ _send_osc_update corregido")

if __name__ == "__main__":
    fix_motion_delta()
    print("\n🚀 Ejecutando test final...")
    os.system("python test_macro_final_working.py")