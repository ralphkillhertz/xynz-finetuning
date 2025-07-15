#!/usr/bin/env python3
"""
🔍 Encontrar el modo de movimiento correcto para velocidad constante
⚡ Problema: estamos usando 'velocity' pero no existe ese modo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_movement_modes():
    """Analizar cómo funcionan los modos de movimiento"""
    print("🔍 ANÁLISIS DE MODOS DE MOVIMIENTO")
    print("="*60)
    
    try:
        from trajectory_hub.core.motion_components import (
            IndividualTrajectory, TrajectoryMovementMode, MotionState
        )
        import numpy as np
        
        # Crear trayectoria de prueba
        traj = IndividualTrajectory()
        traj.set_trajectory('circle', center=np.array([0, 0, 0]), radius=1.0)
        
        # Estado inicial
        state = MotionState(position=np.array([0, 0, 0]))
        
        # Probar cada modo
        for mode in TrajectoryMovementMode:
            print(f"\n📍 Probando modo: {mode.name} ({mode.value})")
            
            # Resetear fase
            traj.position_on_trajectory = 0.0
            
            # Configurar modo
            try:
                traj.set_movement_mode(mode, movement_speed=1.0)
                print(f"   ✅ Modo configurado")
                
                # Hacer algunos updates
                initial_phase = traj.position_on_trajectory
                for i in range(3):
                    new_state = traj.update(state, i * 0.016, 0.016)
                    
                final_phase = traj.position_on_trajectory
                
                if final_phase > initial_phase:
                    print(f"   ✅ LA FASE AVANZA: {initial_phase:.3f} → {final_phase:.3f}")
                    print(f"   🎯 ESTE ES EL MODO PARA VELOCIDAD CONSTANTE")
                else:
                    print(f"   ❌ Fase no avanza: {final_phase:.3f}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def check_interactive_controller_mapping():
    """Ver cómo el controlador interactivo mapea las opciones"""
    print("\n\n📋 MAPEO EN CONTROLADOR INTERACTIVO")
    print("="*60)
    
    try:
        # Leer el archivo del controlador
        with open('trajectory_hub/interactive_controller.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar el mapeo de modos
        import re
        
        # Buscar donde se define el menú de modos
        menu_match = re.search(r'Modo de movimiento:.*?Seleccionar modo:', content, re.DOTALL)
        if menu_match:
            print("Menú encontrado:")
            print(menu_match.group(0))
        
        # Buscar el mapeo de opciones a modos
        mapping_patterns = [
            r'mode_map\s*=\s*\{[^}]+\}',
            r'modes\s*=\s*\[[^\]]+\]',
            r'if\s+mode_choice\s*==\s*.*?:.*?TrajectoryMovementMode\.\w+',
            r'movement_mode\s*=\s*["\'](\w+)["\']'
        ]
        
        for pattern in mapping_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
            if matches:
                print(f"\n📍 Patrón encontrado: {pattern}")
                for match in matches[:3]:  # Mostrar máximo 3
                    print(f"   {match[:100]}...")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

def create_working_test():
    """Crear un test que funcione con el modo correcto"""
    print("\n\n✅ TEST CON MODO CORRECTO")
    print("="*60)
    
    try:
        from trajectory_hub.core.motion_components import (
            IndividualTrajectory, TrajectoryMovementMode, MotionState
        )
        import numpy as np
        
        # Basándonos en el menú interactivo:
        # 1. Sin movimiento = STOP
        # 2. Velocidad constante = FIX (?)
        # 3. Cambios aleatorios = RANDOM
        # 4. Vibración = VIBRATION
        # 5. Giro ultra-rápido = SPIN
        # 6. Congelado en posición = FREEZE
        
        print("Probando modo FIX (opción 2 del menú)...")
        
        traj = IndividualTrajectory()
        traj.set_trajectory('circle', center=np.array([0, 0, 0]), radius=1.0)
        
        # Probar modo FIX
        traj.set_movement_mode(TrajectoryMovementMode.FIX, movement_speed=1.0)
        
        state = MotionState(position=np.array([0, 0, 0]))
        
        print(f"Fase inicial: {traj.position_on_trajectory:.3f}")
        
        for i in range(5):
            new_state = traj.update(state, i * 0.016, 0.016)
            print(f"Update {i+1}: fase={traj.position_on_trajectory:.3f}")
            state = new_state
            
        if traj.position_on_trajectory > 0:
            print("\n✅ ¡FUNCIONA! Usar TrajectoryMovementMode.FIX para velocidad constante")
        else:
            print("\n❌ FIX no es el modo correcto")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def suggest_fix():
    """Sugerir la corrección"""
    print("\n\n💡 CORRECCIÓN SUGERIDA")
    print("="*60)
    
    print("El problema es que estamos usando 'velocity' pero ese modo no existe.")
    print("\nBasándome en el menú interactivo:")
    print("  2. Velocidad constante")
    print("\nEl modo correcto probablemente es uno de estos:")
    print("  - TrajectoryMovementMode.FIX")
    print("  - TrajectoryMovementMode.SPIN")
    print("\nCambiar en interactive_controller.py y enhanced_trajectory_engine.py:")
    print("  movement_mode='velocity' → movement_mode='fix' (o el que funcione)")

if __name__ == "__main__":
    print("🔍 ENCONTRAR MODO DE MOVIMIENTO CORRECTO")
    print("="*70)
    
    analyze_movement_modes()
    check_interactive_controller_mapping()
    create_working_test()
    suggest_fix()