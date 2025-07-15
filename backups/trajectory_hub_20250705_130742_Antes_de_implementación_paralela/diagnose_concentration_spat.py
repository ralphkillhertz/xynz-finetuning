#!/usr/bin/env python3
"""
diagnose_concentration_spat.py - Diagnostica por qué la concentración no llega a Spat
"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
import asyncio

async def diagnose_concentration():
    """Diagnosticar el problema de concentración"""
    print("🔍 DIAGNÓSTICO DE CONCENTRACIÓN EN SPAT\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    
    # Crear macro de prueba
    print("1. Creando macro de prueba...")
    macro_id = engine.create_macro("test_concentration", 5, formation="circle", spacing=3.0)
    print(f"   ✅ Macro creado: {macro_id}")
    
    # Obtener posiciones iniciales
    print("\n2. Posiciones iniciales:")
    initial_positions = {}
    if hasattr(engine, '_source_motions'):
        macro = engine._macros.get(macro_id)
        if macro:
            for i, sid in enumerate(list(macro.source_ids)[:3]):  # Primeras 3 fuentes
                if sid in engine._source_motions:
                    pos = engine._source_motions[sid].state.position
                    initial_positions[sid] = pos.copy()
                    print(f"   Fuente {sid}: {pos}")
    
    # Establecer concentración
    print("\n3. Estableciendo concentración en 0.0...")
    engine.set_macro_concentration(macro_id, 0.0)
    
    # Verificar estado del componente
    print("\n4. Verificando componentes de concentración:")
    if hasattr(engine, '_source_motions'):
        macro = engine._macros.get(macro_id)
        if macro:
            for sid in list(macro.source_ids)[:1]:  # Primera fuente
                if sid in engine._source_motions:
                    motion = engine._source_motions[sid]
                    if 'concentration' in motion.components:
                        conc = motion.components['concentration']
                        print(f"   ✅ ConcentrationComponent existe")
                        print(f"      - Enabled: {conc.enabled}")
                        print(f"      - Factor: {conc.factor}")
                        print(f"      - Target point: {conc.target_point}")
                    else:
                        print(f"   ❌ NO hay ConcentrationComponent")
    
    # Hacer varios updates
    print("\n5. Ejecutando updates...")
    for i in range(10):
        engine.update()
    
    # Verificar posiciones después
    print("\n6. Posiciones después de updates:")
    final_positions = {}
    positions_changed = False
    
    if hasattr(engine, '_source_motions'):
        macro = engine._macros.get(macro_id)
        if macro:
            for i, sid in enumerate(list(macro.source_ids)[:3]):
                if sid in engine._source_motions:
                    pos = engine._source_motions[sid].state.position
                    final_positions[sid] = pos.copy()
                    
                    if sid in initial_positions:
                        diff = np.linalg.norm(pos - initial_positions[sid])
                        print(f"   Fuente {sid}: {pos} (cambio: {diff:.3f})")
                        if diff > 0.01:
                            positions_changed = True
    
    # Verificar el array _positions que se envía a Spat
    print("\n7. Verificando array _positions (lo que se envía a Spat):")
    if hasattr(engine, '_positions'):
        for sid in list(macro.source_ids)[:3]:
            pos = engine._positions[sid]
            print(f"   _positions[{sid}]: {pos}")
    
    # Diagnóstico
    print("\n" + "="*60)
    print("DIAGNÓSTICO:")
    
    if not positions_changed:
        print("❌ Las posiciones NO cambiaron")
        print("\nPosibles causas:")
        print("1. El componente de concentración no se está ejecutando")
        print("2. El componente está deshabilitado")
        print("3. El update no está propagando a los componentes")
    else:
        print("✅ Las posiciones SÍ cambiaron en SourceMotion")
        print("❌ Pero puede que no se estén sincronizando con _positions")
    
    # Verificar sincronización
    print("\n8. Verificando sincronización con _positions:")
    sync_ok = True
    for sid in list(macro.source_ids)[:3]:
        if sid in engine._source_motions:
            motion_pos = engine._source_motions[sid].state.position
            array_pos = engine._positions[sid]
            diff = np.linalg.norm(motion_pos - array_pos)
            if diff > 0.001:
                print(f"   ❌ Fuente {sid} NO sincronizada (diff: {diff})")
                sync_ok = False
            else:
                print(f"   ✅ Fuente {sid} sincronizada")
    
    if not sync_ok:
        print("\n❌ PROBLEMA: Las posiciones no se sincronizan con _positions")
        print("   Esto explica por qué no llega a Spat")
    
    return positions_changed, sync_ok

def check_update_chain():
    """Verificar la cadena de updates"""
    print("\n\n🔍 VERIFICANDO CADENA DE UPDATES...\n")
    
    # Verificar enhanced_trajectory_engine.py
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar en el método update
    print("Buscando en método update()...")
    
    # Verificar si motion.update se llama
    if "motion.update(" in content:
        print("✅ motion.update() se llama")
    else:
        print("❌ motion.update() NO se llama")
    
    # Verificar si se sincronizan las posiciones
    if "self._positions[source_id] = motion.state.position" in content or \
       "self._positions[sid] = motion.state.position" in content:
        print("✅ Las posiciones se sincronizan con _positions")
    else:
        print("❌ Las posiciones NO se sincronizan con _positions")
    
    # Buscar el update específico
    import re
    update_pattern = r'def update\(self\):(.*?)(?=\n    def|\nclass|\Z)'
    match = re.search(update_pattern, content, re.DOTALL)
    
    if match:
        update_content = match.group(1)
        
        # Verificar componentes críticos
        if "motion.update" in update_content:
            print("✅ motion.update está en el método update")
            
            # Ver si sincroniza después
            if "_positions" in update_content:
                print("✅ _positions se actualiza en update")
            else:
                print("❌ _positions NO se actualiza en update")

def create_fix_script():
    """Crear script para corregir el problema"""
    fix_code = '''#!/usr/bin/env python3
"""
fix_concentration_sync.py - Corrige la sincronización de concentración con Spat
"""

import os
import re
from datetime import datetime

def fix_position_sync():
    """Asegurar que las posiciones se sincronizan después de update"""
    print("🔧 CORRIGIENDO SINCRONIZACIÓN DE POSICIONES...\\n")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Backup
    backup_name = f"{filepath}.backup_concsync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método update
    pattern = r'(def update\\(self\\):.*?)(return)'
    
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
            lines = method_content.split('\\n')
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
            
            return '\\n'.join(new_lines) + '\\n' + return_statement
        
        return match.group(0)
    
    # Aplicar fix
    new_content = re.sub(pattern, fix_update, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("\\n✅ Archivo actualizado")
        return True
    
    return False

def verify_concentration_update():
    """Verificar que ConcentrationComponent.update se ejecuta"""
    print("\\n\\n🔍 VERIFICANDO QUE CONCENTRATION SE EJECUTA...\\n")
    
    # Verificar en SourceMotion.update
    filepath = "trajectory_hub/core/motion_components.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar en SourceMotion.update
    pattern = r'class SourceMotion.*?def update\\(self.*?\\):(.*?)(?=\\n    def|\\nclass|\\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        update_content = match.group(1)
        
        # Verificar que concentration se procesa
        if "'concentration'" in update_content:
            print("✅ SourceMotion.update procesa el componente concentration")
            
            # Ver si es el último
            lines = update_content.split('\\n')
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
        
        print("\\n" + "="*60)
        print("✅ CORRECCIONES APLICADAS")
        print("\\nReinicia el controlador y prueba de nuevo la concentración")
    else:
        print("\\n⚠️  No se necesitaron cambios")
        verify_concentration_update()
'''
    
    with open("fix_concentration_sync.py", 'w', encoding='utf-8') as f:
        f.write(fix_code)
    
    print("\n✅ fix_concentration_sync.py creado")

async def main():
    print("="*60)
    print("🔍 DIAGNÓSTICO: CONCENTRACIÓN NO LLEGA A SPAT")
    print("="*60)
    
    # Diagnóstico
    positions_changed, sync_ok = await diagnose_concentration()
    
    # Verificar cadena de updates
    check_update_chain()
    
    # Crear script de corrección
    create_fix_script()
    
    print("\n" + "="*60)
    print("SOLUCIÓN:")
    print("\n1. Ejecuta el script de corrección:")
    print("   python fix_concentration_sync.py")
    print("\n2. Reinicia el controlador")
    print("\n3. Prueba la concentración de nuevo")

if __name__ == "__main__":
    asyncio.run(main())