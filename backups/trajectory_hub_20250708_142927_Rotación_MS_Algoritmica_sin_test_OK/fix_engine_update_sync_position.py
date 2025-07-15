# === fix_engine_update_sync_position.py ===
# 🔧 Fix: Sincronizar state.position ANTES de calcular deltas
# ⚡ CRÍTICO - Sin esto no hay movimiento en el primer update

import os
import re

def fix_position_sync():
    """Mover sincronización de position ANTES del cálculo de deltas"""
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Buscando sección de procesamiento de deltas...")
    
    # Buscar el patrón del procesamiento de deltas
    pattern = r'(# 🔧 PROCESAMIENTO DE DELTAS.*?for source_id, motion in self\.motion_states\.items\(\):)(.*?)(# CRÍTICO: Sincronizar state\.position con engine\._positions\s*motion\.state\.position = self\._positions\[source_id\]\.copy\(\))(.*?)(# FIN PROCESAMIENTO DE DELTAS)'
    
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        print("✅ Sección de deltas encontrada")
        
        # La sincronización está DESPUÉS del for loop, necesita estar DENTRO y AL PRINCIPIO
        # Reconstruir la sección correctamente
        intro = match.group(1)
        sync_line = match.group(3).strip()
        rest_of_loop = match.group(4)
        end = match.group(5)
        
        # Nueva estructura con sincronización AL PRINCIPIO del loop
        new_section = f"""{intro}
            # CRÍTICO: Sincronizar state.position ANTES de calcular deltas
            if hasattr(motion, 'state'):
                motion.state.position = self._positions[source_id].copy()
            {rest_of_loop}{end}"""
        
        # Quitar la línea de sincronización del lugar incorrecto
        new_section = new_section.replace(sync_line, '')
        
        # Reemplazar
        new_content = content.replace(match.group(0), new_section)
        
        if new_content != content:
            # Backup
            import shutil
            from datetime import datetime
            backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_name)
            
            # Guardar
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Sincronización movida al inicio del loop")
            return True
    
    # Si no encontró el patrón exacto, buscar de forma más general
    print("⚠️ Patrón no encontrado, buscando de forma alternativa...")
    
    # Buscar la línea específica
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'motion.state.position = self._positions[source_id].copy()' in line:
            print(f"📍 Sincronización encontrada en línea {i+1}")
            
            # Ver contexto
            print("\n📋 Contexto:")
            for j in range(max(0, i-5), min(len(lines), i+5)):
                print(f"{j+1:4d}: {lines[j]}")
            
            # Si está FUERA del loop de update_with_deltas, moverla DENTRO
            # Buscar el for loop más cercano hacia arriba
            for j in range(i, max(0, i-20), -1):
                if 'for source_id, motion in self.motion_states.items():' in lines[j]:
                    print(f"\n✅ Loop encontrado en línea {j+1}")
                    
                    # Insertar la sincronización justo después del for
                    indent = len(lines[j]) - len(lines[j].lstrip()) + 4
                    sync_line = ' ' * indent + 'if hasattr(motion, "state"):\n'
                    sync_line += ' ' * (indent + 4) + 'motion.state.position = self._positions[source_id].copy()\n'
                    
                    # Insertar después del for
                    lines.insert(j+1, sync_line)
                    
                    # Eliminar la línea original
                    if i < len(lines) - 1:
                        lines.pop(i+2)  # +2 porque insertamos una línea
                    
                    # Guardar
                    new_content = '\n'.join(lines)
                    
                    import shutil
                    from datetime import datetime
                    backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(file_path, backup_name)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print("\n✅ Sincronización movida exitosamente")
                    return True
            
            break
    
    print("\n❌ No se pudo aplicar el fix automáticamente")
    return False

if __name__ == "__main__":
    print("🔧 Arreglando sincronización de state.position...")
    
    if fix_position_sync():
        print("\n✅ Fix aplicado - ESTE ES EL FIX FINAL")
        print("📝 Ejecuta: python test_macro_rotation_final_working.py")
        print("\n🎉 Con este fix, MacroRotation debería funcionar al 100%")
    else:
        print("\n⚠️ Aplicar manualmente:")
        print("  En engine.update(), mover la línea:")
        print("    motion.state.position = self._positions[source_id].copy()")
        print("  DENTRO del loop 'for source_id, motion' y AL PRINCIPIO")