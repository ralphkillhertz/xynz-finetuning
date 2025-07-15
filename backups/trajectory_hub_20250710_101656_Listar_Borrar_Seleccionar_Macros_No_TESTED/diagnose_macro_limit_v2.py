#!/usr/bin/env python3
"""
🔍 Diagnóstico: ¿Por qué solo 2 macros?
⚡ Versión corregida con rutas correctas
"""
import os
import re

def diagnose():
    print("🔍 DIAGNÓSTICO LÍMITE DE MACROS")
    print("=" * 50)
    
    # 1. Buscar config
    print("\n1️⃣ Buscando configuración...")
    config_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file == "config.py" or file.endswith("_config.py"):
                config_files.append(os.path.join(root, file))
    
    if config_files:
        print(f"   Encontrados: {config_files}")
        for cf in config_files:
            with open(cf, 'r') as f:
                content = f.read()
                if "n_sources" in content or "MAX" in content:
                    print(f"\n   En {cf}:")
                    for line in content.split('\n'):
                        if ("sources" in line.lower() or "max" in line.lower()) and not line.strip().startswith('#'):
                            print(f"   → {line.strip()}")
    
    # 2. Verificar engine
    print("\n2️⃣ Analizando Engine...")
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r') as f:
        content = f.read()
    
    # Buscar creación de sources
    print("\n3️⃣ Análisis de IDs de sources:")
    
    # Patrón de creación
    create_pattern = r'source_id\s*=\s*([^\n]+)'
    matches = re.findall(create_pattern, content)
    for m in matches[:5]:  # Primeros 5
        print(f"   ID generation: {m}")
    
    # Buscar si hay límite de 16 sources (común en audio)
    if "16" in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "16" in line and ("source" in line.lower() or "limit" in line.lower()):
                print(f"\n   ⚠️ Posible límite: línea {i+1}: {line.strip()}")
    
    # 4. Verificar create_macro
    print("\n4️⃣ Analizando create_macro:")
    
    # Buscar el método
    if "def create_macro" in content:
        start = content.find("def create_macro")
        end = content.find("\n    def", start + 1)
        method = content[start:end if end > 0 else start + 1000]
        
        # Buscar cómo genera IDs
        print("   Buscando generación de IDs en create_macro...")
        for line in method.split('\n')[:20]:
            if "source_id" in line or "create_source" in line:
                print(f"   → {line.strip()}")
    
    # 5. Teoría
    print("\n5️⃣ DIAGNÓSTICO PROBABLE:")
    print("   📌 Los IDs de sources están colisionando")
    print("   📌 Cada macro de 8 sources usa IDs 1-8")
    print("   📌 El 3er macro intenta usar IDs ya ocupados")
    print("\n   💡 SOLUCIÓN: Generar IDs únicos incrementales")

if __name__ == "__main__":
    diagnose()