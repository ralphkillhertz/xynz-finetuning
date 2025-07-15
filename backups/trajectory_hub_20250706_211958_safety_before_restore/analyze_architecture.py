#!/usr/bin/env python3
"""
🔍 ANÁLISIS PROFUNDO DE ARQUITECTURA
⚡ Identifica dependencias y bloqueos entre componentes
"""

import os
import re
from collections import defaultdict

print("=" * 80)
print("🔍 ANÁLISIS DE ARQUITECTURA Y DEPENDENCIAS")
print("=" * 80)

# Archivos clave a analizar
key_files = {
    "motion": "trajectory_hub/core/motion_components.py",
    "engine": "trajectory_hub/core/enhanced_trajectory_engine.py",
    "rotation": "trajectory_hub/core/rotation_system.py",
    "controller": "trajectory_hub/interface/interactive_controller.py"
}

# Patrones a buscar
patterns = {
    "blocking_checks": [
        r"if.*\.enabled.*return",  # Componente deshabilitado bloquea
        r"if not.*\.enabled.*return",
        r"if.*is None.*return",
        r"else.*return.*None"
    ],
    "dependencies": [
        r"if.*trajectory.*\.enabled",  # Un componente depende de otro
        r"if.*rotation.*\.enabled",
        r"if.*concentration.*\.enabled",
        r"requires.*=.*True",
        r"depends_on.*="
    ],
    "overwrites": [
        r"position\s*=\s*",  # Sobrescribe posición en lugar de sumar
        r"orientation\s*=\s*",
        r"state\s*=\s*"
    ],
    "accumulation": [
        r"position\s*\+=",  # Acumula correctamente
        r"orientation\s*\+=",
        r"\+\s*=.*position",
        r"\+\s*=.*orientation"
    ]
}

results = defaultdict(lambda: defaultdict(list))

# Analizar cada archivo
for file_key, filepath in key_files.items():
    if not os.path.exists(filepath):
        # Buscar alternativas
        base = os.path.basename(filepath)
        for root, dirs, files in os.walk("trajectory_hub"):
            if base in files:
                filepath = os.path.join(root, base)
                break
    
    if os.path.exists(filepath):
        print(f"\n📄 ANALIZANDO {filepath}")
        print("-" * 60)
        
        with open(filepath, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar patrones problemáticos
        for pattern_type, patterns_list in patterns.items():
            for pattern in patterns_list:
                for i, line in enumerate(lines):
                    if re.search(pattern, line, re.IGNORECASE):
                        results[file_key][pattern_type].append({
                            'line': i + 1,
                            'code': line.strip(),
                            'pattern': pattern
                        })

# Análisis específico de SourceMotion.update()
print("\n🔧 ANÁLISIS DE SourceMotion.update()")
print("-" * 60)

motion_file = key_files["motion"]
if os.path.exists(motion_file):
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar el método update
    update_match = re.search(r'class SourceMotion.*?def update\(self.*?\):(.*?)(?=\n    def|\nclass|\Z)', 
                            content, re.DOTALL)
    
    if update_match:
        update_body = update_match.group(1)
        
        # Verificar orden de aplicación
        component_order = []
        for line in update_body.split('\n'):
            if 'component' in line and 'apply' in line:
                component_order.append(line.strip())
        
        print("Orden de aplicación de componentes:")
        for i, comp in enumerate(component_order):
            print(f"  {i+1}. {comp}")
        
        # Verificar si hay returns tempranos
        if 'return' in update_body and update_body.count('return') > 1:
            print("\n⚠️ PROBLEMA: Múltiples returns pueden bloquear componentes")

# Identificar el problema principal
print("\n🎯 PROBLEMAS IDENTIFICADOS:")
print("-" * 60)

problems = []

# 1. Bloqueos mutuos
for file_key, file_results in results.items():
    if file_results['blocking_checks']:
        problems.append(f"❌ {file_key}: Componentes se bloquean mutuamente")
        for item in file_results['blocking_checks'][:3]:
            print(f"   Línea {item['line']}: {item['code']}")

# 2. Dependencias incorrectas
for file_key, file_results in results.items():
    if file_results['dependencies']:
        problems.append(f"❌ {file_key}: Dependencias entre componentes")
        for item in file_results['dependencies'][:3]:
            print(f"   Línea {item['line']}: {item['code']}")

# 3. Sobrescrituras vs acumulación
overwrites_count = sum(len(r['overwrites']) for r in results.values())
accumulation_count = sum(len(r['accumulation']) for r in results.values())

print(f"\n📊 ESTADÍSTICAS:")
print(f"   Sobrescrituras (=): {overwrites_count}")
print(f"   Acumulaciones (+=): {accumulation_count}")

if overwrites_count > accumulation_count:
    print("   ❌ Más sobrescrituras que acumulaciones - PROBLEMA")

# Buscar la implementación de concentración
print("\n🔍 IMPLEMENTACIÓN DE CONCENTRACIÓN:")
print("-" * 60)

concentration_found = False
for root, dirs, files in os.walk("trajectory_hub"):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                if 'class Concentration' in content or 'def concentration' in content:
                    concentration_found = True
                    print(f"✅ Encontrado en: {filepath}")
                    
                    # Verificar si depende de IS
                    if 'individual_trajectory' in content or 'IS' in content:
                        print("   ❌ PROBLEMA: Concentración depende de IS")
                    
                    # Verificar si bloquea otros componentes
                    if re.search(r'if.*enabled.*return', content):
                        print("   ❌ PROBLEMA: Puede bloquear otros componentes")
            except:
                pass

# PROPUESTA DE SOLUCIÓN
print("\n💡 ARQUITECTURA PROPUESTA: COMPONENTES PARALELOS")
print("=" * 80)

print("""
ACTUAL (Problemático):
  SourceMotion.update()
    └─> Componente1 (puede return y bloquear resto)
    └─> Componente2 (depende de Componente1)
    └─> Componente3 (sobrescribe resultado de Componente2)

PROPUESTA (Paralelo):
  SourceMotion.update()
    ├─> MS_Trajectory    → delta_position_ms
    ├─> IS_Trajectory    → delta_position_is
    ├─> Concentration    → delta_position_conc
    ├─> MS_Rotation      → delta_orientation_ms
    ├─> IS_Rotation      → delta_orientation_is
    └─> SUMA FINAL: position += Σ(deltas)

VENTAJAS:
  ✅ Componentes independientes
  ✅ No hay bloqueos mutuos
  ✅ Cada uno aporta su delta
  ✅ Se pueden activar/desactivar sin afectar otros
""")

print("\n⚡ PRÓXIMO PASO: python implement_parallel_architecture.py")
print("=" * 80)