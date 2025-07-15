# === fix_syntax_line_520.py ===
# 🔧 Fix: Error de sintaxis en enhanced_trajectory_engine.py línea 520
# ⚡ Solución directa para continuar con tests

import os

def fix_syntax_error():
    """Arreglar error de sintaxis en línea 520"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_fix_520', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    # Mostrar contexto alrededor de línea 520
    print("🔍 Contexto alrededor de línea 520:")
    for i in range(max(0, 515), min(len(lines), 530)):
        if i < len(lines):
            marker = ">>>" if i == 519 else "   "
            print(f"{marker} Línea {i+1}: {lines[i].rstrip()}")
    
    # Buscar el problema específico
    if 519 < len(lines):
        # Verificar líneas anteriores para encontrar paréntesis sin cerrar
        open_parens = 0
        for i in range(max(0, 510), 520):
            if i < len(lines):
                open_parens += lines[i].count('(') - lines[i].count(')')
        
        if open_parens > 0:
            print(f"\n⚠️ Detectados {open_parens} paréntesis sin cerrar antes de línea 520")
            
            # Buscar la línea anterior que podría necesitar cerrar paréntesis
            for i in range(519, max(0, 510), -1):
                if i < len(lines) and '(' in lines[i] and not lines[i].rstrip().endswith(')'):
                    if not lines[i].rstrip().endswith(':'):
                        print(f"✅ Arreglando línea {i+1}")
                        lines[i] = lines[i].rstrip() + ')\n'
                        break
    
    # Guardar cambios
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Archivo corregido")

def quick_test():
    """Test rápido del import"""
    print("\n🧪 Verificando import...")
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        print("✅ Import exitoso!")
        
        # Test básico
        engine = EnhancedTrajectoryEngine(n_sources=10)
        print("✅ Engine creado correctamente")
        
        # Ejecutar test completo
        print("\n🚀 Ejecutando test de deltas...")
        import subprocess
        result = subprocess.run(['python', 'test_delta_100.py'], 
                              capture_output=True, text=True)
        
        if result.stdout:
            # Mostrar solo resumen
            lines = result.stdout.split('\n')
            for line in lines:
                if 'RESUMEN' in line or '%' in line or 'funcional' in line:
                    print(line)
        
        if result.stderr:
            print(f"\n❌ Error: {result.stderr[-500:]}")
            
    except SyntaxError as e:
        print(f"❌ Todavía hay error de sintaxis:")
        print(f"   Archivo: {e.filename}")
        print(f"   Línea: {e.lineno}")
        print(f"   Texto: {e.text}")
        
        # Intentar fix más agresivo
        print("\n🔧 Aplicando fix más específico...")
        with open(e.filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if e.lineno and e.lineno > 0:
            problem_line = e.lineno - 1
            if problem_line < len(lines):
                print(f"   Línea problemática: {lines[problem_line].strip()}")
                
                # Si es un if sin dos puntos
                if lines[problem_line].strip().startswith('if ') and not lines[problem_line].rstrip().endswith(':'):
                    lines[problem_line] = lines[problem_line].rstrip() + ':\n'
                    print("   ✅ Añadiendo ':' faltante")
                    
                    with open(e.filename, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    
                    # Reintentar
                    quick_test()
                    return
    
    except Exception as e:
        print(f"❌ Error diferente: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("🔧 FIXING SYNTAX ERROR LINE 520")
    print("=" * 60)
    
    fix_syntax_error()
    quick_test()