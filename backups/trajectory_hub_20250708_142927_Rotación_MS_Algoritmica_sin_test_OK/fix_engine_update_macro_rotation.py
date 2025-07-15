# === fix_engine_update_macro_rotation.py ===
# 🔧 Fix: Asegurar que engine.update() procese macro_rotation
# ⚡ Impacto: CRÍTICO - Sin esto no hay movimiento

import os
import re

def fix_engine_update():
    """Asegurar que update() procese macro_rotation"""
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método update
    print("🔍 Buscando método update()...")
    
    # Buscar la sección donde se procesan deltas
    pattern = r'(def update\s*\(.*?\):.*?)(# Procesar deltas de todos los motion_states.*?)(for source_id, motion in self\.motion_states\.items\(\):.*?)(if motion\.state:.*?)(# Aplicar deltas a las posiciones)'
    
    def check_macro_rotation(content):
        """Verificar si macro_rotation está en la lista de componentes a procesar"""
        # Buscar donde se define qué componentes procesar
        if 'macro_rotation' in content:
            return True
        return False
    
    if not check_macro_rotation(content):
        print("⚠️ macro_rotation no está siendo procesado")
        
        # Buscar donde se procesan los componentes
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'components_to_process = [' in line or 'component_order = [' in line:
                print(f"📍 Encontrada lista de componentes en línea {i+1}")
                # Verificar las siguientes líneas
                for j in range(i, min(i+10, len(lines))):
                    print(f"  {lines[j]}")
                    if ']' in lines[j]:
                        # Insertar macro_rotation si no está
                        if 'macro_rotation' not in content[lines[i]:lines[j]]:
                            # Añadir macro_rotation antes del cierre
                            lines[j-1] = lines[j-1] + ",\n            'macro_rotation'"
                            print("✅ Añadido 'macro_rotation' a la lista")
                            content = '\n'.join(lines)
                        break
    
    # Si no encontramos una lista específica, buscar el método update completo
    if 'def update' in content:
        # Buscar si procesa active_components
        update_section = re.search(r'def update\s*\([^)]*\):(.*?)(?=\n    def|\nclass|\Z)', content, re.DOTALL)
        
        if update_section:
            update_content = update_section.group(1)
            
            # Verificar si procesa active_components correctamente
            if 'active_components' in update_content and 'calculate_delta' in update_content:
                print("✅ update() parece procesar componentes")
                
                # Verificar específicamente macro_rotation
                if "'macro_rotation'" not in update_content:
                    print("⚠️ Pero no menciona específicamente macro_rotation")
                    
                    # Buscar donde añadir el procesamiento
                    # Típicamente después de macro_trajectory
                    if "'macro_trajectory'" in update_content:
                        print("📍 Añadiendo después de macro_trajectory")
                        content = content.replace(
                            "'macro_trajectory'",
                            "'macro_trajectory',\n                    'macro_rotation'"
                        )
            else:
                print("❌ update() no procesa active_components correctamente")
    
    # Verificar si se hizo algún cambio
    if content != open(file_path, 'r', encoding='utf-8').read():
        # Backup
        import shutil
        from datetime import datetime
        backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_name)
        
        # Escribir
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Archivo actualizado")
        return True
    
    # Si no se hizo cambio, mostrar el método update actual
    print("\n📋 Mostrando método update() actual:")
    lines = content.split('\n')
    in_update = False
    update_lines = []
    
    for i, line in enumerate(lines):
        if 'def update' in line and '(self' in line:
            in_update = True
            indent = len(line) - len(line.lstrip())
        
        if in_update:
            update_lines.append(f"{i+1:4d}: {line}")
            
            # Si es otro método al mismo nivel, terminar
            if line.strip().startswith('def ') and len(line) - len(line.lstrip()) <= indent and 'def update' not in line:
                break
    
    # Mostrar solo las líneas relevantes
    print("\n".join(update_lines[:50]))  # Primeras 50 líneas
    
    return False

if __name__ == "__main__":
    print("🔧 Verificando procesamiento de macro_rotation en update()...")
    
    if fix_engine_update():
        print("\n✅ Fix aplicado")
        print("📝 Ejecuta: python test_macro_rotation_final_working.py")
    else:
        print("\n⚠️ Revisar manualmente el método update()")
        print("\n💡 Buscar donde dice 'components_to_process' o similar")
        print("   y añadir 'macro_rotation' a la lista")