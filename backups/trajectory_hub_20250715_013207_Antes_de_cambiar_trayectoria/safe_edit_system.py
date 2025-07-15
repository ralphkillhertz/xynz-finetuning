#!/usr/bin/env python3
"""
Sistema de Edición Segura para Archivos Python
Previene errores de sintaxis e indentación al editar archivos grandes
"""

import ast
import difflib
import shutil
from datetime import datetime
from typing import Optional, Tuple, List
import subprocess
import sys
import os


class SafeEditSystem:
    def __init__(self):
        self.edit_history = []
        
    def create_verified_backup(self, file_path: str) -> Optional[str]:
        """Crea backup solo si el archivo tiene sintaxis válida"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Verificar sintaxis
            ast.parse(content)
            
            # Crear backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{file_path}.safe_{timestamp}"
            shutil.copy2(file_path, backup_path)
            
            print(f"✅ Backup verificado creado: {backup_path}")
            return backup_path
            
        except SyntaxError as e:
            print(f"❌ ERROR: El archivo tiene errores de sintaxis:")
            print(f"   Línea {e.lineno}: {e.msg}")
            return None
            
    def extract_function(self, file_path: str, function_name: str) -> Optional[Tuple[str, int, int]]:
        """Extrae una función específica con su contexto"""
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        in_function = False
        start_line = -1
        indent_level = 0
        function_lines = []
        
        for i, line in enumerate(lines):
            # Detectar inicio de función
            if f"def {function_name}(" in line:
                in_function = True
                start_line = i
                indent_level = len(line) - len(line.lstrip())
                function_lines.append(line)
                continue
                
            if in_function:
                # Verificar si seguimos en la función
                current_indent = len(line) - len(line.lstrip())
                
                # Si la línea no está vacía y tiene menor indentación, terminamos
                if line.strip() and current_indent <= indent_level:
                    break
                    
                function_lines.append(line)
                
        if start_line >= 0:
            return (''.join(function_lines), start_line, start_line + len(function_lines))
        return None
        
    def validate_indentation(self, code: str, base_indent: int = 0) -> bool:
        """Valida que la indentación sea consistente"""
        lines = code.split('\n')
        indent_stack = [base_indent]
        
        for line_num, line in enumerate(lines):
            if not line.strip():  # Línea vacía
                continue
                
            current_indent = len(line) - len(line.lstrip())
            
            # Verificar que la indentación sea múltiplo de 4
            if current_indent % 4 != 0:
                print(f"❌ Error de indentación en línea {line_num + 1}: indentación no es múltiplo de 4")
                return False
                
            # Verificar consistencia con el stack de indentación
            if line.strip().endswith(':'):
                indent_stack.append(current_indent + 4)
            elif current_indent < indent_stack[-1]:
                # Desindentación - debe coincidir con un nivel anterior
                while indent_stack and current_indent < indent_stack[-1]:
                    indent_stack.pop()
                if not indent_stack or current_indent != indent_stack[-1]:
                    print(f"❌ Error de indentación en línea {line_num + 1}: desindentación inconsistente")
                    return False
                    
        return True
        
    def safe_replace_function(self, file_path: str, function_name: str, new_implementation: str) -> bool:
        """Reemplaza una función de forma segura"""
        # 1. Crear backup verificado
        backup = self.create_verified_backup(file_path)
        if not backup:
            return False
            
        try:
            # 2. Leer archivo
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            # 3. Encontrar función
            func_data = self.extract_function(file_path, function_name)
            if not func_data:
                print(f"❌ Función '{function_name}' no encontrada")
                return False
                
            old_impl, start_line, end_line = func_data
            
            # 4. Validar nueva implementación
            base_indent = len(lines[start_line]) - len(lines[start_line].lstrip())
            if not self.validate_indentation(new_implementation, base_indent):
                return False
                
            # 5. Preparar nueva implementación
            new_lines = new_implementation.split('\n')
            if not new_lines[-1].endswith('\n'):
                new_lines[-1] += '\n'
                
            # 6. Reemplazar
            new_content = lines[:start_line] + [line + '\n' for line in new_lines[:-1]] + [new_lines[-1]] + lines[end_line:]
            
            # 7. Verificar sintaxis antes de escribir
            try:
                ast.parse(''.join(new_content))
            except SyntaxError as e:
                print(f"❌ Error de sintaxis en el código resultante:")
                print(f"   Línea {e.lineno}: {e.msg}")
                return False
                
            # 8. Escribir archivo
            with open(file_path, 'w') as f:
                f.writelines(new_content)
                
            # 9. Verificar con Python
            result = subprocess.run([sys.executable, '-m', 'py_compile', file_path], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Error de compilación:")
                print(result.stderr)
                # Restaurar backup
                shutil.copy2(backup, file_path)
                return False
                
            print(f"✅ Función '{function_name}' actualizada correctamente")
            
            # 10. Registrar cambio exitoso
            self.edit_history.append({
                'timestamp': datetime.now().isoformat(),
                'file': file_path,
                'function': function_name,
                'backup': backup,
                'status': 'success'
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            # Restaurar backup
            if backup:
                shutil.copy2(backup, file_path)
            return False
            
    def show_diff(self, file_path: str, backup_path: str):
        """Muestra las diferencias entre archivo actual y backup"""
        with open(backup_path, 'r') as f:
            old_lines = f.readlines()
        with open(file_path, 'r') as f:
            new_lines = f.readlines()
            
        diff = difflib.unified_diff(old_lines, new_lines, 
                                   fromfile=f"{backup_path} (original)",
                                   tofile=f"{file_path} (modificado)")
        
        print("\n📝 Cambios realizados:")
        print("="*60)
        for line in diff:
            if line.startswith('+'):
                print(f"\033[92m{line}\033[0m", end='')  # Verde
            elif line.startswith('-'):
                print(f"\033[91m{line}\033[0m", end='')  # Rojo
            else:
                print(line, end='')
                
    def restore_backup(self, file_path: str, backup_path: str) -> bool:
        """Restaura un backup específico"""
        try:
            shutil.copy2(backup_path, file_path)
            print(f"✅ Restaurado desde: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Error al restaurar: {e}")
            return False
            
    def list_safe_backups(self, file_path: str) -> List[str]:
        """Lista todos los backups seguros de un archivo"""
        import os
        import glob
        
        pattern = f"{file_path}.safe_*"
        backups = glob.glob(pattern)
        return sorted(backups, reverse=True)  # Más recientes primero


# Funciones de conveniencia
def safe_edit_function(file_path: str, function_name: str, new_implementation: str) -> bool:
    """Edita una función de forma segura"""
    editor = SafeEditSystem()
    return editor.safe_replace_function(file_path, function_name, new_implementation)


def test_syntax(file_path: str) -> bool:
    """Prueba rápida de sintaxis"""
    try:
        with open(file_path, 'r') as f:
            ast.parse(f.read())
        print(f"✅ {file_path} - Sintaxis correcta")
        return True
    except SyntaxError as e:
        print(f"❌ {file_path} - Error de sintaxis:")
        print(f"   Línea {e.lineno}: {e.msg}")
        return False


if __name__ == "__main__":
    # Ejemplo de uso
    print("🛡️ Sistema de Edición Segura")
    print("="*60)
    
    # Probar sintaxis de archivos principales
    files_to_check = [
        "trajectory_hub/interface/interactive_controller.py",
        "trajectory_hub/core/enhanced_trajectory_engine.py",
        "trajectory_hub/core/motion_components.py"
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            test_syntax(file)