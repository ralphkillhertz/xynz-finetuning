import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def diagnose_update():
    """Diagnóstico profundo del método update"""
    print("🔍 DIAGNÓSTICO PROFUNDO DE ENGINE.UPDATE()")
    print("=" * 60)
    
    # 1. Ver el código actual de update()
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar update
    update_start = content.find("def update(self):")
    if update_start == -1:
        print("❌ No se encontró update()")
        return
        
    # Extraer el método
    next_method = content.find("\n    def ", update_start + 1)
    if next_method == -1:
        next_method = content.find("\nclass", update_start)
        if next_method == -1:
            next_method = len(content)
    
    update_method = content[update_start:next_method]
    
    print("📄 Método update() actual:")
    print("-" * 60)
    # Mostrar solo las primeras 30 líneas
    lines = update_method.split('\n')[:30]
    for i, line in enumerate(lines):
        print(f"{i+1:3}: {line}")
    print("-" * 60)
    
    # 2. Test con hooks de debug
    print("\n\n🧪 TEST CON HOOKS DE DEBUG:")
    print("=" * 60)
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        import numpy as np
        
        # Crear sistema
        engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
        sid = engine.create_source(0)
        engine._positions[0] = np.array([3.0, 0.0, 0.0])
        
        # Configurar rotación
        engine.set_manual_individual_rotation(0, yaw=90.0, interpolation_speed=90.0)
        
        # Verificar motion_states
        print("\n1️⃣ Verificando motion_states:")
        print(f"   motion_states keys: {list(engine.motion_states.keys())}")
        
        if 0 in engine.motion_states:
            motion = engine.motion_states[0]
            print(f"   Motion para fuente 0: ✅")
            print(f"   Active components: {list(motion.active_components.keys())}")
            
            # Hook en motion.update
            original_motion_update = motion.update
            motion_update_called = [False]
            
            def debug_motion_update(*args, **kwargs):
                motion_update_called[0] = True
                print("   🔔 motion.update() LLAMADO")
                return original_motion_update(*args, **kwargs)
                
            motion.update = debug_motion_update
            
            # Hook en motion.update_with_deltas
            if hasattr(motion, 'update_with_deltas'):
                original_deltas = motion.update_with_deltas
                deltas_called = [False]
                
                def debug_deltas(*args, **kwargs):
                    deltas_called[0] = True
                    result = original_deltas(*args, **kwargs)
                    print(f"   🔔 update_with_deltas() LLAMADO, retornó: {result}")
                    return result
                    
                motion.update_with_deltas = debug_deltas
            
            # Hook en el componente
            comp = motion.active_components['manual_individual_rotation']
            original_comp_update = comp.update
            comp_update_called = [False]
            
            def debug_comp_update(*args, **kwargs):
                comp_update_called[0] = True
                print("   🔔 component.update() LLAMADO")
                result = original_comp_update(*args, **kwargs)
                print(f"      current_yaw después: {np.degrees(comp.current_yaw):.1f}°")
                return result
                
            comp.update = debug_comp_update
            
            # Hook en calculate_delta
            original_calc = comp.calculate_delta
            calc_called = [False]
            
            def debug_calc(*args, **kwargs):
                calc_called[0] = True
                result = original_calc(*args, **kwargs)
                print(f"   🔔 calculate_delta() LLAMADO")
                if result:
                    print(f"      Delta: {result.position}")
                else:
                    print(f"      Delta: None")
                return result
                
            comp.calculate_delta = debug_calc
        
        # Ejecutar update
        print("\n2️⃣ Ejecutando engine.update()...")
        print("-" * 40)
        
        pos_before = engine._positions[0].copy()
        engine.update()
        pos_after = engine._positions[0].copy()
        
        print("-" * 40)
        print(f"\n3️⃣ Resultados:")
        print(f"   motion.update llamado: {motion_update_called[0]}")
        print(f"   motion.update_with_deltas llamado: {deltas_called[0] if 'deltas_called' in locals() else 'N/A'}")
        print(f"   component.update llamado: {comp_update_called[0]}")
        print(f"   calculate_delta llamado: {calc_called[0]}")
        print(f"   Posición cambió: {not np.array_equal(pos_before, pos_after)}")
        
        # Verificar si el problema es el tiempo
        print(f"\n4️⃣ Verificando tiempo:")
        if hasattr(engine, '_time'):
            print(f"   engine._time: {engine._time}")
        else:
            print(f"   ❌ engine._time NO EXISTE")
            
        if hasattr(engine, '_last_update_time'):
            print(f"   engine._last_update_time: {engine._last_update_time}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_update()