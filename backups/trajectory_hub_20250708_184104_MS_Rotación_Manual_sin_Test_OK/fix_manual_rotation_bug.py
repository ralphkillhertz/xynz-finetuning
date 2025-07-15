# fix_manual_rotation_bug.py
# Corrige el bug en ManualMacroRotation.calculate_delta

def fix_rotation_bug():
    print("🔧 Corrigiendo bug en ManualMacroRotation.calculate_delta...")
    
    # Leer el archivo
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Buscar y reemplazar las líneas problemáticas
    fixed = False
    new_lines = []
    
    for i, line in enumerate(lines):
        # Línea problemática 1: retorna None si el delta es pequeño
        if i > 1150 and 'if np.linalg.norm(delta.position) < 0.0001:' in line:
            print(f"   Encontrada línea problemática {i+1}: {line.strip()}")
            # Comentar esta condición
            new_lines.append('        # BUGFIX: No retornar None para deltas pequeños')
            new_lines.append('        # ' + line)
            # Siguiente línea (return None)
            if i+1 < len(lines) and 'return None' in lines[i+1]:
                new_lines.append('        # ' + lines[i+1])
                i += 1  # Saltar la siguiente línea
                fixed = True
                continue
        else:
            new_lines.append(line)
    
    if not fixed:
        print("⚠️ No se encontró la línea exacta, buscando alternativa...")
        
        # Buscar de otra forma
        new_lines = []
        for i, line in enumerate(lines):
            if 'return None' in line and i > 1150 and i < 1160:
                # Verificar contexto
                if i > 0 and 'np.linalg.norm(delta.position)' in lines[i-1]:
                    print(f"   Encontrado return None problemático en línea {i+1}")
                    # Comentar las dos líneas
                    new_lines[-1] = '        # BUGFIX: ' + new_lines[-1].lstrip()
                    new_lines.append('        # ' + line)
                    # Añadir código correcto
                    new_lines.append('        # Siempre retornar el delta, incluso si es pequeño')
                    fixed = True
                    continue
            new_lines.append(line)
    
    if fixed:
        # Guardar el archivo corregido
        with open('trajectory_hub/core/motion_components.py', 'w') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Bug corregido - Las fuentes con X=0 ahora deberían rotar correctamente")
    else:
        print("❌ No se pudo aplicar el fix automáticamente")
        print("\n📋 Fix manual:")
        print("   1. Abrir trajectory_hub/core/motion_components.py")
        print("   2. Buscar ManualMacroRotation.calculate_delta")
        print("   3. Comentar o eliminar las líneas:")
        print("      if np.linalg.norm(delta.position) < 0.0001:")
        print("          return None")
        print("   4. El método siempre debe retornar el delta")
    
    # También buscar otros posibles problemas
    print("\n🔍 Buscando otros posibles problemas...")
    
    # Buscar divisiones que podrían causar problemas con X=0
    for i, line in enumerate(lines):
        if 'rel_pos[0]' in line and '/' in line:
            print(f"   ⚠️ Posible división por X en línea {i+1}: {line.strip()}")

if __name__ == "__main__":
    fix_rotation_bug()
    
    print("\n📝 Próximos pasos:")
    print("1. python test_rotation_controlled.py")
    print("2. Todas las fuentes deberían rotar ahora")
    print("\n💡 El bug era que retornaba None para deltas pequeños")
    print("   Esto afectaba a fuentes con X=0 por algún cálculo interno")