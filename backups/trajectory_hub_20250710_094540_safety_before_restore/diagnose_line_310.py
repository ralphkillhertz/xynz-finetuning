#!/usr/bin/env python3
"""
🔍 Diagnóstico detallado de línea 310
⚡ Muestra contexto alrededor del error
"""

def diagnose_error():
    """Muestra contexto detallado del error"""
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    print("🔍 DIAGNÓSTICO DE ERROR - LÍNEA 310")
    print("=" * 60)
    
    with open(engine_path, 'r') as f:
        lines = f.readlines()
    
    # Mostrar líneas 300-320
    print("\nCONTEXTO (líneas 300-320):")
    print("-" * 60)
    
    for i in range(max(0, 299), min(len(lines), 320)):
        marker = ">>> " if i == 309 else "    "
        print(f"{i+1:4d}{marker}{lines[i]}", end='')
    
    print("-" * 60)
    
    # Análisis específico
    print("\nANÁLISIS:")
    
    # Verificar línea anterior a 310
    if len(lines) > 309:
        prev_line = lines[308].rstrip()
        curr_line = lines[309].rstrip()
        
        print(f"Línea 309: '{prev_line}'")
        print(f"Línea 310: '{curr_line}'")
        
        # Verificar problemas comunes
        if prev_line and not prev_line.endswith(':') and not prev_line.endswith(')'):
            print("\n⚠️ La línea 309 podría estar incompleta")
        
        if "def " in curr_line and not curr_line.startswith('    def'):
            print("\n⚠️ Problema de indentación en def")
        
        if "->" in curr_line:
            print("\n⚠️ Type hint podría causar problema")

if __name__ == "__main__":
    diagnose_error()