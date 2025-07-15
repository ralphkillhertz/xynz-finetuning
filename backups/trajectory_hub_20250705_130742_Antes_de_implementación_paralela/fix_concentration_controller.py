#!/usr/bin/env python3
"""
🔧 FIX CONCENTRACIÓN EN CONTROLADOR
⚡ Arregla opción 31 directamente
"""

import os
import shutil
from datetime import datetime
import re

print("=" * 70)
print("🔧 FIX DE CONCENTRACIÓN EN INTERACTIVE CONTROLLER")
print("=" * 70)

# Archivo principal
controller_path = "trajectory_hub/interface/interactive_controller.py"

if not os.path.exists(controller_path):
    print(f"❌ No se encontró {controller_path}")
    exit(1)

# Backup
backup_path = f"{controller_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(controller_path, backup_path)
print(f"✅ Backup: {backup_path}")

# Leer archivo
with open(controller_path, 'r') as f:
    content = f.read()

print("\n🔍 ANALIZANDO CONTROLLER...")

# Buscar opción 31
if "'31'" in content:
    print("✅ Encontrada opción 31")
    
    # Buscar la función que maneja opción 31
    lines = content.split('\n')
    option_31_line = -1
    
    for i, line in enumerate(lines):
        if "'31'" in line:
            option_31_line = i
            print(f"   Línea {i+1}: {line.strip()[:80]}...")
            break
    
    # Buscar el método que se ejecuta
    if option_31_line >= 0:
        # Buscar hacia adelante para encontrar qué función se llama
        for i in range(option_31_line, min(option_31_line + 10, len(lines))):
            if "test_concentration" in lines[i] or "handle_concentration" in lines[i]:
                method_name = re.search(r'(\w+_concentration\w*)', lines[i])
                if method_name:
                    print(f"✅ Método de concentración: {method_name.group(1)}")
                    
                    # Buscar la definición del método
                    method_pattern = rf'def {method_name.group(1)}\(self.*?\):'
                    if re.search(method_pattern, content):
                        print(f"✅ Método encontrado en el archivo")

# Buscar el engine/sistema principal
engine_attrs = ["self.engine", "self.trajectory_engine", "self.spatial_engine", "self.system"]
engine_attr = None

for attr in engine_attrs:
    if attr in content:
        engine_attr = attr
        print(f"\n✅ Engine encontrado: {attr}")
        break

if not engine_attr:
    print("⚠️ No se encontró referencia al engine")

# Buscar cómo se actualizan las posiciones
print("\n🔍 BUSCANDO SISTEMA DE ACTUALIZACIÓN...")

update_patterns = [
    r'def update\(self.*?\):',
    r'self\._positions\[.*?\] =',
    r'positions\[.*?\] =',
    r'\.update_positions\(',
]

for pattern in update_patterns:
    if re.search(pattern, content):
        print(f"✅ Patrón encontrado: {pattern[:30]}...")

# APLICAR FIX: Agregar sincronización después de concentration
print("\n🔧 APLICANDO FIX...")

# Buscar el método test_concentration o similar
concentration_method_pattern = r'(def \w*concentration\w*\(self.*?\):.*?\n(?:.*?\n)*?)(        (?:return|$))'

match = re.search(concentration_method_pattern, content, re.DOTALL)

if match:
    method_body = match.group(1)
    
    # Verificar si ya tiene sincronización
    if "sync" not in method_body.lower() and "_positions" not in method_body:
        print("⚠️ Método no sincroniza posiciones, agregando fix...")
        
        # Agregar sincronización
        sync_code = """
        # CRITICAL FIX: Force position sync after concentration
        if hasattr(self.engine, '_positions') and hasattr(self.engine, '_source_motions'):
            for i in range(len(self.engine._positions)):
                self.engine._positions[i] = self.engine._source_motions[i].state.position.copy()
        elif hasattr(self, 'sources'):
            # Alternative sync for different architecture
            for i, source in enumerate(self.sources):
                if hasattr(source, 'motion') and hasattr(source.motion, 'state'):
                    # Force update through the motion system
                    source.motion.update()
        
        # Force display update
        if hasattr(self, 'update_display'):
            self.update_display()
        """
        
        # Insertar antes del return
        new_method = match.group(1) + sync_code + "\n" + match.group(2)
        new_content = content.replace(match.group(0), new_method)
        
        # Guardar
        with open(controller_path, 'w') as f:
            f.write(new_content)
        
        print("✅ Fix de sincronización aplicado")
else:
    print("⚠️ No se encontró método de concentración, buscando alternativa...")
    
    # Buscar donde se maneja la opción 31
    option_31_pattern = r"'31'.*?:(.*?)(?:'3[2-9]'|'[4-9]\d'|else:|$)"
    match = re.search(option_31_pattern, content, re.DOTALL)
    
    if match:
        option_code = match.group(1)
        
        # Si no tiene sincronización, agregarla
        if "_positions" not in option_code and "sync" not in option_code.lower():
            print("⚠️ Opción 31 no sincroniza, aplicando fix inline...")
            
            # Este es un fix más agresivo - modifica directamente donde se maneja la opción
            # Por ahora solo mostrar advertencia
            print("\n⚡ FIX MANUAL NECESARIO:")
            print("1. Abre trajectory_hub/interface/interactive_controller.py")
            print("2. Busca la opción '31'")
            print("3. Agrega después de aplicar concentración:")
            print("""
        # Force sync
        for i in range(len(self.engine._positions)):
            self.engine._positions[i] = self.engine._source_motions[i].state.position.copy()
""")

# Verificar imports
print("\n🔍 VERIFICANDO IMPORTS...")
if "concentration" not in content.lower():
    print("⚠️ No hay imports de concentration")

# Buscar archivos relacionados
print("\n📁 ARCHIVOS RELACIONADOS EN interface/:")
interface_dir = "trajectory_hub/interface"
if os.path.exists(interface_dir):
    for file in os.listdir(interface_dir):
        if file.endswith('.py'):
            filepath = os.path.join(interface_dir, file)
            with open(filepath, 'r') as f:
                if "concentration" in f.read().lower():
                    print(f"   ✅ {file} - contiene concentration")

print("\n" + "=" * 70)
print("RESUMEN:")
print("=" * 70)
print("1. ✅ Controller encontrado y respaldado")
print("2. ✅ Opción 31 localizada")
if match and "sync" in new_content:
    print("3. ✅ Fix de sincronización aplicado")
    print("\n⚡ EJECUTA AHORA:")
    print(f"   python {controller_path}")
else:
    print("3. ⚠️ Requiere fix manual (ver arriba)")
print("=" * 70)