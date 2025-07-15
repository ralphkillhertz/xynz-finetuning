# === fix_update_with_deltas_macro_rotation.py ===
# 🔧 Fix: Asegurar que update_with_deltas procese macro_rotation
# ⚡ ÚLTIMO FIX - Sin esto no hay movimiento

import os
import re

def fix_update_with_deltas():
    """Asegurar que update_with_deltas procese macro_rotation"""
    
    file_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Buscando update_with_deltas en SourceMotion...")
    
    # Buscar el método update_with_deltas
    pattern = r'(class SourceMotion.*?def update_with_deltas\s*\([^)]*\):.*?)(return deltas)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ No se encontró update_with_deltas")
        return False
    
    method_content = match.group(1)
    print("✅ Método encontrado")
    
    # Buscar el orden de componentes
    component_order_pattern = r'component_order\s*=\s*\[(.*?)\]'
    order_match = re.search(component_order_pattern, method_content, re.DOTALL)
    
    if order_match:
        components = order_match.group(1)
        print(f"\n📋 Orden actual de componentes: {components}")
        
        if "'macro_rotation'" not in components and '"macro_rotation"' not in components:
            print("❌ macro_rotation NO está en el orden")
            
            # Añadir macro_rotation después de macro_trajectory
            if "'macro_trajectory'" in components:
                new_components = components.replace("'macro_trajectory'", "'macro_trajectory', 'macro_rotation'")
            elif '"macro_trajectory"' in components:
                new_components = components.replace('"macro_trajectory"', '"macro_trajectory", "macro_rotation"')
            else:
                # Añadir al final
                new_components = components.rstrip() + ", 'macro_rotation'"
            
            # Reemplazar
            new_method = method_content.replace(
                f'component_order = [{components}]',
                f'component_order = [{new_components}]'
            )
            
            # Actualizar el contenido
            new_content = content.replace(method_content, new_method)
            
            print(f"✅ Añadido macro_rotation al orden")
            
        else:
            print("✅ macro_rotation ya está en el orden")
            # Verificar si hay algún problema con el procesamiento
            
            # Buscar dónde se procesa cada componente
            if "for comp_name in component_order:" in method_content:
                print("\n🔍 Verificando bucle de procesamiento...")
                # El código parece correcto
                new_content = content
            else:
                print("⚠️ No se encontró el bucle de procesamiento esperado")
                new_content = content
    else:
        print("❌ No se encontró component_order")
        
        # Buscar una forma alternativa
        # Buscar si hay una lista hardcodeada
        if "'concentration'" in method_content:
            print("\n🔍 Buscando procesamiento directo...")
            
            # Insertar macro_rotation
            lines = method_content.split('\n')
            new_lines = []
            
            for line in lines:
                new_lines.append(line)
                # Después de procesar macro_trajectory, añadir macro_rotation
                if "'macro_trajectory' in self.active_components" in line:
                    # Encontrar la indentación
                    indent = len(line) - len(line.lstrip())
                    new_lines.extend([
                        '',
                        ' ' * indent + "# Procesar macro_rotation",
                        ' ' * indent + "if 'macro_rotation' in self.active_components:",
                        ' ' * (indent + 4) + "comp = self.active_components['macro_rotation']",
                        ' ' * (indent + 4) + "if comp and comp.enabled and hasattr(comp, 'calculate_delta'):",
                        ' ' * (indent + 8) + "delta = comp.calculate_delta(self.state, current_time, dt)",
                        ' ' * (indent + 8) + "if delta:",
                        ' ' * (indent + 12) + "deltas.append(delta)",
                    ])
            
            new_method = '\n'.join(new_lines)
            new_content = content.replace(method_content, new_method)
            print("✅ Añadido procesamiento de macro_rotation")
        else:
            new_content = content
    
    # Guardar si hubo cambios
    if new_content != content:
        import shutil
        from datetime import datetime
        backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"\n✅ Archivo actualizado")
        print(f"📦 Backup: {backup_name}")
        return True
    else:
        # Mostrar el método actual para debug
        print("\n📋 Mostrando update_with_deltas actual:")
        lines = content.split('\n')
        in_method = False
        count = 0
        
        for i, line in enumerate(lines):
            if 'def update_with_deltas' in line and 'SourceMotion' in content[max(0, i-100):i]:
                in_method = True
            
            if in_method:
                print(f"{i+1:4d}: {line}")
                count += 1
                
                if count > 40:  # Mostrar 40 líneas
                    break
                
                if 'return' in line and not line.strip().startswith('#'):
                    break
        
        return False

if __name__ == "__main__":
    print("🔧 Arreglando update_with_deltas...")
    
    if fix_update_with_deltas():
        print("\n✅ Fix aplicado - ÚLTIMO PASO")
        print("📝 Ejecuta: python test_macro_rotation_final_working.py")
        print("\n🎉 Si funciona, MacroRotation estará 100% operativo!")
    else:
        print("\n⚠️ Revisar manualmente")