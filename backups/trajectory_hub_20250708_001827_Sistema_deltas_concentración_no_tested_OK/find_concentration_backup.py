# === find_concentration_backup.py ===
# 🔧 Busca ConcentrationComponent en los backups
# ⚡ Encuentra el archivo correcto

import os
import re
from datetime import datetime

def find_concentration_in_backups():
    """Busca ConcentrationComponent en todos los backups"""
    
    backup_dir = "trajectory_hub/core"
    print("🔍 BUSCANDO ConcentrationComponent EN BACKUPS")
    print("="*60)
    
    # Listar todos los backups
    backups = []
    for file in os.listdir(backup_dir):
        if file.startswith('motion_components.py.backup_'):
            backups.append(file)
    
    backups.sort(reverse=True)  # Más reciente primero
    
    print(f"\n📋 Analizando {len(backups)} backups...")
    
    found_backups = []
    
    for backup in backups:
        backup_path = os.path.join(backup_dir, backup)
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar ConcentrationComponent
            if 'class ConcentrationComponent' in content:
                # Contar clases
                classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
                
                # Verificar sintaxis
                try:
                    compile(content, backup_path, 'exec')
                    syntax_ok = True
                except:
                    syntax_ok = False
                
                # Obtener fecha del backup
                date_match = re.search(r'backup_.*?(\d{8}_\d{6})', backup)
                if date_match:
                    date_str = date_match.group(1)
                    try:
                        date = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                        date_formatted = date.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        date_formatted = date_str
                else:
                    date_formatted = "Fecha desconocida"
                
                found_backups.append({
                    'file': backup,
                    'path': backup_path,
                    'classes': len(classes),
                    'syntax_ok': syntax_ok,
                    'date': date_formatted,
                    'has_delta': 'MotionDelta' in classes,
                    'has_update': 'def update_with_deltas' in content
                })
                
        except Exception as e:
            print(f"   ❌ Error leyendo {backup}: {e}")
    
    if found_backups:
        print(f"\n✅ Encontrado en {len(found_backups)} backups:")
        for i, backup in enumerate(found_backups[:10]):  # Mostrar máx 10
            print(f"\n{i+1}. {backup['file']}")
            print(f"   Fecha: {backup['date']}")
            print(f"   Clases: {backup['classes']}")
            print(f"   Sintaxis: {'✅' if backup['syntax_ok'] else '❌'}")
            print(f"   MotionDelta: {'✅' if backup['has_delta'] else '❌'}")
            print(f"   update_with_deltas: {'✅' if backup['has_update'] else '❌'}")
        
        # Recomendar el mejor
        best = None
        for backup in found_backups:
            if backup['syntax_ok'] and backup['has_delta']:
                best = backup
                break
        
        if best:
            print(f"\n🎯 MEJOR OPCIÓN: {best['file']}")
            print(f"\n📋 Para restaurar:")
            print(f"$ cp '{best['path']}' 'trajectory_hub/core/motion_components.py'")
            
            # Crear script de restauración
            with open('restore_concentration.sh', 'w') as f:
                f.write(f"#!/bin/bash\n")
                f.write(f"cp '{best['path']}' 'trajectory_hub/core/motion_components.py'\n")
                f.write(f"echo '✅ ConcentrationComponent restaurado desde {best['file']}'\n")
            
            os.chmod('restore_concentration.sh', 0o755)
            print("\n📌 O ejecuta:")
            print("$ ./restore_concentration.sh")
    else:
        print("\n❌ ConcentrationComponent NO encontrado en ningún backup")
        print("\n🔧 Necesitamos crear ConcentrationComponent desde cero")
        print("   Ejecuta: python create_concentration_component.py")

if __name__ == "__main__":
    find_concentration_in_backups()