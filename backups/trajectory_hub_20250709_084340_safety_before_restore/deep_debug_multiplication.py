# === deep_debug_multiplication.py ===
# 🔍 Debug profundo para encontrar float * MotionState
# ⚡ Rastreo línea por línea

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def find_multiplication_in_files():
    """Buscar todas las multiplicaciones sospechosas"""
    print("🔍 BUSCANDO MULTIPLICACIONES EN ARCHIVOS")
    print("=" * 60)
    
    files = [
        'trajectory_hub/core/enhanced_trajectory_engine.py',
        'trajectory_hub/core/motion_components.py'
    ]
    
    suspicious_lines = []
    
    for file_path in files:
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"\n📄 {file_path}:")
        
        for i, line in enumerate(lines, 1):
            # Buscar líneas con multiplicación
            if '*' in line and ('motion' in line or 'state' in line):
                # Excluir comentarios y strings
                code_part = line.split('#')[0]
                if '"' in code_part or "'" in code_part:
                    continue
                    
                # Patrones sospechosos
                patterns = [
                    'dt * motion',
                    'motion * dt',
                    'dt * state',
                    'state * dt',
                    '* motion)',
                    '* state)',
                    'motion *',
                    'state *'
                ]
                
                for pattern in patterns:
                    if pattern in code_part:
                        print(f"   Línea {i}: {line.strip()}")
                        suspicious_lines.append((file_path, i, line.strip()))
                        break
    
    return suspicious_lines

def trace_update_execution():
    """Trazar la ejecución del update con monkey patching"""
    print("\n\n🔬 TRAZANDO EJECUCIÓN DE UPDATE")
    print("=" * 60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    from trajectory_hub.core.motion_components import SourceMotion
    
    # Guardar el update original
    original_motion_update = SourceMotion.update
    
    # Crear wrapper para debug
    def debug_update(self, *args, **kwargs):
        print(f"\n🔍 SourceMotion.update llamado con:")
        print(f"   • self: {type(self)}")
        print(f"   • args: {[type(arg).__name__ for arg in args]}")
        print(f"   • kwargs: {kwargs}")
        
        try:
            # Intentar llamar al original
            result = original_motion_update(self, *args, **kwargs)
            print(f"   ✅ Update exitoso")
            return result
        except TypeError as e:
            print(f"   ❌ ERROR: {e}")
            print(f"   • Intentando diagnosticar...")
            
            # Verificar qué está pasando
            if len(args) >= 2:
                for i, arg in enumerate(args):
                    print(f"   • args[{i}]: {type(arg)} = {arg if not hasattr(arg, '__dict__') else 'objeto complejo'}")
            
            raise
    
    # Aplicar monkey patch
    SourceMotion.update = debug_update
    
    try:
        # Test
        engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
        macro = engine.create_macro("debug", 2)
        engine.set_macro_concentration(macro, 0.5)
        
        print("\n📍 Llamando engine.update()...")
        engine.update()
        
    except Exception as e:
        print(f"\n💥 Error capturado: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Restaurar
        SourceMotion.update = original_motion_update

def check_motion_components_update():
    """Verificar la firma del método update en motion_components"""
    print("\n\n📋 VERIFICANDO MÉTODO UPDATE EN COMPONENTS")
    print("=" * 60)
    
    file_path = 'trajectory_hub/core/motion_components.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método update de SourceMotion
    import re
    pattern = r'class SourceMotion.*?(\n\s+def update\(self[^)]*\):[^\n]*)'
    
    matches = re.findall(pattern, content, re.DOTALL)
    
    if matches:
        for match in matches:
            print(f"Encontrado: {match}")
    
    # Buscar también en las líneas alrededor
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'def update(self' in line and i > 0:
            # Mostrar contexto
            start = max(0, i - 2)
            end = min(len(lines), i + 10)
            
            print(f"\n📍 Contexto del método update (líneas {start+1}-{end+1}):")
            for j in range(start, end):
                marker = ">>>" if j == i else "   "
                print(f"{marker} {j+1}: {lines[j]}")

if __name__ == "__main__":
    # 1. Buscar multiplicaciones sospechosas
    suspicious = find_multiplication_in_files()
    
    # 2. Trazar ejecución
    trace_update_execution()
    
    # 3. Verificar firmas de métodos
    check_motion_components_update()
    
    print("\n\n📊 RESUMEN:")
    print(f"Se encontraron {len(suspicious)} líneas sospechosas")
    print("\nRevisa el output anterior para identificar el problema exacto")