#!/usr/bin/env python3
"""
⚠️ EVALUACIÓN DE RIESGOS - CAMBIO ARQUITECTÓNICO
📊 Análisis completo antes de proceder
"""

import os
import re
from datetime import datetime
from collections import defaultdict

print("=" * 80)
print("⚠️ EVALUACIÓN DE RIESGOS - ARQUITECTURA PARALELA")
print("=" * 80)

# 1. ANÁLISIS DEL TAMAÑO DEL PROYECTO
print("\n📊 1. TAMAÑO Y COMPLEJIDAD DEL PROYECTO")
print("-" * 60)

stats = {
    'total_files': 0,
    'total_lines': 0,
    'motion_components': 0,
    'test_files': 0,
    'dependencies': set()
}

for root, dirs, files in os.walk("trajectory_hub"):
    # Ignorar backups
    if 'backup' in root or '__pycache__' in root:
        continue
    
    for file in files:
        if file.endswith('.py'):
            stats['total_files'] += 1
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    stats['total_lines'] += len(content.split('\n'))
                    
                    # Contar componentes de movimiento
                    if any(word in content.lower() for word in ['trajectory', 'rotation', 'motion', 'movement']):
                        stats['motion_components'] += 1
                    
                    # Contar tests
                    if 'test' in file.lower() or 'test' in content:
                        stats['test_files'] += 1
                    
                    # Buscar dependencias
                    imports = re.findall(r'from\s+(\S+)\s+import|import\s+(\S+)', content)
                    for imp in imports:
                        dep = imp[0] or imp[1]
                        if 'trajectory_hub' in dep:
                            stats['dependencies'].add(dep)
            except:
                pass

print(f"Total archivos Python: {stats['total_files']}")
print(f"Total líneas de código: {stats['total_lines']:,}")
print(f"Componentes de movimiento: {stats['motion_components']}")
print(f"Archivos de test: {stats['test_files']}")
print(f"Módulos interdependientes: {len(stats['dependencies'])}")

# 2. IDENTIFICAR PUNTOS CRÍTICOS
print("\n🎯 2. PUNTOS CRÍTICOS A MODIFICAR")
print("-" * 60)

critical_files = {
    'motion_components.py': {'found': False, 'risk': 'ALTO', 'changes': []},
    'rotation_system.py': {'found': False, 'risk': 'ALTO', 'changes': []},
    'enhanced_trajectory_engine.py': {'found': False, 'risk': 'MEDIO', 'changes': []},
    'interactive_controller.py': {'found': False, 'risk': 'BAJO', 'changes': []}
}

for root, dirs, files in os.walk("trajectory_hub"):
    for file in files:
        if file in critical_files:
            critical_files[file]['found'] = True
            filepath = os.path.join(root, file)
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Analizar cambios necesarios
            if 'def update(' in content:
                critical_files[file]['changes'].append('Método update() a modificar')
            if 'position =' in content:
                critical_files[file]['changes'].append('Asignaciones directas de position')
            if 'return' in content and content.count('return') > 5:
                critical_files[file]['changes'].append('Múltiples returns que pueden bloquear')

for file, info in critical_files.items():
    if info['found']:
        print(f"\n{file}:")
        print(f"  Riesgo: {info['risk']}")
        print(f"  Cambios necesarios: {len(info['changes'])}")
        for change in info['changes']:
            print(f"    - {change}")

# 3. EVALUAR RIESGOS
print("\n⚠️ 3. MATRIZ DE RIESGOS")
print("-" * 60)

risks = {
    'CRÍTICOS': [
        {
            'riesgo': 'Ruptura de funcionalidad existente',
            'probabilidad': 'MEDIA',
            'impacto': 'ALTO',
            'mitigación': 'Backups completos + tests exhaustivos + implementación gradual'
        },
        {
            'riesgo': 'Incompatibilidad con módulos no identificados',
            'probabilidad': 'MEDIA',
            'impacto': 'ALTO', 
            'mitigación': 'Análisis de dependencias + modo compatibilidad temporal'
        },
        {
            'riesgo': 'Degradación de performance',
            'probabilidad': 'BAJA',
            'impacto': 'MEDIO',
            'mitigación': 'Benchmarks antes/después + optimización de loops'
        }
    ],
    'IMPORTANTES': [
        {
            'riesgo': 'Complejidad adicional en mantenimiento',
            'probabilidad': 'MEDIA',
            'impacto': 'MEDIO',
            'mitigación': 'Documentación exhaustiva + ejemplos claros'
        },
        {
            'riesgo': 'Efectos no deseados en suma de componentes',
            'probabilidad': 'MEDIA',
            'impacto': 'BAJO',
            'mitigación': 'Sistema de pesos/factores para cada componente'
        }
    ]
}

for nivel, riesgos_nivel in risks.items():
    print(f"\n{nivel}:")
    for r in riesgos_nivel:
        print(f"\n  • {r['riesgo']}")
        print(f"    Probabilidad: {r['probabilidad']}")
        print(f"    Impacto: {r['impacto']}")
        print(f"    Mitigación: {r['mitigación']}")

# 4. ALTERNATIVAS
print("\n💡 4. ALTERNATIVAS A CONSIDERAR")
print("-" * 60)

alternatives = [
    {
        'nombre': 'Fix Puntual (Mínimo Riesgo)',
        'descripcion': 'Solo arreglar las dependencias específicas IS/MS sin cambiar arquitectura',
        'pros': ['Riesgo mínimo', 'Cambios localizados', 'Rápido'],
        'contras': ['No resuelve el problema de fondo', 'Pueden surgir nuevos conflictos'],
        'tiempo': '1-2 horas'
    },
    {
        'nombre': 'Refactor Gradual (Riesgo Medio)',
        'descripcion': 'Implementar arquitectura paralela componente por componente',
        'pros': ['Permite testing incremental', 'Rollback fácil', 'Menor riesgo'],
        'contras': ['Más tiempo', 'Estado intermedio complejo'],
        'tiempo': '4-6 horas'
    },
    {
        'nombre': 'Refactor Completo (Riesgo Alto)',
        'descripcion': 'Cambiar toda la arquitectura de una vez',
        'pros': ['Solución definitiva', 'Arquitectura limpia', 'Mejor mantenibilidad'],
        'contras': ['Alto riesgo', 'Puede romper funcionalidad', 'Testing exhaustivo'],
        'tiempo': '2-3 horas + testing'
    }
]

for alt in alternatives:
    print(f"\n{alt['nombre']}:")
    print(f"  {alt['descripcion']}")
    print(f"  ✅ Pros: {', '.join(alt['pros'])}")
    print(f"  ❌ Contras: {', '.join(alt['contras'])}")
    print(f"  ⏱️ Tiempo estimado: {alt['tiempo']}")

# 5. PLAN DE SALVAGUARDA
print("\n🛡️ 5. PLAN DE SALVAGUARDA")
print("-" * 60)

safeguards = [
    "1. BACKUP COMPLETO antes de cualquier cambio",
    "2. BRANCH/VERSIÓN PARALELA para testing",
    "3. TESTS AUTOMATIZADOS para cada componente",
    "4. MODO COMPATIBILIDAD: flag para activar/desactivar nuevo sistema",
    "5. ROLLBACK PLAN: script automático para revertir",
    "6. VALIDACIÓN INCREMENTAL: probar cada cambio",
    "7. DOCUMENTACIÓN: cada cambio documentado"
]

for sg in safeguards:
    print(f"  {sg}")

# 6. RECOMENDACIÓN
print("\n" + "=" * 80)
print("📋 RECOMENDACIÓN PROFESIONAL")
print("=" * 80)

print("""
Dado el estado avanzado del proyecto ({} archivos, {:,} líneas):

🔸 OPCIÓN RECOMENDADA: Refactor Gradual (Riesgo Medio)

PLAN DE IMPLEMENTACIÓN:
1. Crear modo "PARALLEL_MODE" configurable
2. Implementar un componente a la vez
3. Testing exhaustivo después de cada cambio
4. Mantener compatibilidad hacia atrás
5. Migración completa solo cuando todo esté probado

GARANTÍAS:
✅ Cada cambio será reversible
✅ Funcionalidad existente protegida
✅ Testing en cada paso
✅ Documentación completa
✅ Backup en cada fase

⚠️ IMPORTANTE: Este cambio ES necesario para resolver los conflictos
actuales, pero podemos hacerlo de forma SEGURA y GRADUAL.
""".format(stats['total_files'], stats['total_lines']))

print("\n¿Procedemos con el enfoque GRADUAL y SEGURO? (menos riesgo)")
print("=" * 80)

# Crear script de backup completo
backup_script = '''#!/bin/bash
# BACKUP COMPLETO ANTES DE CAMBIOS
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="trajectory_hub_backup_before_parallel_$timestamp"
echo "Creating complete backup: $backup_dir"
cp -r trajectory_hub "$backup_dir"
echo "✅ Backup complete: $backup_dir"
echo "To restore: rm -rf trajectory_hub && cp -r $backup_dir trajectory_hub"
'''

with open("create_safety_backup.sh", 'w') as f:
    f.write(backup_script)
os.chmod("create_safety_backup.sh", 0o755)

print("\n⚡ Creado: ./create_safety_backup.sh (ejecutar primero)")