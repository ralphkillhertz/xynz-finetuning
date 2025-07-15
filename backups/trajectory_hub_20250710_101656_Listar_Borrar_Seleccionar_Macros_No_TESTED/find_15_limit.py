#!/usr/bin/env python3
# 🔧 Fix: Encontrar límite de 15 sources
# ⚡ Buscar en todos los archivos del proyecto
# 🎯 Impacto: CRÍTICO

import os
import re

def find_15_limit():
    print("\n🔍 BUSCANDO LÍMITE DE 15 SOURCES")
    print("=" * 60)
    
    # Patrones a buscar
    patterns = [
        r'\b15\b',              # número 15 solo
        r'[:]\s*15',            # [:15]
        r'range\s*\([^)]*15[^)]*\)',  # range(...15...)
        r'<\s*15',              # < 15
        r'<=\s*15',             # <= 15
        r'==\s*15',             # == 15
        r'for\s+.*\s+in\s+range\s*\([^)]*\)'  # cualquier range
    ]
    
    # Archivos a revisar
    files_to_check = [
        "trajectory_hub/core/spat_osc_bridge.py",
        "trajectory_hub/core/enhanced_trajectory_engine.py",
        "trajectory_hub/config.py",
        "trajectory_hub/interface/interactive_controller.py"
    ]
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            print(f"\n📄 {filepath}:")
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            found_something = False
            for i, line in enumerate(lines):
                # Buscar número 15
                if '15' in line and not line.strip().startswith('#'):
                    print(f"   Línea {i+1}: {line.strip()}")
                    found_something = True
                    
                # Buscar range específicos
                if 'range(' in line and not line.strip().startswith('#'):
                    print(f"   ⚠️ Range en línea {i+1}: {line.strip()}")
                    found_something = True
                    
            if not found_something:
                print("   (Nada relevante encontrado)")

if __name__ == "__main__":
    find_15_limit()