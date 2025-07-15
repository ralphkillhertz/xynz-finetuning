# === fix_import_closure.py ===
# 🔧 Fix: Arreglar cierre prematuro de import
# ⚡ Línea 40 termina con ,) pero línea 41 continúa

import os

def fix_import_closure():
    """Arreglar imports mal cerrados"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_closure', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Arreglando imports mal cerrados...")
    
    # Mostrar contexto del problema
    print("\n📋 Contexto del error:")
    for i in range(37, min(45, len(lines))):
        if i < len(lines):
            marker = ">>>" if i == 40 else "   "
            print(f"{marker} {i+1}: {lines[i].rstrip()}")
    
    # Arreglar línea 40 - quitar el ) extra
    if 39 < len(lines) and lines[39].rstrip().endswith(',)'):
        print("\n✅ Quitando ) extra de línea 40")
        lines[39] = lines[39].replace(',)', ',\n')
    
    # Arreglar línea 41 - asegurar indentación correcta
    if 40 < len(lines):
        # La línea 41 debe tener la misma indentación que la 40
        if 39 < len(lines):
            indent_40 = len(lines[39]) - len(lines[39].lstrip())
            lines[40] = ' ' * indent_40 + lines[40].lstrip()
            print("✅ Corregida indentación de línea 41")
    
    # Buscar y arreglar otros imports con problemas similares
    for i in range(len(lines)):
        line = lines[i]
        
        # Si una línea termina con ,) y la siguiente está indentada
        if line.rstrip().endswith(',)') and i+1 < len(lines):
            next_line = lines[i+1]
            if next_line.strip() and not next_line.strip().startswith(('from', 'import', '#', 'def', 'class')):
                # La siguiente línea probablemente es continuación del import
                print(f"❌ Import mal cerrado en línea {i+1}")
                lines[i] = line.replace(',)', ',\n')
                print(f"✅ Arreglado")
    
    # Asegurar que todos los imports multi-línea estén bien cerrados
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith('from ') and '(' in lines[i]:
            # Encontrar dónde se cierra
            j = i + 1
            indent = len(lines[i]) - len(lines[i].lstrip())
            
            while j < len(lines) and j < i + 20:
                if ')' in lines[j]:
                    break
                elif lines[j].strip() and not lines[j].strip().startswith('#'):
                    # Asegurar indentación correcta
                    expected_indent = indent + 4
                    actual_indent = len(lines[j]) - len(lines[j].lstrip())
                    if actual_indent != expected_indent:
                        lines[j] = ' ' * expected_indent + lines[j].lstrip()
                j += 1
        i += 1
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Imports corregidos")

def test_syntax():
    """Test final de sintaxis y funcionalidad"""
    print("\n🧪 Test de sintaxis...")
    
    import subprocess
    
    # Compilar para verificar sintaxis
    result = subprocess.run(
        ['python', '-m', 'py_compile', 'trajectory_hub/core/enhanced_trajectory_engine.py'],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print("✅ ¡SINTAXIS CORRECTA!")
        
        # Test del sistema
        print("\n🚀 Ejecutando test del sistema de deltas...")
        
        try:
            # Import directo
            from trajectory_hub.core import EnhancedTrajectoryEngine
            print("✅ Import exitoso")
            
            # Test mínimo
            engine = EnhancedTrajectoryEngine(n_sources=5)
            macro = engine.create_macro("test", source_count=3)
            print("✅ Engine y macro creados")
            
            # Test completo
            result = subprocess.run(['python', 'test_delta_100.py'], 
                                  capture_output=True, text=True, timeout=15)
            
            # Mostrar resultados
            if result.stdout:
                print("\n📊 Resultados del test:")
                lines = result.stdout.split('\n')
                for line in lines:
                    if any(word in line.lower() for word in ['resumen', 'final', '%', 'funcional', 'concentración']):
                        print(line)
                        
            if result.returncode == 0 and '100%' in result.stdout:
                print("\n🎉 ¡SISTEMA DE DELTAS 100% FUNCIONAL!")
            else:
                # Buscar porcentaje
                import re
                match = re.search(r'(\d+)%', result.stdout)
                if match:
                    print(f"\n📊 Sistema de deltas al {match.group(1)}%")
                    
        except Exception as e:
            print(f"❌ Error en test: {type(e).__name__}: {str(e)[:200]}")
            
    else:
        print(f"❌ Error de sintaxis:\n{result.stderr}")

if __name__ == "__main__":
    print("🔧 FIXING IMPORT CLOSURE")
    print("=" * 60)
    
    fix_import_closure()
    test_syntax()