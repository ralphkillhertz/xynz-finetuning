#!/usr/bin/env python3
"""
🔍 Diagnóstico: ¿Existe command_processor?
"""

import ast

def check_command_processor():
    print("🔍 DIAGNÓSTICO COMMAND_PROCESSOR")
    print("=" * 50)
    
    # 1. Verificar en InteractiveController
    print("\n1️⃣ Verificando InteractiveController...")
    
    with open("trajectory_hub/interface/interactive_controller.py", 'r') as f:
        content = f.read()
    
    # Buscar __init__
    if "def __init__" in content:
        init_start = content.find("def __init__")
        init_end = content.find("\n    def", init_start + 1)
        init_method = content[init_start:init_end if init_end > 0 else len(content)]
        
        print("📋 En __init__:")
        if "self.command_processor" in init_method:
            print("   ✅ self.command_processor SÍ se inicializa")
            # Buscar la línea exacta
            for line in init_method.split('\n'):
                if "self.command_processor" in line:
                    print(f"   → {line.strip()}")
        else:
            print("   ❌ self.command_processor NO se inicializa")
    
    # 2. Buscar dónde se usa
    print("\n2️⃣ Usos de command_processor:")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "command_processor" in line and not line.strip().startswith('#'):
            print(f"   Línea {i+1}: {line.strip()[:80]}...")
    
    # 3. Verificar imports
    print("\n3️⃣ Imports relacionados:")
    for line in lines[:50]:  # Primeras 50 líneas
        if "CommandProcessor" in line or "command_processor" in line:
            print(f"   → {line.strip()}")
    
    # 4. Ver el error específico
    print("\n4️⃣ Buscando la línea del error...")
    for i, line in enumerate(lines):
        if "create_macro" in line and "command" in line.lower():
            print(f"   Línea {i+1}: {line.strip()}")
            # Ver contexto
            print("   Contexto:")
            for j in range(max(0, i-3), min(len(lines), i+3)):
                print(f"   {j+1}: {lines[j]}")

if __name__ == "__main__":
    check_command_processor()