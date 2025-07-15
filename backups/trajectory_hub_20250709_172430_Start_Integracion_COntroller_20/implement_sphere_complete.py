import os
import re
from datetime import datetime
import shutil

def implement_sphere_complete():
    """Implementar sphere en todas las capas necesarias"""
    print("🚀 IMPLEMENTACIÓN COMPLETA DE SPHERE 3D")
    print("="*60)
    
    # 1. FormationManager - Añadir cálculo 3D
    fix_formation_manager()
    
    # 2. CommandProcessor - Asegurar que use FormationManager
    fix_command_processor()
    
    # 3. Verificar el flujo completo
    verify_flow()

def fix_formation_manager():
    """Añadir sphere a FormationManager"""
    print("\n1️⃣ FORMATION MANAGER - Añadiendo cálculo 3D")
    print("-" * 40)
    
    fm_file = "trajectory_hub/control/managers/formation_manager.py"
    
    if not os.path.exists(fm_file):
        print("❌ No existe FormationManager")
        return False
    
    # Backup
    backup = f"{fm_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(fm_file, backup)
    
    with open(fm_file, 'r') as f:
        content = f.read()
    
    # Buscar self.formations = {
    pattern = r'(self\.formations\s*=\s*\{[^}]+\})'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ No encontré self.formations")
        return False
    
    old_dict = match.group(1)
    
    # Verificar si ya tiene sphere
    if '"sphere"' in old_dict:
        print("✅ Ya tiene sphere en el diccionario")
    else:
        # Añadir sphere
        new_dict = old_dict.rstrip('}').rstrip()
        if not new_dict.endswith(','):
            new_dict += ','
        new_dict += '\n            "sphere": self._create_sphere_formation\n        }'
        content = content.replace(old_dict, new_dict)
        print("✅ Añadido sphere al diccionario")
    
    # Verificar si tiene el método
    if '_create_sphere_formation' not in content:
        print("✅ Añadiendo método _create_sphere_formation...")
        
        # Método sphere 3D completo
        sphere_method = '''
    def _create_sphere_formation(self, source_ids, center=(0, 0, 0), radius=2.0):
        """
        Crear formación esférica 3D con distribución uniforme.
        Usa el algoritmo de espiral de Fibonacci para distribución óptima.
        
        Args:
            source_ids: Lista de IDs de fuentes
            center: Centro de la esfera (x, y, z)
            radius: Radio de la esfera
            
        Returns:
            dict: {source_id: (x, y, z)}
        """
        import numpy as np
        
        positions = {}
        n = len(source_ids)
        
        if n == 0:
            return positions
        
        print(f"🌐 Creando esfera 3D con {n} fuentes, radio={radius}")
        
        # Algoritmo de espiral de Fibonacci para distribución uniforme
        golden_angle = np.pi * (3.0 - np.sqrt(5.0))  # ~2.39996 radianes
        
        for i, sid in enumerate(source_ids):
            # y va de 1 a -1 (de polo norte a polo sur)
            if n > 1:
                y = 1 - (i / float(n - 1)) * 2
            else:
                y = 0  # Centro si solo hay una fuente
            
            # Radio en el plano XZ para esta altura Y
            radius_at_y = np.sqrt(1 - y * y)
            
            # Ángulo usando la proporción áurea para distribución uniforme
            theta = golden_angle * i
            
            # Coordenadas cartesianas
            x = np.cos(theta) * radius_at_y
            z = np.sin(theta) * radius_at_y
            
            # Escalar por el radio deseado y trasladar al centro
            positions[sid] = (
                center[0] + x * radius,
                center[1] + y * radius,  # Y es la altura
                center[2] + z * radius
            )
            
            # Debug
            if i < 3:  # Primeras 3 posiciones
                print(f"   Fuente {sid}: x={positions[sid][0]:.2f}, "
                      f"y={positions[sid][1]:.2f}, z={positions[sid][2]:.2f}")
        
        print(f"✅ Esfera 3D creada con {len(positions)} posiciones")
        return positions
'''
        
        # Insertar antes del final de la clase
        # Buscar el último método
        methods = list(re.finditer(r'\n    def \w+', content))
        if methods:
            last_method_start = methods[-1].start()
            
            # Encontrar el final del último método
            next_class = content.find('\nclass', last_method_start)
            next_dedent = re.search(r'\n(?!    )', content[last_method_start + 1:])
            
            if next_dedent:
                insert_pos = last_method_start + 1 + next_dedent.start()
            elif next_class > 0:
                insert_pos = next_class
            else:
                insert_pos = len(content)
            
            content = content[:insert_pos] + sphere_method + '\n' + content[insert_pos:]
            print("✅ Método sphere 3D añadido")
    else:
        print("✅ Ya tiene _create_sphere_formation")
    
    # Guardar
    with open(fm_file, 'w') as f:
        f.write(content)
    
    print("✅ FormationManager actualizado")
    return True

def fix_command_processor():
    """Verificar que CommandProcessor use FormationManager correctamente"""
    print("\n2️⃣ COMMAND PROCESSOR - Verificando flujo")
    print("-" * 40)
    
    cp_file = "trajectory_hub/control/processors/command_processor.py"
    
    if not os.path.exists(cp_file):
        print("❌ No existe CommandProcessor")
        return False
    
    with open(cp_file, 'r') as f:
        content = f.read()
    
    # Buscar handle_create_macro
    pattern = r'def handle_create_macro.*?(?=\n    def|\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ No encontré handle_create_macro")
        return False
    
    method = match.group(0)
    
    # Verificar que use FormationManager
    if 'formation_manager' in method.lower() or 'FormationManager' in method:
        print("✅ CommandProcessor usa FormationManager")
        
        # Verificar que no tenga mapeo incorrecto
        if 'sphere' in method and 'circle' in method:
            print("⚠️ Posible mapeo incorrecto sphere → circle")
    else:
        print("⚠️ CommandProcessor podría no estar usando FormationManager")
        
        # Buscar si calcula formaciones directamente
        if '_calculate_' in method:
            print("❌ CommandProcessor calcula formaciones directamente")
            print("   Debería delegar a FormationManager")
    
    return True

def verify_flow():
    """Verificar el flujo completo"""
    print("\n3️⃣ VERIFICACIÓN DEL FLUJO")
    print("-" * 40)
    
    # Test de importación
    try:
        from trajectory_hub.control.managers.formation_manager import FormationManager
        fm = FormationManager()
        
        if hasattr(fm, 'formations') and 'sphere' in fm.formations:
            print("✅ FormationManager.formations contiene 'sphere'")
            
            # Test del método
            if hasattr(fm, '_create_sphere_formation'):
                # Probar con 5 fuentes
                test_ids = ['src1', 'src2', 'src3', 'src4', 'src5']
                positions = fm._create_sphere_formation(test_ids)
                
                if len(positions) == 5:
                    print("✅ _create_sphere_formation funciona")
                    print(f"   Ejemplo: {list(positions.items())[0]}")
                else:
                    print("❌ _create_sphere_formation no devuelve posiciones correctas")
        else:
            print("❌ FormationManager no tiene sphere en formations")
            
    except Exception as e:
        print(f"❌ Error al verificar: {e}")
    
    print("\n" + "="*60)
    print("📊 RESUMEN:")
    print("- FormationManager: Implementa cálculo 3D de sphere")
    print("- CommandProcessor: Debe usar FormationManager.create_formation()")
    print("- CLI: Muestra sphere en el menú")
    
    print("\n🧪 TEST MANUAL:")
    print("1. python main.py --interactive")
    print("2. Crear macro → Seleccionar sphere")
    print("3. Deberías ver posiciones 3D (x, y, z) no solo en plano XY")

if __name__ == "__main__":
    implement_sphere_complete()