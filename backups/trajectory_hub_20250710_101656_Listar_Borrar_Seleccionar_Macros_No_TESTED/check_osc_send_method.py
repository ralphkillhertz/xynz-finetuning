#!/usr/bin/env python3
# 🔧 Fix: Revisar método send_source_positions
# ⚡ Buscar límites ocultos en el envío OSC
# 🎯 Impacto: CRÍTICO

import os

def check_osc_send():
    print("\n🔍 REVISANDO MÉTODO send_source_positions")
    print("=" * 60)
    
    file_path = "trajectory_hub/core/spat_osc_bridge.py"
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Buscar el método send_source_positions
        in_method = False
        method_lines = []
        indent_level = None
        
        for i, line in enumerate(lines):
            if 'def send_source_positions' in line:
                in_method = True
                indent_level = len(line) - len(line.lstrip())
                print(f"\n📍 Método encontrado en línea {i+1}:")
                
            if in_method:
                # Si encontramos una línea con menor indentación, salimos
                if line.strip() and (len(line) - len(line.lstrip())) <= indent_level and i > 0:
                    if 'def ' in line:
                        break
                        
                method_lines.append((i+1, line.rstrip()))
                
        # Mostrar el método completo
        for line_num, line in method_lines:
            print(f"{line_num:4d}: {line}")
            
        # Buscar posibles problemas
        print("\n⚠️ POSIBLES PROBLEMAS:")
        for line_num, line in method_lines:
            if 'for' in line and 'in' in line:
                print(f"   Loop en línea {line_num}: {line.strip()}")
            if 'enumerate' in line:
                print(f"   Enumerate en línea {line_num}: {line.strip()}")
            if '[' in line and ']' in line:
                print(f"   Posible slice en línea {line_num}: {line.strip()}")

if __name__ == "__main__":
    check_osc_send()