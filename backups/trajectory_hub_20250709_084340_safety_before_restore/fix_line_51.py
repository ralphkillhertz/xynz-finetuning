# === fix_line_51.py ===
# 🔧 Fix: Error de sintaxis en línea 51
# ⚡ Import anterior no cerrado correctamente

import os

def fix_line_51():
    """Arreglar error en línea 51"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_line51', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Analizando contexto de línea 51...")
    
    # Mostrar líneas 40-55
    print("\n📋 Contexto alrededor de línea 51:")
    for i in range(40, min(55, len(lines))):
        if i < len(lines):
            marker = ">>>" if i == 50 else "   "
            print(f"{marker} {i+1}: {lines[i].rstrip()}")
    
    # Buscar imports sin cerrar
    open_imports = []
    for i in range(50):
        if i < len(lines):
            line = lines[i].strip()
            if line.startswith('from ') and '(' in line and ')' not in line:
                open_imports.append(i)
                print(f"\n📍 Import abierto en línea {i+1}")
            elif ')' in line and i > 0:
                # Verificar si cierra algún import
                if open_imports and not line.startswith('from'):
                    open_imports.pop()
    
    # Si hay imports sin cerrar antes de línea 51
    if open_imports:
        last_open = open_imports[-1]
        print(f"\n❌ Import sin cerrar desde línea {last_open+1}")
        
        # Buscar dónde debería cerrarse
        for i in range(last_open + 1, min(51, len(lines))):
            if i < len(lines):
                line = lines[i].strip()
                # Si encontramos una línea que no es continuación del import
                if (line and not line.startswith('#') and 
                    not any(x in line for x in [',', ')', 'import']) and
                    '=' in line):
                    # Cerrar el import en la línea anterior
                    if i > 0 and not lines[i-1].rstrip().endswith(')'):
                        lines[i-1] = lines[i-1].rstrip() + ')\n'
                        print(f"✅ Cerrado import en línea {i}")
                        break
        else:
            # Si no encontramos dónde cerrar, buscar la última línea con contenido antes de 51
            for i in range(50, last_open, -1):
                if lines[i].strip() and not lines[i].strip().startswith('#'):
                    if not lines[i].rstrip().endswith(')'):
                        lines[i] = lines[i].rstrip() + ')\n'
                        print(f"✅ Cerrado import en línea {i+1}")
                        break
    
    # Fix específico para líneas problemáticas conocidas
    # Línea 47 parece tener solo un comentario
    if 46 < len(lines) and lines[46].strip() == '# import continuation':
        # Esta línea probablemente debería ser eliminada o tener contenido
        # Buscar si la línea anterior necesita cierre
        if 45 < len(lines) and ',' in lines[45] and ')' not in lines[45]:
            lines[46] = ')\n'
            print("✅ Reemplazado comentario en línea 47 con cierre de import")
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo corregido")

def quick_syntax_check():
    """Verificación rápida de sintaxis"""
    print("\n🧪 Verificación de sintaxis...")
    
    import ast
    
    try:
        with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
            content = f.read()
        
        ast.parse(content)
        print("✅ ¡SINTAXIS CORRECTA!")
        
        # Si la sintaxis es correcta, ejecutar test
        print("\n🚀 Ejecutando test del sistema...")
        import subprocess
        
        result = subprocess.run(['python', 'test_delta_100.py'], 
                              capture_output=True, text=True, timeout=10)
        
        if '100%' in result.stdout:
            print("\n🎉 ¡SISTEMA DE DELTAS 100% FUNCIONAL!")
        else:
            # Mostrar resumen
            lines = result.stdout.split('\n')
            for line in lines[-20:]:
                if '%' in line or 'funcional' in line:
                    print(line)
                    
    except SyntaxError as e:
        print(f"❌ Error en línea {e.lineno}: {e.msg}")
        if e.text:
            print(f"   {e.text.strip()}")
            
        # Mostrar contexto
        with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
            lines = f.readlines()
        
        if e.lineno:
            print("\n📋 Contexto:")
            for i in range(max(0, e.lineno-5), min(len(lines), e.lineno+3)):
                marker = ">>>" if i == e.lineno-1 else "   "
                if i < len(lines):
                    print(f"{marker} {i+1}: {lines[i].rstrip()}")

if __name__ == "__main__":
    print("🔧 FIXING LINE 51 ERROR")
    print("=" * 60)
    
    fix_line_51()
    quick_syntax_check()