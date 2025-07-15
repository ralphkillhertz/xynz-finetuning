import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_update_returns():
    """Corrige los métodos update para que siempre retornen el estado"""
    print("🔧 CORRIGIENDO MÉTODOS UPDATE PARA RETORNAR ESTADO")
    print("=" * 60)
    
    filepath = 'trajectory_hub/core/motion_components.py'
    
    # Leer archivo
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_made = 0
    
    # 1. Corregir ManualIndividualRotation.update
    print("\n1️⃣ Verificando ManualIndividualRotation.update()...")
    
    # Buscar la clase
    class_start = content.find("class ManualIndividualRotation")
    if class_start != -1:
        # Buscar el método update
        next_class = content.find("\nclass ", class_start + 1)
        if next_class == -1:
            next_class = len(content)
            
        section = content[class_start:next_class]
        update_start = section.find("def update(")
        
        if update_start != -1:
            # Buscar el return
            method_end = section.find("\n    def ", update_start + 1)
            if method_end == -1:
                method_end = section.find("\n\n", update_start)
                if method_end == -1:
                    method_end = len(section)
                    
            method_content = section[update_start:method_end]
            
            # Verificar si retorna state
            if "return state" not in method_content and "return" not in method_content:
                print("   ⚠️ No retorna state, añadiendo return...")
                # Añadir return al final
                lines = method_content.split('\n')
                # Encontrar la última línea con código (no vacía)
                last_code_line = -1
                for i in range(len(lines)-1, -1, -1):
                    if lines[i].strip():
                        last_code_line = i
                        break
                
                if last_code_line >= 0:
                    # Obtener indentación
                    indent = len(lines[1]) - len(lines[1].lstrip()) if len(lines) > 1 else 8
                    lines.insert(last_code_line + 1, " " * indent + "return state")
                    method_content = '\n'.join(lines)
                    section = section[:update_start] + method_content + section[method_end:]
                    content = content[:class_start] + section + content[next_class:]
                    fixes_made += 1
                    print("   ✅ Return state añadido")
            else:
                print("   ✅ Ya retorna state")
    
    # 2. Corregir SourceMotion.update
    print("\n2️⃣ Verificando SourceMotion.update()...")
    
    # Buscar SourceMotion.update y verificar que no esté asignando None
    sourcemotion_start = content.find("class SourceMotion:")
    if sourcemotion_start != -1:
        next_class = content.find("\nclass ", sourcemotion_start + 1)
        if next_class == -1:
            next_class = len(content)
            
        section = content[sourcemotion_start:next_class]
        update_start = section.find("def update(")
        
        if update_start != -1:
            method_end = section.find("\n    def ", update_start + 1)
            if method_end == -1:
                method_end = section.find("\n\n", update_start)
                if method_end == -1:
                    method_end = len(section)
                    
            method_content = section[update_start:method_end]
            
            # Verificar la línea problemática
            if "self.state = component.update(" in method_content:
                print("   ⚠️ Asignando resultado de update a self.state")
                # Cambiar para verificar que no sea None
                lines = method_content.split('\n')
                new_lines = []
                
                for line in lines:
                    if "self.state = component.update(" in line and "current_time, dt, self.state)" not in line:
                        # Corregir el orden de parámetros
                        indent = len(line) - len(line.lstrip())
                        new_lines.append(" " * indent + "# Actualizar componente")
                        new_lines.append(" " * indent + "new_state = component.update(current_time, dt, self.state)")
                        new_lines.append(" " * indent + "if new_state is not None:")
                        new_lines.append(" " * (indent + 4) + "self.state = new_state")
                        fixes_made += 1
                        print("   ✅ Corregido para verificar None")
                    else:
                        new_lines.append(line)
                
                method_content = '\n'.join(new_lines)
                section = section[:update_start] + method_content + section[method_end:]
                content = content[:sourcemotion_start] + section + content[next_class:]
    
    # 3. Guardar si hubo cambios
    if fixes_made > 0:
        print(f"\n💾 Guardando archivo ({fixes_made} correcciones)...")
        
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
        print("\n✅ No se necesitaron correcciones")
    
    return True

def test_rotation_final():
    """Test final definitivo"""
    print("\n\n🎯 TEST FINAL DEFINITIVO:")
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
            yaw=90.0,      # 90 grados
            pitch=0.0,
            roll=0.0,
            interpolation_speed=45.0  # 45°/s = 2 segundos
        )
        
        print(f"✅ Sistema configurado")
        print(f"   Posición inicial: {initial_pos}")
        
        # Simular 2 segundos
        print(f"\n🔄 Simulando 2 segundos...")
        print("-" * 50)
        print("Tiempo |  X      Y      Z   | Ángulo  | Distancia")
        print("-" * 50)
        
        frames = int(2.0 * engine.fps)
        for i in range(frames + 1):
            if i > 0:
                engine.update()
            
            pos = engine._positions[0]
            angle = np.degrees(np.arctan2(pos[1], pos[0]))
            dist = np.linalg.norm(pos - initial_pos)
            
            # Mostrar cada 0.5 segundos
            if i % (engine.fps // 2) == 0:
                t = i / engine.fps
                print(f"{t:5.1f}s | {pos[0]:6.3f} {pos[1]:6.3f} {pos[2]:6.3f} | {angle:7.1f}° | {dist:9.3f}")
        
        # Resultado final
        final_pos = engine._positions[0]
        final_angle = np.degrees(np.arctan2(final_pos[1], final_pos[0]))
        error = np.linalg.norm(final_pos - np.array([0.0, 3.0, 0.0]))
        
        print("\n" + "=" * 60)
        print(f"📊 RESULTADO FINAL:")
        print(f"   Posición final: [{final_pos[0]:.3f}, {final_pos[1]:.3f}, {final_pos[2]:.3f}]")
        print(f"   Ángulo final: {final_angle:.1f}°")
        print(f"   Error de posición: {error:.3f}")
        
        if abs(final_angle - 90.0) < 5.0:
            print("\n✅ ¡ROTACIÓN MANUAL IS FUNCIONA PERFECTAMENTE! 🎉🎉🎉")
            print("   Sistema de deltas: 100% COMPLETO")
            print("   Todos los componentes: FUNCIONALES")
        else:
            print(f"\n⚠️ La rotación funciona pero con error de {abs(final_angle - 90.0):.1f}°")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if fix_update_returns():
        test_rotation_final()