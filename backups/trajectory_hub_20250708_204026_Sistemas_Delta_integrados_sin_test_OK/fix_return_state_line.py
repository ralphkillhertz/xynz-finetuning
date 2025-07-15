# === fix_return_state_line.py ===
# 🔧 Corregir línea 1294 que tiene return sin state
# ⚡ Fix específico para el return vacío

import shutil
from datetime import datetime

print("🔧 CORRIGIENDO LÍNEA 1294 (return vacío)")
print("=" * 60)

try:
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        lines = f.readlines()
    
    # Verificar línea 1293-1295
    print("📄 Líneas problemáticas:")
    print("-" * 60)
    for i in range(1292, 1296):
        if i < len(lines):
            print(f"{i+1:4d}: {lines[i].rstrip()}")
    print("-" * 60)
    
    # Corregir línea 1294 (índice 1293)
    if lines[1293].strip() == 'return':
        print("\n⚠️ Línea 1294 tiene 'return' vacío, corrigiendo...")
        
        # Backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f'trajectory_hub/core/motion_components.py.backup_{timestamp}'
        shutil.copy2('trajectory_hub/core/motion_components.py', backup_path)
        print(f"💾 Backup: {backup_path}")
        
        # Cambiar la línea
        indent = len(lines[1293]) - len(lines[1293].lstrip())
        lines[1293] = ' ' * indent + 'return state\n'
        
        # Guardar
        with open('trajectory_hub/core/motion_components.py', 'w') as f:
            f.writelines(lines)
        
        print("✅ Cambiado 'return' por 'return state'")
    
    # Test rápido
    print("\n🎯 TEST RÁPIDO:")
    print("-" * 60)
    
    from trajectory_hub.core.motion_components import ManualIndividualRotation, MotionState
    import numpy as np
    import math
    
    # Crear componente
    component = ManualIndividualRotation(center=np.array([0.0, 0.0, 0.0]))
    component.target_yaw = math.pi/2
    component.interpolation_speed = 0.1
    component.enabled = True
    
    # Crear estado
    state = MotionState()
    state.position = np.array([3.0, 0.0, 0.0])
    
    # Test update
    print("1️⃣ Llamando update()...")
    result = component.update(0.0, 0.05, state)
    
    if result is None:
        print("   ❌ update() retornó None")
    else:
        print("   ✅ update() retornó state")
        print(f"   current_yaw: {math.degrees(component.current_yaw):.1f}°")
    
    # Test calculate_delta
    if result:
        print("\n2️⃣ Llamando calculate_delta()...")
        delta = component.calculate_delta(result, 0.0, 0.05)
        
        if delta is None:
            print("   ⚠️ calculate_delta retornó None")
        else:
            print(f"   ✅ Delta: {delta.position}")
            print(f"   Magnitud: {np.linalg.norm(delta.position):.6f}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Fix completado")