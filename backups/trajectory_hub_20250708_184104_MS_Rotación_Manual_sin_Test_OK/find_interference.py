# === find_interference.py ===
# 🔍 Buscar qué está interfiriendo con la rotación
# ⚡ Compara el delta calculado vs el movimiento real
# 🎯 Impacto: IDENTIFICAR INTERFERENCIA

import numpy as np
import math

def find_interference():
    """Encuentra qué está interfiriendo con la rotación"""
    print("🔍 BUSCANDO INTERFERENCIA EN engine.update()")
    print("="*60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)
    
    # Crear una sola fuente para simplificar
    motion = engine.create_source(0)
    
    # Establecer posición inicial
    engine._positions[0] = np.array([3.0, 0.0, 0.0])
    if 0 in engine.motion_states:
        engine.motion_states[0].position = [3.0, 0.0, 0.0]
    
    # Crear macro con esa fuente
    macro_name = engine.create_macro("test", source_count=1)
    
    # Desactivar TODOS los componentes
    print("\n1️⃣ Desactivando TODOS los componentes...")
    state = engine.motion_states[0]
    for name, comp in state.active_components.items():
        if hasattr(comp, 'enabled'):
            comp.enabled = False
            print(f"   ✅ {name} desactivado")
    
    # Configurar SOLO rotación manual
    print("\n2️⃣ Activando SOLO rotación manual...")
    engine.set_manual_macro_rotation(macro_name, yaw=math.pi/2, interpolation_speed=1.0)
    
    # Verificar componentes
    print("\n3️⃣ Componentes activos:")
    for name, comp in state.active_components.items():
        enabled = getattr(comp, 'enabled', '?')
        print(f"   {name}: enabled={enabled}")
    
    # Obtener el componente de rotación
    rotation = state.active_components.get('manual_macro_rotation')
    
    print("\n4️⃣ Ejecutando UN SOLO update...")
    
    # Posición antes
    pos_before = engine._positions[0].copy()
    state_pos_before = list(state.position)
    
    # Calcular delta esperado manualmente
    if rotation:
        expected_delta = rotation.calculate_delta(state, 0.0, 1/60.0)
        if expected_delta:
            print(f"   Delta esperado: {expected_delta.position}")
    
    # Ejecutar update
    engine.update()
    
    # Posición después
    pos_after = engine._positions[0]
    state_pos_after = state.position
    
    # Comparar
    actual_change = pos_after - pos_before
    
    print(f"\n📊 RESULTADOS:")
    print(f"   engine._positions[0]:")
    print(f"      Antes:  {pos_before}")
    print(f"      Después: {pos_after}")
    print(f"      Cambio: {actual_change}")
    
    print(f"\n   motion_states[0].position:")
    print(f"      Antes:  {state_pos_before}")
    print(f"      Después: {state_pos_after}")
    
    if expected_delta and not np.allclose(actual_change, expected_delta.position, atol=0.001):
        print(f"\n❌ INTERFERENCIA DETECTADA!")
        print(f"   Cambio esperado: {expected_delta.position}")
        print(f"   Cambio real:     {actual_change}")
        print(f"   Diferencia:      {actual_change - expected_delta.position}")
        
        # Buscar la causa
        print(f"\n🔍 Posibles causas:")
        
        # Verificar si hay step fijo
        if hasattr(engine, '_fixed_step') or hasattr(engine, 'fixed_step'):
            print("   - Puede haber un paso fijo que sobrescribe posiciones")
        
        # Verificar formación
        if hasattr(macro_name, 'formation') or 'formation' in dir(engine._macros[macro_name]):
            print("   - La formación del macro puede estar actualizándose")
        
        # Ver si hay algún update adicional
        print("\n5️⃣ Investigando el código de engine.update()...")
        print("   El problema puede estar en:")
        print("   - El orden de procesamiento de componentes")
        print("   - Algún código que actualiza _positions directamente")
        print("   - La formación del macro sobrescribiendo posiciones")
    else:
        print(f"\n✅ No hay interferencia, el cambio coincide con lo esperado")

if __name__ == "__main__":
    find_interference()