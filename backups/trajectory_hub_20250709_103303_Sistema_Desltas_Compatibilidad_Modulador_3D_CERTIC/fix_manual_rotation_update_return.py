import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_update_return():
    """Corrige ManualIndividualRotation.update para que siempre retorne el estado"""
    print("🔧 CORRIGIENDO ManualIndividualRotation.update()")
    print("=" * 60)
    
    filepath = 'trajectory_hub/core/motion_components.py'
    
    # Leer archivo
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar ManualIndividualRotation
    print("1️⃣ Buscando ManualIndividualRotation.update()...")
    
    class_start = content.find("class ManualIndividualRotation")
    if class_start == -1:
        print("❌ No se encontró la clase")
        return False
    
    # Buscar el final de la clase
    next_class = content.find("\nclass ", class_start + 1)
    if next_class == -1:
        next_class = len(content)
    
    class_section = content[class_start:next_class]
    
    # Buscar el método update
    update_start = class_section.find("def update(")
    if update_start == -1:
        print("❌ No se encontró el método update")
        return False
    
    # Encontrar el final del método
    method_start = update_start
    indent_level = len(class_section[update_start:].split('\n')[0]) - len(class_section[update_start:].split('\n')[0].lstrip())
    
    # Buscar siguiente método o final de clase
    lines = class_section[update_start:].split('\n')
    method_end_line = len(lines)
    
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() and not line.startswith(' '):
            method_end_line = i
            break
        if line.strip().startswith('def ') and len(line) - len(line.lstrip()) <= indent_level:
            method_end_line = i
            break
    
    # Extraer el método
    method_lines = lines[:method_end_line]
    
    print("\n📄 Método update actual:")
    print("-" * 60)
    for i, line in enumerate(method_lines[:20]):  # Primeras 20 líneas
        print(f"{i+1:3}: {line}")
    print("-" * 60)
    
    # Verificar si retorna state
    method_text = '\n'.join(method_lines)
    has_return = False
    returns_state = False
    
    for line in method_lines:
        if 'return' in line:
            has_return = True
            if 'state' in line:
                returns_state = True
                break
    
    if not returns_state:
        print("\n⚠️ El método NO retorna state, corrigiendo...")
        
        # Encontrar la última línea con código
        last_code_line = -1
        for i in range(len(method_lines)-1, -1, -1):
            if method_lines[i].strip() and not method_lines[i].strip().startswith('#'):
                last_code_line = i
                break
        
        # Añadir return state
        if last_code_line >= 0:
            # Obtener indentación
            base_indent = '    '  # 4 espacios base de la clase
            method_indent = '        '  # 8 espacios para el contenido del método
            
            # Si la última línea es un return, reemplazarlo
            if 'return' in method_lines[last_code_line]:
                method_lines[last_code_line] = method_indent + 'return state'
                print("✅ Reemplazado return existente con 'return state'")
            else:
                # Añadir return state al final
                method_lines.insert(last_code_line + 1, method_indent + 'return state')
                print("✅ Añadido 'return state' al final del método")
        
        # Reconstruir el método
        new_method = '\n'.join(method_lines)
        
        # Reemplazar en la sección de la clase
        class_section = class_section[:update_start] + new_method + class_section[update_start + len('\n'.join(lines[:method_end_line])):]
        
        # Reemplazar en el contenido completo
        content = content[:class_start] + class_section + content[next_class:]
        
        # Guardar
        print("\n💾 Guardando archivo...")
        
        import shutil
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f'{filepath}.backup_{timestamp}'
        shutil.copy(filepath, backup_path)
        print(f"✅ Backup: {backup_path}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Archivo guardado")
    else:
        print("\n✅ El método ya retorna state")
    
    return True

def test_rotation_complete():
    """Test completo de la rotación"""
    print("\n\n🎯 TEST COMPLETO DE ROTACIÓN:")
    print("=" * 60)
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        import numpy as np
        
        # Crear sistema
        engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
        sid = engine.create_source(0)
        
        # Posición inicial
        initial_pos = np.array([3.0, 0.0, 0.0])
        engine._positions[0] = initial_pos.copy()
        
        # Configurar rotación
        success = engine.set_manual_individual_rotation(
            source_id=0,
            yaw=90.0,
            pitch=0.0,
            roll=0.0,
            interpolation_speed=45.0  # 2 segundos para 90°
        )
        
        print(f"✅ Sistema configurado")
        
        # Simular
        print(f"\n🔄 Simulando rotación...")
        print("-" * 60)
        print("Tiempo |  Posición [X, Y, Z]  | Ángulo  | Radio")
        print("-" * 60)
        
        frames = int(2.5 * engine.fps)  # 2.5 segundos
        for i in range(frames + 1):
            if i > 0:
                engine.update()
            
            pos = engine._positions[0]
            angle = np.degrees(np.arctan2(pos[1], pos[0]))
            radius = np.linalg.norm(pos[:2])
            
            # Mostrar cada 0.5 segundos
            if i % (engine.fps // 2) == 0:
                t = i / engine.fps
                print(f"{t:5.1f}s | [{pos[0]:6.3f}, {pos[1]:6.3f}, {pos[2]:6.3f}] | {angle:7.1f}° | {radius:6.3f}")
        
        # Resultado final
        final_pos = engine._positions[0]
        final_angle = np.degrees(np.arctan2(final_pos[1], final_pos[0]))
        expected_pos = np.array([0.0, 3.0, 0.0])
        error = np.linalg.norm(final_pos - expected_pos)
        
        print("\n" + "=" * 60)
        print(f"📊 RESULTADO FINAL:")
        print(f"   Posición esperada: [0.000, 3.000, 0.000]")
        print(f"   Posición final:    [{final_pos[0]:.3f}, {final_pos[1]:.3f}, {final_pos[2]:.3f}]")
        print(f"   Ángulo final: {final_angle:.1f}° (esperado: 90.0°)")
        print(f"   Error: {error:.3f}")
        
        if error < 0.1:
            print("\n✅ ¡ROTACIÓN MANUAL IS FUNCIONA PERFECTAMENTE! 🎉🎉🎉")
            print("   ManualIndividualRotation: 100% FUNCIONAL")
            print("   Sistema de deltas: COMPLETO")
        else:
            print(f"\n⚠️ La rotación tiene un error de {error:.3f} unidades")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if fix_update_return():
        test_rotation_complete()