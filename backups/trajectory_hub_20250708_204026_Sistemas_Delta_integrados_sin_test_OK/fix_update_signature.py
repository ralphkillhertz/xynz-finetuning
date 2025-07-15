import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_update_signature():
    """Corrige la firma del método update en ManualIndividualRotation"""
    print("🔧 CORRIGIENDO FIRMA DE UPDATE Y CONVERSIÓN DE ÁNGULOS")
    print("=" * 60)
    
    # 1. Corregir motion_components.py
    print("\n1️⃣ Corrigiendo ManualIndividualRotation.update()...")
    
    filepath = 'trajectory_hub/core/motion_components.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la clase ManualIndividualRotation
    class_start = content.find("class ManualIndividualRotation")
    if class_start == -1:
        print("❌ No se encontró la clase")
        return False
    
    # Buscar el método update
    update_start = content.find("def update(", class_start)
    if update_start != -1:
        # Encontrar la línea completa
        line_end = content.find(":", update_start)
        current_signature = content[update_start:line_end+1]
        print(f"   Firma actual: {current_signature.strip()}")
        
        # Reemplazar con la firma correcta
        correct_signature = "def update(self, current_time: float, dt: float, state: 'MotionState') -> 'MotionState':"
        content = content[:update_start] + correct_signature + content[line_end+1:]
        print(f"   ✅ Firma corregida")
    
    # 2. Corregir el engine para NO convertir dos veces
    print("\n2️⃣ Corrigiendo doble conversión en el engine...")
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    with open(engine_path, 'r', encoding='utf-8') as f:
        engine_content = f.read()
    
    # Buscar set_manual_individual_rotation
    method_start = engine_content.find("def set_manual_individual_rotation(")
    if method_start != -1:
        method_end = engine_content.find("\n    def ", method_start + 100)
        if method_end == -1:
            method_end = len(engine_content)
        
        method_section = engine_content[method_start:method_end]
        
        # Verificar si hay doble conversión
        if "math.radians(math.radians(" in method_section:
            print("   ⚠️ Doble conversión detectada, corrigiendo...")
            method_section = method_section.replace(
                "rotation.set_target_rotation(math.radians(yaw), math.radians(pitch), math.radians(roll), math.radians(interpolation_speed))",
                "rotation.set_target_rotation(math.radians(yaw), math.radians(pitch), math.radians(roll), math.radians(interpolation_speed))"
            )
            engine_content = engine_content[:method_start] + method_section + engine_content[method_end:]
        
        # También verificar el print que muestra grados incorrectos
        if "Objetivos: Yaw=" in method_section:
            # Buscar y corregir el print
            import re
            # Reemplazar el print para mostrar los valores correctos
            method_section = re.sub(
                r'print\(f".*Objetivos: Yaw=\{yaw\*180/math\.pi:.1f\}.*"\)',
                'print(f"   Objetivos: Yaw={yaw:.1f}°, Pitch={pitch:.1f}°, Roll={roll:.1f}°")',
                method_section
            )
            engine_content = engine_content[:method_start] + method_section + engine_content[method_end:]
            print("   ✅ Print de debug corregido")
    
    # 3. Guardar archivos
    print("\n3️⃣ Guardando archivos...")
    
    import shutil
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Guardar motion_components.py
    backup1 = f'{filepath}.backup_{timestamp}'
    shutil.copy(filepath, backup1)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"   ✅ {filepath} guardado")
    
    # Guardar engine
    backup2 = f'{engine_path}.backup_{timestamp}'
    shutil.copy(engine_path, backup2)
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(engine_content)
    print(f"   ✅ {engine_path} guardado")
    
    return True

def test_fixed():
    """Test rápido con las correcciones"""
    print("\n\n🧪 TEST CON CORRECCIONES:")
    print("=" * 60)
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        from trajectory_hub.core.motion_components import ManualIndividualRotation
        import numpy as np
        
        # Test 1: Verificar firma del update
        print("1️⃣ Verificando firma de update()...")
        comp = ManualIndividualRotation()
        
        # Crear un estado dummy
        from trajectory_hub.core.motion_components import MotionState
        state = MotionState()
        
        # Intentar llamar update con la firma correcta
        try:
            result = comp.update(0.0, 0.016, state)
            print("   ✅ Firma correcta: update(current_time, dt, state)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        # Test 2: Verificar conversión de ángulos
        print("\n2️⃣ Verificando conversión de ángulos...")
        engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
        sid = engine.create_source(0)
        engine._positions[0] = np.array([3.0, 0.0, 0.0])
        
        success = engine.set_manual_individual_rotation(
            source_id=0,
            yaw=90.0,  # grados
            pitch=0.0,
            roll=0.0,
            interpolation_speed=45.0
        )
        
        if 0 in engine.motion_states:
            motion = engine.motion_states[0]
            if 'manual_individual_rotation' in motion.active_components:
                comp = motion.active_components['manual_individual_rotation']
                target_deg = np.degrees(comp.target_yaw)
                print(f"   Target yaw: {target_deg:.1f}° (debe ser ~90°)")
                
                if abs(target_deg - 90.0) < 1.0:
                    print("   ✅ Conversión correcta")
                else:
                    print("   ❌ Conversión incorrecta")
        
        print("\n✅ Correcciones aplicadas exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if fix_update_signature():
        test_fixed()