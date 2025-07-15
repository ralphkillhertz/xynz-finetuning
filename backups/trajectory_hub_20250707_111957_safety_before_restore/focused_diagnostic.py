#!/usr/bin/env python3
"""
🎯 DIAGNÓSTICO ENFOCADO - PROBLEMAS ESPECÍFICOS
⚡ Versión optimizada que busca los problemas conocidos
"""

import os
import re
import json
from datetime import datetime

print("🔍 DIAGNÓSTICO ENFOCADO - ARQUITECTURA ACTUAL")
print("="*80)

results = {
    'timestamp': datetime.now().isoformat(),
    'problems_found': [],
    'architecture_type': 'unknown',
    'component_locations': {},
    'recommendations': []
}

# 1. LOCALIZAR COMPONENTES CLAVE
print("\n1️⃣ LOCALIZANDO COMPONENTES CLAVE...")
print("-"*60)

component_methods = {
    'concentration': {
        'methods': ['set_concentration_factor', 'toggle_concentration', 'animate_concentration'],
        'file': None,
        'found': []
    },
    'rotation_ms': {
        'methods': ['set_macro_rotation', 'rotate_macro', '_apply_macro_rotation'],
        'file': None,
        'found': []
    },
    'rotation_is': {
        'methods': ['set_individual_rotation', 'rotate_individual', 'set_trajectory_rotation'],
        'file': None,
        'found': []
    },
    'trajectories_is': {
        'methods': ['set_individual_trajectory', 'configure_individual_trajectories'],
        'file': None,
        'found': []
    }
}

# Buscar en archivos principales
files_to_check = [
    "trajectory_hub/core/enhanced_trajectory_engine.py",
    "trajectory_hub/core/motion_components.py",
    "trajectory_hub/core/rotation_system.py",
    "trajectory_hub/interface/interactive_controller.py"
]

for filepath in files_to_check:
    if os.path.exists(filepath):
        print(f"\n📄 Analizando: {os.path.basename(filepath)}")
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Buscar métodos de cada componente
            for comp_name, comp_info in component_methods.items():
                for method in comp_info['methods']:
                    if f'def {method}' in content:
                        comp_info['found'].append(method)
                        comp_info['file'] = filepath
                        print(f"  ✅ {comp_name}: {method}")
                        
        except Exception as e:
            print(f"  ⚠️ Error leyendo archivo: {e}")

# 2. BUSCAR PROBLEMAS ESPECÍFICOS
print("\n\n2️⃣ BUSCANDO PROBLEMAS CONOCIDOS...")
print("-"*60)

# Problema 1: Concentración depende de IS
print("\n🔍 Problema 1: Concentración depende de IS")
concentration_file = component_methods['concentration']['file']
if concentration_file and os.path.exists(concentration_file):
    with open(concentration_file, 'r') as f:
        content = f.read()
    
    # Buscar el método set_concentration_factor
    method_start = content.find('def set_concentration_factor')
    if method_start == -1:
        # Buscar método alternativo
        method_start = content.find('def apply_concentration')
        
    if method_start != -1:
        # Extraer las siguientes ~50 líneas
        method_snippet = content[method_start:method_start+2000]
        
        # Buscar dependencias de IS
        if 'individual_trajectory' in method_snippet or 'individual_trajectories' in method_snippet:
            print("  ❌ CONFIRMADO: Concentración verifica trayectorias individuales")
            results['problems_found'].append({
                'problem': 'concentration_depends_on_is',
                'severity': 'HIGH',
                'location': concentration_file
            })
        else:
            print("  ✅ No se encontró dependencia directa de IS")
else:
    print("  ⚠️ No se encontró implementación de concentración")
    
# Problema 2: Rotación MS bloqueada por IS
print("\n🔍 Problema 2: Rotación MS bloqueada por IS")

# Buscar en enhanced_trajectory_engine
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
if os.path.exists(engine_file):
    with open(engine_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar patrones de bloqueo más específicos
    for i, line in enumerate(lines):
        # Buscar condiciones que saltan rotación MS cuando IS está activa
        if 'individual_trajectory' in line and ('continue' in line or 'return' in line or 'skip' in line):
            # Ver contexto (5 líneas antes y después)
            context_start = max(0, i-5)
            context_end = min(len(lines), i+5)
            
            # Verificar si está en contexto de rotación macro
            context = ''.join(lines[context_start:context_end])
            if 'macro' in context.lower() and ('rotation' in context or 'rotate' in context):
                print(f"  ❌ CONFIRMADO: Bloqueo en línea {i+1}")
                print(f"     {line.strip()}")
                results['problems_found'].append({
                    'problem': 'ms_rotation_blocked_by_is',
                    'severity': 'HIGH',
                    'location': f"{engine_file}:{i+1}"
                })
                break
    else:
        print("  ℹ️ No se encontró bloqueo directo obvio")

# 3. ANALIZAR ARQUITECTURA
print("\n\n3️⃣ ANALIZANDO TIPO DE ARQUITECTURA...")
print("-"*60)

# Buscar en motion_components el método update de SourceMotion
motion_file = "trajectory_hub/core/motion_components.py"
if os.path.exists(motion_file):
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar el método update
    update_match = re.search(r'class SourceMotion.*?def update\(self.*?\):(.*?)(?=\n    def|\nclass|\Z)', 
                            content, re.DOTALL)
    
    if update_match:
        update_body = update_match.group(1)
        
        # Contar asignaciones vs acumulaciones
        direct_assigns = len(re.findall(r'position\s*=(?!=)', update_body))
        accumulations = len(re.findall(r'position\s*\+=', update_body))
        
        print(f"  Asignaciones directas (=): {direct_assigns}")
        print(f"  Acumulaciones (+=): {accumulations}")
        
        if direct_assigns > accumulations:
            print("  ❌ Arquitectura SECUENCIAL detectada (sobrescritura)")
            results['architecture_type'] = 'sequential'
        else:
            print("  ✅ Posible arquitectura paralela")
            results['architecture_type'] = 'possibly_parallel'

# 4. GENERAR RECOMENDACIONES
print("\n\n4️⃣ GENERANDO RECOMENDACIONES...")
print("-"*60)

if len(results['problems_found']) > 0:
    print(f"\n⚠️ Se encontraron {len(results['problems_found'])} problemas:")
    
    for problem in results['problems_found']:
        print(f"  • {problem['problem']} ({problem['severity']})")
    
    results['recommendations'] = [
        "1. Hacer concentración independiente de IS",
        "2. Eliminar bloqueos de rotación MS cuando IS está activa",
        "3. Cambiar arquitectura a modelo de deltas paralelos",
        "4. Implementar suma de componentes en lugar de sobrescritura"
    ]
else:
    print("\n✅ No se encontraron los problemas específicos conocidos")
    print("   (Puede que ya estén parcialmente resueltos)")

# 5. GUARDAR REPORTE
report_file = f"FOCUSED_DIAGNOSTIC_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(report_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n\n💾 Reporte guardado: {report_file}")

# RESUMEN EJECUTIVO
print("\n" + "="*80)
print("📊 RESUMEN EJECUTIVO")
print("="*80)

print(f"\nComponentes encontrados:")
for comp_name, comp_info in component_methods.items():
    if comp_info['found']:
        print(f"  ✅ {comp_name}: {len(comp_info['found'])} métodos")
    else:
        print(f"  ❌ {comp_name}: No encontrado")

print(f"\nProblemas confirmados: {len(results['problems_found'])}")
print(f"Arquitectura detectada: {results['architecture_type']}")

if results['problems_found']:
    print("\n🚀 PRÓXIMO PASO: Implementar soluciones gradualmente")
    print("   Comenzar con: Hacer concentración independiente")
else:
    print("\n🤔 Los problemas conocidos no fueron detectados claramente")
    print("   Puede requerir análisis manual más profundo")

print("\n✅ Diagnóstico completado")