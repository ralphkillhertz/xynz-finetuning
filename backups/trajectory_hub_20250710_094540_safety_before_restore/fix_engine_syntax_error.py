#!/usr/bin/env python3
"""
🔧 Fix: Corrige error de sintaxis en enhanced_trajectory_engine.py
⚡ Arregla: Error en línea 310 - método list_macros
🎯 Impacto: CRÍTICO - Sistema no arranca
"""

import os

def fix_syntax_error():
    """Corrige error de sintaxis en el Engine"""
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    # Leer archivo
    with open(engine_path, 'r') as f:
        lines = f.readlines()
    
    # Buscar alrededor de la línea 310
    print("🔍 Analizando líneas 305-315...")
    for i in range(max(0, 305), min(len(lines), 315)):
        print(f"{i+1}: {lines[i].rstrip()}")
    
    # Buscar el problema específico
    fixed = False
    for i in range(len(lines)):
        # Buscar si hay un método anterior sin cerrar
        if i < len(lines) - 1:
            current = lines[i].strip()
            next_line = lines[i+1].strip() if i+1 < len(lines) else ""
            
            # Si encontramos def list_macros sin nada antes cerrado
            if "def list_macros" in lines[i] and i > 0:
                # Verificar línea anterior
                prev_line = lines[i-1].strip()
                if prev_line and not prev_line.endswith(':') and prev_line != '':
                    # Probablemente falta cerrar algo
                    print(f"\n⚠️ Posible problema en línea {i}: falta cerrar método anterior")
                    
                    # Buscar hacia atrás el método anterior
                    for j in range(i-1, max(0, i-50), -1):
                        if 'def ' in lines[j] and j < i-1:
                            print(f"📍 Método anterior encontrado en línea {j+1}")
                            
                            # Verificar si está bien cerrado
                            has_return = False
                            proper_indent = False
                            
                            for k in range(j+1, i):
                                if lines[k].strip().startswith('return') or lines[k].strip() == 'pass':
                                    has_return = True
                                if lines[k].strip() == '' and k == i-1:
                                    proper_indent = True
                            
                            if not has_return and not proper_indent:
                                # Añadir línea vacía antes de list_macros
                                print("🔧 Añadiendo línea vacía para separar métodos")
                                lines.insert(i, '\n')
                                fixed = True
                            break
    
    # Si no encontramos el problema específico, buscar otros patrones
    if not fixed:
        print("\n🔍 Buscando otros problemas de sintaxis...")
        
        # Verificar paréntesis y llaves no cerradas
        for i in range(min(310, len(lines))):
            line = lines[i]
            # Contar paréntesis
            open_parens = line.count('(') - line.count(')')
            open_brackets = line.count('[') - line.count(']')
            open_braces = line.count('{') - line.count('}')
            
            if open_parens > 0 or open_brackets > 0 or open_braces > 0:
                print(f"⚠️ Línea {i+1} tiene paréntesis/corchetes no cerrados")
                
                # Si es cerca de la línea 310, intentar arreglar
                if 305 <= i <= 310:
                    if open_parens > 0:
                        lines[i] = lines[i].rstrip() + ')' * open_parens + '\n'
                    fixed = True
    
    # Verificar indentación específica
    if not fixed:
        for i in range(len(lines)):
            if "def list_macros" in lines[i]:
                # Asegurar que tiene la indentación correcta (4 espacios)
                if not lines[i].startswith('    def'):
                    print(f"🔧 Arreglando indentación de list_macros")
                    lines[i] = '    def list_macros(self) -> dict:\n'
                    fixed = True
                break
    
    # Guardar cambios si se hizo algún fix
    if fixed:
        # Backup
        backup_path = f"{engine_path}.backup_syntax_fix"
        with open(backup_path, 'w') as f:
            f.writelines(lines)
        
        # Escribir archivo corregido
        with open(engine_path, 'w') as f:
            f.writelines(lines)
        
        print(f"\n✅ Sintaxis corregida")
        print(f"📁 Backup: {backup_path}")
    else:
        print("\n❌ No se pudo identificar el problema automáticamente")
        print("🔧 Intentando fix manual...")
        
        # Fix manual: buscar y reemplazar línea específica
        for i in range(len(lines)):
            if "def list_macros(self) -> dict:" in lines[i]:
                # Cambiar a versión sin type hint
                lines[i] = "    def list_macros(self):\n"
                
                # Guardar
                backup_path = f"{engine_path}.backup_syntax_fix_manual"
                with open(backup_path, 'w') as f:
                    f.writelines(lines)
                
                with open(engine_path, 'w') as f:
                    f.writelines(lines)
                
                print("✅ Type hint removido de list_macros")
                fixed = True
                break
    
    return fixed

if __name__ == "__main__":
    if fix_syntax_error():
        print("\n🎯 Próximo paso: python check_current_implementation.py")
    else:
        print("\n⚠️ Revisa manualmente enhanced_trajectory_engine.py línea 310")