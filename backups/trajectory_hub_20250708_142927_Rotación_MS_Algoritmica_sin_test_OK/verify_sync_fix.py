# === verify_sync_fix.py ===
# 🔍 Verificar: Si el fix de sincronización se aplicó correctamente
# ⚡ Debug del problema persistente

import os

def verify_sync_fix():
    """Verificar si la sincronización está en el lugar correcto"""
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("🔍 Buscando sincronización de state.position...")
    
    # Buscar el procesamiento de deltas
    in_delta_section = False
    sync_found = False
    sync_position = "unknown"
    
    for i, line in enumerate(lines):
        # Detectar inicio de sección de deltas
        if '# 🔧 PROCESAMIENTO DE DELTAS' in line:
            in_delta_section = True
            print(f"\n✅ Sección de deltas encontrada en línea {i+1}")
            print("\n📋 Contenido de la sección:")
            continue
        
        # Detectar fin de sección
        if '# FIN PROCESAMIENTO DE DELTAS' in line:
            in_delta_section = False
            print(f"\n📍 Fin de sección en línea {i+1}")
            break
        
        # Mostrar contenido de la sección
        if in_delta_section:
            print(f"{i+1:4d}: {line.rstrip()}")
            
            # Buscar la sincronización
            if 'motion.state.position = self._positions[source_id].copy()' in line:
                sync_found = True
                # Ver si está dentro del loop
                if 'for source_id, motion' in lines[i-1] or 'for source_id, motion' in lines[i-2]:
                    sync_position = "AL INICIO del loop ✅"
                else:
                    sync_position = "FUERA o AL FINAL del loop ❌"
                print(f"\n⚠️ SINCRONIZACIÓN en línea {i+1}: {sync_position}")
    
    print("\n📊 ANÁLISIS:")
    print(f"  Sincronización encontrada: {'✅ SÍ' if sync_found else '❌ NO'}")
    print(f"  Posición: {sync_position}")
    
    if sync_position == "FUERA o AL FINAL del loop ❌":
        print("\n❌ La sincronización NO está en el lugar correcto")
        print("   Debe estar DENTRO del loop y AL PRINCIPIO")
        return False
    
    # Verificar también que update_with_deltas se llame
    print("\n🔍 Verificando llamada a update_with_deltas...")
    for i, line in enumerate(lines):
        if in_delta_section and 'update_with_deltas' in line:
            print(f"  ✅ update_with_deltas llamado en línea {i+1}")
    
    return sync_found and "AL INICIO" in sync_position

if __name__ == "__main__":
    print("🔧 Verificando fix de sincronización...")
    
    if verify_sync_fix():
        print("\n✅ El fix está aplicado correctamente")
        print("\n🔍 El problema debe estar en otro lugar")
        print("   Posiblemente:")
        print("   1. El loop no se está ejecutando")
        print("   2. Los deltas no se están aplicando")
        print("   3. Hay otro código que sobrescribe las posiciones")
    else:
        print("\n❌ El fix NO se aplicó correctamente")
        print("   Necesitamos aplicarlo manualmente")