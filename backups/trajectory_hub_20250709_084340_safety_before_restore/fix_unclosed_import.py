# === fix_unclosed_import.py ===
# 🔧 Fix: Arreglar import sin cerrar antes de línea 39
# ⚡ ConcentrationCurve y MacroRotation están flotando

import os

def fix_unclosed_import():
    """Arreglar imports sin cerrar correctamente"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_unclosed', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Analizando estructura de imports...")
    
    # Mostrar primeros 50 líneas para entender la estructura
    print("\n📋 Primeros imports del archivo:")
    for i in range(min(50, len(lines))):
        if i < len(lines):
            line = lines[i].rstrip()
            if 'import' in line or i in range(30, 45):
                marker = ">>>" if i in [36, 37, 38, 39] else "   "
                print(f"{marker} {i+1}: {line}")
    
    # Buscar el import que contiene ConcentrationCurve
    import_start = -1
    for i in range(35, -1, -1):  # Buscar hacia atrás desde línea 35
        if 'from' in lines[i] and 'import' in lines[i]:
            import_start = i
            print(f"\n📍 Import anterior encontrado en línea {i+1}: {lines[i].strip()}")
            break
    
    # Si encontramos el inicio del import
    if import_start >= 0:
        # Verificar si tiene paréntesis abierto
        if '(' in lines[import_start]:
            print("✅ El import tiene paréntesis abierto")
            
            # Buscar dónde debería cerrarse
            found_close = False
            for i in range(import_start + 1, min(import_start + 30, len(lines))):
                if ')' in lines[i]:
                    found_close = True
                    print(f"✅ Paréntesis de cierre encontrado en línea {i+1}")
                    break
                elif 'from' in lines[i] and 'import' in lines[i]:
                    # Encontramos otro import antes de cerrar
                    print(f"❌ Nuevo import en línea {i+1} antes de cerrar el anterior")
                    
                    # Insertar cierre antes de esta línea
                    if i > 0 and lines[i-1].strip():
                        lines[i-1] = lines[i-1].rstrip() + ')\n'
                        print(f"✅ Añadido ) al final de línea {i}")
                        found_close = True
                    break
            
            if not found_close:
                # Buscar última línea con contenido antes del siguiente import
                for i in range(import_start + 1, min(len(lines), import_start + 30)):
                    if lines[i].strip() and not lines[i].strip().startswith('from'):
                        # Esta debe ser la última línea del import
                        lines[i] = lines[i].rstrip() + ')\n'
                        print(f"✅ Añadido ) a línea {i+1}")
                        break
    
    # Fix específico para líneas 36-37 si siguen sueltas
    if 35 < len(lines) and 'ConcentrationCurve' in lines[35]:
        # Estas líneas deberían ser parte del import anterior
        print("\n🔧 Arreglando líneas 36-37 sueltas...")
        
        # Buscar el import motion_components más cercano
        for i in range(35, -1, -1):
            if 'from trajectory_hub.core.motion_components import' in lines[i]:
                print(f"📍 Import motion_components en línea {i+1}")
                
                # Si no tiene paréntesis, añadirlos
                if '(' not in lines[i]:
                    lines[i] = lines[i].rstrip() + ' (\n'
                    
                # Asegurar que línea 37 termine con )
                if 36 < len(lines) and 'MacroRotation' in lines[36]:
                    lines[36] = lines[36].rstrip()
                    if not lines[36].endswith(')'):
                        lines[36] += ')\n'
                    print("✅ Cerrado import en línea 37")
                break
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo corregido")

def final_check():
    """Verificación final"""
    print("\n🧪 Verificación final...")
    
    # Test de sintaxis
    import subprocess
    result = subprocess.run(
        ['python', '-m', 'py_compile', 'trajectory_hub/core/enhanced_trajectory_engine.py'],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print("✅ ¡Sintaxis correcta!")
        
        # Ejecutar test
        print("\n🚀 Ejecutando test delta_100...")
        result = subprocess.run(['python', 'test_delta_100.py'], 
                              capture_output=True, text=True, timeout=10)
        
        # Mostrar resumen
        if result.stdout:
            for line in result.stdout.split('\n')[-30:]:
                if any(word in line for word in ['RESUMEN', '%', 'funcional', 'Concentración']):
                    print(line)
                    
    else:
        print("❌ Error de sintaxis:")
        print(result.stderr)
        
        # Mostrar línea exacta del error
        if 'line' in result.stderr:
            import re
            match = re.search(r'line (\d+)', result.stderr)
            if match:
                line_num = int(match.group(1))
                print(f"\n📍 Error en línea {line_num}")
                
                with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
                    lines = f.readlines()
                
                for i in range(max(0, line_num-5), min(len(lines), line_num+3)):
                    marker = ">>>" if i == line_num-1 else "   "
                    print(f"{marker} {i+1}: {lines[i].rstrip()}")

if __name__ == "__main__":
    print("🔧 FIXING UNCLOSED IMPORT")
    print("=" * 60)
    
    fix_unclosed_import()
    final_check()