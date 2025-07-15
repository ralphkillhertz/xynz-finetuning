# === fix_indentation_error.py ===
# 🔧 Fix: Corregir error de indentación
# ⚡ Impacto: CRÍTICO - Sin esto no se puede importar

import os

def fix_indentation():
    """Corregir error de indentación en línea 11"""
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("🔍 Buscando error de indentación...")
    
    # Buscar alrededor de la línea 11
    for i in range(max(0, 10-5), min(len(lines), 10+5)):
        print(f"{i+1:3d}: {lines[i].rstrip()}")
    
    # Corregir - buscar el except sin try correspondiente
    fixed = False
    for i in range(len(lines)):
        if i == 10 and lines[i].strip() == 'except ImportError:':
            # Verificar línea anterior
            if i > 0 and 'try:' in lines[i-1]:
                print(f"\n✅ try/except encontrado en líneas {i}/{i+1}")
            else:
                # Buscar el try más cercano hacia atrás
                for j in range(i-1, max(0, i-10), -1):
                    if 'try:' in lines[j]:
                        print(f"\n⚠️ try está en línea {j+1}, except en {i+1}")
                        # Verificar indentación
                        try_indent = len(lines[j]) - len(lines[j].lstrip())
                        except_indent = len(lines[i]) - len(lines[i].lstrip())
                        
                        if try_indent != except_indent:
                            print(f"❌ Indentación incorrecta: try={try_indent}, except={except_indent}")
                            lines[i] = ' ' * try_indent + 'except ImportError:\n'
                            fixed = True
                        break
    
    # Si no se arregló, buscar el patrón más general
    if not fixed:
        for i in range(len(lines)):
            if lines[i].strip() == 'except ImportError:' and i > 0:
                # Ver si hay algo mal con la línea anterior
                prev_line = lines[i-1]
                if prev_line.strip() and not prev_line.strip().endswith(':'):
                    # Probablemente falta contenido del try
                    print(f"\n⚠️ Línea {i}: except sin bloque try válido")
                    # Añadir un pass temporalmente
                    lines.insert(i, '    pass\n')
                    fixed = True
                    break
    
    if fixed:
        # Guardar
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("\n✅ Indentación corregida")
        return True
    else:
        print("\n⚠️ No se encontró el error específico")
        
        # Mostrar más contexto
        print("\n📋 Mostrando líneas 1-20:")
        for i in range(min(20, len(lines))):
            print(f"{i+1:3d}: {lines[i].rstrip()}")
        
        return False

if __name__ == "__main__":
    print("🔧 Corrigiendo error de indentación...")
    
    if fix_indentation():
        print("\n✅ Archivo corregido")
        print("📝 Ejecuta: python test_macro_rotation_final_working.py")
    else:
        print("\n❌ Necesita revisión manual")
        print("💡 Buscar 'except ImportError:' y verificar que tenga un try correspondiente")