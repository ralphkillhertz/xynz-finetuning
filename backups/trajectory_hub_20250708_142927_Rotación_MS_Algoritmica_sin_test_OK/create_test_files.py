# === create_test_files.py ===
# 🔧 Script para crear los archivos de test
# ⚡ Ejecutar este primero

# Crear test_rotation_api_correct.py
with open("test_rotation_api_correct.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""Test con API 100% correcta"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 Test MacroRotation - API Correcta")
print("=" * 50)

try:
    # 1. Crear engine
    engine = EnhancedTrajectoryEngine()
    print("✅ Engine creado")
    
    # 2. Crear macro con source_count (NO lista de IDs)
    macro_name = engine.create_macro(
        name="rotation_test",
        source_count=4,  # Número de fuentes a crear
        formation="square",
        spacing=4.0
    )
    print(f"✅ Macro creado: {macro_name}")
    
    # Verificar qué fuentes se crearon
    if hasattr(engine, '_macros') and macro_name in engine._macros:
        macro = engine._macros[macro_name]
        print(f"   Fuentes en el macro: {list(macro.source_ids) if hasattr(macro, 'source_ids') else 'desconocido'}")
    
    # 3. Mostrar posiciones iniciales
    print("\\n📍 Posiciones iniciales:")
    positions_found = 0
    for i in range(10):  # Buscar en los primeros 10 slots
        if np.any(engine._positions[i] != 0):
            pos = engine._positions[i]
            print(f"  Fuente {i}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")
            positions_found += 1
            if positions_found >= 4:
                break
    
    # 4. Aplicar rotación
    print("\\n🔄 Aplicando rotación...")
    success = engine.set_macro_rotation(
        macro_name=macro_name,  # Usar el nombre retornado
        speed_x=0.0,
        speed_y=1.0,
        speed_z=0.0
    )
    print(f"   Resultado: {success}")
    
    # 5. Debug del estado
    if success and hasattr(engine, 'motion_states'):
        print("\\n🔍 Debug - Estados de movimiento:")
        count = 0
        for sid, motion in engine.motion_states.items():
            if 'macro_rotation' in motion.active_components:
                rot = motion.active_components['macro_rotation']
                print(f"  Fuente {sid}: MacroRotation {'activa' if rot.enabled else 'inactiva'}")
                if rot.enabled:
                    print(f"    Speed Y: {rot.speed_y}")
                    count += 1
                if count >= 4:
                    break
        print(f"  Total con rotación activa: {count}")
    
    # 6. Simular
    print("\\n⏱️ Simulando 30 frames...")
    for i in range(30):
        engine.update()
        if i % 10 == 0:
            # Mostrar posición de la primera fuente con datos
            for j in range(10):
                if np.any(engine._positions[j] != 0):
                    pos = engine._positions[j]
                    print(f"  Frame {i}: Fuente {j} en [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")
                    break
    
    # 7. Verificar movimiento
    print("\\n📊 Resultado final:")
    movement_detected = False
    
    # Buscar fuentes que se movieron
    for i in range(10):
        if i in engine.motion_states:
            # Comparar con snapshot inicial si lo tenemos
            pos = engine._positions[i]
            if np.any(pos != 0):  # Si tiene posición
                # Simple check: si Z no es 0, probablemente rotó
                if abs(pos[2]) > 0.1:
                    movement_detected = True
                    print(f"  ✅ Fuente {i} se movió: Z = {pos[2]:.3f}")
    
    if movement_detected:
        print("\\n✅ ¡ÉXITO! Rotación detectada")
    else:
        print("\\n❌ No se detectó movimiento")
        
except Exception as e:
    print(f"\\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
''')

# Crear debug_create_macro.py
with open("debug_create_macro.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""Debug de create_macro"""

from trajectory_hub import EnhancedTrajectoryEngine

engine = EnhancedTrajectoryEngine()

# Probar create_macro
print("🔍 Probando create_macro...")
result = engine.create_macro("test_macro", source_count=2)
print(f"Resultado: {result}")
print(f"Tipo: {type(result)}")

# Ver qué se creó
if hasattr(engine, '_macros'):
    print(f"\\nMacros existentes: {list(engine._macros.keys())}")
    if result in engine._macros:
        macro = engine._macros[result]
        print(f"Macro '{result}':")
        print(f"  source_ids: {macro.source_ids if hasattr(macro, 'source_ids') else 'no tiene'}")
        print(f"  tipo: {type(macro)}")

# Ver motion_states
if hasattr(engine, 'motion_states'):
    print(f"\\nMotion states: {list(engine.motion_states.keys())}")

# Ver posiciones
print(f"\\nPosiciones no-cero:")
for i in range(10):
    if engine._positions[i].any():
        print(f"  Posición {i}: {engine._positions[i]}")
''')

print("✅ Archivos creados:")
print("  - test_rotation_api_correct.py")
print("  - debug_create_macro.py")