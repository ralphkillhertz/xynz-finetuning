#!/usr/bin/env python3
"""
🔍 BUSCAR BLOQUEOS DE ROTACIÓN MS POR IS
📍 Encuentra exactamente dónde IS bloquea rotación MS
"""

import os
import re

print("🔍 BUSCANDO BLOQUEOS DE ROTACIÓN MS")
print("="*60)

# Archivos a revisar
files_to_check = [
    "trajectory_hub/core/enhanced_trajectory_engine.py",
    "trajectory_hub/core/rotation_system.py",
    "trajectory_hub/interface/interactive_controller.py"
]

blocks_found = []

for filepath in files_to_check:
    if not os.path.exists(filepath):
        continue
        
    print(f"\n📄 Analizando: {os.path.basename(filepath)}")
    print("-"*50)
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Buscar métodos relacionados con rotación
    in_rotation_method = False
    method_name = ""
    
    for i, line in enumerate(lines):
        # Detectar métodos de rotación
        if 'def ' in line and any(word in line for word in ['rotation', 'rotate', '_apply_algorithmic']):
            in_rotation_method = True
            method_name = re.search(r'def\s+(\w+)', line).group(1)
            
        # Fin del método
        if in_rotation_method and line.strip() and not line.startswith(' ') and i > 0:
            in_rotation_method = False
            
        # Si estamos en un método de rotación
        if in_rotation_method:
            # Buscar condiciones que verifican IS
            if any(check in line for check in ['individual_trajectory', 'individual_trajectories', 'IS']):
                # Ver si hay un return, continue o skip en las siguientes líneas
                context_end = min(i + 10, len(lines))
                context = ''.join(lines[i:context_end])
                
                if any(keyword in context for keyword in ['return', 'continue', 'skip', 'pass']):
                    print(f"\n❌ BLOQUEO ENCONTRADO en {method_name}():")
                    print(f"   Línea {i+1}: {line.strip()}")
                    
                    # Mostrar contexto
                    for j in range(i, min(i+5, len(lines))):
                        if any(k in lines[j] for k in ['return', 'continue', 'skip']):
                            print(f"   Línea {j+1}: {lines[j].strip()}")
                            
                    blocks_found.append({
                        'file': filepath,
                        'method': method_name,
                        'line': i+1,
                        'code': line.strip()
                    })
                    
        # Buscar específicamente el problema mencionado
        if 'algorithmic' in line and 'rotation' in line and 'MS' in line:
            # Ver contexto
            if i > 0 and 'individual_trajectory' in ''.join(lines[max(0, i-10):i]):
                print(f"\n⚠️ Posible interferencia con rotación algorítmica MS:")
                print(f"   Línea {i+1}: {line.strip()}")

# Buscar específicamente en el método update
print("\n\n🔍 ANALIZANDO MÉTODO UPDATE")
print("="*60)

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
if os.path.exists(engine_file):
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar el método update
    update_match = re.search(r'def update\(self.*?\):(.*?)(?=\n    def|\nclass|\Z)', content, re.DOTALL)
    
    if update_match:
        update_body = update_match.group(1)
        lines = update_body.split('\n')
        
        print("Orden de aplicación de componentes:")
        component_calls = []
        
        for i, line in enumerate(lines):
            # Buscar aplicación de rotaciones
            if '_apply' in line and 'rotation' in line:
                component_calls.append((i, line.strip()))
                print(f"   {i}: {line.strip()}")
                
            # Buscar condiciones
            if 'if' in line and 'individual_trajectory' in line:
                print(f"\n⚠️ Condición IS encontrada:")
                print(f"   {i}: {line.strip()}")
                # Ver qué pasa después
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip():
                        print(f"   {j}: {lines[j].strip()}")

# RESUMEN
print("\n\n" + "="*60)
print("📊 RESUMEN DE BLOQUEOS ENCONTRADOS")
print("="*60)

if blocks_found:
    print(f"\n❌ Se encontraron {len(blocks_found)} bloqueos:")
    for block in blocks_found:
        print(f"\n📍 {block['file']}:")
        print(f"   Método: {block['method']}()")
        print(f"   Línea {block['line']}: {block['code']}")
else:
    print("\n✅ No se encontraron bloqueos obvios")
    print("   (El problema puede ser más sutil)")

print("\n💡 SOLUCIÓN PROPUESTA:")
print("   Eliminar todas las verificaciones de IS en métodos de rotación MS")
print("   Permitir que ambos sistemas funcionen en paralelo")

print("\n✅ Análisis completado")