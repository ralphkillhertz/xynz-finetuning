#!/usr/bin/env python3
"""
🔧 Fix: Añade las clases base que faltan
⚡ Error: MotionState is not defined
🎯 Solución: Verificar y añadir todas las clases base necesarias
"""

import re

def check_and_add_base_classes():
    """Verifica y añade las clases base necesarias"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    print("🔍 Verificando clases base en motion_components.py...\n")
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Lista de clases base necesarias
    base_classes = {
        'MotionState': '''@dataclass
class MotionState:
    """Estado completo de movimiento de una fuente"""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    orientation: np.ndarray = field(default_factory=lambda: np.zeros(3))
    aperture: float = 0.0
    gain: float = 0.0
    distance: float = 1.0
    presence: float = 1.0
    brightness: float = 0.0
    warmth: float = 0.0
    name: str = ""
''',
        
        'MotionDelta': '''@dataclass
class MotionDelta:
    """Representa un cambio incremental en posición/orientación"""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    orientation: np.ndarray = field(default_factory=lambda: np.zeros(3))
    aperture: float = 0.0
    weight: float = 1.0
    source: str = ""
    
    def scale(self, factor: float) -> 'MotionDelta':
        return MotionDelta(
            position=self.position * factor,
            orientation=self.orientation * factor,
            aperture=self.aperture * factor,
            weight=self.weight * factor,
            source=self.source
        )
''',
        
        'MotionComponent': '''class MotionComponent:
    """Clase base para componentes de movimiento"""
    
    def __init__(self):
        self.enabled = True
        
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        """Actualiza el estado - debe ser implementado por subclases"""
        return state
        
    def reset(self):
        """Reinicia el componente a su estado inicial"""
        pass
'''
    }
    
    # Verificar cada clase
    classes_added = []
    
    for class_name, class_code in base_classes.items():
        if f'class {class_name}' not in content:
            print(f"❌ {class_name} no encontrado - añadiendo...")
            classes_added.append((class_name, class_code))
        else:
            print(f"✅ {class_name} ya existe")
    
    # Si hay clases que añadir
    if classes_added:
        print(f"\n📝 Añadiendo {len(classes_added)} clases...")
        
        # Buscar dónde insertar (después de imports)
        # Buscar el final de los imports
        import_section_end = 0
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('import') and not line.startswith('from'):
                if i > 10:  # Asumimos que los imports están en las primeras líneas
                    import_section_end = i
                    break
        
        # Insertar las clases base
        new_content_parts = []
        new_content_parts.append('\n'.join(lines[:import_section_end]))
        new_content_parts.append('\n\n# ===== CLASES BASE =====\n')
        
        for class_name, class_code in classes_added:
            new_content_parts.append(class_code)
            new_content_parts.append('\n')
        
        new_content_parts.append('\n# ===== FIN CLASES BASE =====\n\n')
        new_content_parts.append('\n'.join(lines[import_section_end:]))
        
        new_content = '\n'.join(new_content_parts)
        
        # Guardar
        with open(motion_file, 'w') as f:
            f.write(new_content)
        
        print("✅ Clases base añadidas")
    
    return len(classes_added) > 0

def verify_imports():
    """Verifica que los imports necesarios estén presentes"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    print("\n🔍 Verificando imports necesarios...")
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    required_imports = [
        "import numpy as np",
        "from dataclasses import dataclass, field",
        "from typing import"
    ]
    
    missing_imports = []
    
    for imp in required_imports:
        if imp not in content:
            missing_imports.append(imp)
            print(f"❌ Falta: {imp}")
        else:
            print(f"✅ {imp}")
    
    if missing_imports:
        # Añadir imports faltantes al principio
        new_imports = '\n'.join(missing_imports) + '\n\n'
        content = new_imports + content
        
        with open(motion_file, 'w') as f:
            f.write(content)
        
        print("✅ Imports añadidos")

def test_basic_imports():
    """Test rápido de imports"""
    print("\n🧪 Test de imports básicos...")
    
    try:
        from trajectory_hub.core.motion_components import MotionState, MotionDelta, MotionComponent
        print("✅ MotionState importado")
        print("✅ MotionDelta importado")
        print("✅ MotionComponent importado")
        
        # Crear instancias de prueba
        ms = MotionState()
        print(f"   MotionState position: {ms.position}")
        
        md = MotionDelta()
        print(f"   MotionDelta source: '{md.source}'")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔧 ARREGLANDO CLASES BASE FALTANTES")
    print("=" * 60)
    
    # 1. Verificar imports
    verify_imports()
    
    # 2. Añadir clases base
    modified = check_and_add_base_classes()
    
    # 3. Test
    if test_basic_imports():
        print("\n✅ CLASES BASE ARREGLADAS")
        print("\n📋 Ahora ejecuta:")
        print("$ python test_delta_system_complete.py")
    else:
        print("\n⚠️ Puede necesitar revisión manual")

if __name__ == "__main__":
    main()