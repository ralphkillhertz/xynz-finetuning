# === debug_array_error_deep.py ===
# 🔍 Debug profundo del error array ambiguous
# ⚡ Encontrar la línea exacta del problema
# 🎯 Impacto: DIAGNÓSTICO

import traceback
import sys
import numpy as np

# Monkey patch para capturar el error exacto
original_exception_hook = sys.excepthook

def custom_exception_hook(exc_type, exc_value, exc_traceback):
    if "ambiguous" in str(exc_value):
        print("\n🚨 ERROR ARRAY AMBIGUOUS CAPTURADO!")
        print("=" * 60)
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print("=" * 60)
    original_exception_hook(exc_type, exc_value, exc_traceback)

sys.excepthook = custom_exception_hook

# Test directo del engine
print("🔍 Debug profundo del error array ambiguous")
print("=" * 50)

try:
    from trajectory_hub import EnhancedTrajectoryEngine
    
    # Crear engine con debug activado
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=1)
    
    # Crear fuentes
    for i in range(4):
        engine.create_source(f"test_{i}")
    
    # Crear macro
    engine.create_macro("test_macro", [0, 1, 2, 3])
    
    # Aplicar rotación con debug
    print("\n🔄 Aplicando rotación con debug...")
    
    # Interceptar el método update_with_deltas para debug
    original_update = engine.motion_states[0].update_with_deltas
    
    def debug_update(current_time, dt):
        print(f"\n📍 update_with_deltas llamado: time={current_time}, dt={dt}")
        print(f"   active_components: {list(engine.motion_states[0].active_components.keys())}")
        
        # Llamar a cada componente individualmente para aislar el error
        for comp_name, component in engine.motion_states[0].active_components.items():
            print(f"\n   🔍 Procesando {comp_name}...")
            try:
                if hasattr(component, 'calculate_delta'):
                    delta = component.calculate_delta(current_time, dt, engine.motion_states[0])
                    print(f"      ✅ Delta calculado: {delta}")
            except Exception as e:
                print(f"      ❌ ERROR en {comp_name}: {e}")
                if "ambiguous" in str(e):
                    # Inspeccionar el componente
                    print(f"      📋 Atributos del componente:")
                    for attr in ['enabled', 'speed_x', 'speed_y', 'speed_z']:
                        if hasattr(component, attr):
                            value = getattr(component, attr)
                            print(f"         {attr}: {value} (tipo: {type(value)})")
                raise
        
        return original_update(current_time, dt)
    
    engine.motion_states[0].update_with_deltas = debug_update
    
    # Configurar rotación
    engine.set_macro_rotation("test_macro", speed_x=0.0, speed_y=1.0, speed_z=0.0)
    
    # Un solo update para capturar el error
    print("\n⏱️ Ejecutando update()...")
    engine.update()
    
except Exception as e:
    print(f"\n❌ Error capturado: {e}")
    print(f"   Tipo: {type(e)}")
    
    # Si es array ambiguous, hacer más debug
    if "ambiguous" in str(e):
        print("\n🔍 Debug adicional del error:")
        
        # Test directo de comparaciones
        print("\n📋 Test de comparaciones:")
        test_values = [
            ("float", 1.0),
            ("int", 1),
            ("array 1D", np.array([1.0])),
            ("array 2D", np.array([[1.0]])),
            ("list", [1.0])
        ]
        
        for name, value in test_values:
            try:
                result = abs(value) > 0.001
                print(f"   {name}: abs({value}) > 0.001 = {result} ✅")
            except Exception as test_e:
                print(f"   {name}: abs({value}) > 0.001 = ERROR: {test_e} ❌")
                
            # Test con 'or'
            try:
                result = abs(value) > 0.001 or False
                print(f"   {name}: con 'or' = {result} ✅")
            except Exception as test_e:
                print(f"   {name}: con 'or' = ERROR ❌")

print("\n✅ Debug completado")