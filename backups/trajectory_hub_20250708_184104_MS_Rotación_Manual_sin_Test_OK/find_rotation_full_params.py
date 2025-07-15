# find_rotation_full_params.py
# Encuentra la definición completa de set_manual_macro_rotation

def find_full_definition():
    print("🔍 Buscando definición completa de set_manual_macro_rotation...")
    
    with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Buscar el método
    method_start = -1
    for i, line in enumerate(lines):
        if 'def set_manual_macro_rotation' in line:
            method_start = i
            break
    
    if method_start == -1:
        print("❌ No se encontró el método")
        return
    
    print(f"✅ Encontrado en línea {method_start + 1}")
    
    # Mostrar la definición completa (puede ser multilínea)
    print("\n📋 Definición completa:")
    
    # Buscar el final de la definición (hasta el ':')
    definition_lines = []
    i = method_start
    while i < len(lines):
        definition_lines.append(lines[i])
        if ':' in lines[i] and not lines[i].strip().endswith(','):
            break
        i += 1
    
    for line in definition_lines:
        print(f"   {line}")
    
    # Extraer parámetros
    full_def = ' '.join(definition_lines)
    import re
    match = re.search(r'def set_manual_macro_rotation\((.*?)\):', full_def)
    
    if match:
        params_str = match.group(1)
        # Limpiar y dividir parámetros
        params = [p.strip() for p in params_str.split(',') if p.strip()]
        
        print("\n📌 Parámetros encontrados:")
        for p in params:
            if ':' in p:
                name = p.split(':')[0].strip()
                if '=' in p:
                    default = p.split('=')[1].strip()
                    print(f"   - {name} (default: {default})")
                else:
                    print(f"   - {name} (requerido)")
            else:
                print(f"   - {p}")
    
    # Ver cómo se usa en debug_rotation_final.py
    print("\n🔍 Uso en debug_rotation_final.py:")
    
    with open('debug_rotation_final.py', 'r') as f:
        debug_lines = f.read().split('\n')
    
    in_call = False
    call_lines = []
    
    for line in debug_lines:
        if 'set_manual_macro_rotation' in line:
            in_call = True
        
        if in_call:
            call_lines.append(line)
            if ')' in line and not line.strip().endswith(','):
                break
    
    for line in call_lines:
        print(f"   {line}")

if __name__ == "__main__":
    find_full_definition()
    
    print("\n💡 Ahora podemos ver qué parámetros usar")