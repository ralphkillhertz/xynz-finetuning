#!/usr/bin/env python3
"""
🔍 BUSCAR ARCHIVOS DEL PROYECTO
⚡ Encuentra archivos clave para aplicar fixes
"""

import os

print("=" * 60)
print("🔍 BUSCANDO ARCHIVOS CLAVE")
print("=" * 60)

# Archivos que necesitamos encontrar
targets = {
    "engine": ["engine.py", "trajectory_engine.py", "spatial_engine.py"],
    "concentration": ["concentration.py"],
    "rotation": ["orientation_modulation.py", "rotation_system.py"],
    "motion": ["motion_components.py", "source_motion.py"]
}

found = {}

# Buscar recursivamente
for root, dirs, files in os.walk("."):
    # Ignorar directorios ocultos y __pycache__
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
    
    for file in files:
        if file.endswith(".py"):
            for category, target_files in targets.items():
                if file in target_files:
                    path = os.path.join(root, file)
                    if category not in found:
                        found[category] = []
                    found[category].append(path)

# Mostrar resultados
for category, paths in found.items():
    print(f"\n📁 {category.upper()}:")
    for path in paths:
        print(f"   ✅ {path}")
        
        # Verificar contenido clave
        with open(path, 'r') as f:
            content = f.read()
            
        if category == "engine":
            if "def update(" in content:
                print("      → Contiene método update()")
            if "_positions" in content:
                print("      → Usa _positions")
            elif "positions" in content:
                print("      → Usa positions")
                
        elif category == "concentration":
            if "_apply_concentration" in content:
                print("      → Contiene _apply_concentration()")
            if "ConcentrationMode" in content:
                print("      → Define ConcentrationMode")
                
        elif category == "rotation":
            if "def apply(" in content:
                print("      → Contiene método apply()")
            if "ms_rotation" in content or "MS_rotation" in content:
                print("      → Maneja rotación MS")

# Archivos no encontrados
print("\n❌ NO ENCONTRADOS:")
for category, target_files in targets.items():
    if category not in found:
        print(f"   - {category}: {', '.join(target_files)}")

# Estructura general
print("\n📂 ESTRUCTURA DEL PROYECTO:")
main_dirs = ["core", "modules", "controllers", "config", "tests"]
for dir_name in main_dirs:
    if os.path.exists(dir_name):
        print(f"\n{dir_name}/:")
        for item in os.listdir(dir_name):
            item_path = os.path.join(dir_name, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                print(f"  📁 {item}/")
                # Mostrar algunos archivos
                sub_files = [f for f in os.listdir(item_path) if f.endswith('.py')][:3]
                for f in sub_files:
                    print(f"      - {f}")
            elif item.endswith('.py') and not item.startswith('__'):
                print(f"  📄 {item}")

print("\n" + "=" * 60)