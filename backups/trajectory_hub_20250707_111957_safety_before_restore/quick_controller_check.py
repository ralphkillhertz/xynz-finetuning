#!/usr/bin/env python3
"""
⚡ VERIFICACIÓN RÁPIDA DEL CONTROLADOR
🎮 Encuentra qué opciones están disponibles
"""

import os
import re

print("🎮 ANALIZANDO CONTROLADOR INTERACTIVO")
print("="*60)

controller_file = "trajectory_hub/interface/interactive_controller.py"

if not os.path.exists(controller_file):
    print(f"❌ No se encuentra: {controller_file}")
    # Buscar en otras ubicaciones
    for root, dirs, files in os.walk("."):
        if "interactive_controller.py" in files:
            controller_file = os.path.join(root, "interactive_controller.py")
            print(f"✅ Encontrado en: {controller_file}")
            break

if os.path.exists(controller_file):
    with open(controller_file, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Buscar opciones del menú
    print("\n📋 OPCIONES DEL MENÚ PRINCIPAL:")
    print("-"*60)
    
    menu_options = []
    for i, line in enumerate(lines):
        # Buscar líneas que parecen opciones de menú (número seguido de punto o paréntesis)
        if re.match(r'^\s*\d+[\.\)]\s+\w+', line):
            menu_options.append((i+1, line.strip()))
            
            # Si es opción de concentración, mostrarla destacada
            if 'concentra' in line.lower():
                print(f"🎯 Línea {i+1}: {line.strip()}")
            else:
                print(f"   Línea {i+1}: {line.strip()}")
    
    # Buscar métodos relacionados con concentración
    print("\n🔍 MÉTODOS DE CONCENTRACIÓN EN EL CONTROLADOR:")
    print("-"*60)
    
    # Buscar definiciones de métodos
    methods = re.findall(r'def\s+(\w+)\s*\(self', content)
    concentration_methods = []
    
    for method in methods:
        if any(kw in method.lower() for kw in ['concentra', 'focus', 'converge']):
            concentration_methods.append(method)
            
            # Buscar la implementación
            method_start = content.find(f'def {method}')
            if method_start != -1:
                # Extraer las primeras líneas del método
                method_snippet = content[method_start:method_start+500]
                
                # Buscar qué método del engine llama
                engine_calls = re.findall(r'self\.engine\.(\w+)\(', method_snippet)
                if engine_calls:
                    print(f"\n✅ Método: {method}()")
                    print(f"   Llama a engine.{engine_calls[0]}()")
    
    # Buscar la opción 31 específicamente (mencionada en el paste.txt)
    print("\n🎯 BUSCANDO OPCIÓN 31 (Control de Concentración):")
    print("-"*60)
    
    for i, line in enumerate(lines):
        if '31' in line and ('concentra' in line.lower() or 'control' in line.lower()):
            # Mostrar contexto
            print(f"\nEncontrado en línea {i+1}:")
            for j in range(max(0, i-2), min(len(lines), i+5)):
                print(f"   {lines[j]}")
            
            # Buscar el case o if que maneja esta opción
            for j in range(i, min(len(lines), i+50)):
                if 'selection == 31' in lines[j] or 'choice == 31' in lines[j] or 'option == 31' in lines[j]:
                    print(f"\n📍 Handler encontrado en línea {j+1}")
                    # Mostrar qué hace
                    for k in range(j, min(len(lines), j+10)):
                        if 'self.' in lines[k]:
                            print(f"   {lines[k].strip()}")
                    break
else:
    print("❌ No se pudo encontrar el archivo del controlador")

print("\n✅ Análisis completado")