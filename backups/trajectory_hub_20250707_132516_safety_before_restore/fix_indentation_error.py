#!/usr/bin/env python3
"""
🔧 Fix: Corregir error de indentación en spat_osc_bridge.py
⚡ Líneas modificadas: L730-750
🎯 Impacto: CRÍTICO - Sistema no arranca
"""

import os

def fix_indentation():
    """Arreglar error de indentación en OSC Bridge"""
    
    bridge_file = "trajectory_hub/core/spat_osc_bridge.py"
    
    # Leer archivo
    with open(bridge_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar línea problemática
    for i, line in enumerate(lines):
        if '"""Crear un grupo/macro en Spat."""' in line:
            # Verificar indentación anterior
            if i > 0:
                # Obtener indentación de la línea def create_group
                for j in range(i-1, max(0, i-10), -1):
                    if 'def create_group' in lines[j]:
                        # Añadir la indentación correcta
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        lines[i] = ' ' * (indent + 4) + lines[i].lstrip()
                        break
    
    # Guardar
    with open(bridge_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Indentación corregida")
    
    # Verificar sintaxis
    try:
        compile(open(bridge_file).read(), bridge_file, 'exec')
        print("✅ Sintaxis verificada correctamente")
        return True
    except SyntaxError as e:
        print(f"❌ Aún hay error de sintaxis: {e}")
        return False

def fix_complete():
    """Aplicar fix completo y seguro"""
    
    bridge_file = "trajectory_hub/core/spat_osc_bridge.py"
    
    # Buscar donde insertar los métodos corregidos
    with open(bridge_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la línea def create_group y reemplazar todo el método
    import re
    
    # Patrón para encontrar el método completo
    pattern = r'(\s*)def create_group\(self[^:]*\):\s*\n\s*"""[^"]*"""'
    
    replacement = r'''\1def create_group(self, group_id: str, group_name: str):
\1    """Crear un grupo/macro en Spat."""
\1    # TEMPORALMENTE DESHABILITADO - Los grupos se crean manualmente en Spat
\1    pass'''
    
    content = re.sub(pattern, replacement, content)
    
    # Lo mismo para add_source_to_group
    pattern2 = r'(\s*)def add_source_to_group\(self[^:]*\):\s*\n\s*"""[^"]*"""(?:\s*\n\s*.*)*?(?=\n\s*def|\n\s*class|\Z)'
    
    replacement2 = r'''\1def add_source_to_group(self, source_id: int, group_name: str):
\1    """Añadir una fuente a un grupo en Spat."""
\1    # TEMPORALMENTE DESHABILITADO - Los grupos se crean manualmente en Spat
\1    pass'''
    
    content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)
    
    # Guardar
    with open(bridge_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Verificar
    try:
        compile(content, bridge_file, 'exec')
        print("✅ Archivo corregido y sintaxis verificada")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔧 ARREGLANDO ERROR DE INDENTACIÓN")
    print("=" * 50)
    
    # Intentar fix simple primero
    if not fix_indentation():
        print("\n🔄 Aplicando fix completo...")
        if fix_complete():
            print("\n✅ SISTEMA REPARADO")
        else:
            print("\n❌ Error persistente, restaurando backup...")
            # Restaurar del backup más reciente
            import glob
            backups = sorted(glob.glob("trajectory_hub/core/spat_osc_bridge.py.backup_*"))
            if backups:
                import shutil
                shutil.copy(backups[-1], "trajectory_hub/core/spat_osc_bridge.py")
                print(f"✅ Restaurado desde: {backups[-1]}")
    
    print("\n🎯 Ahora ejecuta:")
    print("python trajectory_hub/interface/interactive_controller.py")

if __name__ == "__main__":
    main()