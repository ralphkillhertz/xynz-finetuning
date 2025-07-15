#!/usr/bin/env python3
"""
🔍 Busca el mejor backup disponible
⚡ Lista todos los backups con información útil
"""

import os
import glob
from datetime import datetime

def find_best_backup():
    """Lista y analiza todos los backups disponibles"""
    
    print("🔍 BUSCANDO BACKUPS DEL ENGINE")
    print("=" * 60)
    
    # Buscar todos los backups
    backups = glob.glob("trajectory_hub/core/enhanced_trajectory_engine.py.backup*")
    
    if not backups:
        print("❌ No se encontraron backups")
        return
    
    print(f"📁 Encontrados {len(backups)} backups:\n")
    
    valid_backups = []
    
    for i, backup in enumerate(sorted(backups, reverse=True)):
        try:
            # Obtener info del archivo
            size = os.path.getsize(backup)
            mtime = os.path.getmtime(backup)
            date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            # Analizar contenido
            with open(backup, 'r') as f:
                content = f.read()
                lines = len(content.split('\n'))
                
                # Verificar métodos clave
                has_create = "def create_macro" in content
                has_list = "def list_macros" in content
                has_delete = "def delete_macro" in content
                has_select = "def select_macro" in content
                has_implementation = "# Generar ID único" in content or "_next_source_id" in content
                
                # Contar métodos
                method_count = content.count("def ")
                
                print(f"{i+1}. {os.path.basename(backup)}")
                print(f"   📅 Fecha: {date}")
                print(f"   📏 Tamaño: {size:,} bytes ({lines} líneas)")
                print(f"   🔧 Métodos: {method_count}")
                print(f"   ✅ create_macro: {'SÍ' if has_create else 'NO'}")
                print(f"   ✅ Implementación: {'COMPLETA' if has_implementation else 'VACÍA'}")
                print(f"   ✅ list_macros: {'SÍ' if has_list else 'NO'}")
                print(f"   ✅ delete_macro: {'SÍ' if has_delete else 'NO'}")
                print(f"   ✅ select_macro: {'SÍ' if has_select else 'NO'}")
                
                # Si es válido, añadir a la lista
                if has_create and has_implementation:
                    valid_backups.append({
                        'path': backup,
                        'size': size,
                        'date': date,
                        'score': sum([has_create, has_list, has_delete, has_select, has_implementation])
                    })
                
                print()
                
        except Exception as e:
            print(f"{i+1}. {os.path.basename(backup)} - ERROR: {e}\n")
    
    if valid_backups:
        # Ordenar por score
        valid_backups.sort(key=lambda x: x['score'], reverse=True)
        best = valid_backups[0]
        
        print("=" * 60)
        print(f"🏆 MEJOR BACKUP: {os.path.basename(best['path'])}")
        print(f"   Score: {best['score']}/5")
        print(f"\n🎯 Para restaurar, ejecuta:")
        print(f"   cp '{best['path']}' trajectory_hub/core/enhanced_trajectory_engine.py")
        
        # Ofrecer restauración automática
        print("\n¿Restaurar automáticamente? (s/n): ", end='')
        if input().lower() == 's':
            # Backup actual
            current_backup = "trajectory_hub/core/enhanced_trajectory_engine.py.backup_current"
            os.system(f"cp trajectory_hub/core/enhanced_trajectory_engine.py '{current_backup}'")
            
            # Restaurar
            os.system(f"cp '{best['path']}' trajectory_hub/core/enhanced_trajectory_engine.py")
            
            print(f"\n✅ RESTAURADO desde: {os.path.basename(best['path'])}")
            print(f"📁 Backup actual guardado como: {os.path.basename(current_backup)}")
            print("\n🎯 Ahora ejecuta: python -m trajectory_hub.interface.interactive_controller")

if __name__ == "__main__":
    find_best_backup()