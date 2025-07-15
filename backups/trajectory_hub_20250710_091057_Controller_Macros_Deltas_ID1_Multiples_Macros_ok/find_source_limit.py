#!/usr/bin/env python3
# 🔧 Fix: Encontrar dónde se limitan las sources
# ⚡ Líneas a revisar en spat_osc_bridge.py
# 🎯 Impacto: ALTO

import os
import re

def find_limits():
    print("\n🔍 BUSCANDO LÍMITES DE SOURCES")
    print("=" * 60)
    
    files_to_check = [
        "trajectory_hub/core/spat_osc_bridge.py",
        "trajectory_hub/core/enhanced_trajectory_engine.py",
        "trajectory_hub/config.py"
    ]
    
    patterns = [
        r'range\s*\(\s*1\s*,\s*17\s*\)',  # range(1, 17)
        r'range\s*\(\s*2\s*,\s*17\s*\)',  # range(2, 17)
        r'for\s+i\s+in\s+range\s*\([^)]*16[^)]*\)',
        r'[:]\s*16\s*]',  # [:16]
        r'source_id\s*[<>]=?\s*16',
        r'if\s+.*\s+16\s+',
        r'MAX_SOURCES?\s*=\s*16'
    ]
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            print(f"\n📄 {filepath}:")
            with open(filepath, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
            for i, line in enumerate(lines):
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        print(f"   Línea {i+1}: {line.strip()}")
                        
                # Buscar source_id + 1
                if 'source_id + 1' in line or 'i + 1' in line:
                    print(f"   ⚠️ Línea {i+1}: {line.strip()}")

if __name__ == "__main__":
    find_limits()