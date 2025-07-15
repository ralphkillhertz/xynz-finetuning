#!/usr/bin/env python3
"""
🔧 Fix: Busca y restaura el cuerpo de create_macro
⚡ Arregla: IndentationError - falta implementación
🎯 Impacto: CRÍTICO - Sistema no arranca
"""

def fix_create_macro_body():
    """Busca o restaura el cuerpo de create_macro"""
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    # Leer archivo actual
    with open(engine_path, 'r') as f:
        lines = f.readlines()
    
    print("🔍 Analizando estructura de create_macro...")
    
    # Buscar dónde está create_macro
    create_macro_line = -1
    list_macros_line = -1
    
    for i, line in enumerate(lines):
        if "def create_macro" in line:
            create_macro_line = i
        elif "def list_macros" in line:
            list_macros_line = i
            if create_macro_line != -1:
                break
    
    print(f"📍 create_macro en línea: {create_macro_line + 1}")
    print(f"📍 list_macros en línea: {list_macros_line + 1}")
    
    # Verificar si hay contenido entre create_macro y list_macros
    if create_macro_line != -1 and list_macros_line != -1:
        content_between = lines[create_macro_line + 1:list_macros_line]
        
        # Verificar si hay código con indentación correcta
        has_body = any(line.startswith('        ') and line.strip() for line in content_between)
        
        if not has_body:
            print("⚠️ create_macro no tiene cuerpo implementado")
            
            # Buscar en backups
            import glob
            backups = glob.glob(f"{engine_path}.backup*")
            
            if backups:
                print(f"\n🔍 Buscando en {len(backups)} backups...")
                
                # Buscar el backup más reciente con create_macro completo
                for backup in sorted(backups, reverse=True):
                    try:
                        with open(backup, 'r') as f:
                            backup_content = f.read()
                        
                        # Si tiene create_macro con cuerpo
                        if "def create_macro" in backup_content and "# Generar ID único" in backup_content:
                            print(f"✅ Encontrado create_macro completo en: {backup}")
                            
                            # Extraer el método completo
                            backup_lines = backup_content.split('\n')
                            
                            # Buscar inicio y fin del método
                            start = -1
                            end = -1
                            indent_level = None
                            
                            for i, line in enumerate(backup_lines):
                                if "def create_macro" in line:
                                    start = i
                                    # Detectar nivel de indentación
                                    indent_level = len(line) - len(line.lstrip())
                                elif start != -1 and line.strip() and not line.startswith(' ' * (indent_level + 4)):
                                    # Encontramos el siguiente método o línea sin indentar
                                    end = i
                                    break
                            
                            if start != -1:
                                if end == -1:
                                    end = len(backup_lines)
                                
                                # Extraer el método
                                method_lines = backup_lines[start:end]
                                
                                # Insertar en el archivo actual
                                print(f"📋 Restaurando {len(method_lines)} líneas de create_macro")
                                
                                # Reemplazar desde create_macro hasta list_macros
                                new_lines = lines[:create_macro_line]
                                
                                # Añadir el método restaurado
                                for method_line in method_lines:
                                    new_lines.append(method_line + '\n')
                                
                                # Añadir línea vacía de separación
                                new_lines.append('\n')
                                
                                # Añadir el resto desde list_macros
                                new_lines.extend(lines[list_macros_line:])
                                
                                # Guardar
                                backup_path = f"{engine_path}.backup_before_restore_body"
                                with open(backup_path, 'w') as f:
                                    f.writelines(lines)
                                
                                with open(engine_path, 'w') as f:
                                    f.writelines(new_lines)
                                
                                print(f"✅ create_macro restaurado desde backup")
                                print(f"📁 Backup actual: {backup_path}")
                                return True
                            
                    except Exception as e:
                        print(f"⚠️ Error leyendo {backup}: {e}")
                        continue
            
            # Si no encontramos en backups, añadir implementación mínima
            print("\n🔧 Añadiendo implementación mínima temporal...")
            
            # Insertar un pass temporal
            lines.insert(create_macro_line + 1, '        """Implementación temporal"""\n')
            lines.insert(create_macro_line + 2, '        pass\n')
            lines.insert(create_macro_line + 3, '\n')
            
            # Guardar
            backup_path = f"{engine_path}.backup_minimal_fix"
            with open(backup_path, 'w') as f:
                f.writelines(lines)
            
            with open(engine_path, 'w') as f:
                f.writelines(lines)
            
            print("✅ Añadido cuerpo mínimo a create_macro")
            return True
    
    return False

if __name__ == "__main__":
    if fix_create_macro_body():
        print("\n🎯 Ahora ejecuta: python check_current_implementation.py")
    else:
        print("\n⚠️ No se pudo arreglar automáticamente")