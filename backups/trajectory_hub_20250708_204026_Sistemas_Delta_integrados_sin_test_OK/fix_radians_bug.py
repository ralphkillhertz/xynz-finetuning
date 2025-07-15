# === fix_radians_bug.py ===
# 🔧 Corregir conversión doble de radianes
# ⚡ NO aplicar math.radians() a valores ya en radianes

import shutil
from datetime import datetime

print("🔧 CORRIGIENDO BUG DE CONVERSIÓN DOBLE DE RADIANES")
print("=" * 60)

try:
    # Leer archivo
    with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
        content = f.read()
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f'trajectory_hub/core/enhanced_trajectory_engine.py.backup_{timestamp}'
    shutil.copy2('trajectory_hub/core/enhanced_trajectory_engine.py', backup_path)
    print(f"💾 Backup: {backup_path}")
    
    # Buscar y reemplazar la línea problemática
    old_line = "rotation.set_target_rotation(math.radians(yaw), math.radians(pitch), math.radians(roll), math.radians(interpolation_speed))"
    new_line = "rotation.set_target_rotation(yaw, pitch, roll, interpolation_speed)"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("\n✅ Línea problemática encontrada y corregida:")
        print(f"   ❌ ANTES: {old_line}")
        print(f"   ✅ AHORA: {new_line}")
        
        # También en la creación del componente
        old_create = "component.set_target_rotation(math.radians(yaw), math.radians(pitch), math.radians(roll), math.radians(interpolation_speed))"
        new_create = "component.set_target_rotation(yaw, pitch, roll, interpolation_speed)"
        
        if old_create in content:
            content = content.replace(old_create, new_create)
            print("\n✅ También corregido en creación de componente")
        
        # Guardar
        with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'w') as f:
            f.write(content)
        
        print("\n✅ Archivo guardado")
    else:
        print("\n⚠️ No se encontró la línea exacta, buscando variaciones...")
        
        # Buscar variaciones
        import re
        pattern = r'rotation\.set_target_rotation\s*\([^)]+\)'
        matches = re.findall(pattern, content)
        
        if matches:
            print("\n📋 Llamadas encontradas:")
            for match in matches:
                print(f"   - {match}")
                if 'math.radians' in match:
                    print("     ⚠️ Esta tiene math.radians")
    
    # Test rápido
    print("\n🎯 TEST RÁPIDO:")
    print("-" * 60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    import numpy as np
    import math
    
    engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
    sid = engine.create_source(0)
    engine._positions[0] = np.array([3.0, 0.0, 0.0])
    
    # Configurar rotación 90°
    success = engine.set_manual_individual_rotation(
        0,
        yaw=math.pi/2,  # 90 grados en radianes
        pitch=0.0,
        roll=0.0,
        interpolation_speed=0.5
    )
    
    if success and 0 in engine.motion_states:
        comp = engine.motion_states[0].active_components.get('manual_individual_rotation')
        if comp:
            print(f"✅ Target configurado: {math.degrees(comp.target_yaw):.1f}°")
            
            if abs(comp.target_yaw - math.pi/2) < 0.001:
                print("✅ ¡CORRECTO! Ahora sí es 90°")
            else:
                print(f"❌ Incorrecto: {comp.target_yaw:.6f} rad")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Corrección completada")