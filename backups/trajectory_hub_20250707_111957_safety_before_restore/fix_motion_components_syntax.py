#!/usr/bin/env python3
"""
🔧 FIX - Corregir error de sintaxis en línea 1018
⚡ Arreglar el return result que está mal
"""

import os

def fix_syntax_line_1018():
    """Corregir el error de sintaxis específico"""
    
    print("🔧 CORRIGIENDO ERROR DE SINTAXIS EN motion_components.py\n")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    if not os.path.exists(motion_file):
        print("❌ No se encuentra el archivo")
        return False
    
    # Leer el archivo
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    print(f"📄 Archivo tiene {len(lines)} líneas")
    
    # Verificar alrededor de la línea 1018
    if len(lines) >= 1018:
        print(f"\n🔍 Contexto alrededor de la línea 1018:")
        
        # Mostrar contexto
        start = max(0, 1015)  # línea 1016
        end = min(len(lines), 1020)  # línea 1020
        
        for i in range(start, end):
            prefix = ">>> " if i == 1017 else "    "  # línea 1018 es índice 1017
            print(f"{prefix}L{i+1}: {lines[i].rstrip()}")
        
        # El problema probablemente es un return suelto
        if 1017 < len(lines):
            line_1018 = lines[1017]
            
            if line_1018.strip() == "return result":
                print("\n❌ Encontrado: 'return result' suelto")
                
                # Buscar hacia atrás para encontrar el contexto
                indent_level = len(line_1018) - len(line_1018.lstrip())
                print(f"   Nivel de indentación: {indent_level} espacios")
                
                # Opción 1: Si es parte de get_position, arreglarlo
                # Buscar hacia atrás por def get_position
                for i in range(1016, max(0, 1000), -1):
                    if 'def get_position' in lines[i]:
                        print(f"\n✅ Encontrado get_position en línea {i+1}")
                        
                        # Verificar la indentación correcta
                        # Un return dentro de un método debe tener 8 espacios
                        correct_indent = "        "  # 8 espacios
                        
                        # Corregir la línea
                        lines[1017] = correct_indent + "return result\n"
                        
                        # También verificar si falta algo antes
                        if 1016 < len(lines) and 'result' not in lines[1016]:
                            # Agregar la asignación de result
                            lines[1017] = correct_indent + "result = (self.base_position + \n"
                            lines.insert(1018, correct_indent + "          self.trajectory_offset + \n")
                            lines.insert(1019, correct_indent + "          self.concentration_offset + \n")
                            lines.insert(1020, correct_indent + "          self.macro_rotation_offset +\n")
                            lines.insert(1021, correct_indent + "          self.algorithmic_rotation_offset)\n")
                            lines.insert(1022, correct_indent + "return result\n")
                        
                        break
                
                # Guardar el archivo corregido
                print("\n💾 Guardando archivo corregido...")
                
                # Backup
                backup_file = motion_file + ".backup_syntax"
                with open(backup_file, 'w') as f:
                    f.writelines(lines)
                
                with open(motion_file, 'w') as f:
                    f.writelines(lines)
                
                print("✅ Archivo corregido")
                return True
    
    # Si no encontramos el problema específico, intentar otra cosa
    print("\n🔍 Analizando estructura del archivo...")
    
    # Buscar métodos incompletos
    in_method = False
    method_name = ""
    method_start = 0
    
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            in_method = True
            method_name = line.strip()
            method_start = i
        elif in_method and (line.strip().startswith('def ') or line.strip().startswith('class ')):
            # Nuevo método o clase, el anterior terminó
            in_method = False
        elif in_method and i == 1017 and line.strip() == "return result":
            # Return suelto en un método
            print(f"\n❌ Return suelto en {method_name} (línea {method_start+1})")
            
            # Arreglar con indentación correcta
            lines[i] = "        return result\n"
            
            # Guardar
            with open(motion_file, 'w') as f:
                f.writelines(lines)
            
            print("✅ Corregido con indentación estándar")
            return True
    
    print("\n❌ No se pudo identificar el problema exacto")
    return False

def verify_fix():
    """Verificar que el fix funcionó"""
    
    print("\n🔍 VERIFICANDO FIX...")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    try:
        with open(motion_file, 'r') as f:
            content = f.read()
        
        # Intentar compilar
        compile(content, motion_file, 'exec')
        print("✅ Sintaxis correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ Todavía hay error de sintaxis:")
        print(f"   Línea {e.lineno}: {e.text}")
        return False

if __name__ == "__main__":
    success = fix_syntax_line_1018()
    
    if success:
        if verify_fix():
            print("\n🎉 FIX COMPLETADO EXITOSAMENTE")
            print("\n🚀 Ahora ejecuta:")
            print("   python direct_diagnostic_test.py")
        else:
            print("\n⚠️  El archivo fue modificado pero aún hay errores")
    else:
        print("\n❌ No se pudo aplicar el fix")
        print("\nOPCIONES:")
        print("1. Restaurar desde backup:")
        print("   cp trajectory_hub/core/motion_components.py.backup_syntax trajectory_hub/core/motion_components.py")
        print("2. Revisar manualmente la línea 1018")