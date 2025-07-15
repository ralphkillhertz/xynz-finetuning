#!/usr/bin/env python3
"""
🚨 RESTAURACIÓN DE EMERGENCIA
⚡ Restaura engine desde backup funcional conocido
"""

import os
import glob

def emergency_restore():
    """Restaura engine desde el mejor backup disponible"""
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    # Buscar backups
    backups = glob.glob(f"{engine_path}.backup*")
    
    print("🚨 RESTAURACIÓN DE EMERGENCIA")
    print("=" * 60)
    print(f"📁 Encontrados {len(backups)} backups")
    
    # Buscar backup con create_macro y list_macros
    best_backup = None
    
    priority_backups = [
        "enhanced_trajectory_engine.py.backup_20250710_091915",
        "enhanced_trajectory_engine.py.backup_macro_fix",
        "enhanced_trajectory_engine.py.backup_proven_fix"
    ]
    
    # Primero buscar backups prioritarios
    for priority in priority_backups:
        full_path = f"trajectory_hub/core/{priority}"
        if os.path.exists(full_path):
            print(f"✅ Encontrado backup prioritario: {priority}")
            best_backup = full_path
            break
    
    # Si no, buscar cualquier backup con los métodos necesarios
    if not best_backup:
        for backup in sorted(backups, reverse=True):
            try:
                with open(backup, 'r') as f:
                    content = f.read()
                
                if "def create_macro" in content and "def list_macros" in content:
                    if "# Generar ID único" in content:  # Señal de implementación completa
                        best_backup = backup
                        print(f"✅ Backup válido encontrado: {os.path.basename(backup)}")
                        break
            except:
                continue
    
    if best_backup:
        # Hacer backup del estado actual
        current_backup = f"{engine_path}.backup_emergency_before"
        with open(engine_path, 'r') as f:
            current = f.read()
        with open(current_backup, 'w') as f:
            f.write(current)
        
        # Restaurar
        with open(best_backup, 'r') as f:
            restored = f.read()
        
        with open(engine_path, 'w') as f:
            f.write(restored)
        
        print(f"\n✅ ENGINE RESTAURADO desde: {os.path.basename(best_backup)}")
        print(f"📁 Backup del estado anterior: {current_backup}")
        print("\n🎯 Ejecuta: python -m trajectory_hub.interface.interactive_controller")
        return True
    else:
        print("\n❌ No se encontró un backup válido")
        return False

if __name__ == "__main__":
    emergency_restore()