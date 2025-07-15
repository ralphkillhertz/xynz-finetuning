# === diagnose_motion_state_error.py ===
# 🔍 Diagnóstico profundo: motion.state es float en lugar de MotionState
# ⚡ Análisis del problema en update()

import ast

def analyze_update_method():
    """Analizar el método update() alrededor de la línea 1919"""
    print("🔍 DIAGNÓSTICO PROFUNDO: motion.state error")
    print("=" * 70)
    
    with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
        lines = f.readlines()
    
    # Buscar contexto alrededor de la línea 1919
    start = max(0, 1919 - 30)
    end = min(len(lines), 1919 + 10)
    
    print(f"\n📄 Contexto líneas {start}-{end}:")
    print("-" * 70)
    
    for i in range(start, end):
        marker = ">>> " if i == 1918 else "    "
        print(f"{i+1:4d}: {marker}{lines[i].rstrip()}")
    
    # Buscar dónde se usa motion.state
    print("\n🔍 Buscando asignaciones a motion.state:")
    for i, line in enumerate(lines):
        if "motion.state =" in line or "motion.state." in line:
            print(f"   Línea {i+1}: {line.strip()}")
    
    # Buscar el tipo de motion
    print("\n🔍 Buscando tipo de motion:")
    for i in range(max(0, 1900), min(len(lines), 1930)):
        if "motion" in lines[i] and ("=" in lines[i] or "for" in lines[i]):
            print(f"   Línea {i+1}: {lines[i].strip()}")

def check_motion_components():
    """Verificar la estructura de motion_components.py"""
    print("\n📋 Verificando SourceMotion en motion_components.py:")
    
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        content = f.read()
    
    # Buscar definición de SourceMotion
    if "class SourceMotion" in content:
        start = content.find("class SourceMotion")
        end = content.find("\nclass ", start + 1)
        if end == -1:
            end = len(content)
        
        source_motion_code = content[start:start+500]
        print(source_motion_code)
    
    # Buscar el método update de SourceMotion
    print("\n🔍 Buscando SourceMotion.update():")
    if "def update(" in content:
        idx = content.find("def update(", content.find("class SourceMotion"))
        if idx > 0:
            update_code = content[idx:idx+300]
            print(update_code)

if __name__ == "__main__":
    analyze_update_method()
    check_motion_components()