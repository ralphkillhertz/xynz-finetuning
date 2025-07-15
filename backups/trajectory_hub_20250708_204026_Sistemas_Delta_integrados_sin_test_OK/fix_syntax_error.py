# === fix_syntax_error.py ===
# 🔧 Fix: Error de sintaxis en línea 798
# ⚡ Corregir string literal no cerrado

import os
import re

def fix_syntax_error():
    """Corrige el error de sintaxis en enhanced_trajectory_engine.py"""
    
    print("🔧 FIX: Error de sintaxis en línea 798")
    print("=" * 60)
    
    # Ruta del archivo
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encuentra {file_path}")
        return False
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📄 Total de líneas en el archivo: {len(lines)}")
    
    # Buscar alrededor de la línea 798
    if len(lines) >= 798:
        print("\n🔍 Líneas alrededor de 798:")
        start = max(0, 798 - 5)
        end = min(len(lines), 798 + 5)
        
        for i in range(start, end):
            line_num = i + 1
            line = lines[i].rstrip()
            marker = " <-- ERROR" if line_num == 798 else ""
            print(f"   {line_num}: {line}{marker}")
        
        # Buscar el error específico
        line_798 = lines[797] if len(lines) > 797 else ""
        
        # Buscar print(f" sin cerrar
        if 'print(f"' in line_798 and not (line_798.strip().endswith('")') or line_798.strip().endswith('")')):
            print("\n✅ Error encontrado: f-string no cerrado")
            
            # Buscar el print completo
            full_print = ""
            start_line = 797
            
            # Buscar hacia atrás si es necesario
            while start_line >= 0 and 'print(' not in lines[start_line]:
                start_line -= 1
            
            # Reconstruir el print completo
            i = start_line
            while i < len(lines):
                full_print += lines[i]
                if ')' in lines[i] and not lines[i].strip().endswith(','):
                    break
                i += 1
            
            # Corregir el print
            if 'print(f"' in full_print and '")' not in full_print:
                # Cerrar el f-string correctamente
                lines[797] = lines[797].rstrip() + '")\n'
                print("✅ String cerrado correctamente")
    
    # Buscar otros posibles errores de f-string no cerrados
    print("\n🔍 Buscando otros f-strings no cerrados...")
    
    fixed_count = 0
    for i, line in enumerate(lines):
        # Buscar print(f" que no termina con ")
        if 'print(f"' in line:
            # Verificar si la línea está completa
            stripped = line.strip()
            if stripped.startswith('print(f"') and not (stripped.endswith('")') or '")' in stripped):
                # Si no hay comillas de cierre, añadirlas
                if not line.rstrip().endswith('"'):
                    lines[i] = line.rstrip() + '")\n'
                    fixed_count += 1
                    print(f"   ✅ Corregida línea {i+1}")
    
    if fixed_count > 0:
        print(f"\n✅ Corregidos {fixed_count} f-strings no cerrados")
    
    # Escribir el archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo corregido")
    
    # Verificar sintaxis
    print("\n🔍 Verificando sintaxis...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            compile(f.read(), file_path, 'exec')
        print("✅ Sintaxis correcta")
        return True
    except SyntaxError as e:
        print(f"❌ Todavía hay errores de sintaxis: {e}")
        print(f"   Línea {e.lineno}: {e.text}")
        return False

if __name__ == "__main__":
    if fix_syntax_error():
        print("\n✅ LISTO para ejecutar test_individual_rotations.py")
    else:
        print("\n❌ Necesita más correcciones")