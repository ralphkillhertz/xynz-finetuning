# === diagnose_rotation_simple.py ===
# 🔍 Diagnóstico: Test simple de MacroRotation
# ⚡ Ver si el componente funciona aisladamente

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_macro_rotation_isolated():
    """Probar MacroRotation directamente"""
    
    print("🔧 Test directo de MacroRotation")
    print("=" * 60)
    
    # Importar las clases necesarias
    try:
        from trajectory_hub.core.motion_components import MacroRotation, MotionState, MotionDelta
        print("✅ Imports exitosos")
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return
    
    # Crear MacroRotation
    try:
        rotation = MacroRotation()
        print("✅ MacroRotation creado")
        print(f"   - Tipo: {type(rotation).__name__}")
        print(f"   - enabled: {rotation.enabled}")
        print(f"   - tiene calculate_delta: {hasattr(rotation, 'calculate_delta')}")
    except Exception as e:
        print(f"❌ Error creando MacroRotation: {e}")
        return
    
    # Configurar rotación
    try:
        rotation.enabled = True
        rotation.speed_y = 1.0  # 1 rad/s en Y
        rotation.center = np.array([0.0, 0.0, 0.0])
        print("\n✅ Configuración aplicada")
        print(f"   - enabled: {rotation.enabled}")
        print(f"   - speed_y: {rotation.speed_y}")
    except Exception as e:
        print(f"❌ Error configurando: {e}")
        return
    
    # Probar calculate_delta
    try:
        state = MotionState()
        state.position = np.array([10.0, 0.0, 0.0])
        print(f"\n📍 Estado inicial: {state.position}")
        
        # Llamar calculate_delta
        delta = rotation.calculate_delta(state, current_time=0.0, dt=0.1)
        print(f"✅ calculate_delta ejecutado")
        
        if delta:
            print(f"   - Delta tipo: {type(delta).__name__}")
            if hasattr(delta, 'position'):
                print(f"   - Delta position: {delta.position}")
                print(f"   - Magnitud: {np.linalg.norm(delta.position):.6f}")
            else:
                print("   - Delta sin atributo position")
        else:
            print("   - Delta es None o vacío")
            
    except Exception as e:
        print(f"❌ Error en calculate_delta: {e}")
        import traceback
        traceback.print_exc()
    
    # Test del engine simplificado
    print("\n" + "="*60)
    print("🔧 Test con EnhancedTrajectoryEngine")
    
    try:
        from trajectory_hub import EnhancedTrajectoryEngine
        
        # Intentar con diferentes constructores
        engine = None
        for args in [
            {"max_sources": 10, "fps": 60},
            {"max_sources": 10, "update_rate": 60},
            {"n_sources": 10, "update_rate": 60},
            {}
        ]:
            try:
                engine = EnhancedTrajectoryEngine(**args)
                print(f"✅ Engine creado con: {args}")
                break
            except:
                continue
        
        if engine:
            # Ver métodos disponibles
            print("\n📋 Métodos de rotación disponibles:")
            for method in dir(engine):
                if 'rotation' in method.lower():
                    print(f"   - {method}")
    
    except Exception as e:
        print(f"❌ Error con engine: {e}")

if __name__ == "__main__":
    test_macro_rotation_isolated()