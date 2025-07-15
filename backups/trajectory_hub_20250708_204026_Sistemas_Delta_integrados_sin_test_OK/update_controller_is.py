# === update_controller_is.py ===
# 🔧 Actualizar controlador interactivo con rotaciones IS
# ⚡ Añadir opciones al menú

import os
import re
from datetime import datetime

def update_controller():
    """Añade opciones de rotación IS al controlador interactivo"""
    
    print("🔧 ACTUALIZANDO CONTROLADOR INTERACTIVO")
    print("=" * 60)
    
    # Ruta del archivo
    file_path = "trajectory_hub/interface/interactive_controller.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encuentra {file_path}")
        return False
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # 1. Añadir opciones al menú
    print("\n🔍 Añadiendo opciones al menú...")
    
    # Buscar dónde añadir las opciones (después de las opciones de macro)
    menu_pattern = r'(print\("│ 10\. Toggle.*?│"\))'
    
    menu_additions = '''
        
        # Rotaciones individuales
        print("\\n🔄 ROTACIONES INDIVIDUALES (IS):")
        print("│ 30. Rotación Algorítmica IS    │ Rotación continua individual      │")
        print("│ 31. Rotación Manual IS         │ Rotar a ángulo específico         │")
        print("│ 32. Batch Rotation IS          │ Rotar múltiples fuentes           │")
        print("│ 33. Detener Rotación IS        │ Parar rotación individual         │")'''
    
    # Insertar después de la línea encontrada
    match = re.search(menu_pattern, content)
    if match:
        insert_pos = match.end()
        # Buscar el siguiente print para mantener la estructura
        next_print = content.find('\n        print', insert_pos)
        if next_print > 0:
            content = content[:next_print] + menu_additions + content[next_print:]
            print("✅ Opciones de menú añadidas")
    
    # 2. Añadir los casos en el método run()
    print("\n🔍 Añadiendo casos al método run()...")
    
    cases_code = '''
            elif choice == "30":
                # Rotación algorítmica individual
                try:
                    source_id = int(input("ID de fuente: "))
                    print("Velocidades de rotación (rad/s):")
                    speed_x = float(input("  Velocidad X (default 0): ") or "0")
                    speed_y = float(input("  Velocidad Y (default 1.0): ") or "1.0")
                    speed_z = float(input("  Velocidad Z (default 0): ") or "0")
                    
                    if self.server.set_individual_rotation(source_id, speed_x, speed_y, speed_z):
                        print("✅ Rotación algorítmica configurada")
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            elif choice == "31":
                # Rotación manual individual
                try:
                    source_id = int(input("ID de fuente: "))
                    print("Ángulos objetivo (grados):")
                    yaw = math.radians(float(input("  Yaw (default 90): ") or "90"))
                    pitch = math.radians(float(input("  Pitch (default 0): ") or "0"))
                    roll = math.radians(float(input("  Roll (default 0): ") or "0"))
                    speed = float(input("Velocidad interpolación (0.01-1.0, default 0.1): ") or "0.1")
                    
                    if self.server.set_manual_individual_rotation(source_id, yaw, pitch, roll, speed):
                        print("✅ Rotación manual configurada")
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            elif choice == "32":
                # Batch rotation
                try:
                    ids_str = input("IDs de fuentes (separados por comas): ")
                    source_ids = [int(x.strip()) for x in ids_str.split(',')]
                    
                    print("Velocidades base (rad/s):")
                    speed_x = float(input("  Velocidad X (default 0): ") or "0")
                    speed_y = float(input("  Velocidad Y (default 0.5): ") or "0.5")
                    speed_z = float(input("  Velocidad Z (default 0): ") or "0")
                    offset = float(input("Factor desfase entre fuentes (default 0.1): ") or "0.1")
                    
                    count = self.server.set_batch_individual_rotation(source_ids, speed_x, speed_y, speed_z, offset)
                    print(f"✅ Configuradas {count} fuentes")
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            elif choice == "33":
                # Detener rotación
                try:
                    source_id = int(input("ID de fuente: "))
                    rot_type = input("Tipo (algorithmic/manual/both, default both): ") or "both"
                    
                    if self.server.stop_individual_rotation(source_id, rot_type):
                        print("✅ Rotación detenida")
                except Exception as e:
                    print(f"❌ Error: {e}")'''
    
    # Buscar dónde insertar (después del último elif)
    # Buscar el patrón del último elif antes del else final
    pattern_elif = r'(elif choice == "\d+":[^}]+?)(?=\s*else:)'
    matches = list(re.finditer(pattern_elif, content, re.DOTALL))
    
    if matches:
        last_match = matches[-1]
        insert_pos = last_match.end()
        content = content[:insert_pos] + cases_code + content[insert_pos:]
        print("✅ Casos añadidos al método run()")
    
    # 3. Añadir import de math si no existe
    if 'import math' not in content:
        import_pattern = r'(import.*?\n)'
        content = re.sub(import_pattern, r'\1import math\n', content, count=1)
    
    # Escribir el archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Controlador actualizado con:")
    print("   - Opción 30: Rotación algorítmica IS")
    print("   - Opción 31: Rotación manual IS")
    print("   - Opción 32: Batch rotation IS")
    print("   - Opción 33: Detener rotación IS")
    
    return True

if __name__ == "__main__":
    update_controller()