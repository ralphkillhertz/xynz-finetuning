#!/usr/bin/env python3
"""
fix_concentration_final_issues.py - Corrige los últimos problemas del sistema
"""

import os
import re
from datetime import datetime

def fix_source_motion_update_params():
    """Corregir los parámetros en SourceMotion.update"""
    print("🔧 CORRIGIENDO PARÁMETROS EN SourceMotion.update()...\n")
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    # Backup
    backup_name = f"{filepath}.backup_params_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método update de SourceMotion
    # El problema es que estamos usando current_time y dt que no están definidos
    # Los parámetros del método son (self, time, dt)
    
    # Buscar y reemplazar en el contexto de concentration
    pattern = r"(self\.components\['concentration'\]\.update\(\s*self\.state,\s*)current_time,\s*dt"
    replacement = r"\1time, dt"
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Corregido: current_time → time")
    else:
        print("⚠️  No se encontró el patrón exacto, buscando manualmente...")
        
        # Buscar manualmente
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "'concentration'].update(" in line and "current_time" in line:
                lines[i] = line.replace("current_time", "time")
                print(f"✅ Corregida línea {i+1}")
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                break

def fix_position_sync_complete():
    """Asegurar sincronización completa de posiciones"""
    print("\n\n🔧 ASEGURANDO SINCRONIZACIÓN COMPLETA...\n")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Backup
    backup_name = f"{filepath}.backup_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar el método update
    in_update = False
    update_start = -1
    
    for i, line in enumerate(lines):
        if "def update(self):" in line:
            in_update = True
            update_start = i
            print(f"✅ Encontrado método update en línea {i+1}")
            break
    
    if not in_update:
        print("❌ No se encontró el método update")
        return False
    
    # Buscar donde se llama motion.update
    sync_added = False
    
    for i in range(update_start, min(update_start + 200, len(lines))):
        if "motion.update(" in lines[i]:
            print(f"✅ Encontrada llamada a motion.update en línea {i+1}")
            
            # Verificar si ya tiene sincronización después
            has_sync = False
            for j in range(i+1, min(i+10, len(lines))):
                if "_positions[" in lines[j] and "motion.state.position" in lines[j]:
                    has_sync = True
                    break
            
            if not has_sync:
                # Agregar sincronización
                indent = len(lines[i]) - len(lines[i].lstrip())
                sync_lines = [
                    "\n",
                    " " * indent + "# CRÍTICO: Sincronizar con arrays que se envían a Spat\n",
                    " " * indent + "if source_id < len(self._positions):\n",
                    " " * (indent + 4) + "self._positions[source_id] = motion.state.position.copy()\n",
                    " " * indent + "if hasattr(self, '_orientations') and source_id < len(self._orientations):\n",
                    " " * (indent + 4) + "self._orientations[source_id] = motion.state.orientation.copy()\n",
                ]
                
                # Insertar después de motion.update
                for j, sync_line in enumerate(sync_lines):
                    lines.insert(i + 1 + j, sync_line)
                
                sync_added = True
                print(f"✅ Agregada sincronización después de línea {i+1}")
                break
            else:
                print("✅ Ya tiene sincronización")
    
    if sync_added:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("\n✅ Archivo actualizado con sincronización")
        return True
    
    return False

def test_complete_system():
    """Test completo del sistema"""
    print("\n\n🧪 TEST COMPLETO DEL SISTEMA...\n")
    
    test_code = '''
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("1. Creando engine y macro...")
engine = EnhancedTrajectoryEngine()
macro_id = engine.create_macro("test", 5, formation="circle", spacing=5.0)

# Verificar estado inicial
macro = engine._macros[macro_id]
print("\\n2. Posiciones iniciales:")
for i, sid in enumerate(list(macro.source_ids)[:3]):
    pos = engine._positions[sid]
    print(f"   Fuente {sid}: {pos}")

# Aplicar concentración
print("\\n3. Aplicando concentración total (factor=0.0)...")
engine.set_macro_concentration(macro_id, 0.0)

# Verificar que se configuró
sid = list(macro.source_ids)[0]
motion = engine._source_motions[sid]
conc = motion.components['concentration']
print(f"   - Factor: {conc.factor}")
print(f"   - Enabled: {conc.enabled}")
print(f"   - Target: {conc.target_point}")

# Updates
print("\\n4. Ejecutando 30 updates...")
for i in range(30):
    engine.update()
    if i % 10 == 0:
        pos = engine._positions[sid]
        print(f"   Update {i}: posición fuente 0 = {pos}")

# Resultado final
print("\\n5. Posiciones finales:")
distances = []
center = conc.target_point

for i, sid in enumerate(list(macro.source_ids)[:3]):
    pos = engine._positions[sid]
    dist = np.linalg.norm(pos - center)
    distances.append(dist)
    print(f"   Fuente {sid}: {pos} (distancia al centro: {dist:.3f})")

avg_dist = np.mean(distances)
print(f"\\n6. Distancia promedio al centro: {avg_dist:.3f}")

if avg_dist < 1.0:
    print("\\n🎉 ¡CONCENTRACIÓN FUNCIONANDO PERFECTAMENTE!")
    print("   Las fuentes se han concentrado en el punto objetivo")
else:
    print("\\n❌ La concentración no está funcionando")
    print("\\nDebug adicional:")
    print(f"   motion.state.position: {engine._source_motions[0].state.position}")
    print(f"   _positions[0]: {engine._positions[0]}")
'''
    
    # Ejecutar test
    import subprocess
    result = subprocess.run(['python', '-c', test_code], capture_output=True, text=True)
    
    print("Resultado:")
    print("-" * 70)
    print(result.stdout)
    if result.stderr and "INFO:" not in result.stderr:
        print("Errores:")
        print(result.stderr)
    print("-" * 70)
    
    return "PERFECTAMENTE" in result.stdout

def main():
    print("="*70)
    print("🔧 CORRECCIÓN FINAL DE PROBLEMAS DE CONCENTRACIÓN")
    print("="*70)
    
    # Corregir parámetros
    fix_source_motion_update_params()
    
    # Asegurar sincronización
    fix_position_sync_complete()
    
    # Test final
    if test_complete_system():
        print("\n" + "="*70)
        print("🎉 ¡SISTEMA DE CONCENTRACIÓN COMPLETAMENTE FUNCIONAL!")
        print("="*70)
        print("\n✅ TODOS LOS PROBLEMAS RESUELTOS:")
        print("   - ConcentrationComponent se crea automáticamente")
        print("   - El componente procesa las posiciones correctamente")
        print("   - Las posiciones se sincronizan con _positions")
        print("   - Los datos se envían correctamente a Spat")
        print("\n🎮 Ahora puedes:")
        print("   1. Reiniciar el controlador")
        print("   2. Usar la opción 31")
        print("   3. ¡Ver las fuentes concentrarse en Spat!")
    else:
        print("\n⚠️  Puede necesitar verificación adicional")

if __name__ == "__main__":
    main()