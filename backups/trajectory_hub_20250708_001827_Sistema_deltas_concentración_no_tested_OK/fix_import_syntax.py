#!/usr/bin/env python3
"""
🔧 Fix: Corrige error de sintaxis en imports
⚡ Línea: 20 en enhanced_trajectory_engine.py
🎯 Impacto: CRÍTICO - Bloquea todo
"""

import re

def fix_imports():
    """Arregla el import de MotionDelta"""
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar el patrón problemático
    # Parece que hay una coma extra o paréntesis mal cerrado
    bad_patterns = [
        r'from trajectory_hub\.core\.motion_components import MotionDelta,\s*\(',
        r'from trajectory_hub\.core\.motion_components import MotionDelta,\s*$',
        r'from trajectory_hub\.core\.motion_components import MotionDelta,\s*\n\s*\(',
    ]
    
    for pattern in bad_patterns:
        if re.search(pattern, content, re.MULTILINE):
            print(f"❌ Encontrado patrón problemático: {pattern}")
            # Extraer la línea completa del import
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'from trajectory_hub.core.motion_components import' in line:
                    print(f"   Línea {i+1}: {line}")
                    # Ver las siguientes líneas
                    if i < len(lines) - 1:
                        next_line = lines[i+1]
                        if next_line.strip().startswith('('):
                            # Es un import multi-línea
                            print("   Import multi-línea detectado")
                            # Arreglar añadiendo MotionDelta correctamente
                            lines[i] = line.rstrip().rstrip(',') + ' ('
                            lines[i+1] = '    MotionDelta,' + next_line.strip()[1:]
                        else:
                            # Import de una línea - quitar coma extra
                            lines[i] = line.rstrip(',')
                    break
            
            content = '\n'.join(lines)
            break
    
    # Si no encontramos el patrón problemático, buscar imports normales
    import_line = None
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'from trajectory_hub.core.motion_components import' in line:
            import_line = i
            break
    
    if import_line is not None:
        # Verificar si MotionDelta está en los imports
        if 'MotionDelta' not in lines[import_line]:
            # Buscar si es import multi-línea
            if lines[import_line].strip().endswith('('):
                # Añadir en la siguiente línea
                lines[import_line + 1] = '    MotionDelta,\n' + lines[import_line + 1]
            else:
                # Extraer los imports existentes
                match = re.search(r'from trajectory_hub\.core\.motion_components import (.+)', lines[import_line])
                if match:
                    imports = match.group(1)
                    lines[import_line] = f'from trajectory_hub.core.motion_components import MotionDelta, {imports}'
    
    # Escribir de vuelta
    with open(engine_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print("✅ Imports corregidos")

def verify_fix():
    """Verifica que el archivo se puede importar"""
    try:
        import trajectory_hub.core.enhanced_trajectory_engine
        print("✅ enhanced_trajectory_engine.py importa correctamente")
        return True
    except SyntaxError as e:
        print(f"❌ Todavía hay error de sintaxis: {e}")
        # Mostrar las líneas alrededor del error
        with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'r') as f:
            lines = f.readlines()
            error_line = e.lineno - 1
            print(f"\nContexto (líneas {max(0, error_line-2)} a {min(len(lines), error_line+3)}):")
            for i in range(max(0, error_line-2), min(len(lines), error_line+3)):
                marker = ">>>" if i == error_line else "   "
                print(f"{marker} {i+1}: {lines[i].rstrip()}")
        return False
    except ImportError as e:
        # Puede ser que MotionDelta no esté definido aún
        if "MotionDelta" in str(e):
            print("⚠️ MotionDelta no está definido en motion_components.py")
            print("   Esto se arreglará cuando agreguemos la clase")
            return True
        else:
            print(f"❌ Error de import: {e}")
            return False

# Quick fix directo
def quick_fix():
    """Fix rápido y directo"""
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar la línea problemática
    for i, line in enumerate(lines):
        if 'from trajectory_hub.core.motion_components import' in line and 'MotionDelta' in line:
            # Si termina con coma y paréntesis abierto
            if line.rstrip().endswith(',') and i < len(lines) - 1 and lines[i+1].strip().startswith('('):
                lines[i] = line.replace('MotionDelta,', '')
                if 'MotionDelta' not in lines[i+1]:
                    lines[i+1] = lines[i+1].replace('(', '(\n    MotionDelta,')
            # Si termina solo con coma
            elif line.rstrip().endswith(',') and not line.rstrip().endswith('('):
                lines[i] = line.rstrip().rstrip(',') + '\n'
    
    with open(engine_file, 'w') as f:
        f.writelines(lines)
    
    print("✅ Quick fix aplicado")

if __name__ == "__main__":
    print("🔧 Arreglando error de sintaxis en imports...\n")
    
    # Intentar quick fix primero
    quick_fix()
    
    # Luego el fix completo
    fix_imports()
    
    # Verificar
    print("\n🧪 Verificando...")
    if verify_fix():
        print("\n✅ Error corregido! Ahora puedes ejecutar el test.")
    else:
        print("\n❌ Necesita revisión manual")