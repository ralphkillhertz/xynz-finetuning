import os
import re
from datetime import datetime
import shutil

def emergency_fix():
    """Arreglar el menú roto inmediatamente"""
    print("🚨 REPARACIÓN DE EMERGENCIA DEL MENÚ")
    print("="*60)
    
    cli_file = "trajectory_hub/control/interfaces/cli_interface.py"
    
    # Buscar el backup más reciente
    backups = [f for f in os.listdir(os.path.dirname(cli_file) or '.') 
               if f.startswith(os.path.basename(cli_file) + '.backup_')]
    
    if backups:
        backups.sort()
        latest_backup = backups[-1]
        print(f"✅ Backup encontrado: {latest_backup}")
        
        # Restaurar desde backup
        backup_path = os.path.join(os.path.dirname(cli_file) or '.', latest_backup)
        shutil.copy(backup_path, cli_file)
        print("✅ Archivo restaurado desde backup")
    
    # Ahora arreglar correctamente
    with open(cli_file, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Buscar el problema específico - la lista mal formateada
    fixed = False
    for i, line in enumerate(lines):
        if "['circle', 'line', 'grid', 'spiral', 'random']" in line:
            print(f"\n❌ Problema encontrado en línea {i+1}")
            
            # Buscar hacia atrás para encontrar dónde empieza la definición
            for j in range(i-1, max(0, i-20), -1):
                if 'formations' in lines[j] and '=' in lines[j]:
                    print(f"✅ Definición de formations en línea {j+1}")
                    
                    # Reemplazar con el formato correcto
                    indent = len(lines[j]) - len(lines[j].lstrip())
                    
                    # Crear las líneas correctas
                    new_lines = [
                        lines[j],  # formations = [
                        ' ' * (indent + 4) + '"circle",',
                        ' ' * (indent + 4) + '"line",',
                        ' ' * (indent + 4) + '"grid",',
                        ' ' * (indent + 4) + '"spiral",',
                        ' ' * (indent + 4) + '"random",',
                        ' ' * (indent + 4) + '"sphere"',
                        ' ' * indent + ']'
                    ]
                    
                    # Encontrar dónde termina la lista actual
                    k = j + 1
                    while k < len(lines) and ']' not in lines[k]:
                        k += 1
                    
                    # Reemplazar
                    lines[j:k+1] = new_lines
                    fixed = True
                    print("✅ Formato corregido")
                    break
            
            if fixed:
                break
    
    if not fixed:
        print("\n🔍 Buscando formato alternativo...")
        
        # Buscar donde se muestra el menú
        for i, line in enumerate(lines):
            if "get_choice_from_list" in line and "formations" in line:
                print(f"\n✅ Llamada a get_choice_from_list en línea {i+1}")
                
                # Verificar formato correcto
                # El método espera una lista de strings
                
                # Buscar la definición de formations antes
                for j in range(i-1, max(0, i-30), -1):
                    if 'formations' in lines[j] and '=' in lines[j]:
                        # Verificar si está en formato correcto
                        k = j
                        formation_block = []
                        while k < i and k < len(lines):
                            formation_block.append(lines[k])
                            if ']' in lines[k]:
                                break
                            k += 1
                        
                        block_text = '\n'.join(formation_block)
                        print(f"\nBloque actual:\n{block_text}")
                        
                        # Si tiene el formato incorrecto con ['circle'...] en una línea
                        if re.search(r"\[.*'circle'.*'random'.*\]", block_text):
                            print("\n✅ Formato incorrecto detectado, corrigiendo...")
                            
                            # Reemplazar
                            indent = len(lines[j]) - len(lines[j].lstrip())
                            new_lines = [
                                lines[j].split('=')[0] + '= [',
                                ' ' * (indent + 4) + '"circle",',
                                ' ' * (indent + 4) + '"line",',
                                ' ' * (indent + 4) + '"grid",',
                                ' ' * (indent + 4) + '"spiral",',
                                ' ' * (indent + 4) + '"random",',
                                ' ' * (indent + 4) + '"sphere"',
                                ' ' * indent + ']'
                            ]
                            
                            lines[j:k+1] = new_lines
                            fixed = True
                            break
    
    if fixed:
        # Guardar
        backup = f"{cli_file}.backup_emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(cli_file, backup)
        
        with open(cli_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print("\n✅ MENÚ REPARADO")
        print("\nFormato correcto:")
        print("  1. circle")
        print("  2. line")
        print("  3. grid")
        print("  4. spiral")
        print("  5. random")
        print("  6. sphere")
    else:
        print("\n❌ No se pudo arreglar automáticamente")
        print("\n💡 Solución manual:")
        print("1. Busca en cli_interface.py donde dice:")
        print("   formations = [...]")
        print("2. Reemplaza con:")
        print('   formations = [')
        print('       "circle",')
        print('       "line",')
        print('       "grid",')
        print('       "spiral",')
        print('       "random",')
        print('       "sphere"')
        print('   ]')

if __name__ == "__main__":
    emergency_fix()
    print("\n🚀 Prueba ahora: python main.py --interactive")