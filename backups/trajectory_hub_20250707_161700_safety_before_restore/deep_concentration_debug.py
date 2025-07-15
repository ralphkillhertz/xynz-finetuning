#!/usr/bin/env python3
"""
deep_concentration_debug.py - Diagnóstico profundo del sistema de concentración
"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent

def debug_concentration_step_by_step():
    """Debug paso a paso del sistema de concentración"""
    print("🔍 DEBUG PROFUNDO DE CONCENTRACIÓN\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    
    # Crear macro simple
    print("1. Creando macro...")
    macro_id = engine.create_macro("debug", 3, formation="circle", spacing=3.0)
    macro = engine._macros[macro_id]
    
    # Tomar la primera fuente
    sid = list(macro.source_ids)[0]
    motion = engine._source_motions[sid]
    
    print(f"   ✅ Macro creado con {len(macro.source_ids)} fuentes")
    print(f"   Primera fuente ID: {sid}")
    print(f"   Posición inicial: {motion.state.position}")
    
    # Verificar componentes
    print("\n2. Verificando componentes de la fuente:")
    for comp_name, comp in motion.components.items():
        print(f"   - {comp_name}: {'✅ Enabled' if comp.enabled else '❌ Disabled'}")
    
    # Verificar si concentration existe
    if 'concentration' not in motion.components:
        print("\n❌ NO HAY COMPONENTE concentration")
        print("   Agregándolo manualmente...")
        motion.components['concentration'] = ConcentrationComponent()
    
    concentration = motion.components['concentration']
    
    # Estado inicial del componente
    print("\n3. Estado inicial de ConcentrationComponent:")
    print(f"   - Enabled: {concentration.enabled}")
    print(f"   - Factor: {concentration.factor}")
    print(f"   - Target point: {concentration.target_point}")
    print(f"   - Mode: {concentration.mode}")
    
    # Aplicar concentración
    print("\n4. Aplicando concentración...")
    engine.set_macro_concentration(macro_id, 0.0)
    
    # Verificar estado después
    print("\n5. Estado después de set_macro_concentration:")
    print(f"   - Enabled: {concentration.enabled}")
    print(f"   - Factor: {concentration.factor}")
    print(f"   - Target point: {concentration.target_point}")
    
    # Hacer UN solo update manual
    print("\n6. Ejecutando UN update manual...")
    
    # Guardar posición antes
    pos_before = motion.state.position.copy()
    
    # Llamar update manualmente en el componente
    print("   Llamando concentration.update() directamente...")
    new_state = concentration.update(motion.state, engine._time, engine.dt)
    
    print(f"   Posición antes: {pos_before}")
    print(f"   Posición después: {new_state.position}")
    print(f"   ¿Cambió?: {not np.array_equal(pos_before, new_state.position)}")
    
    # Actualizar el estado en motion
    motion.state = new_state
    
    # Ahora hacer un update completo del engine
    print("\n7. Ejecutando engine.update()...")
    pos_before_engine = motion.state.position.copy()
    engine.update()
    pos_after_engine = motion.state.position
    
    print(f"   Posición antes: {pos_before_engine}")
    print(f"   Posición después: {pos_after_engine}")
    print(f"   ¿Cambió?: {not np.array_equal(pos_before_engine, pos_after_engine)}")
    
    # Verificar _positions
    print(f"\n8. Verificando _positions[{sid}]: {engine._positions[sid]}")
    print(f"   ¿Sincronizado?: {np.array_equal(motion.state.position, engine._positions[sid])}")

def check_concentration_component_code():
    """Verificar el código del componente"""
    print("\n\n🔍 VERIFICANDO CÓDIGO DE ConcentrationComponent...\n")
    
    # Crear un componente directamente
    comp = ConcentrationComponent()
    
    print("1. Creando componente directamente:")
    print(f"   - Enabled por defecto: {comp.enabled}")
    print(f"   - Factor por defecto: {comp.factor}")
    
    # Configurar para concentrar
    comp.enabled = True
    comp.factor = 0.0
    comp.target_point = np.array([0.0, 0.0, 0.0])
    
    # Crear un estado de prueba
    from trajectory_hub.core.motion_components import MotionState
    state = MotionState()
    state.position = np.array([5.0, 5.0, 0.0])
    
    print("\n2. Estado de prueba:")
    print(f"   - Posición inicial: {state.position}")
    print(f"   - Target: {comp.target_point}")
    print(f"   - Factor: {comp.factor} (0=concentrado)")
    
    # Aplicar update
    new_state = comp.update(state, 0.0, 0.016)
    
    print("\n3. Después de update:")
    print(f"   - Nueva posición: {new_state.position}")
    print(f"   - Distancia movida: {np.linalg.norm(new_state.position - state.position):.3f}")
    
    if np.array_equal(state.position, new_state.position):
        print("\n❌ LA POSICIÓN NO CAMBIÓ")
        print("   El problema está en ConcentrationComponent.update()")
    else:
        print("\n✅ La posición cambió correctamente")

def check_update_chain_detailed():
    """Verificar la cadena de updates con más detalle"""
    print("\n\n🔍 VERIFICANDO CADENA DE UPDATES DETALLADA...\n")
    
    import os
    
    # Verificar SourceMotion.update
    filepath = "trajectory_hub/core/motion_components.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar el update de SourceMotion
    in_source_motion = False
    in_update = False
    update_lines = []
    
    for i, line in enumerate(lines):
        if "class SourceMotion" in line:
            in_source_motion = True
        elif in_source_motion and "def update(" in line:
            in_update = True
        elif in_update and (line.strip() and not line.startswith("        ")):
            # Salimos del método
            break
        elif in_update:
            update_lines.append((i+1, line.rstrip()))
    
    print("Contenido de SourceMotion.update():")
    print("-" * 60)
    
    concentration_found = False
    for line_num, line in update_lines[-20:]:  # Últimas 20 líneas
        if "concentration" in line:
            print(f">>> {line_num}: {line}")
            concentration_found = True
        else:
            print(f"    {line_num}: {line}")
    
    if concentration_found:
        print("\n✅ concentration se procesa en SourceMotion.update()")
    else:
        print("\n❌ concentration NO se encuentra en SourceMotion.update()")

def main():
    print("="*70)
    print("🔍 DIAGNÓSTICO PROFUNDO DEL SISTEMA DE CONCENTRACIÓN")
    print("="*70)
    
    # Debug paso a paso
    debug_concentration_step_by_step()
    
    # Verificar el componente
    check_concentration_component_code()
    
    # Verificar la cadena
    check_update_chain_detailed()
    
    print("\n" + "="*70)
    print("RESUMEN DEL DIAGNÓSTICO")
    print("="*70)

if __name__ == "__main__":
    main()