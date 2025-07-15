# === diagnose_delta_issue.py ===
# 🔧 Diagnóstico: Ver exactamente qué está pasando con deltas
# ⚡ Impacto: Diagnóstico completo

import os

def diagnose_issue():
    """Diagnóstica el problema con deltas"""
    
    print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA DE DELTAS\n")
    
    # 1. Verificar MotionDelta
    print("1️⃣ Verificando clase MotionDelta...")
    motion_path = "trajectory_hub/core/motion_components.py"
    
    with open(motion_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if "class MotionDelta" in line:
            print(f"   Línea {i+1}: {line.strip()}")
            # Mostrar las siguientes 10 líneas
            for j in range(i+1, min(i+11, len(lines))):
                print(f"   Línea {j+1}: {lines[j].rstrip()}")
            break
    
    # 2. Verificar _send_osc_update
    print("\n2️⃣ Verificando _send_osc_update...")
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar _send_osc_update y mostrar las líneas problemáticas
    import re
    match = re.search(r'def _send_osc_update\(self\):(.*?)(?=\n    def|\n\nclass|\Z)', content, re.DOTALL)
    if match:
        method_content = match.group(0)
        lines = method_content.split('\n')
        for i, line in enumerate(lines[:20]):  # Primeras 20 líneas
            if 'delta' in line:
                print(f"   L{i}: {line}")
    
    # 3. Crear fix directo
    print("\n3️⃣ Creando fix directo...")
    
    # Remover referencias a delta en _send_osc_update
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y reemplazar la sección problemática
    old_pattern = r'self\._positions\[delta\.source_id\] \+= delta\.position'
    new_pattern = '# Delta processing moved to update method'
    
    content = content.replace(old_pattern, new_pattern)
    
    # También buscar cualquier otra referencia a delta en _send_osc_update
    content = re.sub(
        r'if delta\.source_id.*?\n.*?self\._positions.*?\n',
        '# Delta processing handled in update()\n',
        content,
        flags=re.DOTALL
    )
    
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Referencias a delta removidas de _send_osc_update")

if __name__ == "__main__":
    diagnose_issue()
    print("\n🚀 Ejecutando test final...")
    os.system("python test_macro_final_working.py")