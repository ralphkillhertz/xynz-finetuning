#!/usr/bin/env python3
"""
fix_concentration_final.py - Corrección final del sistema de concentración
"""

import os
import re
from datetime import datetime

def fix_concentration_component_creation():
    """Asegurar que concentration se crea automáticamente"""
    print("🔧 CORRIGIENDO CREACIÓN AUTOMÁTICA DE CONCENTRATION...\n")
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    # Backup
    backup_name = f"{filepath}.backup_finalfix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar SourceMotion.__init__
    pattern = r'(class SourceMotion.*?def __init__.*?)(self\.components\[\'environmental_forces\'\].*?\n)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Buscar si ya tiene concentration
        init_content = match.group(0)
        
        if "self.components['concentration']" not in init_content:
            print("❌ concentration NO se crea en __init__")
            
            # Agregar después de environmental_forces
            insert_after = match.group(2)
            concentration_line = "        self.components['concentration'] = ConcentrationComponent()\n"
            
            # Reemplazar
            new_content = content.replace(
                insert_after,
                insert_after + concentration_line
            )
            
            # Guardar
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Agregada creación automática de ConcentrationComponent")
            return True
        else:
            print("✅ concentration ya se crea automáticamente")
            return False
    else:
        print("❌ No se encontró SourceMotion.__init__")
        return False

def fix_position_sync_in_update():
    """Corregir la sincronización de posiciones en engine.update()"""
    print("\n\n🔧 CORRIGIENDO SINCRONIZACIÓN EN ENGINE.UPDATE()...\n")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Backup
    backup_name = f"{filepath}.backup_syncfix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método update
    # Necesitamos encontrar dónde se llama motion.update y asegurar que después se sincroniza
    
    # Buscar el patrón de motion.update
    pattern = r'(motion\.update\(self\._time, self\.dt\))'
    
    # Verificar si ya tiene sincronización después
    sync_pattern = r'motion\.update\(self\._time, self\.dt\)\s*\n\s*.*self\._positions\[source_id\]'
    
    if re.search(sync_pattern, content):
        print("✅ Ya tiene sincronización después de motion.update")
        return False
    
    # Si no tiene, agregar
    def add_sync(match):
        update_call = match.group(0)
        # Obtener la indentación
        lines = content[:match.start()].split('\n')
        last_line = lines[-1] if lines else ""
        indent = len(last_line) - len(last_line.lstrip())
        
        # Agregar sincronización
        sync_code = f'''
                
                # CRÍTICO: Sincronizar posición después de update
                self._positions[source_id] = motion.state.position.copy()
                
                # Sincronizar también orientación y apertura
                if hasattr(self, '_orientations'):
                    self._orientations[source_id] = motion.state.orientation
                if hasattr(self, '_apertures'):
                    self._apertures[source_id] = motion.state.aperture'''
        
        return update_call + sync_code
    
    # Aplicar el reemplazo
    new_content = re.sub(pattern, add_sync, content)
    
    if new_content != content:
        # Guardar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Agregada sincronización después de motion.update()")
        return True
    else:
        print("⚠️  No se encontró el patrón esperado")
        
        # Buscar manualmente en el método update
        lines = content.split('\n')
        in_update = False
        changes_made = False
        
        for i, line in enumerate(lines):
            if 'def update(self):' in line:
                in_update = True
            elif in_update and 'motion.update(' in line:
                # Verificar las siguientes líneas
                if i+1 < len(lines) and '_positions' not in lines[i+1]:
                    # Agregar sincronización
                    indent = len(line) - len(line.lstrip())
                    lines.insert(i+1, " " * indent + "# Sincronizar con arrays principales")
                    lines.insert(i+2, " " * indent + "self._positions[source_id] = motion.state.position.copy()")
                    changes_made = True
                    print(f"✅ Agregada sincronización en línea {i+2}")
                    break
        
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return True
        
        return False

def test_concentration_final():
    """Test final del sistema completo"""
    print("\n\n🧪 TEST FINAL DEL SISTEMA...\n")
    
    test_code = '''
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

# Crear engine
engine = EnhancedTrajectoryEngine()

# Crear macro
macro_id = engine.create_macro("test", 5, formation="circle", spacing=3.0)
macro = engine._macros[macro_id]

# Verificar componentes
sid = list(macro.source_ids)[0]
motion = engine._source_motions[sid]

print("1. Verificando componentes:")
if 'concentration' in motion.components:
    print("   ✅ ConcentrationComponent existe")
else:
    print("   ❌ ConcentrationComponent NO existe")

# Posición inicial
initial_pos = engine._positions[sid].copy()
print(f"\\n2. Posición inicial en _positions: {initial_pos}")

# Aplicar concentración
engine.set_macro_concentration(macro_id, 0.0)

# Updates
print("\\n3. Ejecutando 10 updates...")
for i in range(10):
    engine.update()

# Verificar resultado
final_pos = engine._positions[sid]
motion_pos = motion.state.position

print(f"\\n4. Resultados:")
print(f"   motion.state.position: {motion_pos}")
print(f"   _positions[{sid}]: {final_pos}")
print(f"   ¿Sincronizado?: {np.allclose(motion_pos, final_pos)}")

distance = np.linalg.norm(final_pos - initial_pos)
print(f"\\n5. Distancia movida: {distance:.3f}")

if distance > 0.1:
    print("\\n✅ ¡LA CONCENTRACIÓN FUNCIONA Y SE SINCRONIZA CON SPAT!")
else:
    print("\\n❌ La concentración NO funciona")
'''
    
    # Ejecutar test
    import subprocess
    result = subprocess.run(['python', '-c', test_code], capture_output=True, text=True)
    
    print("Resultado:")
    print("-" * 60)
    print(result.stdout)
    if result.stderr and "INFO:" not in result.stderr:
        print("Errores:")
        print(result.stderr)
    print("-" * 60)
    
    return "FUNCIONA Y SE SINCRONIZA" in result.stdout

def main():
    print("="*70)
    print("🔧 CORRECCIÓN FINAL DEL SISTEMA DE CONCENTRACIÓN")
    print("="*70)
    
    # Aplicar correcciones
    fix1 = fix_concentration_component_creation()
    fix2 = fix_position_sync_in_update()
    
    if fix1 or fix2:
        print("\n✅ Correcciones aplicadas")
        
        # Test final
        if test_concentration_final():
            print("\n" + "="*70)
            print("🎉 ¡SISTEMA DE CONCENTRACIÓN COMPLETAMENTE FUNCIONAL!")
            print("="*70)
            print("\nAhora:")
            print("1. Reinicia el controlador")
            print("2. La concentración funcionará correctamente en Spat")
            print("\n✅ Las fuentes se concentrarán visualmente en Spat")
        else:
            print("\n⚠️  Se aplicaron correcciones pero puede necesitar verificación adicional")
    else:
        print("\n⚠️  No se necesitaron cambios adicionales")
        print("   Verifica que el controlador esté actualizado")

if __name__ == "__main__":
    main()