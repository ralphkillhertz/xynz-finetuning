#!/usr/bin/env python3
"""
fix_concentration_sync.py - Corrige la sincronización de concentración con Spat
"""

import os
import re
from datetime import datetime

def fix_position_sync():
    """Asegurar que las posiciones se sincronizan después de update"""
    print("🔧 CORRIGIENDO SINCRONIZACIÓN DE POSICIONES...\n")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Backup
    backup_name = f"{filepath}.backup_concsync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método update
    pattern = r'(def update\(self\):.*?)(return)'
    
    def fix_update(match):
        method_content = match.group(1)
        return_statement = match.group(2)
        
        # Verificar si ya tiene sincronización correcta
        if "self._positions[source_id] = motion.state.position" in method_content:
            print("✅ Ya tiene sincronización de posiciones")
            return match.group(0)
        
        # Buscar donde se llama motion.update
        if "motion.update(" in method_content:
            # Agregar sincronización después de motion.update
            lines = method_content.split('\n')
            new_lines = []
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                # Después de motion.update, agregar sincronización
                if "motion.update(" in line:
                    indent = len(line) - len(line.lstrip())
                    
                    # Agregar líneas de sincronización
                    new_lines.append(" " * indent + "")
                    new_lines.append(" " * indent + "# Sincronizar posición con el array principal")
                    new_lines.append(" " * indent + "self._positions[source_id] = motion.state.position.copy()")
                    new_lines.append(" " * indent + "")
                    new_lines.append(" " * indent + "# Sincronizar orientación si existe")
                    new_lines.append(" " * indent + "if hasattr(self, '_orientations'):")
                    new_lines.append(" " * (indent + 4) + "self._orientations[source_id] = motion.state.orientation")
                    
                    print(f"✅ Agregada sincronización después de motion.update")
            
            return '\n'.join(new_lines) + '\n' + return_statement
        
        return match.group(0)
    
    # Aplicar fix
    new_content = re.sub(pattern, fix_update, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("\n✅ Archivo actualizado")
        return True
    
    return False

def verify_concentration_update():
    """Verificar que ConcentrationComponent.update se ejecuta"""
    print("\n\n🔍 VERIFICANDO QUE CONCENTRATION SE EJECUTA...\n")
    
    # Verificar en SourceMotion.update
    filepath = "trajectory_hub/core/motion_components.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar en SourceMotion.update
    pattern = r'class SourceMotion.*?def update\(self.*?\):(.*?)(?=\n    def|\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        update_content = match.group(1)
        
        # Verificar que concentration se procesa
        if "'concentration'" in update_content:
            print("✅ SourceMotion.update procesa el componente concentration")
            
            # Ver si es el último
            lines = update_content.split('\n')
            concentration_line = -1
            last_component_line = -1
            
            for i, line in enumerate(lines):
                if "'concentration'" in line:
                    concentration_line = i
                if "components" in line and "update" in line:
                    last_component_line = i
            
            if concentration_line > last_component_line - 5:
                print("✅ Concentration se procesa al final (correcto)")
            else:
                print("⚠️  Concentration NO se procesa al final")
        else:
            print("❌ SourceMotion.update NO procesa concentration")
            print("   Necesitamos agregarlo")

if __name__ == "__main__":
    print("="*60)
    print("🔧 FIX PARA SINCRONIZACIÓN DE CONCENTRACIÓN")
    print("="*60)
    
    # Aplicar correcciones
    if fix_position_sync():
        verify_concentration_update()
        
        print("\n" + "="*60)
        print("✅ CORRECCIONES APLICADAS")
        print("\nReinicia el controlador y prueba de nuevo la concentración")
    else:
        print("\n⚠️  No se necesitaron cambios")
        verify_concentration_update()
