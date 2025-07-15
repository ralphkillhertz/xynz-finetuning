# === fix_init_definition.py ===
# 🔧 Fix: Arreglar definición de __init__
# ⚡ Falta cerrar paréntesis antes de :

import os

def fix_init_definition():
    """Arreglar definición de __init__ mal cerrada"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_init', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Arreglando definición de __init__...")
    
    # Mostrar contexto
    print("\n📋 Contexto del error:")
    for i in range(104, min(115, len(lines))):
        if i < len(lines):
            marker = ">>>" if i == 108 else "   "
            print(f"{marker} {i+1}: {lines[i].rstrip()}")
    
    # Arreglar línea 109
    if 108 < len(lines):
        line = lines[108]
        if 'enable_modulator: bool = True:' in line:
            print("\n✅ Arreglando línea 109")
            lines[108] = line.replace('True:', 'True):\n')
        elif line.rstrip().endswith(':') and ')' not in line:
            # Añadir paréntesis antes de :
            lines[108] = line.rstrip()[:-1] + '):\n'
            print("\n✅ Añadido ) antes de :")
    
    # Buscar otros métodos con el mismo problema
    print("\n🔍 Buscando otros métodos con problemas similares...")
    fixes = 0
    
    for i in range(len(lines)):
        line = lines[i].strip()
        
        # Si es una línea que parece ser el último parámetro de una función
        if (line.endswith(':') and 
            '=' in line and 
            ')' not in line and
            i > 0 and ('def ' in lines[i-1] or ',' in lines[i-1])):
            
            # Verificar que no sea una línea de código normal
            if not any(keyword in line for keyword in ['if ', 'for ', 'while ', 'with ']):
                print(f"❌ Posible error en línea {i+1}: {line}")
                lines[i] = lines[i].rstrip()[:-1] + '):\n'
                fixes += 1
                print("✅ Arreglado")
    
    if fixes > 0:
        print(f"\n✅ Total de {fixes + 1} correcciones aplicadas")
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo guardado")

def test_and_run():
    """Test completo del sistema"""
    print("\n🧪 Verificando sintaxis...")
    
    import subprocess
    import ast
    
    # Primero verificar sintaxis
    try:
        with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
            ast.parse(f.read())
        
        print("✅ ¡SINTAXIS CORRECTA!")
        
        # Import test
        print("\n🔍 Verificando imports...")
        try:
            from trajectory_hub.core import EnhancedTrajectoryEngine
            print("✅ Import exitoso")
            
            # Test básico
            engine = EnhancedTrajectoryEngine(max_sources=5)
            print("✅ Engine creado")
            
            # Test completo
            print("\n🚀 Ejecutando test del sistema de deltas...")
            result = subprocess.run(['python', 'test_delta_100.py'], 
                                  capture_output=True, text=True, timeout=20)
            
            # Analizar resultados
            if result.stdout:
                lines = result.stdout.split('\n')
                
                # Buscar resumen
                showing = False
                for line in lines:
                    if 'RESUMEN FINAL' in line:
                        showing = True
                    if showing or any(word in line for word in ['%', 'funcional', 'Concentración']):
                        print(line)
                
                # Verificar éxito
                if '100%' in result.stdout:
                    print("\n🎉 ¡SISTEMA DE DELTAS 100% FUNCIONAL!")
                elif 'Error' in result.stdout:
                    print("\n⚠️ El sistema tiene errores")
                else:
                    import re
                    match = re.search(r'(\d+)%', result.stdout)
                    if match:
                        print(f"\n📊 Sistema al {match.group(1)}% funcional")
                        
        except ImportError as e:
            print(f"❌ Error de import: {e}")
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {str(e)[:200]}")
            
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en línea {e.lineno}")
        print(f"   {e.text}")

if __name__ == "__main__":
    print("🔧 FIXING __INIT__ DEFINITION")
    print("=" * 60)
    
    fix_init_definition()
    test_and_run()