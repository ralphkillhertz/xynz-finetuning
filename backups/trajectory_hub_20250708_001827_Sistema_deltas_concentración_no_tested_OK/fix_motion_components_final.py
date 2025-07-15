#!/usr/bin/env python3
"""
🔧 Fix: Arregla motion_components.py de forma definitiva
⚡ Problema: Pass añadidos incorrectamente + indentación rota
🎯 Solución: Limpiar y reconstruir correctamente
"""

import re

def clean_and_fix():
    """Limpia y arregla el archivo completamente"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    print("🔧 Limpiando y arreglando motion_components.py...")
    
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    # Primera pasada: eliminar 'pass' incorrectos
    cleaned_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Si es un 'pass' seguido de un docstring o código, eliminarlo
        if stripped == 'pass':
            # Ver qué hay después
            next_non_empty = i + 1
            while next_non_empty < len(lines) and not lines[next_non_empty].strip():
                next_non_empty += 1
            
            if next_non_empty < len(lines):
                next_line = lines[next_non_empty].strip()
                # Si lo siguiente es un docstring o código, eliminar el pass
                if next_line.startswith('"""') or (next_line and not next_line.startswith('def') and not next_line.startswith('class')):
                    print(f"   Eliminando 'pass' innecesario en línea {i+1}")
                    i += 1
                    continue
        
        cleaned_lines.append(line)
        i += 1
    
    # Segunda pasada: arreglar indentación específica
    fixed_lines = []
    
    for i, line in enumerate(cleaned_lines):
        # Buscar docstrings mal indentados después de def
        if i > 0 and cleaned_lines[i-1].strip().endswith(':') and line.strip().startswith('"""'):
            # Calcular indentación correcta
            prev_line = cleaned_lines[i-1]
            prev_indent = len(prev_line) - len(prev_line.lstrip())
            correct_indent = prev_indent + 4
            
            # Aplicar indentación correcta
            fixed_line = ' ' * correct_indent + line.strip() + '\n'
            fixed_lines.append(fixed_line)
            print(f"   Arreglando indentación de docstring en línea {i+1}")
        else:
            fixed_lines.append(line)
    
    # Tercera pasada: añadir pass SOLO donde realmente se necesita
    final_lines = []
    i = 0
    
    while i < len(fixed_lines):
        line = fixed_lines[i]
        final_lines.append(line)
        
        # Si termina con : y necesita un bloque
        if line.strip().endswith(':'):
            # Buscar la siguiente línea no vacía
            next_idx = i + 1
            while next_idx < len(fixed_lines) and not fixed_lines[next_idx].strip():
                next_idx += 1
            
            # Si no hay más líneas o la siguiente tiene menor o igual indentación
            if next_idx >= len(fixed_lines):
                # Añadir pass al final
                indent = len(line) - len(line.lstrip()) + 4
                final_lines.append(' ' * indent + 'pass\n')
                print(f"   Añadiendo 'pass' necesario después de línea {i+1}")
            else:
                next_line = fixed_lines[next_idx]
                current_indent = len(line) - len(line.lstrip())
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # Solo añadir pass si realmente no hay contenido
                if next_indent <= current_indent and not any(
                    keyword in line for keyword in ['if', 'elif', 'else', 'try', 'except', 'finally']
                ):
                    # Verificar que no es parte de una estructura condicional
                    if 'def ' in line or 'class ' in line:
                        indent = current_indent + 4
                        # Insertar pass después de las líneas vacías
                        insert_pos = i + 1
                        while insert_pos < len(final_lines) and not final_lines[insert_pos - 1].strip():
                            insert_pos += 1
                        final_lines.insert(insert_pos - 1, ' ' * indent + 'pass\n')
                        print(f"   Añadiendo 'pass' necesario para método vacío en línea {i+1}")
        
        i += 1
    
    # Guardar
    with open(motion_file, 'w') as f:
        f.writelines(final_lines)
    
    print("✅ Archivo limpiado y arreglado")

def fix_calculate_delta_indentation():
    """Arregla específicamente calculate_delta"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    print("\n🔧 Arreglando calculate_delta específicamente...")
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar calculate_delta y arreglar su indentación
    pattern = r'(\n)(    def calculate_delta.*?)(\n        """.*?""".*?)(\n        if not hasattr)'
    
    def fix_indent(match):
        return match.group(1) + match.group(2) + match.group(3) + '\n        ' + match.group(4).strip()
    
    content = re.sub(pattern, fix_indent, content, flags=re.DOTALL)
    
    # Arreglar la línea problemática
    content = content.replace(
        "        if not hasattr(self, 'enabled'):\n        self.enabled = True",
        "        if not hasattr(self, 'enabled'):\n            self.enabled = True"
    )
    
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print("✅ calculate_delta arreglado")

def final_verification():
    """Verificación final"""
    print("\n🧪 Verificación final...")
    
    try:
        import trajectory_hub.core.motion_components as mc
        print("✅ motion_components importa correctamente")
        
        # Verificar clases importantes
        if hasattr(mc, 'MotionDelta'):
            print("✅ MotionDelta existe")
        
        if hasattr(mc, 'ConcentrationComponent'):
            print("✅ ConcentrationComponent existe")
            
            if hasattr(mc.ConcentrationComponent, 'calculate_delta'):
                print("✅ ConcentrationComponent.calculate_delta existe")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # Mostrar línea específica del error
        if hasattr(e, 'lineno'):
            with open("trajectory_hub/core/motion_components.py", 'r') as f:
                lines = f.readlines()
            
            if e.lineno <= len(lines):
                print(f"\nLínea {e.lineno}: {lines[e.lineno-1].rstrip()}")
        
        return False

if __name__ == "__main__":
    print("🔧 FIX DEFINITIVO DE MOTION_COMPONENTS\n")
    
    # 1. Limpiar y arreglar
    clean_and_fix()
    
    # 2. Arreglar calculate_delta
    fix_calculate_delta_indentation()
    
    # 3. Verificar
    if final_verification():
        print("\n✅ TODO ARREGLADO DEFINITIVAMENTE!")
        print("\n📋 Ahora ejecuta:")
        print("$ python test_delta_final.py")
    else:
        print("\n❌ Aún hay problemas - revisar manualmente")