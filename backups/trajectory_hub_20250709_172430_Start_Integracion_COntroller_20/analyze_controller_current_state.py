# === analyze_controller_current_state.py ===
# 🔍 Análisis exhaustivo del controlador actual
# ⚡ Identificar qué mantener, añadir y eliminar

import os
import ast
import json

print("🔍 ANÁLISIS COMPLETO DEL CONTROLADOR INTERACTIVO")
print("=" * 60)

controller_file = "trajectory_hub/interface/interactive_controller.py"

# 1. Analizar estructura actual
print("\n📊 1. ANÁLISIS DE ESTRUCTURA ACTUAL:")
with open(controller_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar métodos existentes
import re
methods = re.findall(r'def (\w+)\(self[^)]*\):', content)
print(f"\n  Total de métodos: {len(methods)}")

# Categorizar métodos
categories = {
    "macros": [],
    "trayectorias": [],
    "distancias": [],
    "deformacion": [],
    "comportamiento": [],
    "presets": [],
    "info": [],
    "menu": [],
    "otros": []
}

for method in methods:
    if 'macro' in method:
        categories["macros"].append(method)
    elif 'trajectory' in method or 'trayectoria' in method:
        categories["trayectorias"].append(method)
    elif 'distance' in method or 'distancia' in method:
        categories["distancias"].append(method)
    elif 'deform' in method:
        categories["deformacion"].append(method)
    elif 'behavior' in method or 'comportamiento' in method:
        categories["comportamiento"].append(method)
    elif 'preset' in method:
        categories["presets"].append(method)
    elif 'info' in method or 'show' in method or 'print' in method:
        categories["info"].append(method)
    elif 'menu' in method or 'handle' in method:
        categories["menu"].append(method)
    else:
        categories["otros"].append(method)

for cat, methods in categories.items():
    if methods:
        print(f"\n  {cat.upper()} ({len(methods)}):")
        for m in methods[:5]:  # Mostrar solo primeros 5
            print(f"    - {m}")
        if len(methods) > 5:
            print(f"    ... y {len(methods)-5} más")

# 2. Verificar integración con sistema de deltas
print("\n\n📊 2. INTEGRACIÓN CON SISTEMA DE DELTAS:")
delta_components = [
    "ConcentrationComponent",
    "IndividualTrajectory", 
    "MacroTrajectory",
    "MacroRotation",
    "ManualMacroRotation",
    "IndividualRotation",
    "ManualIndividualRotation"
]

for component in delta_components:
    if component in content:
        print(f"  ✅ {component} - Referenciado")
    else:
        print(f"  ❌ {component} - NO encontrado")

# 3. Métodos que faltan según el sistema de deltas
print("\n\n📊 3. FUNCIONALIDADES DELTA QUE FALTAN:")
required_methods = {
    "Concentración": ["set_concentration", "apply_concentration", "set_concentration_factor"],
    "Trayectorias Individuales": ["configure_individual_trajectories", "set_individual_movement"],
    "Rotaciones MS": ["set_macro_rotation", "set_manual_macro_rotation"],
    "Rotaciones IS": ["set_individual_rotation", "set_manual_individual_rotation"],
    "Modulador 3D": ["apply_orientation_preset", "set_orientation_lfo", "set_orientation_intensity"]
}

missing = []
for category, methods in required_methods.items():
    print(f"\n  {category}:")
    for method in methods:
        found = any(method in m for m in categories.get("otros", []) + 
                   categories.get("trayectorias", []) + 
                   categories.get("macros", []))
        if found:
            print(f"    ✅ {method}")
        else:
            print(f"    ❌ {method}")
            missing.append(method)

# 4. Funciones obsoletas o redundantes
print("\n\n📊 4. FUNCIONES OBSOLETAS/REDUNDANTES:")
obsolete_patterns = [
    "test_", "debug_", "_old", "backup_", "temp_"
]

obsolete = []
for method in methods:
    if any(pattern in method for pattern in obsolete_patterns):
        obsolete.append(method)
        print(f"  ⚠️ {method} - Candidato a eliminar")

# 5. Generar reporte
report = {
    "total_methods": len(methods),
    "categories": {k: len(v) for k, v in categories.items()},
    "delta_integration": {
        "components_found": sum(1 for c in delta_components if c in content),
        "total_components": len(delta_components)
    },
    "missing_methods": missing,
    "obsolete_methods": obsolete,
    "recommendations": [
        "Añadir métodos para todos los componentes delta",
        "Crear menú unificado para sistema de deltas",
        "Eliminar funciones de debug/test",
        "Mejorar organización por categorías",
        "Añadir validación de parámetros"
    ]
}

# Guardar reporte
with open("controller_analysis_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("\n\n📋 RESUMEN EJECUTIVO:")
print(f"  - Métodos actuales: {len(methods)}")
print(f"  - Métodos faltantes: {len(missing)}")
print(f"  - Métodos obsoletos: {len(obsolete)}")
print(f"  - Integración delta: {report['delta_integration']['components_found']}/{report['delta_integration']['total_components']}")
print("\n✅ Reporte guardado en: controller_analysis_report.json")
print("\n🚀 Siguiente paso: Crear plan de actualización")