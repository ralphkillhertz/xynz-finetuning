#!/usr/bin/env python3
# 🔧 Fix: Encontrar valor de n_sources
# ⚡ Buscar en constructor y config
# 🎯 Impacto: CRÍTICO

import os
import re

def find_n_sources():
    print("\n🔍 BUSCANDO VALOR DE n_sources")
    print("=" * 60)
    
    file_path = "trajectory_hub/core/spat_osc_bridge.py"
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Buscar n_sources
        for i, line in enumerate(lines):
            if 'n_sources' in line and not line.strip().startswith('#'):
                print(f"   Línea {i+1}: {line.strip()}")
                
        # Buscar __init__
        print("\n📍 Buscando constructor __init__:")
        in_init = False
        for i, line in enumerate(lines):
            if 'def __init__' in line:
                in_init = True
                print(f"\n   Constructor en línea {i+1}:")
                
            if in_init:
                if line.strip() and not line[0].isspace() and 'def' in line and '__init__' not in line:
                    break
                if in_init:
                    print(f"   {i+1}: {line.rstrip()}")
                    
    # Buscar en config.py también
    config_path = "trajectory_hub/config.py"
    if os.path.exists(config_path):
        print("\n📍 Buscando en config.py:")
        with open(config_path, 'r') as f:
            for i, line in enumerate(f):
                if 'n_sources' in line.lower() or 'sources' in line:
                    print(f"   Línea {i+1}: {line.strip()}")

if __name__ == "__main__":
    find_n_sources()