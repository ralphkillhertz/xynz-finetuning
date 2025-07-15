# === fix_line_710_definitive.py ===
# 🔧 Fix: Solución DEFINITIVA para línea 710
# ⚡ Cambiar lógica del 'or'
# 🎯 Impacto: CRÍTICO

import shutil
from datetime import datetime

def fix_line_710_definitivo():
    """Arregla definitivamente el error en línea 710"""
    
    file_path = "trajectory_hub/core/motion_components.py"
    
    # Backup
    backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(file_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Leer archivo
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    fixed = False
    
    # Buscar y arreglar la línea problemática
    for i in range(len(lines)):
        line = lines[i]
        
        # Buscar la línea exacta con el problema
        if 'self.enabled = (abs(sx) > 0.001) or (abs(sy) > 0.001) or (abs(sz) > 0.001)' in line:
            print(f"\n🔍 Encontrado problema en línea {i+1}:")
            print(f"   Antes: {line.strip()}")
            
            # Reemplazar con lógica que no use 'or'
            indent = line[:len(line) - len(line.lstrip())]
            
            # Nueva lógica sin 'or'
            new_line = f"{indent}self.enabled = any([abs(sx) > 0.001, abs(sy) > 0.001, abs(sz) > 0.001])\n"
            
            lines[i] = new_line
            print(f"   Después: {new_line.strip()}")
            fixed = True
            break
    
    if not fixed:
        # Buscar patrón alternativo
        print("\n🔍 Buscando patrón alternativo...")
        for i in range(700, min(720, len(lines))):
            if i < len(lines):
                line = lines[i]
                if 'self.enabled' in line and ' or ' in line and 'abs(' in line:
                    print(f"\n📍 Encontrado en línea {i+1}:")
                    print(f"   {line.strip()}")
                    
                    # Si contiene el patrón problemático
                    if '(abs(sx)' in line or '(abs(sy)' in line or '(abs(sz)' in line:
                        indent = line[:len(line) - len(line.lstrip())]
                        new_line = f"{indent}self.enabled = any([abs(sx) > 0.001, abs(sy) > 0.001, abs(sz) > 0.001])\n"
                        lines[i] = new_line
                        print(f"   Cambiado a: {new_line.strip()}")
                        fixed = True
                        break
    
    if fixed:
        # Escribir archivo
        with open(file_path, "w") as f:
            f.writelines(lines)
        
        print("\n✅ Archivo corregido exitosamente")
        print("   Usando any() en lugar de 'or' para evitar problemas con arrays")
    else:
        print("\n❌ No se encontró la línea problemática")
        
        # Mostrar contexto alrededor de línea 710
        print("\n📋 Contexto alrededor de línea 710:")
        for i in range(705, min(715, len(lines))):
            if i < len(lines):
                print(f"   {i+1}: {lines[i].rstrip()}")

if __name__ == "__main__":
    print("🔧 Fix DEFINITIVO para error array ambiguous")
    print("=" * 50)
    fix_line_710_definitivo()
    
    print("\n📝 Próximo paso:")
    print("   python test_rotation_ms_final.py")