import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_motion_update():
    """Corrige SourceMotion.update() para que actualice sus componentes"""
    print("🔧 CORRIGIENDO SourceMotion.update()")
    print("=" * 60)
    
    filepath = 'trajectory_hub/core/motion_components.py'
    
    # Leer el archivo
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la clase SourceMotion
    print("\n1️⃣ Buscando clase SourceMotion...")
    class_start = content.find("class SourceMotion:")
    if class_start == -1:
        print("❌ No se encontró SourceMotion")
        return False
    
    # Buscar el método update
    print("2️⃣ Buscando método update()...")
    
    # Buscar desde class_start hasta la siguiente clase
    next_class = content.find("\nclass ", class_start + 1)
    if next_class == -1:
        next_class = len(content)
    
    section = content[class_start:next_class]
    
    # Buscar update en esta sección
    update_start = section.find("def update(")
    
    if update_start == -1:
        print("⚠️ No existe update(), añadiéndolo...")
        
        # Buscar dónde insertar (después de __init__)
        init_pos = section.find("def __init__")
        if init_pos != -1:
            # Buscar el final de __init__
            next_def = section.find("\n    def ", init_pos + 1)
            if next_def == -1:
                next_def = len(section)
            
            # Insertar update
            update_method = '''
    
    def update(self, current_time: float, dt: float) -> 'MotionState':
        """Actualiza el estado y todos los componentes activos"""
        # Actualizar cada componente activo
        for comp_name, component in self.active_components.items():
            if hasattr(component, 'update') and hasattr(component, 'enabled'):
                if component.enabled:
                    # Actualizar el componente
                    self.state = component.update(current_time, dt, self.state)
        
        # Actualizar timestamp
        self.state.last_update = current_time
        
        return self.state
'''
            
            section = section[:next_def] + update_method + section[next_def:]
            content = content[:class_start] + section + content[next_class:]
            print("✅ Método update() añadido")
    else:
        print("✅ update() existe, verificando si actualiza componentes...")
        
        # Extraer el método update
        method_end = section.find("\n    def ", update_start + 1)
        if method_end == -1:
            method_end = len(section)
            
        update_content = section[update_start:method_end]
        
        # Verificar si ya actualiza componentes
        if "component.update(" not in update_content:
            print("⚠️ No actualiza componentes, corrigiendo...")
            
            # Buscar dónde insertar el código
            # Buscar después del docstring
            docstring_end = update_content.find('"""', 10)
            if docstring_end != -1:
                docstring_end = update_content.find('\n', docstring_end) + 1
            else:
                # Si no hay docstring, insertar después de la definición
                docstring_end = update_content.find('\n') + 1
            
            # Código para actualizar componentes
            component_update = '''        # Actualizar cada componente activo
        for comp_name, component in self.active_components.items():
            if hasattr(component, 'update') and hasattr(component, 'enabled'):
                if component.enabled:
                    # Actualizar el componente
                    self.state = component.update(current_time, dt, self.state)
        
'''
            
            update_content = update_content[:docstring_end] + component_update + update_content[docstring_end:]
            section = section[:update_start] + update_content + section[method_end:]
            content = content[:class_start] + section + content[next_class:]
            print("✅ Código de actualización de componentes añadido")
    
    # 3. Guardar
    print("\n3️⃣ Guardando archivo...")
    
    import shutil
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f'{filepath}.backup_{timestamp}'
    shutil.copy(filepath, backup_path)
    print(f"✅ Backup: {backup_path}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Archivo guardado")
    
    return True

def test_complete_flow():
    """Test completo del flujo"""
    print("\n\n🧪 TEST COMPLETO DEL FLUJO:")
    print("=" * 60)
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        import numpy as np
        
        # Crear sistema
        engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
        sid = engine.create_source(0)
        engine._positions[0] = np.array([3.0, 0.0, 0.0])
        
        # Configurar rotación
        engine.set_manual_individual_rotation(
            source_id=0,
            yaw=90.0,
            pitch=0.0,
            roll=0.0,
            interpolation_speed=90.0  # Rápido para test
        )
        
        print("✅ Sistema configurado")
        
        # Estado inicial
        motion = engine.motion_states[0]
        comp = motion.active_components['manual_individual_rotation']
        print(f"\n📊 Estado inicial:")
        print(f"   Posición: {engine._positions[0]}")
        print(f"   Current yaw: {np.degrees(comp.current_yaw):.1f}°")
        print(f"   Target yaw: {np.degrees(comp.target_yaw):.1f}°")
        
        # 5 updates
        print(f"\n🔄 Ejecutando 5 updates...")
        for i in range(5):
            pos_before = engine._positions[0].copy()
            yaw_before = comp.current_yaw
            
            engine.update()
            
            pos_after = engine._positions[0].copy()
            yaw_after = comp.current_yaw
            
            pos_changed = not np.array_equal(pos_before, pos_after)
            yaw_changed = yaw_after != yaw_before
            
            print(f"\n   Update {i+1}:")
            print(f"   - Current yaw: {np.degrees(yaw_after):.1f}° {'✅ CAMBIÓ' if yaw_changed else '❌ NO cambió'}")
            print(f"   - Posición: [{pos_after[0]:.3f}, {pos_after[1]:.3f}, {pos_after[2]:.3f}] {'✅ CAMBIÓ' if pos_changed else '❌ NO cambió'}")
        
        # Resultado final
        print(f"\n📊 Estado final:")
        print(f"   Posición: {engine._positions[0]}")
        print(f"   Current yaw: {np.degrees(comp.current_yaw):.1f}°")
        print(f"   Ángulo real: {np.degrees(np.arctan2(engine._positions[0][1], engine._positions[0][0])):.1f}°")
        
        if not np.array_equal(engine._positions[0], [3.0, 0.0, 0.0]):
            print("\n✅ ¡ROTACIÓN MANUAL IS FUNCIONA PERFECTAMENTE! 🎉")
        else:
            print("\n❌ La rotación aún no funciona")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if fix_motion_update():
        test_complete_flow()