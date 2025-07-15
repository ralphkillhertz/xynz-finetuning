# === fix_sync_position_timing.py ===
# 🔧 Fix: Sincronizar ANTES de update_with_deltas
# ⚡ ESTE ES EL FIX DEFINITIVO

import os

def fix_sync_timing():
    """Asegurar que la sincronización ocurra ANTES de update_with_deltas"""
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("🔍 Buscando sección de procesamiento de deltas...")
    
    # Buscar las líneas clave
    sync_line_idx = -1
    update_deltas_idx = -1
    
    for i, line in enumerate(lines):
        if 'motion.state.position = self._positions[source_id].copy()' in line:
            sync_line_idx = i
            print(f"📍 Sincronización encontrada en línea {i+1}")
        elif 'motion.update_with_deltas' in line:
            update_deltas_idx = i
            print(f"📍 update_with_deltas en línea {i+1}")
    
    if sync_line_idx > 0 and update_deltas_idx > 0:
        print(f"\n📊 Orden actual:")
        print(f"   Sincronización: línea {sync_line_idx+1}")
        print(f"   update_with_deltas: línea {update_deltas_idx+1}")
        
        if sync_line_idx > update_deltas_idx:
            print("❌ PROBLEMA: Sincronización ocurre DESPUÉS de calcular deltas")
            
            # Necesitamos mover la sincronización ANTES
            # Extraer las líneas de sincronización
            sync_lines = []
            # Obtener la línea de sync y la anterior (el if)
            if 'if hasattr' in lines[sync_line_idx-1]:
                sync_lines.append(lines[sync_line_idx-1])
                sync_lines.append(lines[sync_line_idx])
                # Eliminar estas líneas
                del lines[sync_line_idx]
                del lines[sync_line_idx-1]
            else:
                sync_lines.append(lines[sync_line_idx])
                del lines[sync_line_idx]
            
            # Encontrar dónde insertarlas (justo después del for loop)
            for i, line in enumerate(lines):
                if 'for source_id, motion in self.motion_states.items():' in line:
                    # Insertar después del for
                    for j, sync_line in enumerate(sync_lines):
                        lines.insert(i+1+j, sync_line)
                    break
            
            # Guardar
            import shutil
            from datetime import datetime
            backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_name)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print("\n✅ Sincronización movida ANTES de update_with_deltas")
            return True
        else:
            print("✅ El orden ya es correcto")
            
            # Pero verificar que esté DENTRO del loop
            # Mostrar contexto
            print("\n📋 Contexto:")
            for i in range(max(0, sync_line_idx-5), min(len(lines), sync_line_idx+5)):
                print(f"{i+1:4d}: {lines[i].rstrip()}")
                if i == sync_line_idx:
                    print("      ^^^ SINCRONIZACIÓN")
    
    return False

if __name__ == "__main__":
    print("🔧 Arreglando timing de sincronización...")
    
    if fix_sync_timing():
        print("\n✅ Fix aplicado - AHORA SÍ DEFINITIVO")
        print("📝 Ejecuta: python test_macro_rotation_final_working.py")
        print("\n🎉 MacroRotation debería funcionar al 100%")
    else:
        print("\n⚠️ Verificar manualmente el orden")