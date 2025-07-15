#!/usr/bin/env python3
"""
🧪 VERIFICACIÓN FINAL: ¿Funciona la concentración?
"""

import os
import sys
import numpy as np

# Setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("""
================================================================================
🧪 VERIFICACIÓN FINAL DE CONCENTRACIÓN
================================================================================
""")

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    from trajectory_hub.core.motion_components import SourceMotion
    
    print("✅ Imports exitosos\n")
    
    # 1. Crear engine y macro
    print("1️⃣ CREANDO ENGINE Y MACRO...")
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=5.0)
    
    # 2. Verificar posiciones iniciales
    print("\n2️⃣ POSICIONES INICIALES:")
    initial_positions = {}
    for i in range(4):
        pos = engine._positions[i].copy()
        initial_positions[i] = pos
        print(f"   Fuente {i}: {pos}")
    
    # Calcular centro
    center = np.mean(list(initial_positions.values()), axis=0)
    print(f"\n   Centro del macro: {center}")
    
    # 3. Aplicar concentración
    print("\n3️⃣ APLICANDO CONCENTRACIÓN (factor=0.5)...")
    try:
        engine.set_macro_concentration(macro_id, 0.5)
        print("   ✅ set_macro_concentration ejecutado")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        sys.exit(1)
    
    # 4. Verificar offsets
    print("\n4️⃣ VERIFICANDO OFFSETS:")
    offsets_ok = True
    for i in range(4):
        if i in engine._source_motions:
            motion = engine._source_motions[i]
            
            # Verificar que tiene concentration_offset
            if hasattr(motion, 'concentration_offset'):
                offset = motion.concentration_offset
                magnitude = np.linalg.norm(offset)
                print(f"   Fuente {i}:")
                print(f"      offset: {offset}")
                print(f"      magnitud: {magnitude:.4f}")
                
                if magnitude < 0.01:
                    offsets_ok = False
                    print(f"      ❌ Offset muy pequeño!")
            else:
                print(f"   Fuente {i}: ❌ NO tiene concentration_offset")
                offsets_ok = False
    
    if not offsets_ok:
        print("\n❌ Los offsets no se calcularon correctamente")
        sys.exit(1)
    
    # 5. Ejecutar simulación
    print("\n5️⃣ EJECUTANDO SIMULACIÓN...")
    
    # Primer frame
    print("\n   Frame 1:")
    engine.step()
    
    movements_frame1 = []
    for i in range(4):
        current_pos = engine._positions[i]
        movement = np.linalg.norm(current_pos - initial_positions[i])
        movements_frame1.append(movement)
        
        if movement > 0.001:
            print(f"   Fuente {i}: ✅ se movió {movement:.4f}")
        else:
            print(f"   Fuente {i}: ❌ NO se movió")
    
    # Si hay movimiento, continuar
    if any(m > 0.001 for m in movements_frame1):
        print("\n   ✅ Las fuentes se están moviendo!")
        
        # Ejecutar más frames
        print("\n   Ejecutando 99 frames más...")
        for frame in range(2, 101):
            engine.step()
            
            if frame % 25 == 0:
                pos0 = engine._positions[0]
                mov = np.linalg.norm(pos0 - initial_positions[0])
                print(f"   Frame {frame}: Fuente 0 ha movido {mov:.4f} total")
        
        # Análisis final
        print("\n6️⃣ ANÁLISIS FINAL (100 frames):")
        
        final_movements = []
        print("\n   Movimientos totales:")
        for i in range(4):
            final_pos = engine._positions[i]
            total_movement = np.linalg.norm(final_pos - initial_positions[i])
            final_movements.append(total_movement)
            
            print(f"   Fuente {i}:")
            print(f"      Inicial: {initial_positions[i]}")
            print(f"      Final:   {final_pos}")
            print(f"      Movimiento: {total_movement:.4f}")
        
        # Análisis de concentración
        initial_dispersion = np.std(list(initial_positions.values()))
        final_positions = [engine._positions[i] for i in range(4)]
        final_dispersion = np.std(final_positions)
        reduction_percent = (1 - final_dispersion/initial_dispersion) * 100
        
        print(f"\n   📊 CONCENTRACIÓN:")
        print(f"      Dispersión inicial: {initial_dispersion:.4f}")
        print(f"      Dispersión final:   {final_dispersion:.4f}")
        print(f"      Reducción:          {reduction_percent:.1f}%")
        
        if reduction_percent > 10:
            print("\n" + "="*60)
            print("✅ ¡ÉXITO TOTAL! LA CONCENTRACIÓN FUNCIONA PERFECTAMENTE")
            print("="*60)
            print("\n🎉 Las fuentes se concentran hacia el centro")
            print(f"🎯 Reducción de dispersión: {reduction_percent:.1f}%")
            print("\n🚀 AHORA PUEDES USAR:")
            print("   python trajectory_hub/interface/interactive_controller.py")
            print("\n💡 En el controlador:")
            print("   - Tecla 'C' para activar concentración")
            print("   - Teclas '1-9' para ajustar intensidad")
        else:
            print("\n⚠️ Las fuentes se mueven pero no se concentran mucho")
    
    else:
        print("\n❌ ERROR: Las fuentes NO se mueven en absoluto")
        print("\n🔍 DIAGNÓSTICO:")
        
        # Verificar manualmente
        if 0 in engine._source_motions:
            motion = engine._source_motions[0]
            print(f"\n   Motion 0:")
            print(f"      state.position: {motion.state.position}")
            print(f"      concentration_offset: {getattr(motion, 'concentration_offset', 'NO EXISTE')}")
            
            # Calcular posición esperada
            if hasattr(motion, 'concentration_offset'):
                expected_pos = motion.state.position + motion.concentration_offset
                print(f"      Posición esperada: {expected_pos}")
                print(f"      Posición actual en _positions: {engine._positions[0]}")
        
        print("\n💡 El problema está en step() - no aplica los offsets")
        
except Exception as e:
    print(f"\n❌ ERROR CRÍTICO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)