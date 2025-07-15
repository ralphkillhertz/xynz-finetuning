# === diagnose_update_method.py ===
# 🔧 Diagnóstico del método update() completo
# ⚡ Ver exactamente qué está pasando

import os
import re

def diagnose_update():
    """Muestra el método update completo y busca el problema"""
    
    print("🔍 DIAGNÓSTICO DEL MÉTODO UPDATE")
    print("="*60)
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método update completo
    pattern = r'def update\(self\).*?(?=\n    def|\n\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        update_method = match.group(0)
        lines = update_method.split('\n')
        
        print("\n📋 Método update() completo:")
        print("-"*60)
        
        # Buscar líneas clave
        has_delta_processing = False
        delta_line = -1
        return_line = -1
        
        for i, line in enumerate(lines):
            # Imprimir con número de línea
            print(f"{i:3d}: {line}")
            
            if 'PROCESAMIENTO DE DELTAS' in line:
                has_delta_processing = True
                delta_line = i
            
            if 'return {' in line:
                return_line = i
        
        print("-"*60)
        
        # Análisis
        print("\n📊 ANÁLISIS:")
        print(f"   Tiene procesamiento de deltas: {'✅' if has_delta_processing else '❌'}")
        
        if has_delta_processing and return_line > 0:
            if delta_line > return_line:
                print(f"   ❌ PROBLEMA: Deltas (línea {delta_line}) está DESPUÉS del return (línea {return_line})")
                print("      El código nunca se ejecuta!")
            else:
                print(f"   ✅ Deltas (línea {delta_line}) está ANTES del return (línea {return_line})")
                
                # Verificar si hay algún return temprano
                for i in range(delta_line, return_line):
                    if 'return' in lines[i] and i < return_line:
                        print(f"   ❌ PROBLEMA: Hay un return en línea {i} que impide llegar a los deltas")
        
        # Buscar si hay condiciones que impidan ejecutar
        if has_delta_processing:
            print("\n🔍 Verificando contexto del código de deltas:")
            start = max(0, delta_line - 5)
            end = min(len(lines), delta_line + 15)
            
            for i in range(start, end):
                if i == delta_line:
                    print(f">>> {i:3d}: {lines[i]} <<<")
                else:
                    print(f"    {i:3d}: {lines[i]}")
            
            # Verificar indentación
            if delta_line > 0:
                delta_indent = len(lines[delta_line]) - len(lines[delta_line].lstrip())
                print(f"\n   Indentación del código de deltas: {delta_indent} espacios")
                
                # Verificar si está dentro de un if
                for i in range(delta_line-1, max(0, delta_line-10), -1):
                    if lines[i].strip().startswith('if '):
                        print(f"   ⚠️ El código está dentro de un if en línea {i}: {lines[i].strip()}")
                        break

if __name__ == "__main__":
    diagnose_update()