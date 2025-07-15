# === fix_imports.py ===
# 🔧 Fix: Arreglar imports rotos en enhanced_trajectory_engine.py
# ⚡ Problema con paréntesis en imports multi-línea

import os

def fix_imports():
    """Arreglar imports problemáticos"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_imports', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Buscando imports problemáticos...")
    
    # Buscar línea 39 y contexto
    for i in range(35, min(45, len(lines))):
        if i < len(lines):
            print(f"Línea {i+1}: {lines[i].rstrip()}")
    
    # Arreglar imports multi-línea
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Si encontramos un import con paréntesis abierto
        if line.startswith('from ') and line.endswith('('):
            print(f"\n📍 Import multi-línea en línea {i+1}")
            
            # Buscar el cierre del paréntesis
            j = i + 1
            found_close = False
            import_lines = [lines[i].rstrip()]
            
            while j < len(lines) and j < i + 20:  # Max 20 líneas
                import_lines.append(lines[j].rstrip())
                if ')' in lines[j]:
                    found_close = True
                    break
                j += 1
            
            if not found_close:
                print("❌ Import sin cerrar")
                # Cerrar en la última línea
                if j > i and j <= len(lines):
                    lines[j-1] = lines[j-1].rstrip() + ')\n'
                    print("✅ Paréntesis de cierre añadido")
            
            # Verificar que no haya líneas vacías problemáticas
            for k in range(i, j+1):
                if k < len(lines) and lines[k].strip() == '' and k < j:
                    lines[k] = '    # import continuation\n'
                    
        i += 1
    
    # Arreglar imports específicos conocidos
    for i in range(len(lines)):
        # Si es un import de trajectory_deformers sin cerrar
        if 'from trajectory_hub.core.trajectory_deformers import' in lines[i] and '(' in lines[i] and ')' not in lines[i]:
            # Buscar siguiente línea no vacía
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            
            if j < len(lines):
                # Si la siguiente línea tiene nombres de clases
                if any(x in lines[j] for x in ['Deformer', 'Field', 'Wave']):
                    # Asegurar que termine con )
                    if ')' not in lines[j]:
                        lines[j] = lines[j].rstrip() + ')\n'
                        print(f"✅ Cerrado import en línea {j+1}")
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Imports arreglados")

def check_and_run():
    """Verificar y ejecutar test"""
    print("\n🧪 Verificando sintaxis...")
    
    # Primero verificar solo sintaxis básica
    result = os.system('python -m py_compile trajectory_hub/core/enhanced_trajectory_engine.py 2>&1')
    
    if result == 0:
        print("✅ Sintaxis correcta!")
        
        # Ahora el test real
        print("\n🚀 Ejecutando test de deltas...")
        try:
            from trajectory_hub.core import EnhancedTrajectoryEngine
            
            # Test mínimo
            engine = EnhancedTrajectoryEngine(n_sources=4)
            macro = engine.create_macro("test", source_count=3)
            
            print(f"✅ Sistema básico funciona")
            
            # Test completo
            import subprocess
            result = subprocess.run(['python', 'test_delta_100.py'], 
                                  capture_output=True, text=True, timeout=15)
            
            # Buscar resultados
            if result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'RESUMEN' in line or '%' in line or 'funcional' in line:
                        print(line)
                        
            if result.returncode == 0:
                print("\n✅ Test completado")
            else:
                print(f"\n⚠️ Test con errores: {result.returncode}")
                if result.stderr:
                    print(result.stderr[-500:])
                    
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {str(e)[:300]}")
    else:
        print("❌ Todavía hay errores de sintaxis")
        print("\n💡 Ejecutar: python -c \"import ast; ast.parse(open('trajectory_hub/core/enhanced_trajectory_engine.py').read())\"")
        print("   para ver el error exacto")

if __name__ == "__main__":
    print("🔧 FIXING IMPORTS")
    print("=" * 60)
    
    fix_imports()
    check_and_run()