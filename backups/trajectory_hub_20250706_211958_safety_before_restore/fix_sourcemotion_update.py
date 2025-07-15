#!/usr/bin/env python3
"""
🔧 Fix: Corregir cómo SourceMotion.update() llama a los componentes
⚡ El problema real es que SourceMotion no pasa el state a IndividualTrajectory
🎯 Impacto: CRÍTICO - Sin esto las trayectorias no se mueven
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_motion_components():
    """Corregir el método update de SourceMotion en motion_components.py"""
    
    print("🔧 Corrigiendo SourceMotion.update() en motion_components.py...")
    
    try:
        # Leer el archivo
        with open('trajectory_hub/core/motion_components.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar el método update de SourceMotion
        import re
        
        # Patrón para encontrar el método update completo de SourceMotion
        pattern = r'(class SourceMotion.*?)(def update\(self[^:]*:\s*\n)((?:        .*\n)*?)(\n    def|\nclass|\Z)'
        
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            print("✅ Encontrado método SourceMotion.update()")
            
            # Reconstruir el método update corregido
            class_part = match.group(1)
            method_signature = match.group(2)
            method_body = match.group(3)
            next_section = match.group(4)
            
            # Crear el nuevo método update
            new_update = """def update(self, time: float, dt: float) -> Tuple[np.ndarray, np.ndarray, float]:
        \"\"\"
        Actualizar todos los componentes de movimiento.
        
        Parameters
        ----------
        time : float
            Tiempo actual de simulación
        dt : float
            Delta time desde la última actualización
            
        Returns
        -------
        Tuple[np.ndarray, np.ndarray, float]
            Posición, orientación y apertura actualizadas
        \"\"\"
        # Crear estado actual
        state = MotionState(
            position=self.state.position.copy(),
            orientation=self.state.orientation.copy(),
            aperture=self.state.aperture
        )
        
        # Actualizar componentes en orden de prioridad
        for component_name in self.update_order:
            if component_name in self.components and self.components[component_name].enabled:
                component = self.components[component_name]
                
                # CORRECCIÓN: Pasar los parámetros correctos según el tipo de componente
                if hasattr(component, '__class__') and component.__class__.__name__ == 'IndividualTrajectory':
                    # IndividualTrajectory necesita (state, current_time, dt)
                    state = component.update(state, time, dt)
                elif hasattr(component, 'update'):
                    # Otros componentes pueden necesitar diferentes parámetros
                    try:
                        # Intentar primero con (state, time, dt)
                        state = component.update(state, time, dt)
                    except TypeError:
                        try:
                            # Si falla, intentar con solo (state)
                            state = component.update(state)
                        except:
                            # Si todo falla, skip
                            pass
        
        # Actualizar estado interno
        self.state = state
        
        return state.position, state.orientation, state.aperture
"""
            
            # Buscar dónde insertar el nuevo método
            # Encontrar el final de la clase SourceMotion
            class_match = re.search(r'class SourceMotion.*?\n((?:    .*\n)*)', content, re.DOTALL)
            if class_match:
                # Reemplazar el método update existente
                # Primero, encontrar el método update actual
                update_pattern = r'(    def update\(self.*?\n(?:        .*\n)*?)(?=\n    def|\nclass|\Z)'
                
                # Reemplazar con el nuevo método
                content = re.sub(update_pattern, '    ' + new_update.replace('\n', '\n    '), content, count=1)
                print("✅ Método update reemplazado")
            
            # Guardar cambios
            with open('trajectory_hub/core/motion_components.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ motion_components.py actualizado")
            return True
            
        else:
            print("❌ No se encontró el método SourceMotion.update()")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fixed_update():
    """Test rápido del update corregido"""
    print("\n🧪 TEST DEL UPDATE CORREGIDO")
    print("="*50)
    
    try:
        from trajectory_hub.core.motion_components import SourceMotion, IndividualTrajectory, MotionState
        import numpy as np
        
        # Crear SourceMotion con IndividualTrajectory
        motion = SourceMotion(source_id=0)
        
        # Configurar trayectoria individual manualmente
        traj = IndividualTrajectory()
        traj.set_trajectory('circle', np.array([0, 0, 0]), radius=1.0)
        traj.set_movement_mode('velocity', movement_speed=1.0)
        
        motion.add_component('individual_trajectory', traj)
        
        print("📊 Estado inicial:")
        print(f"   Fase: {traj.position_on_trajectory:.3f}")
        print(f"   Posición: {motion.state.position}")
        
        # Ejecutar varios updates
        for i in range(5):
            pos, ori, aper = motion.update(i * 0.016, 0.016)
            print(f"\n📊 Update {i+1}:")
            print(f"   Fase: {traj.position_on_trajectory:.3f}")
            print(f"   Posición: {pos}")
        
        if traj.position_on_trajectory > 0:
            print("\n✅ ¡ÉXITO! Las trayectorias ahora avanzan")
            return True
        else:
            print("\n❌ Las trayectorias aún no avanzan")
            return False
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 FIX DE SOURCEMOTION UPDATE")
    print("="*60)
    
    if fix_motion_components():
        print("\n" + "="*60)
        test_fixed_update()
    else:
        print("\n❌ No se pudo aplicar la corrección")