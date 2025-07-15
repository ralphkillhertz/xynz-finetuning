import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verify_update():
    """Verifica qué hace realmente SourceMotion.update()"""
    print("🔍 VERIFICANDO SourceMotion.update()")
    print("=" * 60)
    
    # 1. Ver el código actual
    filepath = 'trajectory_hub/core/motion_components.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar SourceMotion
    class_start = content.find("class SourceMotion:")
    if class_start == -1:
        print("❌ No se encontró SourceMotion")
        return
        
    # Buscar update
    next_class = content.find("\nclass ", class_start + 1)
    if next_class == -1:
        next_class = len(content)
        
    section = content[class_start:next_class]
    update_start = section.find("def update(")
    
    if update_start != -1:
        # Extraer método
        method_end = section.find("\n    def ", update_start + 1)
        if method_end == -1:
            method_end = section.find("\n\n", update_start)
            if method_end == -1:
                method_end = len(section)
        
        update_method = section[update_start:method_end]
        
        print("📄 Código actual de SourceMotion.update():")
        print("-" * 60)
        for i, line in enumerate(update_method.split('\n')):
            print(f"{i+1:3}: {line}")
        print("-" * 60)
    
    # 2. Test directo
    print("\n\n🧪 TEST DIRECTO DE SourceMotion:")
    print("=" * 60)
    
    try:
        from trajectory_hub.core.motion_components import SourceMotion, MotionState, ManualIndividualRotation
        import numpy as np
        
        # Crear SourceMotion
        state = MotionState()
        state.position = np.array([3.0, 0.0, 0.0])
        motion = SourceMotion(state)
        
        print("1️⃣ SourceMotion creado")
        
        # Añadir componente de rotación
        comp = ManualIndividualRotation()
        comp.set_target_rotation(np.radians(90), 0, 0, np.radians(90))
        motion.active_components['manual_individual_rotation'] = comp
        
        print("2️⃣ Componente añadido:")
        print(f"   Target yaw: {np.degrees(comp.target_yaw):.1f}°")
        print(f"   Current yaw: {np.degrees(comp.current_yaw):.1f}°")
        print(f"   Enabled: {comp.enabled}")
        
        # Verificar que active_components es dict
        print(f"\n3️⃣ Tipo de active_components: {type(motion.active_components)}")
        print(f"   Keys: {list(motion.active_components.keys())}")
        
        # Hook para ver si se llama component.update
        update_called = [False]
        original_update = comp.update
        
        def debug_update(*args, **kwargs):
            update_called[0] = True
            print("   🔔 component.update() LLAMADO!")
            print(f"      Args: {len(args)}")
            return original_update(*args, **kwargs)
        
        comp.update = debug_update
        
        # Llamar update
        print("\n4️⃣ Llamando motion.update()...")
        
        try:
            result = motion.update(0.1, 1/60)
            print(f"   ✅ update() retornó: {type(result)}")
        except Exception as e:
            print(f"   ❌ Error en update(): {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n5️⃣ Resultados:")
        print(f"   component.update llamado: {update_called[0]}")
        print(f"   Current yaw después: {np.degrees(comp.current_yaw):.1f}°")
        
        # Si no se llamó, investigar por qué
        if not update_called[0]:
            print("\n6️⃣ Investigando por qué no se llama...")
            
            # Verificar condiciones
            print(f"   hasattr(component, 'update'): {hasattr(comp, 'update')}")
            print(f"   hasattr(component, 'enabled'): {hasattr(comp, 'enabled')}")
            print(f"   component.enabled: {comp.enabled}")
            
            # Intentar llamar directamente
            print("\n7️⃣ Llamando component.update directamente...")
            try:
                comp.update = original_update  # Quitar el hook
                state2 = comp.update(0.1, 1/60, state)
                print(f"   ✅ Llamada directa exitosa")
                print(f"   Current yaw: {np.degrees(comp.current_yaw):.1f}°")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_update()