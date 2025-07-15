#!/usr/bin/env python3
"""
🔧 Fix: Reordena las clases para resolver dependencias
⚡ Problema: MotionState se usa antes de ser definido
🎯 Solución: Mover MotionState al principio
"""

import re

def reorder_classes():
    """Reordena las clases en el orden correcto"""
    print("🔧 Reordenando clases en motion_components.py...\n")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Extraer cada clase importante
    classes_to_extract = {
        'MotionState': None,
        'MotionDelta': None,
        'MotionComponent': None,
        'SourceMotion': None
    }
    
    # Buscar cada clase
    for class_name in classes_to_extract:
        # Patrón para encontrar la clase completa
        if class_name in ['MotionState', 'MotionDelta']:
            # Estas suelen tener @dataclass
            pattern = rf'(@dataclass\s*\n)?class {class_name}.*?(?=\n@dataclass|\nclass|\Z)'
        else:
            pattern = rf'class {class_name}.*?(?=\n@dataclass|\nclass|\Z)'
        
        match = re.search(pattern, content, re.DOTALL)
        if match:
            classes_to_extract[class_name] = match.group(0)
            print(f"✅ Extraída clase {class_name}")
            # Eliminar del contenido original
            content = content.replace(match.group(0), f"\n# {class_name} movido arriba\n")
    
    # Extraer imports y todo lo que va antes de las clases
    first_class = re.search(r'(@dataclass|class)\s+\w+', content)
    if first_class:
        header = content[:first_class.start()]
    else:
        header = content[:200]  # Tomar los primeros 200 caracteres como header
    
    # Reconstruir en el orden correcto
    print("\n📝 Reconstruyendo archivo con orden correcto...")
    
    new_content = header.rstrip() + "\n\n"
    new_content += "# ===== CLASES BASE (ORDEN CORREGIDO) =====\n\n"
    
    # Orden correcto: MotionState primero, luego MotionDelta, etc.
    correct_order = ['MotionState', 'MotionDelta', 'MotionComponent', 'SourceMotion']
    
    for class_name in correct_order:
        if classes_to_extract[class_name]:
            new_content += classes_to_extract[class_name] + "\n\n"
            print(f"   ✅ {class_name} añadido en posición correcta")
    
    new_content += "# ===== FIN CLASES BASE =====\n\n"
    
    # Añadir el resto del contenido (otras clases)
    # Buscar donde empiezan las otras clases
    remaining_content = content
    for class_name in correct_order:
        marker = f"# {class_name} movido arriba"
        remaining_content = remaining_content.replace(marker, "")
    
    # Limpiar líneas vacías excesivas
    remaining_content = re.sub(r'\n{3,}', '\n\n', remaining_content)
    
    new_content += remaining_content
    
    # Guardar
    with open(motion_file, 'w') as f:
        f.write(new_content)
    
    print("\n✅ Clases reordenadas correctamente")

def verify_order():
    """Verifica que el orden sea correcto"""
    print("\n🔍 Verificando nuevo orden...")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    class_positions = {}
    
    for i, line in enumerate(lines):
        for class_name in ['MotionState', 'MotionDelta', 'MotionComponent', 'SourceMotion']:
            if f'class {class_name}' in line:
                class_positions[class_name] = i + 1
                print(f"   {class_name}: línea {i + 1}")
    
    # Verificar orden
    if all(cls in class_positions for cls in ['MotionState', 'MotionDelta']):
        if class_positions['MotionState'] < class_positions['MotionDelta']:
            print("\n✅ MotionState está antes que MotionDelta")
        else:
            print("\n❌ MotionDelta está antes que MotionState")

def test_imports():
    """Prueba que ahora sí funcionen los imports"""
    print("\n🧪 Probando imports...")
    
    try:
        from trajectory_hub.core.motion_components import (
            MotionState, MotionDelta, MotionComponent, SourceMotion
        )
        
        print("✅ Todos los imports funcionan!")
        
        # Crear instancias
        ms = MotionState()
        print(f"   MotionState creado: position = {ms.position}")
        
        md = MotionDelta()
        print(f"   MotionDelta creado: source = '{md.source}'")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔧 REORDENANDO CLASES PARA RESOLVER DEPENDENCIAS")
    print("=" * 60)
    
    # 1. Reordenar
    reorder_classes()
    
    # 2. Verificar
    verify_order()
    
    # 3. Probar
    if test_imports():
        print("\n🎉 ¡PROBLEMA RESUELTO!")
        print("\n📋 Ahora ejecuta:")
        print("$ python test_delta_system_complete.py")
    else:
        print("\n⚠️ Puede necesitar el test mínimo:")
        print("$ python test_minimal_import.py")

if __name__ == "__main__":
    main()