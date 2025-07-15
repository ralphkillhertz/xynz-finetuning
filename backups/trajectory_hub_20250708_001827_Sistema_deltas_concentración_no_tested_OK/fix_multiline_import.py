#!/usr/bin/env python3
"""
🔧 Fix: Arregla import multi-línea mal formateado
⚡ Línea: 20 en enhanced_trajectory_engine.py
🎯 Solución: Reformatear import correctamente
"""

def fix_multiline_import():
    """Arregla el import multi-línea"""
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar la línea problemática (línea 20, índice 19)
    for i in range(len(lines)):
        if i >= 19 and 'from trajectory_hub.core.motion_components import' in lines[i]:
            # Reconstruir el import completo
            print(f"🔍 Encontrado import en línea {i+1}")
            
            # Recolectar todas las líneas del import
            import_lines = []
            j = i
            while j < len(lines):
                import_lines.append(lines[j].strip())
                if ')' in lines[j]:
                    # Fin del import multi-línea
                    break
                j += 1
            
            # Extraer todos los nombres importados
            import_text = ' '.join(import_lines)
            # Limpiar y extraer nombres
            import_text = import_text.replace('from trajectory_hub.core.motion_components import', '')
            import_text = import_text.replace('MotionDelta,', '')
            import_text = import_text.replace('(', '').replace(')', '')
            
            # Obtener lista de imports
            imports = [name.strip() for name in import_text.split(',') if name.strip()]
            
            # Añadir MotionDelta al principio si no está
            if 'MotionDelta' not in imports:
                imports.insert(0, 'MotionDelta')
            
            # Reconstruir import correctamente
            new_import = "from trajectory_hub.core.motion_components import (\n"
            for idx, imp in enumerate(imports):
                if idx < len(imports) - 1:
                    new_import += f"    {imp},\n"
                else:
                    new_import += f"    {imp}\n"
            new_import += ")\n"
            
            # Reemplazar las líneas del import
            # Eliminar las líneas viejas
            del lines[i:j+1]
            
            # Insertar las nuevas
            for line in new_import.split('\n')[:-1]:
                lines.insert(i, line + '\n')
                i += 1
            
            print("✅ Import reformateado correctamente")
            break
    
    # Escribir de vuelta
    with open(engine_file, 'w') as f:
        f.writelines(lines)
    
    # Mostrar el resultado
    print("\n📋 Import corregido:")
    with open(engine_file, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[15:25], 16):
            if 'from trajectory_hub.core.motion_components import' in line:
                print(f"✨ {i}: {line.rstrip()}")
            else:
                print(f"   {i}: {line.rstrip()}")

def test_import():
    """Prueba que el import funciona"""
    print("\n🧪 Probando import...")
    try:
        # Primero necesitamos asegurarnos de que MotionDelta existe
        add_motion_delta_class()
        
        # Ahora probar el import
        import trajectory_hub.core.enhanced_trajectory_engine
        print("✅ Import exitoso!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def add_motion_delta_class():
    """Asegura que MotionDelta esté definido en motion_components.py"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    if "class MotionDelta" not in content:
        print("⚠️ Añadiendo clase MotionDelta a motion_components.py...")
        
        # Buscar dónde insertar (después de los imports)
        lines = content.split('\n')
        insert_pos = 0
        
        # Buscar después de los imports y antes de la primera clase
        for i, line in enumerate(lines):
            if line.startswith('class ') or line.startswith('@dataclass'):
                insert_pos = i
                break
        
        motion_delta_code = '''
@dataclass
class MotionDelta:
    """Representa un cambio incremental en posición/orientación"""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    orientation: np.ndarray = field(default_factory=lambda: np.zeros(3))
    aperture: float = 0.0
    weight: float = 1.0
    source: str = ""
    
    def scale(self, factor: float) -> 'MotionDelta':
        """Escala el delta por un factor"""
        return MotionDelta(
            position=self.position * factor,
            orientation=self.orientation * factor,
            aperture=self.aperture * factor,
            weight=self.weight * factor,
            source=self.source
        )

'''
        
        lines.insert(insert_pos, motion_delta_code)
        
        with open(motion_file, 'w') as f:
            f.write('\n'.join(lines))
        
        print("✅ MotionDelta añadido a motion_components.py")

if __name__ == "__main__":
    print("🔧 ARREGLANDO IMPORT MULTI-LÍNEA\n")
    
    fix_multiline_import()
    
    if test_import():
        print("\n✅ TODO LISTO! Ahora ejecuta:")
        print("$ python test_concentration_delta.py")
    else:
        print("\n⚠️ Puede que necesites ejecutar el test de todos modos")
        print("$ python test_concentration_delta.py")