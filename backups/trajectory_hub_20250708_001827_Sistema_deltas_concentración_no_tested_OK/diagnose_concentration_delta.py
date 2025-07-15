#!/usr/bin/env python3
"""
🔧 Diagnóstico: Por qué la concentración no mueve las fuentes
⚡ Verificar: Sistema de deltas, motion_states, step()
🎯 Encontrar: El punto de falla
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

def diagnose():
    print("🔍 DIAGNÓSTICO DE CONCENTRACIÓN CON DELTAS\n")
    
    # 1. Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # 2. Verificar estructura
    print("1️⃣ Verificando estructura del engine:")
    print(f"   _positions shape: {engine._positions.shape if hasattr(engine, '_positions') else 'NO EXISTE'}")
    print(f"   motion_states: {'SÍ' if hasattr(engine, 'motion_states') else 'NO'}")
    print(f"   _macros: {'SÍ' if hasattr(engine, '_macros') else 'NO'}")
    
    # 3. Crear macro y verificar
    print("\n2️⃣ Creando macro:")
    source_ids = [0, 1, 2]
    engine.create_macro("test", source_ids)
    
    if hasattr(engine, '_macros'):
        print(f"   Macros existentes: {list(engine._macros.keys())}")
        if 'test' in engine._macros:
            macro = engine._macros['test']
            print(f"   Macro 'test' tiene {len(macro.source_ids)} fuentes: {macro.source_ids}")
    
    # 4. Verificar motion_states
    print("\n3️⃣ Verificando motion_states:")
    if hasattr(engine, 'motion_states'):
        print(f"   motion_states keys: {list(engine.motion_states.keys())}")
        
        # Ver si tienen componente de concentración
        for sid, motion in engine.motion_states.items():
            if sid in source_ids:
                print(f"\n   Source {sid}:")
                print(f"     Clase: {motion.__class__.__name__}")
                if hasattr(motion, 'active_components'):
                    print(f"     Componentes activos: {len(motion.active_components)}")
                    for comp in motion.active_components:
                        print(f"       - {comp.__class__.__name__}")
                if hasattr(motion, 'concentration'):
                    print(f"     Tiene concentración: SÍ")
                    conc = motion.concentration
                    print(f"       - enabled: {conc.enabled if hasattr(conc, 'enabled') else '?'}")
                    print(f"       - factor: {conc.concentration_factor if hasattr(conc, 'concentration_factor') else '?'}")
    
    # 5. Intentar aplicar concentración
    print("\n4️⃣ Aplicando concentración:")
    try:
        # Probar diferentes parámetros
        try:
            engine.set_macro_concentration("test", factor=0.8)
            print("   ✅ set_macro_concentration con factor=0.8")
        except:
            try:
                engine.set_macro_concentration("test", 0.8)
                print("   ✅ set_macro_concentration con 0.8 (sin keyword)")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    except Exception as e:
        print(f"   ❌ Error general: {e}")
    
    # 6. Verificar step()
    print("\n5️⃣ Analizando método step():")
    
    # Ver si step() usa el nuevo sistema
    import inspect
    step_source = inspect.getsource(engine.step)
    
    print("   Verificando contenido de step():")
    if "update_with_deltas" in step_source:
        print("   ✅ step() usa update_with_deltas (sistema de deltas)")
    elif "MotionDelta" in step_source:
        print("   ✅ step() menciona MotionDelta")
    else:
        print("   ❌ step() NO usa sistema de deltas")
    
    if "motion.update(" in step_source:
        print("   ⚠️ step() usa motion.update() antiguo")
    
    # 7. Test manual de delta
    print("\n6️⃣ Test manual del sistema de deltas:")
    
    # Posición inicial
    engine._positions[0] = np.array([10.0, 0.0, 0.0])
    print(f"   Posición inicial source 0: {engine._positions[0]}")
    
    # Un step
    print("   Ejecutando step()...")
    try:
        result = engine.step()
        print(f"   Posición después de step: {engine._positions[0]}")
        
        # Ver si cambió
        if np.allclose(engine._positions[0], [10.0, 0.0, 0.0]):
            print("   ❌ La posición NO cambió")
        else:
            print("   ✅ La posición SÍ cambió")
    except Exception as e:
        print(f"   ❌ Error en step(): {e}")
        import traceback
        traceback.print_exc()
    
    # 8. Verificar ConcentrationComponent
    print("\n7️⃣ Verificando ConcentrationComponent:")
    try:
        from trajectory_hub.core.motion_components import ConcentrationComponent
        
        # Ver si tiene calculate_delta
        if hasattr(ConcentrationComponent, 'calculate_delta'):
            print("   ✅ ConcentrationComponent tiene calculate_delta()")
        else:
            print("   ❌ ConcentrationComponent NO tiene calculate_delta()")
            print("   Métodos disponibles:")
            for method in dir(ConcentrationComponent):
                if not method.startswith('_'):
                    print(f"     - {method}")
    except Exception as e:
        print(f"   ❌ Error importando ConcentrationComponent: {e}")

if __name__ == "__main__":
    diagnose()