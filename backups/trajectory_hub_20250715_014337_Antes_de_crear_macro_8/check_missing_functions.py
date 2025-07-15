#!/usr/bin/env python3
"""
Verificador de funciones faltantes
Encuentra todas las funciones que se llaman pero no están definidas
"""

import ast
import re
from typing import Set, List, Dict


def find_function_calls(filename: str) -> Set[str]:
    """Encuentra todas las llamadas a funciones self._* en un archivo"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Buscar patrones self._function_name()
    pattern = r'self\.(_\w+)\s*\('
    calls = set(re.findall(pattern, content))
    
    return calls


def find_function_definitions(filename: str) -> Set[str]:
    """Encuentra todas las definiciones de funciones en un archivo"""
    with open(filename, 'r') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"Error de sintaxis en {filename}: {e}")
        return set()
    
    definitions = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            definitions.add(node.name)
            
    return definitions


def check_missing_functions(filename: str) -> List[str]:
    """Verifica qué funciones se llaman pero no están definidas"""
    calls = find_function_calls(filename)
    definitions = find_function_definitions(filename)
    
    missing = []
    for call in calls:
        if call not in definitions:
            missing.append(call)
            
    return sorted(missing)


def find_call_locations(filename: str, function_name: str) -> List[int]:
    """Encuentra los números de línea donde se llama una función"""
    locations = []
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    pattern = f'self\\.{function_name}\\s*\\('
    
    for i, line in enumerate(lines, 1):
        if re.search(pattern, line):
            locations.append(i)
            
    return locations


def main():
    import sys
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "/Volumes/RK Work/Ralph Killhertz/XYNZ/XYNZ-SPAT/trajectory_hub/trajectory_hub/interface/interactive_controller.py"
    
    print(f"🔍 Verificando funciones faltantes en: {filename}")
    print("="*70)
    
    missing = check_missing_functions(filename)
    
    if not missing:
        print("✅ Todas las funciones llamadas están definidas!")
    else:
        print(f"\n❌ Se encontraron {len(missing)} funciones faltantes:\n")
        
        for func in missing:
            locations = find_call_locations(filename, func)
            print(f"  • {func}")
            print(f"    Llamada en líneas: {', '.join(map(str, locations))}")
            
    # También verificar funciones definidas pero nunca usadas
    calls = find_function_calls(filename)
    definitions = find_function_definitions(filename)
    
    # Excluir funciones especiales y públicas
    unused = []
    for func in definitions:
        if func.startswith('_') and not func.startswith('__'):
            if func not in calls:
                unused.append(func)
                
    if unused:
        print(f"\n⚠️  Funciones definidas pero no usadas internamente: {len(unused)}")
        for func in sorted(unused):
            print(f"  • {func}")
            

if __name__ == "__main__":
    main()