import os
import re
import subprocess

def find_by_exact_text():
    """Buscar el texto exacto que aparece en pantalla"""
    print("🔍 BÚSQUEDA POR TEXTO EXACTO DEL MENÚ")
    print("="*60)
    
    # Texto exacto que aparece
    search_terms = [
        "Formación inicial",
        "circle",
        "line", 
        "grid",
        "spiral",
        "random"
    ]
    
    # Buscar en TODO el proyecto
    print("\n🔍 Buscando 'Formación inicial' en todo el proyecto...")
    
    try:
        result = subprocess.run(
            ["grep", "-r", "-n", "Formación inicial", "trajectory_hub/"],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print("✅ ENCONTRADO:")
            print(result.stdout)
            
            # Extraer archivos
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if ':' in line:
                    filepath = line.split(':')[0]
                    line_num = line.split(':')[1]
                    print(f"\n📍 Archivo: {filepath}")
                    print(f"📍 Línea: {line_num}")
                    
                    # Mostrar contexto
                    show_context(filepath, int(line_num))
        else:
            print("❌ No encontré 'Formación inicial'")
            
            # Buscar alternativas
            print("\n🔍 Buscando donde se imprimen las formaciones...")
            
            # Buscar patrones de print con formaciones
            patterns = [
                "print.*1.*circle",
                "print.*circle.*line.*grid",
                "options.*circle.*line",
                '"1".*circle.*"2".*line'
            ]
            
            for pattern in patterns:
                print(f"\n🔍 Buscando patrón: {pattern}")
                result = subprocess.run(
                    ["grep", "-r", "-E", "-n", pattern, "trajectory_hub/"],
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    print("✅ Encontrado:")
                    lines = result.stdout.strip().split('\n')[:3]  # Primeros 3
                    for line in lines:
                        print(f"   {line}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Buscar en el command processor que es donde debe estar
    print("\n\n🔍 BÚSQUEDA ESPECÍFICA EN COMMAND PROCESSOR...")
    check_command_processor()

def show_context(filepath, line_num):
    """Mostrar contexto alrededor de la línea"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        start = max(0, line_num - 15)
        end = min(len(lines), line_num + 15)
        
        print(f"\n📄 Contexto ({filepath}):")
        for i in range(start, end):
            marker = ">>>" if i == line_num - 1 else "   "
            print(f"{marker} {i+1}: {lines[i].rstrip()}")
            
    except Exception as e:
        print(f"❌ Error mostrando contexto: {e}")

def check_command_processor():
    """Verificar específicamente el CommandProcessor"""
    cp_file = "trajectory_hub/control/processors/command_processor.py"
    
    if os.path.exists(cp_file):
        print(f"\n📂 Analizando: {cp_file}")
        
        with open(cp_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar handle_create_macro
        for i, line in enumerate(lines):
            if "handle_create_macro" in line or "create_macro" in line:
                print(f"\n📍 Método create_macro en línea {i+1}")
                
                # Buscar formaciones cerca
                for j in range(i, min(len(lines), i + 50)):
                    if any(formation in lines[j] for formation in ["circle", "line", "grid"]):
                        print(f"   ✅ Formaciones en línea {j+1}: {lines[j][:80]}")
                        
                        # Mostrar más contexto
                        start = max(0, j - 5)
                        end = min(len(lines), j + 10)
                        
                        print("\n   📄 Contexto:")
                        for k in range(start, end):
                            marker = ">>>" if k == j else "   "
                            print(f"   {marker} {k+1}: {lines[k]}")
                        
                        return cp_file, j+1
    
    # Buscar en CLIInterface
    cli_file = "trajectory_hub/control/interfaces/cli_interface.py"
    if os.path.exists(cli_file):
        print(f"\n📂 Analizando: {cli_file}")
        
        with open(cli_file, 'r') as f:
            content = f.read()
        
        if "circle" in content and "line" in content:
            print("✅ CLIInterface contiene formaciones")
            
            # Buscar el menú
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "1." in line and "circle" in line:
                    print(f"\n✅ MENÚ ENCONTRADO en línea {i+1}")
                    show_context(cli_file, i+1)
                    return cli_file, i+1

if __name__ == "__main__":
    result = find_by_exact_text()
    
    print("\n\n💡 SOLUCIÓN DIRECTA:")
    print("Si no encuentro el archivo, puedes añadir sphere manualmente:")
    print("1. Busca donde dice '5. random'")
    print("2. Añade después: '  6. sphere'")
    print("3. Busca donde está el mapeo tipo '\"5\": \"random\"'")
    print("4. Añade después: '\"6\": \"sphere\"'")