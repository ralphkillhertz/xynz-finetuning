import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def diagnose_rotation_stop():
    """Diagnostica por qué la rotación se detiene prematuramente"""
    print("🔍 DIAGNÓSTICO: POR QUÉ SE DETIENE LA ROTACIÓN")
    print("=" * 60)
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        import numpy as np
        
        # Crear sistema
        engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
        sid = engine.create_source(0)
        engine._positions[0] = np.array([3.0, 0.0, 0.0])
        
        # Configurar rotación
        success = engine.set_manual_individual_rotation(
            source_id=0,
            yaw=90.0,
            pitch=0.0,
            roll=0.0,
            interpolation_speed=45.0
        )
        
        print("✅ Sistema configurado")
        
        # Obtener componente
        motion = engine.motion_states[0]
        comp = motion.active_components['manual_individual_rotation']
        
        print(f"\n📊 Estado inicial del componente:")
        print(f"   Target yaw: {np.degrees(comp.target_yaw):.1f}° (radianes: {comp.target_yaw:.4f})")
        print(f"   Current yaw: {np.degrees(comp.current_yaw):.1f}°")
        print(f"   Interpolation speed: {np.degrees(comp.interpolation_speed):.1f}°/s (radianes: {comp.interpolation_speed:.4f})")
        print(f"   Enabled: {comp.enabled}")
        
        # Simular frame por frame
        print(f"\n🔄 Simulando frame por frame...")
        print("-" * 80)
        print("Frame | Current Yaw | Target | Diff   | Enabled | Pos X   | Pos Y   | Ángulo")
        print("-" * 80)
        
        for frame in range(20):  # Primeros 20 frames
            # Estado antes
            current_before = comp.current_yaw
            enabled_before = comp.enabled
            
            # Update
            engine.update()
            
            # Estado después
            pos = engine._positions[0]
            angle = np.degrees(np.arctan2(pos[1], pos[0]))
            yaw_diff = comp.target_yaw - comp.current_yaw
            
            print(f"{frame:5} | {np.degrees(comp.current_yaw):11.1f}° | {np.degrees(comp.target_yaw):6.1f}° | {np.degrees(yaw_diff):6.1f}° | {str(comp.enabled):7} | {pos[0]:7.3f} | {pos[1]:7.3f} | {angle:6.1f}°")
            
            # Si se desactivó, investigar por qué
            if enabled_before and not comp.enabled:
                print("\n⚠️ ¡El componente se DESACTIVÓ!")
                print(f"   Diferencia cuando se desactivó: {np.degrees(yaw_diff):.3f}°")
                break
            
            # Si no hay cambio en current_yaw
            if frame > 0 and abs(comp.current_yaw - current_before) < 0.0001:
                print("\n⚠️ ¡current_yaw dejó de cambiar!")
                break
        
        # Verificar condición de parada en el código
        print(f"\n📄 Verificando condición de parada...")
        
        # Ver el código del método update
        filepath = 'trajectory_hub/core/motion_components.py'
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar ManualIndividualRotation.update
        class_start = content.find("class ManualIndividualRotation")
        if class_start != -1:
            # Buscar la condición que desactiva
            section = content[class_start:class_start+3000]  # Siguientes 3000 chars
            
            # Buscar self.enabled = False
            disable_pos = section.find("self.enabled = False")
            if disable_pos != -1:
                # Mostrar contexto
                context_start = max(0, disable_pos - 200)
                context_end = min(len(section), disable_pos + 100)
                context = section[context_start:context_end]
                
                print("\n📋 Código que desactiva el componente:")
                print("-" * 60)
                for line in context.split('\n'):
                    if "self.enabled = False" in line:
                        print(f">>> {line}")
                    else:
                        print(f"    {line}")
                print("-" * 60)
        
        # Diagnóstico final
        print(f"\n📊 DIAGNÓSTICO FINAL:")
        print(f"   La rotación se detiene porque:")
        print(f"   - El componente se desactiva prematuramente")
        print(f"   - Probablemente la condición de parada es muy estricta")
        print(f"   - O hay un error en el cálculo de la diferencia")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_rotation_stop()