#!/usr/bin/env python3
"""
Validador y Reparador Automático
Detecta y corrige errores comunes de sintaxis e indentación
"""

import ast
import re
import os
from typing import List, Tuple, Optional


class AutoFixer:
    def __init__(self):
        self.common_patterns = {
            'missing_colon': (r'^\s*(if|elif|else|for|while|def|class|try|except|finally|with)\s+[^:]+$', 'add_colon'),
            'tab_indent': (r'^\t+', 'convert_tabs'),
            'trailing_whitespace': (r'\s+$', 'strip_trailing'),
            'missing_self': (r'def\s+\w+\([^)]*\):', 'check_method_self'),
            'unclosed_brackets': (r'[(\[{]', 'check_brackets')
        }
        
    def diagnose_file(self, file_path: str) -> List[dict]:
        """Diagnostica problemas en un archivo"""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.splitlines()
                
            # Intento de parseo para detectar errores de sintaxis
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append({
                    'type': 'syntax_error',
                    'line': e.lineno,
                    'message': e.msg,
                    'text': lines[e.lineno - 1] if e.lineno <= len(lines) else '',
                    'fixable': self._is_fixable_syntax_error(e)
                })
                
            # Verificar patrones comunes
            for line_num, line in enumerate(lines, 1):
                # Indentación inconsistente
                if line.strip() and '\t' in line:
                    issues.append({
                        'type': 'tab_indentation',
                        'line': line_num,
                        'message': 'Uso de tabs en lugar de espacios',
                        'text': line,
                        'fixable': True
                    })
                    
                # Mezcla de tabs y espacios
                if line.startswith(' ') and '\t' in line:
                    issues.append({
                        'type': 'mixed_indentation',
                        'line': line_num,
                        'message': 'Mezcla de tabs y espacios',
                        'text': line,
                        'fixable': True
                    })
                    
                # Indentación no múltiplo de 4
                indent = len(line) - len(line.lstrip())
                if line.strip() and indent % 4 != 0:
                    issues.append({
                        'type': 'irregular_indentation',
                        'line': line_num,
                        'message': f'Indentación de {indent} espacios (debe ser múltiplo de 4)',
                        'text': line,
                        'fixable': True
                    })
                    
        except Exception as e:
            issues.append({
                'type': 'read_error',
                'line': 0,
                'message': str(e),
                'text': '',
                'fixable': False
            })
            
        return issues
        
    def _is_fixable_syntax_error(self, error: SyntaxError) -> bool:
        """Determina si un error de sintaxis es auto-reparable"""
        fixable_patterns = [
            'expected ":"',
            'unexpected indent',
            'unindent does not match',
            'invalid syntax'
        ]
        return any(pattern in error.msg.lower() for pattern in fixable_patterns)
        
    def auto_fix_file(self, file_path: str, backup: bool = True) -> Tuple[bool, List[str]]:
        """Intenta reparar automáticamente problemas comunes"""
        fixes_applied = []
        
        if backup:
            from safe_edit_system import SafeEditSystem
            editor = SafeEditSystem()
            backup_path = editor.create_verified_backup(file_path)
            if not backup_path:
                return False, ["No se pudo crear backup - archivo con errores"]
                
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            original_lines = lines.copy()
            
            # Aplicar fixes línea por línea
            for i, line in enumerate(lines):
                # Convertir tabs a espacios
                if '\t' in line:
                    lines[i] = line.replace('\t', '    ')
                    fixes_applied.append(f"Línea {i+1}: Convertidos tabs a espacios")
                    
                # Eliminar espacios al final
                if line.rstrip() != line.rstrip('\n'):
                    lines[i] = line.rstrip() + '\n'
                    fixes_applied.append(f"Línea {i+1}: Eliminados espacios finales")
                    
                # Arreglar indentación irregular
                stripped = line.lstrip()
                if stripped:
                    indent = len(line) - len(stripped)
                    if indent % 4 != 0:
                        new_indent = round(indent / 4) * 4
                        lines[i] = ' ' * new_indent + stripped
                        fixes_applied.append(f"Línea {i+1}: Ajustada indentación de {indent} a {new_indent} espacios")
                        
            # Verificar si hay cambios
            if lines != original_lines:
                # Intentar validar antes de escribir
                try:
                    ast.parse(''.join(lines))
                    
                    # Escribir cambios
                    with open(file_path, 'w') as f:
                        f.writelines(lines)
                        
                    return True, fixes_applied
                    
                except SyntaxError as e:
                    # Los cambios no resolvieron el problema
                    return False, [f"Los cambios automáticos no resolvieron todos los errores: {e}"]
            else:
                return True, ["No se requirieron cambios automáticos"]
                
        except Exception as e:
            return False, [f"Error durante la reparación: {str(e)}"]
            
    def suggest_manual_fixes(self, file_path: str) -> List[str]:
        """Sugiere correcciones manuales para problemas no auto-reparables"""
        issues = self.diagnose_file(file_path)
        suggestions = []
        
        for issue in issues:
            if not issue['fixable']:
                if issue['type'] == 'syntax_error':
                    # Sugerencias específicas por tipo de error
                    if 'expected' in issue['message']:
                        suggestions.append(f"Línea {issue['line']}: {issue['message']}")
                        suggestions.append(f"  Código actual: {issue['text']}")
                        suggestions.append(f"  Sugerencia: Verifica que no falten ':' al final de if/for/def/class")
                    elif 'EOF' in issue['message']:
                        suggestions.append("Error: Posible paréntesis, corchete o llave sin cerrar")
                        suggestions.append("  Sugerencia: Busca '(', '[', o '{' sin su correspondiente cierre")
                        
        return suggestions


def check_project_health():
    """Verifica la salud sintáctica de todo el proyecto"""
    fixer = AutoFixer()
    problem_files = []
    
    for root, dirs, files in os.walk('trajectory_hub'):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py') and not file.endswith('_backup.py'):
                file_path = os.path.join(root, file)
                issues = fixer.diagnose_file(file_path)
                
                if issues:
                    problem_files.append({
                        'file': file_path,
                        'issues': issues,
                        'fixable': any(issue['fixable'] for issue in issues)
                    })
                    
    return problem_files


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Modo archivo específico
        file_path = sys.argv[1]
        fixer = AutoFixer()
        
        print(f"\n🔍 Diagnosticando {file_path}...")
        issues = fixer.diagnose_file(file_path)
        
        if not issues:
            print("✅ No se encontraron problemas!")
        else:
            print(f"\n❌ Se encontraron {len(issues)} problemas:")
            for issue in issues:
                print(f"\n  Línea {issue['line']}: {issue['type']}")
                print(f"  {issue['message']}")
                if issue['text']:
                    print(f"  > {issue['text']}")
                print(f"  Auto-reparable: {'Sí' if issue['fixable'] else 'No'}")
                
            # Ofrecer reparación automática
            fixable = [i for i in issues if i['fixable']]
            if fixable:
                response = input(f"\n¿Intentar reparar {len(fixable)} problemas automáticamente? (s/n): ")
                if response.lower() == 's':
                    success, fixes = fixer.auto_fix_file(file_path)
                    if success:
                        print("\n✅ Reparación completada:")
                        for fix in fixes:
                            print(f"  • {fix}")
                    else:
                        print("\n❌ No se pudieron aplicar todas las correcciones:")
                        for fix in fixes:
                            print(f"  • {fix}")
                            
            # Sugerencias manuales
            suggestions = fixer.suggest_manual_fixes(file_path)
            if suggestions:
                print("\n📝 Sugerencias para corrección manual:")
                for suggestion in suggestions:
                    print(f"  {suggestion}")
    else:
        # Modo verificación completa del proyecto
        print("\n🏥 Verificando salud del proyecto...")
        problems = check_project_health()
        
        if not problems:
            print("✅ Todos los archivos están sintácticamente correctos!")
        else:
            print(f"\n❌ {len(problems)} archivos con problemas:")
            
            for problem in problems:
                print(f"\n📄 {problem['file']}")
                print(f"   Problemas: {len(problem['issues'])}")
                print(f"   Auto-reparable: {'Parcialmente' if problem['fixable'] else 'No'}")