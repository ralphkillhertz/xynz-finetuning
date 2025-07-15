# === inspect_manual_individual_rotation.py ===
# 🔍 Inspeccionar implementación actual de ManualIndividualRotation
# ⚡ Ver qué tiene y qué le falta

import inspect
from trajectory_hub.core.motion_components import ManualIndividualRotation, IndividualRotation
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

def inspect_manual_rotation():
    """Inspeccionar la implementación actual"""
    
    print("🔍 INSPECCIÓN: ManualIndividualRotation")
    print("=" * 60)
    
    # 1. Crear instancia y ver qué tiene
    print("\n1️⃣ CREANDO INSTANCIA:")
    print("-" * 40)
    
    try:
        manual_rot = ManualIndividualRotation()
        print("   ✅ Instancia creada sin parámetros")
        
        # Ver atributos
        print("\n   Atributos:")
        for attr in dir(manual_rot):
            if not attr.startswith('_'):
                try:
                    value = getattr(manual_rot, attr)
                    if not callable(value):
                        print(f"   - {attr}: {value}")
                except:
                    pass
        
        # Ver métodos
        print("\n   Métodos:")
        for method in dir(manual_rot):
            if not method.startswith('_') and callable(getattr(manual_rot, method)):
                print(f"   - {method}")
                
        # Verificar métodos críticos
        print("\n   Métodos críticos:")
        print(f"   - calculate_delta: {'✅ SÍ' if hasattr(manual_rot, 'calculate_delta') else '❌ NO'}")
        print(f"   - update: {'✅ SÍ' if hasattr(manual_rot, 'update') else '❌ NO'}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Ver el código fuente si es posible
    print("\n2️⃣ CÓDIGO FUENTE:")
    print("-" * 40)
    
    try:
        source = inspect.getsource(ManualIndividualRotation)
        lines = source.split('\n')[:20]  # Primeras 20 líneas
        for i, line in enumerate(lines):
            print(f"   {i+1}: {line}")
    except:
        print("   ❌ No se puede obtener el código fuente")
    
    # 3. Probar el método del engine
    print("\n3️⃣ PROBANDO set_manual_individual_rotation:")
    print("-" * 40)
    
    engine = EnhancedTrajectoryEngine(max_sources=2, enable_modulator=False)
    sid = 0
    engine.create_source(sid)
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])
    
    try:
        result = engine.set_manual_individual_rotation(sid, yaw=np.pi/2)
        print(f"   Resultado: {result}")
        
        # Ver qué se creó
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            print(f"   Componentes activos: {list(motion.active_components.keys())}")
            
            if 'manual_individual_rotation' in motion.active_components:
                component = motion.active_components['manual_individual_rotation']
                print(f"   Tipo del componente: {type(component).__name__}")
                
                # Ver atributos del componente
                print("\n   Atributos del componente:")
                for attr in ['target_yaw', 'target_pitch', 'target_roll', 'interpolation_speed']:
                    if hasattr(component, attr):
                        print(f"   - {attr}: {getattr(component, attr)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Conclusión
    print("\n" + "=" * 60)
    print("📊 DIAGNÓSTICO:")
    print("   ManualIndividualRotation existe pero:")
    print("   - Constructor no acepta parámetros de rotación")
    print("   - Probablemente le faltan atributos necesarios")
    print("   - El método del engine intenta usarla pero puede fallar")
    
    print("\n💡 SOLUCIÓN:")
    print("   Necesitamos completar la implementación de ManualIndividualRotation")

if __name__ == "__main__":
    inspect_manual_rotation()