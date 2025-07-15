# find_rotation_params.py
# Encuentra los parámetros correctos de set_manual_macro_rotation

import inspect

def find_params():
    print("🔍 Buscando parámetros de set_manual_macro_rotation...")
    
    # Buscar la definición del método
    with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Buscar el método
    for i, line in enumerate(lines):
        if 'def set_manual_macro_rotation' in line:
            print(f"\n✅ Encontrado en línea {i + 1}:")
            print(f"   {line.strip()}")
            
            # Mostrar las siguientes líneas para ver la documentación
            for j in range(i+1, min(i+10, len(lines))):
                if lines[j].strip().startswith('"""'):
                    print(f"   {lines[j].strip()}")
                    if lines[j].strip().endswith('"""'):
                        break
            
            # Extraer parámetros
            import re
            match = re.search(r'def set_manual_macro_rotation\((.*?)\):', line)
            if match:
                params = match.group(1)
                print(f"\n📋 Parámetros: {params}")
                
                # Analizar cada parámetro
                param_list = [p.strip() for p in params.split(',')]
                print("\n📌 Parámetros individuales:")
                for p in param_list:
                    if '=' in p:
                        name, default = p.split('=')
                        print(f"   - {name.strip()} (default: {default.strip()})")
                    else:
                        print(f"   - {p}")
            
            break
    
    # También buscar cómo se usa en debug_rotation_final.py
    print("\n🔍 Verificando uso en debug_rotation_final.py...")
    
    with open('debug_rotation_final.py', 'r') as f:
        debug_content = f.read()
    
    for line in debug_content.split('\n'):
        if 'set_manual_macro_rotation' in line:
            print(f"   Uso: {line.strip()}")

if __name__ == "__main__":
    find_params()
    
    print("\n💡 Usa los parámetros correctos encontrados arriba")