# === test_trajectory_real.py ===
# 🧪 Test con la estructura REAL del engine

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

def test_real_trajectory():
    """Test usando la estructura real descubierta"""
    print("\n🧪 TEST REAL: Movimiento de trayectorias")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
    print("✅ Engine creado")
    
    # Crear macro - retorna string con el nombre generado
    macro_name = engine.create_macro("test", source_count=3)
    print(f"✅ Macro creado: '{macro_name}'")
    
    # Los macros están en _macros (con guión bajo)
    if hasattr(engine, '_macros') and macro_name in engine._macros:
        macro = engine._macros[macro_name]
        source_ids = list(macro.source_ids) if hasattr(macro, 'source_ids') else [0, 1, 2]
        print(f"✅ Macro encontrado con fuentes: {source_ids}")
    else:
        # Fallback si no encontramos el macro
        source_ids = [0, 1, 2]
        print(f"⚠️ Usando IDs por defecto: {source_ids}")
    
    # Configurar trayectorias individuales
    print("\n🔧 Configurando trayectorias...")
    for i, sid in enumerate(source_ids):
        try:
            # Usar el método correcto con parámetros mínimos
            engine.set_individual_trajectory(
                sid,  # source_id directamente
                shape="circle",
                mode="fix"
            )
            print(f"   ✅ Fuente {sid}: trayectoria circular configurada")
        except Exception as e:
            print(f"   ❌ Error configurando fuente {sid}: {e}")
    
    # Capturar posiciones iniciales
    print("\n📍 Posiciones iniciales:")
    initial_positions = {}
    for sid in source_ids:
        if sid < len(engine._positions):
            initial_positions[sid] = engine._positions[sid].copy()
            print(f"   Fuente {sid}: {initial_positions[sid]}")
    
    # Verificar motion_states antes de update
    print("\n🔍 Estado de motion_states antes de update:")
    if hasattr(engine, 'motion_states'):
        for sid in source_ids:
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                print(f"   Fuente {sid}: {type(motion).__name__}")
                
                # Ver si tiene componentes activos
                if hasattr(motion, 'active_components'):
                    components = list(motion.active_components.keys())
                    print(f"      Componentes: {components}")
                    
                    # Verificar trayectoria individual
                    if 'individual_trajectory' in motion.active_components:
                        traj = motion.active_components['individual_trajectory']
                        enabled = getattr(traj, 'enabled', False)
                        speed = getattr(traj, 'movement_speed', 0)
                        print(f"      Trayectoria: enabled={enabled}, speed={speed}")
    
    # Ejecutar updates - el método update() no tiene parámetros
    print("\n🔄 Ejecutando 20 updates...")
    for i in range(20):
        engine.update()  # Sin parámetros!
        time.sleep(0.05)  # Pequeña pausa para simular tiempo real
        
        if i == 0:
            # Debug después del primer update
            print("\n🔍 Debug después del primer update:")
            sid = source_ids[0]
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                if hasattr(motion, 'state'):
                    phase = getattr(motion.state, 'position_on_trajectory', 0)
                    print(f"   Fase de fuente {sid}: {phase}")
    
    # Verificar posiciones finales
    print("\n📊 RESULTADOS:")
    print("-" * 40)
    
    all_moved = True
    for sid in source_ids:
        if sid < len(engine._positions):
            current_pos = engine._positions[sid]
            initial_pos = initial_positions[sid]
            
            # Calcular distancia
            distance = np.linalg.norm(current_pos - initial_pos)
            moved = distance > 0.01
            
            print(f"Fuente {sid}:")
            print(f"  Inicial: {initial_pos}")
            print(f"  Final:   {current_pos}")
            print(f"  Distancia: {distance:.4f} {'✅ MOVIDA' if moved else '❌ NO MOVIDA'}")
            
            if not moved:
                all_moved = False
    
    # Test manual de update_with_deltas
    if not all_moved:
        print("\n🧪 TEST MANUAL DE DELTAS:")
        print("-" * 40)
        
        sid = source_ids[0]
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            
            # Probar update_with_deltas directamente
            try:
                current_time = time.time()
                dt = 0.1
                deltas = motion.update_with_deltas(current_time, dt)
                print(f"✅ update_with_deltas retornó: {deltas}")
                
                # Ver si los deltas tienen posición
                if deltas:
                    if isinstance(deltas, list):
                        for d in deltas:
                            if hasattr(d, 'position'):
                                print(f"   Delta position: {d.position}")
                    elif hasattr(deltas, 'position'):
                        print(f"   Delta position: {deltas.position}")
            except Exception as e:
                print(f"❌ Error en update_with_deltas: {e}")
    
    # Resultado final
    print("\n" + "=" * 60)
    if all_moved:
        print("✅ ¡ÉXITO! Las trayectorias se están moviendo")
    else:
        print("❌ Las trayectorias NO se están moviendo")
        print("\n💡 El problema parece estar en el sistema de deltas")
        print("   El update() usa deltas pero algo no está funcionando")
    
    return all_moved

if __name__ == "__main__":
    test_real_trajectory()