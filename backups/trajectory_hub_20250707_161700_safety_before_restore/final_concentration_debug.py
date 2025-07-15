#!/usr/bin/env python3
"""
final_concentration_debug.py - Debug final para ver por qué las posiciones no cambian
"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

def detailed_debug():
    """Debug detallado paso a paso"""
    print("🔍 DEBUG DETALLADO DEL SISTEMA DE CONCENTRACIÓN\n")
    
    # Crear engine y macro
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("debug", 3, formation="circle", spacing=3.0)
    macro = engine._macros[macro_id]
    
    # Tomar primera fuente
    sid = list(macro.source_ids)[0]
    motion = engine._source_motions[sid]
    conc = motion.components['concentration']
    
    print("1. Estado inicial:")
    print(f"   - Posición: {motion.state.position}")
    print(f"   - ConcentrationComponent enabled: {conc.enabled}")
    print(f"   - Factor: {conc.factor}")
    print(f"   - Target: {conc.target_point}")
    
    # Aplicar concentración
    print("\n2. Aplicando set_macro_concentration(0.0)...")
    engine.set_macro_concentration(macro_id, 0.0)
    
    print("\n3. Estado después de set_macro_concentration:")
    print(f"   - ConcentrationComponent enabled: {conc.enabled}")
    print(f"   - Factor: {conc.factor}")
    print(f"   - Target: {conc.target_point}")
    
    # Verificar si el componente funciona manualmente
    print("\n4. Test manual del componente:")
    old_pos = motion.state.position.copy()
    print(f"   - Posición antes: {old_pos}")
    
    # Llamar update manualmente
    new_state = conc.update(motion.state, 0.0, 0.016)
    print(f"   - Posición después del update manual: {new_state.position}")
    print(f"   - ¿Cambió?: {not np.allclose(old_pos, new_state.position)}")
    
    # Si cambió manualmente, aplicar el cambio
    if not np.allclose(old_pos, new_state.position):
        motion.state = new_state
        print("   ✅ El componente SÍ funciona manualmente")
    
    # Ahora hacer engine.update()
    print("\n5. Ejecutando engine.update()...")
    pos_before_update = motion.state.position.copy()
    engine.update()
    pos_after_update = motion.state.position
    
    print(f"   - Posición antes: {pos_before_update}")
    print(f"   - Posición después: {pos_after_update}")
    print(f"   - ¿Cambió en engine.update?: {not np.allclose(pos_before_update, pos_after_update)}")
    
    # Verificar _positions
    print(f"\n6. Verificando sincronización:")
    print(f"   - motion.state.position: {motion.state.position}")
    print(f"   - engine._positions[{sid}]: {engine._positions[sid]}")
    print(f"   - ¿Sincronizado?: {np.allclose(motion.state.position, engine._positions[sid])}")
    
    # Verificar si SourceMotion.update está procesando concentration
    print("\n7. Verificando si SourceMotion.update procesa concentration:")
    
    # Hacer un update directo de motion
    result = motion.update(engine._time, engine.dt)
    print(f"   - Resultado de motion.update: {result}")
    
    # Debug del factor
    print(f"\n8. Debug del factor de concentración:")
    print(f"   - Factor actual: {conc.factor}")
    print(f"   - concentration_strength = 1.0 - factor = {1.0 - conc.factor}")
    
    # Si el factor es 1.0, no habrá movimiento
    if conc.factor == 1.0:
        print("   ❌ Factor = 1.0 significa NO concentración (completamente disperso)")
    elif conc.factor == 0.0:
        print("   ✅ Factor = 0.0 significa concentración TOTAL")

def check_concentration_update_logic():
    """Verificar la lógica del update de ConcentrationComponent"""
    print("\n\n🔍 VERIFICANDO LÓGICA DE ConcentrationComponent.update()...\n")
    
    from trajectory_hub.core.motion_components import ConcentrationComponent, MotionState
    
    # Crear componente y estado de prueba
    comp = ConcentrationComponent()
    state = MotionState()
    state.position = np.array([5.0, 0.0, 0.0])
    
    print("1. Prueba con factor = 1.0 (sin concentración):")
    comp.factor = 1.0
    comp.target_point = np.array([0.0, 0.0, 0.0])
    new_state = comp.update(state, 0.0, 0.016)
    print(f"   - Posición inicial: {state.position}")
    print(f"   - Posición final: {new_state.position}")
    print(f"   - ¿Cambió?: {not np.allclose(state.position, new_state.position)}")
    
    print("\n2. Prueba con factor = 0.0 (concentración total):")
    comp.factor = 0.0
    state.position = np.array([5.0, 0.0, 0.0])  # Reset
    new_state = comp.update(state, 0.0, 0.016)
    print(f"   - Posición inicial: {state.position}")
    print(f"   - Posición final: {new_state.position}")
    print(f"   - ¿Cambió?: {not np.allclose(state.position, new_state.position)}")
    
    print("\n3. Prueba con factor = 0.5 (concentración parcial):")
    comp.factor = 0.5
    state.position = np.array([5.0, 0.0, 0.0])  # Reset
    new_state = comp.update(state, 0.0, 0.016)
    print(f"   - Posición inicial: {state.position}")
    print(f"   - Posición final: {new_state.position}")
    print(f"   - ¿Cambió?: {not np.allclose(state.position, new_state.position)}")

def check_concentration_code():
    """Verificar el código de ConcentrationComponent.update"""
    print("\n\n📄 VERIFICANDO CÓDIGO DE ConcentrationComponent.update()...\n")
    
    import os
    filepath = "trajectory_hub/core/motion_components.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar ConcentrationComponent.update
    in_update = False
    update_lines = []
    
    for i, line in enumerate(lines):
        if "class ConcentrationComponent" in line:
            class_start = i
        elif "def update(self" in line and i > class_start:
            in_update = True
        elif in_update and line.strip() and not line.startswith("        "):
            break
        elif in_update:
            update_lines.append(line.rstrip())
    
    if update_lines:
        print("Método update encontrado:")
        print("-" * 70)
        for line in update_lines[:30]:  # Primeras 30 líneas
            print(line)
        print("-" * 70)

def main():
    print("="*70)
    print("🔍 DEBUG FINAL - ¿POR QUÉ NO SE MUEVEN LAS POSICIONES?")
    print("="*70)
    
    # Debug detallado
    detailed_debug()
    
    # Verificar lógica
    check_concentration_update_logic()
    
    # Ver el código
    check_concentration_code()
    
    print("\n" + "="*70)
    print("CONCLUSIONES")
    print("="*70)

if __name__ == "__main__":
    main()