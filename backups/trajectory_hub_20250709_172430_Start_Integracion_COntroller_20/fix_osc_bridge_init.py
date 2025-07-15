#!/usr/bin/env python3
"""
🔧 Fix: OSC Bridge no inicializado
⚡ Asegurar que engine tenga osc_bridge
"""

import os

# Verificar el problema en interactive_controller.py
ic_path = "trajectory_hub/interface/interactive_controller.py"

with open(ic_path, 'r') as f:
    lines = f.readlines()

# Buscar línea 640 y contexto
fixed = False
for i, line in enumerate(lines):
    # Buscar donde se crea el engine
    if "engine = EnhancedTrajectoryEngine" in line and not "self.engine" in line:
        print(f"📍 Encontrado en línea {i+1}: {line.strip()}")
        
        # Verificar las siguientes líneas para osc_bridge
        for j in range(i+1, min(i+10, len(lines))):
            if "osc_bridge" in lines[j] and "add_target" in lines[j]:
                # Añadir verificación antes
                check_line = "    # Verificar que osc_bridge existe\n"
                init_line = "    if engine.osc_bridge is None:\n"
                create_line = "        from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge\n"
                create_line2 = "        engine.osc_bridge = SpatOSCBridge()\n"
                
                lines.insert(j, check_line)
                lines.insert(j+1, init_line)
                lines.insert(j+2, create_line)
                lines.insert(j+3, create_line2)
                
                print("✅ Añadida verificación de osc_bridge")
                fixed = True
                break
        break

if not fixed:
    # Buscar directamente la línea problemática
    for i, line in enumerate(lines):
        if "engine.osc_bridge.add_target" in line and i >= 635:
            # Añadir verificación
            indent = len(line) - len(line.lstrip())
            check = " " * indent + "if engine.osc_bridge is None:\n"
            init1 = " " * (indent + 4) + "from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge\n"
            init2 = " " * (indent + 4) + "engine.osc_bridge = SpatOSCBridge()\n"
            
            lines.insert(i, check)
            lines.insert(i+1, init1)
            lines.insert(i+2, init2)
            print(f"✅ Fix aplicado en línea {i+1}")
            fixed = True
            break

# Guardar
if fixed:
    with open(ic_path, 'w') as f:
        f.writelines(lines)
    print("✅ Archivo corregido")
else:
    print("⚠️  No se encontró la línea problemática")
    print("   Aplicando fix alternativo...")
    
    # Fix alternativo: buscar main() y añadir después de crear engine
    for i, line in enumerate(lines):
        if "def main():" in line:
            # Buscar donde se crea engine
            for j in range(i, min(i+50, len(lines))):
                if "engine = EnhancedTrajectoryEngine()" in lines[j]:
                    # Añadir inicialización de osc_bridge
                    indent = len(lines[j]) - len(lines[j].lstrip())
                    new_lines = [
                        lines[j],
                        " " * indent + "# Asegurar osc_bridge\n",
                        " " * indent + "if engine.osc_bridge is None:\n",
                        " " * (indent + 4) + "from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge\n",
                        " " * (indent + 4) + "engine.osc_bridge = SpatOSCBridge()\n"
                    ]
                    lines[j] = "".join(new_lines)
                    
                    with open(ic_path, 'w') as f:
                        f.writelines(lines)
                    print("✅ Fix alternativo aplicado")
                    break
            break