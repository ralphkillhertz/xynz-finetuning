import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_issues():
    """Corrige los problemas de conversión y update"""
    print("🔧 CORRIGIENDO PROBLEMAS DE ROTACIÓN")
    print("=" * 60)
    
    # 1. Corregir set_manual_individual_rotation en el engine
    print("\n1️⃣ Corrigiendo conversión de ángulos...")
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar set_manual_individual_rotation
    method_start = content.find("def set_manual_individual_rotation(")
    if method_start == -1:
        print("❌ No se encontró set_manual_individual_rotation")
        return False
        
    # Buscar la línea que convierte grados a radianes
    method_end = content.find("\n    def ", method_start + 100)
    if method_end == -1:
        method_end = len(content)
    
    method_section = content[method_start:method_end]
    
    # Buscar conversiones incorrectas
    import re
    
    # Patrón para encontrar math.radians mal usado
    if "rotation.set_target_rotation(yaw, pitch, roll, interpolation_speed)" in method_section:
        print("⚠️ Falta conversión a radianes, corrigiendo...")
        # Reemplazar la llamada
        method_section = method_section.replace(
            "rotation.set_target_rotation(yaw, pitch, roll, interpolation_speed)",
            "rotation.set_target_rotation(math.radians(yaw), math.radians(pitch), math.radians(roll), math.radians(interpolation_speed))"
        )
        content = content[:method_start] + method_section + content[method_end:]
        
    # 2. Verificar el método update() del engine
    print("\n2️⃣ Verificando método update() del engine...")
    
    update_start = content.find("def update(self):")
    if update_start == -1:
        # Buscar con parámetro
        update_start = content.find("def update(self, dt")
        if update_start != -1:
            print("⚠️ update() tiene parámetro dt, corrigiendo para calcularlo internamente...")
            # Cambiar firma
            content = content.replace("def update(self, dt: float):", "def update(self):")
            
            # Añadir cálculo de dt al inicio del método
            update_body_start = content.find(":", update_start) + 1
            indent = "        "
            dt_calc = f"\n{indent}# Calcular dt automáticamente\n{indent}current_time = time.time()\n{indent}dt = current_time - self._last_update_time if hasattr(self, '_last_update_time') else 1.0/self.fps\n{indent}self._last_update_time = current_time\n"
            
            # Insertar después del docstring si existe
            docstring_end = content.find('"""', update_body_start + 10)
            if docstring_end != -1:
                docstring_end = content.find('\n', docstring_end) + 1
                content = content[:docstring_end] + dt_calc + content[docstring_end:]
            else:
                content = content[:update_body_start] + dt_calc + content[update_body_start:]
                
            # Asegurar import time
            if "import time" not in content[:1000]:
                import_pos = content.find("import")
                content = content[:import_pos] + "import time\n" + content[import_pos:]
    
    # 3. Guardar cambios
    print("\n3️⃣ Guardando cambios...")
    
    import shutil
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    backup_path = f'{engine_path}.backup_{timestamp}'
    shutil.copy(engine_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Archivo guardado")
    
    return True

def test_corrected():
    """Test con las correcciones aplicadas"""
    print("\n\n🧪 TEST CON CORRECCIONES:")
    print("=" * 60)
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        import numpy as np
        
        # Crear engine
        engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
        print("✅ Engine creado")
        
        # Crear fuente
        sid = engine.create_source(0)
        engine._positions[0] = np.array([3.0, 0.0, 0.0])
        print(f"✅ Fuente creada en posición: {engine._positions[0]}")
        
        # Configurar rotación
        success = engine.set_manual_individual_rotation(
            source_id=0,
            yaw=90.0,  # grados
            pitch=0.0,
            roll=0.0,
            interpolation_speed=45.0  # grados/segundo
        )
        print(f"✅ Rotación configurada: {success}")
        
        # Verificar valores
        if 0 in engine.motion_states:
            motion = engine.motion_states[0]
            if 'manual_individual_rotation' in motion.active_components:
                comp = motion.active_components['manual_individual_rotation']
                print(f"\n📊 Valores del componente:")
                print(f"   Target yaw: {np.degrees(comp.target_yaw):.1f}° (debe ser ~90°)")
                print(f"   Speed: {np.degrees(comp.interpolation_speed):.1f}°/s (debe ser ~45°/s)")
        
        # Probar update sin parámetros
        print("\n🔄 Probando engine.update()...")
        for i in range(3):
            engine.update()  # Sin parámetros
            pos = engine._positions[0]
            print(f"   Frame {i}: pos=[{pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}]")
        
        print("\n✅ ¡Update funciona sin parámetros!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if fix_issues():
        test_corrected()