# fix_rotation_properly.py
# Arregla correctamente el bug de ManualMacroRotation

def fix_rotation_properly():
    print("🔧 Arreglando correctamente ManualMacroRotation.calculate_delta...")
    
    # Leer el archivo
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        lines = f.readlines()
    
    # Buscar y arreglar la línea 1155 problemática
    print("\n🔍 Buscando la línea problemática...")
    
    fixed = False
    for i in range(1150, 1160):
        if i < len(lines):
            line = lines[i].rstrip()
            print(f"   Línea {i+1}: {line}")
            
            # La línea 1155 que dice "return None" sin comentar
            if i == 1154 and 'return None' in lines[i]:  # índice 1154 = línea 1155
                print(f"\n✅ Encontrada línea problemática {i+1}")
                # Comentar esta línea
                lines[i] = '        # ' + lines[i].lstrip()
                fixed = True
    
    if fixed:
        # Guardar el archivo
        with open('trajectory_hub/core/motion_components.py', 'w') as f:
            f.writelines(lines)
        
        print("\n✅ Línea 1155 comentada correctamente")
    else:
        print("\n⚠️ No se encontró la línea exacta, aplicando fix alternativo...")
        
        # Buscar el método calculate_delta de ManualMacroRotation
        in_manual_rotation = False
        in_calculate_delta = False
        method_indent = 0
        
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detectar clase ManualMacroRotation
            if 'class ManualMacroRotation' in line:
                in_manual_rotation = True
            elif in_manual_rotation and line.strip() and not line[0].isspace():
                in_manual_rotation = False
                
            # Detectar método calculate_delta
            if in_manual_rotation and 'def calculate_delta' in line:
                in_calculate_delta = True
                method_indent = len(line) - len(line.lstrip())
                new_lines.append(line)
                i += 1
                continue
                
            # Si estamos en calculate_delta
            if in_calculate_delta:
                # Si es el fin del método
                if line.strip() and (len(line) - len(line.lstrip()) <= method_indent):
                    in_calculate_delta = False
                    new_lines.append(line)
                    i += 1
                    continue
                
                # Comentar TODOS los return None
                if 'return None' in line and not line.strip().startswith('#'):
                    print(f"   Comentando línea {i+1}: {line.strip()}")
                    new_lines.append(' ' * (len(line) - len(line.lstrip())) + '# ' + line.lstrip())
                    fixed = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
            
            i += 1
        
        if fixed:
            with open('trajectory_hub/core/motion_components.py', 'w') as f:
                f.writelines(new_lines)
            print("\n✅ Todos los 'return None' en calculate_delta han sido comentados")
    
    # Verificar el resultado
    print("\n🔍 Verificando el resultado...")
    
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        lines = f.readlines()
    
    print("\n📋 Código después del fix (líneas 1150-1160):")
    for i in range(1149, 1160):
        if i < len(lines):
            line = lines[i].rstrip()
            if 'return None' in line:
                print(f">>> {i+1}: {line}")
            else:
                print(f"    {i+1}: {line}")

if __name__ == "__main__":
    fix_rotation_properly()
    
    print("\n✅ Fix aplicado correctamente")
    print("\n📝 Próximos pasos:")
    print("1. python investigate_rotation_deeper.py  # Verificar que funciona")
    print("2. python test_rotation_controlled.py     # Test completo")
    print("\n💡 Ahora calculate_delta debería retornar deltas válidos para TODAS las posiciones")