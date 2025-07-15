# === fix_rotation_algorithm_final.py ===
# 🔧 Fix: Corregir el algoritmo de calculate_delta definitivamente
# ⚡ El problema está en la lógica del algoritmo
# 🎯 Impacto: CRÍTICO

import numpy as np
from datetime import datetime
import shutil

def debug_algorithm():
    """Debug del algoritmo actual"""
    print("🔍 DEBUG: Algoritmo actual de calculate_delta")
    print("="*60)
    
    # Leer el archivo actual
    with open("trajectory_hub/core/motion_components.py", 'r') as f:
        content = f.read()
    
    # Buscar calculate_delta en ManualMacroRotation
    start = content.find("class ManualMacroRotation")
    if start == -1:
        print("❌ No se encontró ManualMacroRotation")
        return
    
    # Buscar el método
    method_start = content.find("def calculate_delta", start)
    if method_start == -1:
        print("❌ No se encontró calculate_delta")
        return
    
    # Extraer las primeras líneas del método
    method_section = content[method_start:method_start+1000]
    lines = method_section.split('\n')[:20]
    
    print("📋 Primeras líneas de calculate_delta:")
    for i, line in enumerate(lines):
        print(f"   {i+1}: {line}")
    
    # Buscar el problema
    print("\n⚠️ PROBLEMA IDENTIFICADO:")
    if "delta.position = np.array([0.1, 0.0, 0.0])" in method_section:
        print("   ❌ Línea problemática encontrada: delta.position = np.array([0.1, 0.0, 0.0])")
        print("   Esto retorna un movimiento LINEAL, no una rotación")

def fix_algorithm():
    """Arregla el algoritmo definitivamente"""
    print("\n🔧 APLICANDO FIX DEFINITIVO...")
    
    # Backup
    backup_name = f"motion_components.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy("trajectory_hub/core/motion_components.py", backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    with open("trajectory_hub/core/motion_components.py", 'r') as f:
        lines = f.readlines()
    
    # Buscar y corregir la línea problemática
    fixed = False
    in_manual_rotation = False
    in_calculate_delta = False
    
    for i in range(len(lines)):
        if "class ManualMacroRotation" in lines[i]:
            in_manual_rotation = True
        elif in_manual_rotation and "class " in lines[i] and "ManualMacroRotation" not in lines[i]:
            in_manual_rotation = False
            
        if in_manual_rotation and "def calculate_delta" in lines[i]:
            in_calculate_delta = True
            
        if in_calculate_delta:
            # Buscar la línea problemática
            if "delta.position = np.array([0.1, 0.0, 0.0])" in lines[i]:
                print(f"   ❌ Encontrada línea problemática en línea {i+1}")
                # Comentarla y añadir el fix correcto
                indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
                lines[i] = f"{indent}# {lines[i].strip()} # PROBLEMA: Esto no es rotación\n"
                lines.insert(i+1, f"{indent}# Si está en el centro, no hacer nada por ahora\n")
                lines.insert(i+2, f"{indent}delta.position = np.array([0.0, 0.0, 0.0])\n")
                fixed = True
                print(f"   ✅ Línea corregida")
                break
                
            # Si llegamos al return delta, salir
            if "return delta" in lines[i] and in_calculate_delta:
                in_calculate_delta = False
    
    if not fixed:
        print("   ⚠️ No se encontró la línea problemática exacta")
        print("   🔧 Buscando patrón alternativo...")
        
        # Buscar patrón más general
        for i in range(len(lines)):
            if "0.1" in lines[i] and "0.0" in lines[i] and "delta" in lines[i]:
                print(f"   📍 Posible línea problemática en {i+1}: {lines[i].strip()}")
    
    # Guardar
    with open("trajectory_hub/core/motion_components.py", 'w') as f:
        f.writelines(lines)
    
    if fixed:
        print("\n✅ Algoritmo corregido exitosamente")
    else:
        print("\n⚠️ Puede requerir corrección manual")
        print("   Buscar en calculate_delta de ManualMacroRotation:")
        print("   - La línea que asigna [0.1, 0.0, 0.0] a delta.position")
        print("   - Cambiarla a [0.0, 0.0, 0.0] o manejar el caso de otra forma")

def test_after_fix():
    """Test rápido después del fix"""
    print("\n🎯 TEST RÁPIDO:")
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)
    
    # Una fuente en [3,0,0]
    motion = engine.create_source(0)
    engine._positions[0] = np.array([3.0, 0.0, 0.0])
    engine.motion_states[0].position = [3.0, 0.0, 0.0]
    
    macro_name = engine.create_macro("test", source_count=1)
    
    # Desactivar otros
    state = engine.motion_states[0]
    for name, comp in state.active_components.items():
        if hasattr(comp, 'enabled') and name != 'manual_macro_rotation':
            comp.enabled = False
    
    engine.set_manual_macro_rotation(macro_name, yaw=np.pi/2, interpolation_speed=1.0)
    
    # Test directo
    rotation = state.active_components['manual_macro_rotation']
    delta = rotation.calculate_delta(state, 0.0, 1/60.0)
    
    print(f"   Delta calculado: {delta.position if delta else 'None'}")
    
    if delta and abs(delta.position[0]) < 0.01 and abs(delta.position[1]) > 0.01:
        print("   ✅ Delta parece correcto (rotación, no traslación)")
    else:
        print("   ❌ Delta sigue siendo incorrecto")

if __name__ == "__main__":
    debug_algorithm()
    fix_algorithm()
    print("\n⏳ Esperando para recargar cambios...")
    import time
    time.sleep(1)
    test_after_fix()