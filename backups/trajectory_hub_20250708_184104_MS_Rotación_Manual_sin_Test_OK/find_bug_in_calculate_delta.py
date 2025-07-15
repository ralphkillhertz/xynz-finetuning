# find_bug_in_calculate_delta.py
# Encuentra el bug exacto en calculate_delta

def find_bug():
    print("🔍 Buscando el bug exacto en calculate_delta...")
    
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        lines = f.readlines()
    
    # Buscar alrededor de la línea 1153
    print("\n📋 Código alrededor de la línea 1153 (return None):")
    
    start = max(0, 1153 - 10)
    end = min(len(lines), 1153 + 5)
    
    for i in range(start, end):
        line = lines[i].rstrip()
        if i == 1152:  # Línea 1153 (índice 1152)
            print(f">>> {i+1:4d}: {line} <<<")
        else:
            print(f"    {i+1:4d}: {line}")
    
    # Buscar más contexto
    print("\n📋 Buscando más contexto (líneas 1130-1160):")
    
    for i in range(1130, min(1160, len(lines))):
        line = lines[i].rstrip()
        if 'if' in line or 'return' in line:
            print(f"{i+1:4d}: {line}")
    
    # Buscar división por cero o condiciones con rel_pos
    print("\n🔍 Buscando condiciones problemáticas:")
    
    in_calculate_delta = False
    for i, line in enumerate(lines):
        if 'def calculate_delta' in line and 'ManualMacroRotation' in ''.join(lines[max(0,i-20):i]):
            in_calculate_delta = True
            continue
            
        if in_calculate_delta:
            if line.strip() and not line.startswith(' '):
                break
                
            # Buscar divisiones o condiciones con posición
            if ('/' in line and 'rel_pos' in line) or \
               ('if' in line and ('rel_pos' in line or 'distance' in line or '< 0.001' in line)):
                print(f"{i+1:4d}: {line.rstrip()}")

if __name__ == "__main__":
    find_bug()
    
    print("\n💡 El bug probablemente está en:")
    print("   - Una condición que verifica si rel_pos[0] es muy pequeño")
    print("   - O una división por la distancia cuando está cerca del centro")
    print("   - O una verificación de distancia mínima")