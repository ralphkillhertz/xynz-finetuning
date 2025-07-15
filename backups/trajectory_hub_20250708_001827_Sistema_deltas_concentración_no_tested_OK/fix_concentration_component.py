# === fix_concentration_component.py ===
# 🔧 Fix: Arregla el constructor de ConcentrationComponent
# ⚡ Impacto: BAJO - Simple ajuste de parámetros

import os
import re
from datetime import datetime

def fix_concentration_call():
    """Arregla la llamada a ConcentrationComponent"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Buscar la línea problemática
    old_line = "concentration = ConcentrationComponent(macro=macro)"
    new_line = "concentration = ConcentrationComponent()"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print(f"✅ Actualizado: {new_line}")
        
        # Añadir asignación de macro después si es necesario
        lines = content.split('\n')
        new_lines = []
        for i, line in enumerate(lines):
            new_lines.append(line)
            if line.strip() == new_line.strip():
                # Añadir asignación
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + "concentration.macro = macro")
                new_lines.append(' ' * indent + "concentration.enabled = True")
                print("✅ Añadidas asignaciones de macro y enabled")
        
        content = '\n'.join(new_lines)
    else:
        print("❌ No se encontró la línea a reemplazar")
        print("🔍 Buscando alternativa...")
        
        # Buscar patrón más flexible
        pattern = r'concentration\s*=\s*ConcentrationComponent\([^)]*\)'
        matches = list(re.finditer(pattern, content))
        
        if matches:
            print(f"✅ Encontradas {len(matches)} coincidencias")
            # Reemplazar todas
            content = re.sub(pattern, 'concentration = ConcentrationComponent()', content)
            print("✅ Todas las llamadas actualizadas")
    
    # Escribir archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Verificar sintaxis
    try:
        compile(content, engine_path, 'exec')
        print("✅ Sintaxis verificada")
        return True
    except Exception as e:
        print(f"❌ Error de sintaxis: {e}")
        # Restaurar
        with open(backup_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print("⚠️ Backup restaurado")
        return False

def check_concentration_component():
    """Verifica la estructura de ConcentrationComponent"""
    
    motion_path = "trajectory_hub/core/motion_components.py"
    
    if not os.path.exists(motion_path):
        print("❌ No se encuentra motion_components.py")
        return
    
    print("\n🔍 Analizando ConcentrationComponent...")
    
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar ConcentrationComponent.__init__
    pattern = r'class ConcentrationComponent.*?def __init__\(self([^)]*)\):'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        params = match.group(1).strip()
        print(f"✅ ConcentrationComponent.__init__(self{params})")
        
        if not params:
            print("   📌 No acepta parámetros adicionales")
        else:
            print(f"   📌 Parámetros: {params}")
    else:
        print("❌ No se encontró ConcentrationComponent.__init__")

if __name__ == "__main__":
    print("🔧 FIX DE CONCENTRATION COMPONENT")
    print("="*60)
    
    # Primero verificar la estructura
    check_concentration_component()
    
    # Aplicar fix
    print("\n🔧 Aplicando fix...")
    success = fix_concentration_call()
    
    if success:
        print("\n✅ Fix aplicado exitosamente")
        print("\n📋 Ya casi terminamos! Prueba ahora:")
        print("$ python test_delta_concentration_final.py")
        print("\n🎯 Este debería ser el último error!")
    else:
        print("\n❌ Error al aplicar fix")