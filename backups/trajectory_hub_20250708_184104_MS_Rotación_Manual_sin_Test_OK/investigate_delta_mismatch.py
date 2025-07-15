# === investigate_delta_mismatch.py ===
# 🔍 Investigar: Por qué el delta calculado no coincide con el aplicado
# ⚡ Encuentra la discrepancia
# 🎯 Impacto: CRÍTICO

import numpy as np

def investigate_mismatch():
    """Investiga la discrepancia entre delta calculado y aplicado"""
    print("🔍 INVESTIGACIÓN: Discrepancia de deltas")
    print("="*60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    # Setup mínimo
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)
    motion = engine.create_source(0)
    engine._positions[0] = np.array([3.0, 0.0, 0.0])
    engine.motion_states[0].position = [3.0, 0.0, 0.0]
    
    macro_name = engine.create_macro("test", source_count=1)
    
    # Desactivar otros componentes
    state = engine.motion_states[0]
    for name, comp in state.active_components.items():
        if hasattr(comp, 'enabled') and name != 'manual_macro_rotation':
            comp.enabled = False
    
    engine.set_manual_macro_rotation(macro_name, yaw=np.pi/2, interpolation_speed=1.0)
    
    # Obtener componente
    rotation = state.active_components['manual_macro_rotation']
    
    print("🎯 Calculando delta ANTES de engine.update():")
    
    # Calcular delta directamente
    direct_delta = rotation.calculate_delta(state, 0.0, 1/60.0)
    print(f"   Delta directo: {direct_delta.position if direct_delta else 'None'}")
    
    # Ahora veamos qué pasa dentro de update
    print("\n🔍 Rastreando el flujo de update:")
    
    # Guardar posición inicial
    pos_before = engine._positions[0].copy()
    
    # Interceptar el update de SourceMotion
    if hasattr(state, 'update'):
        print("   ❌ state no debería tener método update")
    
    # El state es un MotionState, no un SourceMotion
    # Necesitamos ver cómo engine.update() procesa esto
    
    print("\n🎯 Verificando tipo de objetos:")
    print(f"   tipo de state: {type(state)}")
    print(f"   tipo de motion_states[0]: {type(engine.motion_states[0])}")
    
    # Ver si hay un SourceMotion wrapper
    print("\n🔍 Buscando SourceMotion:")
    for attr in dir(engine):
        if 'motion' in attr.lower() and not attr.startswith('_'):
            value = getattr(engine, attr)
            if hasattr(value, '__getitem__'):
                print(f"   {attr}: {type(value)}")
    
    # Ejecutar update
    engine.update()
    
    pos_after = engine._positions[0]
    actual_delta = pos_after - pos_before
    
    print(f"\n📊 COMPARACIÓN:")
    print(f"   Delta calculado directamente: {direct_delta.position if direct_delta else 'None'}")
    print(f"   Delta real aplicado: {actual_delta}")
    
    if direct_delta and not np.allclose(direct_delta.position, actual_delta):
        print("\n❌ DISCREPANCIA DETECTADA")
        print("   El delta calculado NO coincide con el aplicado")
        print("   Esto sugiere que hay otro código modificando el resultado")

if __name__ == "__main__":
    investigate_mismatch()