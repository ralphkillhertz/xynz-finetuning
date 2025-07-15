# === diagnose_engine_deep.py ===
# 🔍 Diagnóstico profundo de enhanced_trajectory_engine.py
# ⚡ Identifica TODOS los problemas de sintaxis

import ast
import re
from typing import List, Tuple

def analyze_file_structure(filepath: str):
    """Analiza la estructura del archivo e identifica todos los problemas"""
    
    print("🔍 DIAGNÓSTICO PROFUNDO DE ENHANCED_TRAJECTORY_ENGINE.PY")
    print("=" * 70)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    
    # 1. Detectar funciones sin cuerpo
    print("\n📋 Buscando funciones sin cuerpo...")
    in_function = False
    func_start_line = 0
    func_indent = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Detectar inicio de función
        if re.match(r'^(\s*)def\s+\w+\s*\(', line):
            in_function = True
            func_start_line = i
            func_indent = len(line) - len(line.lstrip())
            func_name = re.search(r'def\s+(\w+)', line).group(1)
            
            # Verificar siguiente línea no vacía
            j = i + 1
            while j < len(lines) and lines[j].strip() in ['', '"""', "'''"]:
                j += 1
            
            if j < len(lines):
                next_line = lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # Si la siguiente línea no está más indentada, falta cuerpo
                if next_indent <= func_indent and next_line.strip():
                    issues.append({
                        'line': i + 1,
                        'type': 'missing_body',
                        'func': func_name,
                        'text': line.rstrip()
                    })
    
    # 2. Detectar docstrings huérfanas
    print("\n📋 Buscando docstrings mal ubicadas...")
    for i, line in enumerate(lines):
        if line.strip().startswith('"""') or line.strip().startswith("'''"):
            # Verificar línea anterior
            if i > 0:
                prev_line = lines[i-1].strip()
                if prev_line and not prev_line.endswith(':'):
                    # Docstring sin función/clase asociada
                    issues.append({
                        'line': i + 1,
                        'type': 'orphan_docstring',
                        'text': line.rstrip()
                    })
    
    # 3. Detectar problemas de indentación
    print("\n📋 Analizando indentación...")
    expected_indent = 0
    indent_stack = [0]
    
    for i, line in enumerate(lines):
        if not line.strip():
            continue
            
        actual_indent = len(line) - len(line.lstrip())
        
        # Si termina en : espera mayor indentación
        if line.strip().endswith(':'):
            expected_indent = actual_indent + 4
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.strip():
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= actual_indent:
                        issues.append({
                            'line': i + 1,
                            'type': 'bad_indent_after_colon',
                            'text': line.rstrip()
                        })
    
    # 4. Buscar imports mal cerrados
    print("\n📋 Verificando imports...")
    in_import = False
    import_start = 0
    
    for i, line in enumerate(lines):
        if re.match(r'^\s*from\s+\S+\s+import\s*\($', line.strip()):
            in_import = True
            import_start = i
        elif in_import and ')' in line:
            in_import = False
        elif in_import and not line.strip().endswith(',') and line.strip() and not ')' in line:
            issues.append({
                'line': i + 1,
                'type': 'import_missing_comma',
                'text': line.rstrip()
            })
    
    # 5. Intentar parsear con AST para encontrar errores de sintaxis
    print("\n📋 Verificando sintaxis con AST...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ Sin errores de sintaxis detectados por AST")
    except SyntaxError as e:
        issues.append({
            'line': e.lineno,
            'type': 'syntax_error',
            'text': f"{e.msg} at line {e.lineno}",
            'ast_error': True
        })
    
    # Mostrar resumen
    print("\n" + "=" * 70)
    print(f"📊 RESUMEN: {len(issues)} problemas encontrados")
    print("=" * 70)
    
    # Agrupar por tipo
    by_type = {}
    for issue in issues:
        issue_type = issue['type']
        if issue_type not in by_type:
            by_type[issue_type] = []
        by_type[issue_type].append(issue)
    
    for issue_type, items in by_type.items():
        print(f"\n❌ {issue_type.upper()} ({len(items)} casos):")
        for item in items[:5]:  # Mostrar máximo 5 ejemplos
            print(f"   Línea {item['line']}: {item['text'][:60]}...")
        if len(items) > 5:
            print(f"   ... y {len(items) - 5} más")
    
    # Recomendación
    print("\n" + "=" * 70)
    print("💡 RECOMENDACIÓN:")
    if len(issues) > 20:
        print("   ⚠️ El archivo está SEVERAMENTE dañado")
        print("   🔄 Se recomienda RESTAURAR desde un backup limpio")
        print("   📁 Buscar: enhanced_trajectory_engine.py.backup_*")
    elif len(issues) > 10:
        print("   ⚠️ Múltiples problemas detectados")
        print("   🛠️ Se puede intentar reparación automática")
    else:
        print("   ✅ Problemas menores, reparación manual viable")
    
    return issues

def find_best_backup():
    """Busca el mejor backup disponible"""
    import glob
    import os
    
    print("\n📁 BUSCANDO BACKUPS...")
    backups = glob.glob("trajectory_hub/core/enhanced_trajectory_engine.py.backup_*")
    
    if not backups:
        print("❌ No se encontraron backups")
        return None
    
    # Ordenar por fecha de modificación
    backups_with_time = []
    for backup in backups:
        mtime = os.path.getmtime(backup)
        size = os.path.getsize(backup)
        backups_with_time.append((backup, mtime, size))
    
    backups_with_time.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n📋 Encontrados {len(backups)} backups:")
    for backup, mtime, size in backups_with_time[:5]:
        from datetime import datetime
        date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"   {backup}: {size:,} bytes - {date}")
    
    # Recomendar el más grande (probablemente más completo)
    largest = max(backups_with_time, key=lambda x: x[2])
    print(f"\n✅ Backup recomendado: {largest[0]} ({largest[2]:,} bytes)")
    
    return largest[0]

if __name__ == "__main__":
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Diagnóstico
    issues = analyze_file_structure(filepath)
    
    # Buscar backups
    best_backup = find_best_backup()
    
    if len(issues) > 20 and best_backup:
        print("\n" + "=" * 70)
        print("🔧 ACCIÓN RECOMENDADA:")
        print(f"   cp {best_backup} {filepath}")
        print("   # Luego aplicar cambios específicos necesarios")