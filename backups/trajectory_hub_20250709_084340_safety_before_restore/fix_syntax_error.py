# === fix_syntax_error.py ===
# 🔧 Fix: Corregir error de sintaxis en set_individual_rotation
# ⚡ Solución rápida para SyntaxError

import os

def fix_syntax_error():
    """Arreglar error de sintaxis en línea 692"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_syntax', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    # Buscar y corregir la línea problemática
    for i, line in enumerate(lines):
        if i == 691:  # Línea 692 (índice 691)
            print(f"🔍 Línea {i+1} actual: {line.strip()}")
            
            # Corregir sintaxis
            if 'center=None: int,' in line:
                lines[i] = line.replace('center=None: int,', 'center=None):\n')
                print(f"✅ Línea corregida")
            elif 'def set_individual_rotation' in line and line.strip().endswith(','):
                # Quitar la coma final y cerrar paréntesis
                lines[i] = line.rstrip().rstrip(',') + '):\n'
                print(f"✅ Línea corregida (quitada coma final)")
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Sintaxis corregida")

def verify_and_run_test():
    """Verificar corrección y ejecutar test"""
    
    print("\n🔍 Verificando corrección...")
    
    # Intentar importar
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        print("✅ Import exitoso")
        
        # Ejecutar test
        print("\n🚀 Ejecutando test...")
        import subprocess
        result = subprocess.run(['python', 'test_delta_final_fixed.py'], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Aplicando corrección adicional...")
        
        # Buscar la línea exacta del problema
        file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i in range(690, min(700, len(lines))):
            if 'def set_individual_rotation' in lines[i]:
                print(f"Encontrada definición en línea {i+1}: {lines[i].strip()}")
                
                # Reconstruir la línea completa
                full_def = lines[i].strip()
                j = i + 1
                while j < len(lines) and not lines[j].strip().endswith(':'):
                    full_def += ' ' + lines[j].strip()
                    j += 1
                
                print(f"Definición completa: {full_def}")
                
                # Crear definición corregida
                corrected = "    def set_individual_rotation(self, source_id: int, speed_x=0.0, speed_y=0.0, speed_z=0.0, center=None):\n"
                
                # Reemplazar
                lines[i] = corrected
                # Eliminar líneas extras si las hay
                if j > i + 1:
                    del lines[i+1:j]
                
                # Guardar
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                print("✅ Definición corregida")
                break

if __name__ == "__main__":
    print("🔧 FIXING SYNTAX ERROR")
    print("=" * 60)
    
    fix_syntax_error()
    verify_and_run_test()