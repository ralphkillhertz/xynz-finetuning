#!/usr/bin/env python3
"""
🔧 Fix rápido: Hacer que 'velocity' funcione como modo de movimiento
⚡ Modificar IndividualTrajectory para aceptar 'velocity' como string
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_movement_mode():
    """Agregar soporte para 'velocity' en set_movement_mode"""
    
    print("🔧 Agregando soporte para movement_mode='velocity'...")
    
    try:
        # Leer motion_components.py
        with open('trajectory_hub/core/motion_components.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar el método set_movement_mode
        import re
        
        # Buscar la definición del método
        method_pattern = r'(def set_movement_mode\(self[^:]*:\s*\n)((?:        .*\n)*?)(        self\.movement_mode = mode)'
        
        match = re.search(method_pattern, content)
        
        if match:
            print("✅ Encontrado método set_movement_mode")
            
            # Insertar código para manejar strings
            fix_code = '''        # CORRECCIÓN: Manejar strings de modo
        if isinstance(mode, str):
            mode_mapping = {
                'velocity': TrajectoryMovementMode.FIX,  # Mapear velocity a FIX
                'stop': TrajectoryMovementMode.STOP,
                'fix': TrajectoryMovementMode.FIX,
                'random': TrajectoryMovementMode.RANDOM,
                'vibration': TrajectoryMovementMode.VIBRATION,
                'spin': TrajectoryMovementMode.SPIN,
                'freeze': TrajectoryMovementMode.FREEZE
            }
            mode = mode_mapping.get(mode.lower(), TrajectoryMovementMode.FIX)
        
'''
            
            # Reconstruir el método
            new_content = content[:match.start()] + \
                          match.group(1) + \
                          match.group(2) + \
                          fix_code + \
                          match.group(3) + \
                          content[match.end():]
            
            # Guardar
            with open('trajectory_hub/core/motion_components.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ motion_components.py actualizado")
            return True
            
        else:
            print("⚠️ No se encontró el patrón exacto, buscando alternativa...")
            
            # Buscar de forma más general
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'def set_movement_mode(self' in line:
                    print(f"📍 Encontrado en línea {i+1}")
                    
                    # Insertar el fix después de la definición del método
                    # Buscar donde empieza el cuerpo del método
                    for j in range(i+1, min(i+20, len(lines))):
                        if 'self.movement_mode = mode' in lines[j]:
                            # Insertar antes de esta línea
                            indent = '        '
                            fix_lines = [
                                f"{indent}# CORRECCIÓN: Manejar strings de modo",
                                f"{indent}if isinstance(mode, str):",
                                f"{indent}    mode = TrajectoryMovementMode.FIX if mode == 'velocity' else TrajectoryMovementMode.STOP",
                                ""
                            ]
                            
                            lines[j:j] = fix_lines
                            
                            # Guardar
                            with open('trajectory_hub/core/motion_components.py', 'w', encoding='utf-8') as f:
                                f.write('\n'.join(lines))
                            
                            print("✅ Fix aplicado con método alternativo")
                            return True
                    
            print("❌ No se pudo aplicar el fix automáticamente")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_velocity_mode():
    """Probar que 'velocity' ahora funcione"""
    print("\n🧪 TEST DE MODO 'velocity'")
    print("="*50)
    
    try:
        from trajectory_hub.core.motion_components import (
            IndividualTrajectory, MotionState
        )
        import numpy as np
        
        traj = IndividualTrajectory()
        traj.set_trajectory('circle', center=np.array([0, 0, 0]), radius=1.0)
        
        # Ahora debería funcionar con 'velocity'
        traj.set_movement_mode('velocity', movement_speed=1.0)
        print("✅ Modo 'velocity' configurado sin errores")
        
        state = MotionState(position=np.array([0, 0, 0]))
        
        print(f"Fase inicial: {traj.position_on_trajectory:.3f}")
        
        for i in range(5):
            new_state = traj.update(state, i * 0.016, 0.016)
            print(f"Update {i+1}: fase={traj.position_on_trajectory:.3f}")
            
        if traj.position_on_trajectory > 0:
            print("\n✅ ¡ÉXITO! Las trayectorias ahora avanzan con mode='velocity'")
            return True
        else:
            print("\n❌ Las trayectorias aún no avanzan")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def manual_instructions():
    """Instrucciones para corrección manual"""
    print("\n📝 CORRECCIÓN MANUAL")
    print("="*60)
    
    print("Si el fix automático no funcionó, edita motion_components.py")
    print("\nBusca el método set_movement_mode en la clase IndividualTrajectory")
    print("y agrega este código al inicio del método:")
    print("""
        # Manejar strings de modo
        if isinstance(mode, str):
            if mode == 'velocity':
                mode = TrajectoryMovementMode.FIX  # o el modo que corresponda
            elif mode == 'stop':
                mode = TrajectoryMovementMode.STOP
            # etc...
    """)

if __name__ == "__main__":
    print("🚀 FIX RÁPIDO - SOPORTE PARA mode='velocity'")
    print("="*60)
    
    if fix_movement_mode():
        if test_velocity_mode():
            print("\n✅ Problema resuelto")
        else:
            print("\n⚠️ El fix se aplicó pero puede haber otro problema")
            manual_instructions()
    else:
        manual_instructions()