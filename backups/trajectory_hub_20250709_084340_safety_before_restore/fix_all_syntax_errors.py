# === fix_all_syntax_errors.py ===
# 🔧 Fix: Limpieza completa de errores de sintaxis
# ⚡ Arregla múltiples problemas de una sola vez

import os
import re

def fix_all_syntax_errors():
    """Arreglar todos los errores de sintaxis en enhanced_trajectory_engine.py"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_fix_all', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Analizando archivo completo...")
    
    # Fixes a aplicar
    fixes_applied = 0
    lines_to_remove = []
    
    # 1. Buscar funciones con definiciones incompletas
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Si encontramos una definición de función
        if line.startswith('def '):
            # Verificar que termine correctamente
            j = i
            complete = False
            params_lines = []
            
            while j < len(lines) and j < i + 10:  # Max 10 líneas para una definición
                if lines[j].rstrip().endswith(':'):
                    complete = True
                    break
                params_lines.append(j)
                j += 1
            
            if not complete and j < len(lines):
                print(f"❌ Función incompleta en línea {i+1}: {line}")
                # Intentar arreglarla
                if 'set_individual_trajectory' in line:
                    # Reemplazar con definición correcta
                    lines[i] = '    def set_individual_trajectory(self, macro_id, source_id: int, ' \
                              'shape: str, shape_params: dict = None, ' \
                              'movement_mode: str = "fix", movement_speed: float = 1.0):\n'
                    # Marcar líneas extra para eliminar
                    for k in range(i+1, j+1):
                        if k < len(lines) and not lines[k].strip().startswith('"""'):
                            lines_to_remove.append(k)
                    fixes_applied += 1
                    
        # 2. Buscar líneas sueltas con parámetros
        elif ':' in line and '=' in line and line.endswith(','):
            # Verificar si no es parte de un diccionario o llamada
            if i > 0 and not any(x in lines[i-1] for x in ['def ', '(', '{', '[']):
                print(f"❌ Parámetros sueltos en línea {i+1}: {line[:50]}...")
                lines_to_remove.append(i)
                
        # 3. Buscar if statements problemáticos
        elif line.startswith('if ') and 'hasattr' in line:
            # Verificar contexto
            if i > 0 and 'def ' not in lines[i-1]:
                # Buscar la función contenedora
                func_start = i - 1
                while func_start > 0 and not lines[func_start].strip().startswith('def '):
                    func_start -= 1
                
                if func_start > 0 and i - func_start > 15:  # Muy lejos de cualquier def
                    print(f"❌ If statement suelto en línea {i+1}")
                    lines_to_remove.append(i)
                    # También eliminar las líneas siguientes del bloque
                    j = i + 1
                    indent = len(lines[i]) - len(lines[i].lstrip())
                    while j < len(lines) and len(lines[j]) - len(lines[j].lstrip()) > indent:
                        lines_to_remove.append(j)
                        j += 1
                    
        i += 1
    
    # 4. Eliminar líneas problemáticas
    print(f"\n✅ Eliminando {len(set(lines_to_remove))} líneas problemáticas...")
    for idx in sorted(set(lines_to_remove), reverse=True):
        if idx < len(lines):
            del lines[idx]
            fixes_applied += 1
    
    # 5. Arreglar problemas específicos conocidos
    for i in range(len(lines)):
        # Quitar comentarios al final de líneas if
        if lines[i].strip().startswith('if ') and '#' in lines[i] and not lines[i].rstrip().endswith(':'):
            lines[i] = lines[i].split('#')[0].rstrip() + ':\n'
            fixes_applied += 1
            
        # Arreglar paréntesis extra
        if lines[i].count('(') < lines[i].count(')'):
            lines[i] = lines[i].replace(')', '', 1)
            fixes_applied += 1
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n✅ {fixes_applied} correcciones aplicadas")

def verify_syntax():
    """Verificar que no hay errores de sintaxis"""
    print("\n🧪 Verificando sintaxis...")
    
    try:
        import ast
        with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
            content = f.read()
        
        ast.parse(content)
        print("✅ Sintaxis correcta!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error en línea {e.lineno}: {e.msg}")
        if e.text:
            print(f"   {e.text}")
        return False

def run_delta_test():
    """Ejecutar test de deltas"""
    print("\n🚀 Ejecutando test del sistema...")
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        print("✅ Import exitoso")
        
        # Test mínimo
        engine = EnhancedTrajectoryEngine(n_sources=5)
        macro = engine.create_macro("test", source_count=3)
        
        if macro:
            print(f"✅ Macro creado: {macro.name}")
            
            # Aplicar concentración
            engine.apply_concentration("test", 0.8)
            
            # Update
            for _ in range(5):
                engine.update()
            
            print("✅ Sistema funcionando")
            
            # Test completo
            import subprocess
            result = subprocess.run(['python', 'test_delta_100.py'], 
                                  capture_output=True, text=True, timeout=10)
            
            if '100%' in result.stdout:
                print("\n🎉 ¡SISTEMA DE DELTAS 100% FUNCIONAL!")
            else:
                # Buscar porcentaje
                import re
                match = re.search(r'(\d+)%', result.stdout)
                if match:
                    print(f"\n📊 Sistema de deltas al {match.group(1)}%")
                    
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)[:200]}")

if __name__ == "__main__":
    print("🔧 FIX ALL SYNTAX ERRORS")
    print("=" * 60)
    
    fix_all_syntax_errors()
    
    if verify_syntax():
        run_delta_test()
    else:
        print("\n⚠️ Todavía hay errores de sintaxis")
        print("📝 Revisar manualmente enhanced_trajectory_engine.py")