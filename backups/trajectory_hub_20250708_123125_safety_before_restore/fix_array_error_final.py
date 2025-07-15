# === fix_array_error_final.py ===
# 🔧 Fix: Error array ambiguous en línea 710
# ⚡ Solución específica
# 🎯 Impacto: CRÍTICO

import shutil
from datetime import datetime

def fix_line_710():
    """Arregla el error en línea 710 que aún persiste"""
    
    file_path = "trajectory_hub/core/motion_components.py"
    
    # Backup
    backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(file_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Leer archivo
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    fixes_applied = 0
    
    # Buscar y arreglar línea 710
    for i in range(700, min(720, len(lines))):  # Buscar alrededor de línea 710
        line = lines[i]
        
        # Buscar la línea problemática
        if 'self.enabled = (abs(sx) > 0.001) or' in line:
            print(f"\n🔍 Encontrado problema en línea {i+1}:")
            print(f"   Antes: {line.strip()}")
            
            # Ver las líneas anteriores para entender el contexto
            print("\n   Contexto:")
            for j in range(max(0, i-5), i):
                print(f"   {j+1}: {lines[j].rstrip()}")
            
            # Buscar dónde se definen sx, sy, sz
            # Probablemente necesitan conversión a float
            for j in range(max(0, i-10), i):
                if 'sx =' in lines[j] or 'sy =' in lines[j] or 'sz =' in lines[j]:
                    print(f"\n   🔍 Definición encontrada en línea {j+1}:")
                    print(f"      {lines[j].strip()}")
                    
                    # Si no tiene conversión a float, agregarla
                    if 'float(' not in lines[j] and 'if hasattr' not in lines[j]:
                        # Reemplazar la línea
                        var_name = lines[j].split('=')[0].strip()
                        value_part = lines[j].split('=')[1].strip()
                        indent = lines[j][:len(lines[j]) - len(lines[j].lstrip())]
                        
                        new_line = f"{indent}{var_name} = float({value_part}) if not hasattr({value_part}, '__len__') else float({value_part}[0] if len({value_part}) > 0 else 0.0)\n"
                        
                        print(f"      Reemplazando con: {new_line.strip()}")
                        lines[j] = new_line
                        fixes_applied += 1
            
            break
    
    if fixes_applied > 0:
        # Escribir archivo
        with open(file_path, "w") as f:
            f.writelines(lines)
        
        print(f"\n✅ Archivo corregido - {fixes_applied} líneas modificadas")
    else:
        print("\n⚠️ No se encontraron líneas para corregir")
        print("   Buscando el error manualmente...")
        
        # Buscar cualquier línea con 'or' y comparaciones
        for i, line in enumerate(lines):
            if ' or ' in line and '>' in line and 'self.enabled' in line:
                print(f"\n   Línea {i+1}: {line.strip()}")

if __name__ == "__main__":
    print("🔧 Arreglando error array ambiguous línea 710")
    print("=" * 50)
    fix_line_710()
    
    print("\n📝 Próximo paso:")
    print("   python test_rotation_ms_final.py")