# === diagnose_delta_flow_complete.py ===
# 🔧 Diagnóstico COMPLETO del flujo de deltas
# ⚡ Rastrea TODO el flujo desde calculate_delta hasta _positions

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent, MotionDelta

def diagnose_complete_flow():
    """Diagnóstico exhaustivo del flujo de deltas"""
    
    print("🔍 DIAGNÓSTICO COMPLETO DEL FLUJO DE DELTAS")
    print("="*60)
    
    # 1. Crear engine y macro
    engine = EnhancedTrajectoryEngine(n_sources=5, update_rate=60, enable_modulator=False)
    source_ids = engine.create_macro("test", count=3, formation="circle", radius=10.0)
    
    print("\n1️⃣ Estado inicial:")
    for sid in source_ids:
        pos = engine._positions[sid]
        print(f"   Source {sid}: {pos}")
    
    # 2. Aplicar concentración
    engine.apply_concentration("test", factor=0.8)
    
    # 3. Test directo de ConcentrationComponent
    print("\n2️⃣ Test directo de ConcentrationComponent:")
    motion = engine.motion_states[source_ids[0]]
    comp = motion.active_components.get('concentration')
    if comp:
        print(f"   ✅ Component encontrado")
        print(f"   Factor: {comp.concentration_factor}")
        print(f"   Centro: {comp.center}")
        
        # Test calculate_delta directamente
        state = motion.motion_state
        delta = comp.calculate_delta(state, 0.0, 0.016)
        print(f"   Delta calculado: {delta}")
        if hasattr(delta, 'position'):
            print(f"   Delta.position: {delta.position}")
    
    # 4. Test update_with_deltas
    print("\n3️⃣ Test de update_with_deltas:")
    deltas = motion.update_with_deltas(0.0, 0.016)
    print(f"   Tipo retornado: {type(deltas)}")
    print(f"   Contenido: {deltas}")
    if isinstance(deltas, list):
        print(f"   Número de deltas: {len(deltas)}")
        for i, d in enumerate(deltas):
            print(f"   Delta {i}: {d}")
            if hasattr(d, 'position'):
                print(f"     - position: {d.position}")
    
    # 5. Test step() del engine
    print("\n4️⃣ Test de engine.step():")
    
    # Capturar posiciones antes
    pos_before = {}
    for sid in source_ids:
        pos_before[sid] = engine._positions[sid].copy()
    
    # Llamar step
    print("   Llamando engine.step()...")
    
    # Verificar si step existe
    if hasattr(engine, 'step'):
        result = engine.step()
        print(f"   ✅ step() ejecutado, retornó: {type(result)}")
    else:
        print("   ❌ engine no tiene método step()")
        
        # Buscar método de actualización
        update_methods = ['update', 'tick', 'process', 'advance']
        for method in update_methods:
            if hasattr(engine, method):
                print(f"   ✅ Encontrado método: {method}")
                break
    
    # Verificar cambios
    print("\n5️⃣ Verificando cambios en posiciones:")
    any_change = False
    for sid in source_ids:
        pos_after = engine._positions[sid]
        change = pos_after - pos_before[sid]
        if np.any(change != 0):
            print(f"   Source {sid}: cambió por {change}")
            any_change = True
        else:
            print(f"   Source {sid}: SIN CAMBIO ❌")
    
    if not any_change:
        print("\n❌ NINGUNA fuente se movió")
        
        # Debug adicional
        print("\n6️⃣ Debug adicional:")
        
        # Verificar si el engine tiene código de deltas
        if hasattr(engine, 'step'):
            import inspect
            code = inspect.getsource(engine.step)
            if 'delta' in code.lower():
                print("   ✅ step() contiene código de deltas")
                # Mostrar las líneas relevantes
                lines = code.split('\n')
                for i, line in enumerate(lines):
                    if 'delta' in line.lower():
                        print(f"     Línea {i}: {line.strip()}")
            else:
                print("   ❌ step() NO contiene código de deltas")

if __name__ == "__main__":
    diagnose_complete_flow()