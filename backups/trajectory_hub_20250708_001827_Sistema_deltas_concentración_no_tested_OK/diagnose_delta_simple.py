# === diagnose_delta_simple.py ===
# 🔧 Diagnóstico simple y directo
# ⚡ Sin parámetros problemáticos

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

def simple_diagnosis():
    """Diagnóstico simple del flujo de deltas"""
    
    print("🔍 DIAGNÓSTICO SIMPLE DE DELTAS")
    print("="*60)
    
    # 1. Crear engine sin parámetros problemáticos
    print("\n1️⃣ Creando engine...")
    try:
        engine = EnhancedTrajectoryEngine()
        print("   ✅ Engine creado sin parámetros")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        # Intentar con parámetros mínimos
        try:
            engine = EnhancedTrajectoryEngine(max_sources=10)
            print("   ✅ Engine creado con max_sources=10")
        except:
            engine = EnhancedTrajectoryEngine(n_sources=10)
            print("   ✅ Engine creado con n_sources=10")
    
    # 2. Crear macro
    print("\n2️⃣ Creando macro...")
    source_ids = engine.create_macro("test", count=3, formation="circle", radius=10.0)
    print(f"   ✅ Macro creado con {len(source_ids)} fuentes")
    
    # 3. Mostrar posiciones iniciales
    print("\n3️⃣ Posiciones iniciales:")
    for sid in source_ids:
        pos = engine._positions[sid]
        print(f"   Source {sid}: {pos}")
    
    # 4. Aplicar concentración
    print("\n4️⃣ Aplicando concentración...")
    engine.apply_concentration("test", factor=0.8)
    print("   ✅ Concentración aplicada")
    
    # 5. Guardar posiciones
    pos_before = {}
    for sid in source_ids:
        pos_before[sid] = engine._positions[sid].copy()
    
    # 6. Actualizar - probar diferentes métodos
    print("\n5️⃣ Buscando método de actualización...")
    updated = False
    
    # Probar update(dt)
    if hasattr(engine, 'update'):
        print("   Probando engine.update(0.016)...")
        try:
            engine.update(0.016)
            updated = True
            print("   ✅ update() ejecutado")
        except Exception as e:
            print(f"   ❌ Error en update: {e}")
    
    # Probar step()
    if not updated and hasattr(engine, 'step'):
        print("   Probando engine.step()...")
        try:
            engine.step()
            updated = True
            print("   ✅ step() ejecutado")
        except Exception as e:
            print(f"   ❌ Error en step: {e}")
    
    # 7. Verificar cambios
    print("\n6️⃣ Verificando movimiento:")
    total_change = 0
    for sid in source_ids:
        pos_after = engine._positions[sid]
        change = np.linalg.norm(pos_after - pos_before[sid])
        total_change += change
        if change > 0.001:
            print(f"   Source {sid}: movió {change:.4f} unidades ✅")
        else:
            print(f"   Source {sid}: NO se movió ❌")
    
    # 8. Diagnóstico final
    print("\n7️⃣ DIAGNÓSTICO FINAL:")
    if total_change > 0.001:
        print("   ✅ ¡LAS FUENTES SE ESTÁN MOVIENDO!")
        print(f"   Movimiento total: {total_change:.4f}")
    else:
        print("   ❌ Las fuentes NO se mueven")
        print("\n   🔍 Verificando componentes...")
        
        # Verificar que los componentes existen
        if hasattr(engine, 'motion_states'):
            motion = engine.motion_states.get(source_ids[0])
            if motion:
                if hasattr(motion, 'active_components'):
                    comps = motion.active_components
                    print(f"   Componentes activos: {list(comps.keys())}")
                    
                    # Verificar concentración
                    if 'concentration' in comps:
                        comp = comps['concentration']
                        print(f"   ConcentrationComponent:")
                        print(f"     - enabled: {getattr(comp, 'enabled', '?')}")
                        print(f"     - factor: {getattr(comp, 'concentration_factor', '?')}")
                        
                        # Test manual de calculate_delta
                        if hasattr(comp, 'calculate_delta'):
                            print("\n   🧪 Test manual de calculate_delta:")
                            state = motion.motion_state
                            delta = comp.calculate_delta(state, 0.0, 0.016)
                            print(f"     Delta: {delta}")
                            if hasattr(delta, 'position'):
                                print(f"     Delta.position: {delta.position}")

if __name__ == "__main__":
    simple_diagnosis()