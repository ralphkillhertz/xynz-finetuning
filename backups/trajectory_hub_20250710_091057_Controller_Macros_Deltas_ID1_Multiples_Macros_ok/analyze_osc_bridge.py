#!/usr/bin/env python3
# 🔧 Fix: Analizar toda la clase SpatOSCBridge
# ⚡ Buscar el método send_source_positions completo
# 🎯 Impacto: CRÍTICO

import os
import re

def analyze_osc_bridge():
    print("\n🔍 ANALIZANDO SPAT OSC BRIDGE")
    print("=" * 60)
    
    file_path = "trajectory_hub/core/spat_osc_bridge.py"
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar el método send_source_positions
        print("\n📍 Buscando método send_source_positions...")
        
        for i, line in enumerate(lines):
            if 'send_source_positions' in line:
                # Mostrar contexto alrededor
                start = max(0, i - 2)
                end = min(len(lines), i + 20)
                
                print(f"\n🎯 Encontrado en línea {i+1}:")
                print("-" * 60)
                for j in range(start, end):
                    prefix = ">>>" if j == i else "   "
                    print(f"{prefix} {j+1:4d}: {lines[j]}")
                print("-" * 60)
        
        # Buscar cualquier iteración sobre positions
        print("\n📍 Buscando iteraciones sobre positions...")
        for i, line in enumerate(lines):
            if ('for' in line and 'positions' in line) or ('enumerate' in line and 'positions' in line):
                print(f"   Línea {i+1}: {line.strip()}")

if __name__ == "__main__":
    analyze_osc_bridge()