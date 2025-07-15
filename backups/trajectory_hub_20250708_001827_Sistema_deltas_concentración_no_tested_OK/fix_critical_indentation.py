#!/usr/bin/env python3
"""
🔧 Fix: Arregla los errores críticos de indentación identificados
⚡ Líneas: 106 y 1162 principalmente
🎯 Solución: Corrección quirúrgica de las líneas problemáticas
"""

def fix_critical_errors():
    """Arregla los errores críticos identificados"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    print("🔧 Arreglando errores críticos de indentación...\n")
    
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    # Fix 1: Línea 105-106 - Docstring mal cerrado
    print("1️⃣ Arreglando línea 105-106 (docstring mal cerrado)...")
    
    # La línea 105 (índice 104) parece tener un docstring incompleto
    if 104 < len(lines) and '"""' in lines[104] and not lines[104].strip().endswith('"""'):
        # Completar el docstring
        lines[104] = lines[104].rstrip() + '"""' + '\n'
        print("   ✅ Docstring cerrado en línea 105")
    
    # Fix 2: Líneas 106-110 - Código mal indentado después de docstring
    print("\n2️⃣ Arreglando indentación líneas 106-110...")
    
    # Estas líneas deberían tener 8 espacios (dentro del método)
    for i in range(105, 111):  # líneas 106-110
        if i < len(lines) and lines[i].strip():
            # Calcular indentación correcta (8 espacios para contenido de método)
            lines[i] = '        ' + lines[i].lstrip()
    
    print("   ✅ Indentación corregida")
    
    # Fix 3: Línea 315 y 318 - Métodos con indentación incorrecta
    print("\n3️⃣ Arreglando métodos mal indentados (líneas 315, 318)...")
    
    # Buscar métodos con 8 espacios que deberían tener 4
    fixes_applied = 0
    for i in range(len(lines)):
        line = lines[i]
        if line.strip().startswith('def ') and len(line) - len(line.lstrip()) == 8:
            # Cambiar a 4 espacios
            lines[i] = '    ' + line.lstrip()
            fixes_applied += 1
            print(f"   ✅ Arreglado método en línea {i+1}")
    
    # Fix 4: Línea 1005 - Método con 0 espacios
    print("\n4️⃣ Buscando métodos sin indentación...")
    
    for i in range(len(lines)):
        line = lines[i]
        # Si es un def sin indentación y está dentro de una clase
        if line.strip().startswith('def ') and not line.startswith(' '):
            # Buscar hacia atrás para ver si estamos dentro de una clase
            in_class = False
            for j in range(i-1, max(0, i-50), -1):
                if lines[j].strip().startswith('class '):
                    in_class = True
                    break
            
            if in_class:
                lines[i] = '    ' + line
                print(f"   ✅ Arreglado método sin indentación en línea {i+1}")
    
    # Fix 5: Línea 1162 - Segundo error crítico
    print("\n5️⃣ Arreglando error en línea 1162...")
    
    # Verificar contexto alrededor de línea 1162
    if 1161 < len(lines):
        # Si hay un método o código mal indentado
        for i in range(1160, min(1165, len(lines))):
            line = lines[i]
            if line.strip() and not line.startswith(' '):
                # Si debería estar dentro de una clase, añadir indentación
                lines[i] = '    ' + line
                print(f"   ✅ Indentación añadida en línea {i+1}")
    
    # Guardar cambios
    with open(motion_file, 'w') as f:
        f.writelines(lines)
    
    print("\n✅ Errores críticos arreglados")

def verify_fixes():
    """Verifica que los fixes funcionaron"""
    print("\n🧪 Verificando arreglos...")
    
    import ast
    motion_file = "trajectory_hub/core/motion_components.py"
    
    try:
        with open(motion_file, 'r') as f:
            content = f.read()
        
        ast.parse(content)
        print("✅ ¡Sintaxis correcta! No hay errores de parsing")
        
        # Intentar importar
        try:
            import trajectory_hub.core.motion_components
            print("✅ ¡El módulo se importa correctamente!")
            return True
        except Exception as e:
            print(f"⚠️ Error al importar: {e}")
            return False
            
    except SyntaxError as e:
        print(f"❌ Todavía hay error de sintaxis en línea {e.lineno}: {e.msg}")
        
        # Mostrar contexto
        with open(motion_file, 'r') as f:
            lines = f.readlines()
        
        if e.lineno <= len(lines):
            print("\nContexto del error:")
            for i in range(max(0, e.lineno-3), min(len(lines), e.lineno+2)):
                marker = ">>>" if i == e.lineno-1 else "   "
                print(f"{marker} {i+1}: {repr(lines[i][:70])}")
        
        return False

def restore_from_backup():
    """Opción para restaurar desde backup si todo falla"""
    print("\n💾 Backups disponibles:")
    
    import glob
    backups = glob.glob("trajectory_hub/core/motion_components.py.backup*")
    
    if backups:
        backups.sort()
        for i, backup in enumerate(backups[-5:]):  # Mostrar últimos 5
            print(f"   {i+1}. {backup}")
        
        print("\n   Para restaurar, ejecuta:")
        print(f"   $ cp {backups[-1]} trajectory_hub/core/motion_components.py")
    else:
        print("   No hay backups disponibles")

if __name__ == "__main__":
    print("🔧 FIX QUIRÚRGICO DE ERRORES CRÍTICOS")
    print("=" * 60)
    
    # Aplicar fixes
    fix_critical_errors()
    
    # Verificar
    if verify_fixes():
        print("\n🎉 ¡ÉXITO! Ahora puedes ejecutar:")
        print("$ python test_delta_final.py")
    else:
        print("\n⚠️ Los errores persisten")
        print("\nOpciones:")
        print("1. Ejecutar este script otra vez")
        print("2. Restaurar desde backup")
        print("3. Ejecutar: python create_rebuild_script.py")
        
        restore_from_backup()