# === fix_syntax_after_uncomment.py ===
# 🔧 Fix de sintaxis después de descomentar
# ⚡ Arregla líneas que deberían ser comentarios

import os
from datetime import datetime

def fix_syntax():
    """Arregla la sintaxis después de descomentar"""
    
    print("🔧 ARREGLANDO SINTAXIS")
    print("="*60)
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    # Buscar y arreglar líneas problemáticas
    fixed = False
    for i, line in enumerate(lines):
        # Si es una línea con texto suelto sin # al principio
        if i > 0 and line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""'):
            # Verificar si parece ser un comentario descriptivo
            if ('Actualizar' in line or 'VERSIÓN' in line or 'Solo procesa' in line) and ':' not in line and '=' not in line:
                print(f"📍 Línea {i+1} parece ser comentario: {line.strip()}")
                # Comentarla
                indent = len(line) - len(line.lstrip())
                lines[i] = ' ' * indent + '# ' + line.lstrip()
                fixed = True
    
    if fixed:
        # Escribir archivo
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ Líneas comentadas correctamente")
        
        # Verificar sintaxis
        try:
            with open(engine_path, 'r', encoding='utf-8') as f:
                compile(f.read(), engine_path, 'exec')
            print("✅ Sintaxis verificada")
            return True
        except SyntaxError as e:
            print(f"❌ Aún hay error de sintaxis en línea {e.lineno}: {e.msg}")
            print(f"   Texto: {e.text}")
            return False
    else:
        print("❌ No se encontraron líneas para arreglar")
        
        # Mostrar el error específico
        try:
            with open(engine_path, 'r', encoding='utf-8') as f:
                compile(f.read(), engine_path, 'exec')
        except SyntaxError as e:
            print(f"\n❌ Error en línea {e.lineno}: {e.msg}")
            if e.lineno and e.lineno > 0:
                print(f"   Contexto:")
                start = max(0, e.lineno - 3)
                end = min(len(lines), e.lineno + 2)
                for i in range(start, end):
                    marker = ">>>" if i == e.lineno - 1 else "   "
                    print(f"{marker} {i+1}: {lines[i].rstrip()}")
        
        return False

if __name__ == "__main__":
    if fix_syntax():
        print("\n✅ SINTAXIS ARREGLADA")
        print("\n🎉 Ahora ejecuta:")
        print("$ python test_concentration_working.py")