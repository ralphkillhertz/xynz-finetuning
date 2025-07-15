# === diagnose_delta_flow_fixed.py ===
# 🔧 Diagnóstico corregido con max_sources
# ⚡ Rastrea TODO el flujo de deltas

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent, MotionDelta

def diagnose_complete_flow():
    """Diagnóstico exhaustivo del flujo de deltas"""
    
    print("🔍 DIAGNÓSTICO COMPLETO DEL FLUJO DE DELTAS")
    print("="*60)
    
    # 1. Crear engine y macro - CORREGIDO: max_sources
    engine = EnhancedTrajectoryEngine(max_sources=5, update_rate=60, enable_modulator=False)
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
    
    # 5. Test update() del engine
    print("\n4️⃣ Test de engine.update():")
    
    # Capturar posiciones antes
    pos_before = {}
    for sid in source_ids:
        pos_before[sid] = engine._positions[sid].copy()
    
    # Buscar método de actualización
    update_method = None
    for method in ['update', 'step', 'tick', 'process']:
        if hasattr(engine, method):
            update_method = method
            print(f"   ✅ Encontrado método: {method}")
            break
    
    if update_method:
        # Llamar al método
        method_func = getattr(engine, update_method)
        if update_method == 'update':
            # update necesita dt
            result = method_func(0.016)
        else:
            result = method_func()
        print(f"   ✅ {update_method}() ejecutado")
    
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
        
        # Debug del método update
        print("\n6️⃣ Debug del método update:")
        if hasattr(engine, 'update'):
            import inspect
            try:
                code = inspect.getsource(engine.update)
                print(f"   Longitud del código: {len(code)} caracteres")
                
                # Buscar líneas clave
                if 'motion_states' in code:
                    print("   ✅ Contiene 'motion_states'")
                else:
                    print("   ❌ NO contiene 'motion_states'")
                    
                if 'update_with_deltas' in code:
                    print("   ✅ Contiene 'update_with_deltas'")
                else:
                    print("   ❌ NO contiene 'update_with_deltas'")
                    
                if 'calculate_delta' in code:
                    print("   ✅ Contiene 'calculate_delta'")
                else:
                    print("   ❌ NO contiene 'calculate_delta'")
                    
                if '_positions' in code:
                    print("   ✅ Contiene '_positions'")
                else:
                    print("   ❌ NO contiene '_positions'")
                    
                # Mostrar líneas con delta
                lines = code.split('\n')
                delta_lines = []
                for i, line in enumerate(lines):
                    if 'delta' in line.lower() and not line.strip().startswith('#'):
                        delta_lines.append((i, line.strip()))
                
                if delta_lines:
                    print(f"\n   Líneas con 'delta' ({len(delta_lines)} encontradas):")
                    for i, line in delta_lines[:5]:  # Mostrar máx 5
                        print(f"     L{i}: {line}")
            except:
                print("   ❌ No se pudo obtener el código fuente")

if __name__ == "__main__":
    diagnose_complete_flow()