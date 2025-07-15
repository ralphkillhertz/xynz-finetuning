# === test_rotation_minimal.py ===
# 🔧 Test minimal para rotación MS
# ⚡ Identificar error exacto
# 🎯 Impacto: DEBUG

import numpy as np
import traceback

print("🔍 Test minimal de rotación MS")
print("=" * 50)

try:
    # Import con manejo de error
    try:
        from trajectory_hub.core.motion_components import MacroRotation, MotionState
        print("✅ Imports exitosos")
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        exit(1)
    
    # Crear estado de prueba
    state = MotionState()
    state.position = np.array([2.0, 2.0, 0.0])
    state.source_id = 0
    print("✅ MotionState creado")
    
    # Test 1: Crear MacroRotation directamente
    print("\n📋 Test 1: Crear MacroRotation")
    try:
        rotation = MacroRotation()
        print("✅ MacroRotation creado")
    except Exception as e:
        print(f"❌ Error creando MacroRotation: {e}")
        traceback.print_exc()
        exit(1)
    
    # Test 2: Configurar velocidades
    print("\n📋 Test 2: Configurar velocidades")
    try:
        # Probar con diferentes tipos de valores
        test_values = [
            (1.0, 0.0, 0.0, "floats"),
            (np.float64(1.0), np.float64(0.0), np.float64(0.0), "numpy floats"),
            (1, 0, 0, "ints"),
        ]
        
        for sx, sy, sz, desc in test_values:
            print(f"\n   Probando con {desc}: ({sx}, {sy}, {sz})")
            try:
                rotation.set_rotation_speeds(sx, sy, sz)
                print(f"   ✅ OK - enabled={rotation.enabled}")
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                if "ambiguous" in str(e):
                    print("   🚨 ERROR ARRAY AMBIGUOUS ENCONTRADO!")
                    # Debug detallado
                    print(f"      speed_x tipo: {type(rotation.speed_x)}")
                    print(f"      speed_y tipo: {type(rotation.speed_y)}")
                    print(f"      speed_z tipo: {type(rotation.speed_z)}")
    except Exception as e:
        print(f"❌ Error en test de velocidades: {e}")
        traceback.print_exc()
    
    # Test 3: calculate_delta
    print("\n📋 Test 3: calculate_delta")
    try:
        rotation.enabled = True
        rotation.speed_x = 0.0
        rotation.speed_y = 1.0
        rotation.speed_z = 0.0
        
        delta = rotation.calculate_delta(0.0, 0.016, state)
        print(f"✅ Delta calculado: position={delta.position}")
    except Exception as e:
        print(f"❌ Error en calculate_delta: {e}")
        if "ambiguous" in str(e):
            print("🚨 ERROR ARRAY AMBIGUOUS EN calculate_delta!")
        traceback.print_exc()
    
    # Test 4: Simular el flujo completo
    print("\n📋 Test 4: Flujo completo con arrays")
    try:
        # Simular lo que podría pasar en el engine
        # Crear arrays que podrían causar problemas
        speed_array = np.array([0.0, 1.0, 0.0])
        
        print(f"   Intentando set_rotation_speeds con array: {speed_array}")
        try:
            rotation.set_rotation_speeds(speed_array[0], speed_array[1], speed_array[2])
            print("   ✅ OK con elementos del array")
        except Exception as e:
            print(f"   ❌ Error con elementos: {e}")
        
        # Probar pasando el array completo (esto debería fallar)
        try:
            rotation.set_rotation_speeds(speed_array, speed_array, speed_array)
            print("   ⚠️ Aceptó arrays completos (no debería)")
        except Exception as e:
            print(f"   ✅ Rechazó arrays completos correctamente: {e}")
            
    except Exception as e:
        print(f"❌ Error en test de flujo: {e}")
        traceback.print_exc()

except Exception as e:
    print(f"\n❌ Error general: {e}")
    traceback.print_exc()

print("\n✅ Test completado")