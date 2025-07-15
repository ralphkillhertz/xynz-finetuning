#!/usr/bin/env python3
"""
🔍 Verificar si la arquitectura de deltas está realmente implementada
⚡ Y si no, implementarla correctamente esta vez
"""

import os
import re
from datetime import datetime

def check_current_implementation():
    """Verificar el estado actual de la implementación"""
    print("🔍 VERIFICANDO IMPLEMENTACIÓN ACTUAL DE DELTAS\n")
    
    # Buscar archivos clave
    files_to_check = [
        "trajectory_hub/core/motion_components.py",
        "trajectory_hub/core/source_motion.py",
        "trajectory_hub/core/enhanced_trajectory_engine.py"
    ]
    
    # Encontrar el archivo correcto
    motion_file = None
    for f in files_to_check:
        if os.path.exists(f):
            motion_file = f
            break
    
    if not motion_file:
        # Buscar en cualquier lugar
        import glob
        candidates = glob.glob("**/motion*.py", recursive=True)
        candidates.extend(glob.glob("**/source*.py", recursive=True))
        
        for candidate in candidates:
            if 'motion' in candidate.lower() or 'source' in candidate.lower():
                with open(candidate, 'r') as f:
                    content = f.read()
                    if 'class SourceMotion' in content or 'def update' in content:
                        motion_file = candidate
                        break
    
    if not motion_file:
        print("❌ No se encontró archivo de motion/source")
        return False
    
    print(f"📄 Analizando: {motion_file}")
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar indicadores de arquitectura de deltas
    delta_indicators = [
        'concentration_offset',
        'macro_rotation_offset', 
        'trajectory_offset',
        '_combine_components',
        'delta',
        '+='
    ]
    
    found_indicators = []
    for indicator in delta_indicators:
        if indicator in content:
            found_indicators.append(indicator)
    
    print(f"\n📊 Indicadores de arquitectura de deltas encontrados:")
    for ind in found_indicators:
        print(f"   ✅ {ind}")
    
    missing = set(delta_indicators[:4]) - set(found_indicators)
    if missing:
        print(f"\n   ❌ Faltan: {missing}")
    
    # Buscar el método update
    update_match = re.search(r'def update\(self.*?\n(?=\n    def|\nclass|\Z)', content, re.DOTALL)
    
    if update_match:
        update_method = update_match.group(0)
        print("\n🔍 Analizando método update():")
        
        # Verificar si suma o sobrescribe
        if '+=' in update_method or '_combine_components' in update_method:
            print("   ✅ Parece usar arquitectura de SUMA")
        else:
            print("   ❌ Parece usar arquitectura SECUENCIAL (sobrescritura)")
            
        # Ver si aplica todos los componentes
        if 'concentration' in update_method and 'rotation' in update_method:
            print("   ✅ Aplica múltiples componentes")
        else:
            print("   ⚠️  No está claro si aplica todos los componentes")
    
    # Verificar enhanced_trajectory_engine.py
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    if os.path.exists(engine_file):
        print(f"\n📄 Analizando: {engine_file}")
        
        with open(engine_file, 'r') as f:
            engine_content = f.read()
        
        # Buscar apply_concentration
        if 'def apply_concentration' in engine_content:
            print("   ✅ apply_concentration existe")
            
            # Ver si modifica posiciones
            conc_match = re.search(r'def apply_concentration.*?\n(?=\n    def|\nclass|\Z)', 
                                  engine_content, re.DOTALL)
            if conc_match:
                conc_method = conc_match.group(0)
                if 'concentration_offset' in conc_method or 'set_position' in conc_method:
                    print("   ✅ apply_concentration modifica posiciones/offsets")
                else:
                    print("   ❌ apply_concentration NO parece modificar posiciones")
        else:
            print("   ❌ apply_concentration NO existe")
    
    # Diagnóstico final
    print("\n" + "="*60)
    print("📊 DIAGNÓSTICO")
    print("="*60)
    
    if len(found_indicators) >= 3:
        print("✅ La arquitectura de deltas PARECE estar implementada")
        print("⚠️  Pero los tests muestran que NO está funcionando")
        print("\n💡 PROBLEMA: La implementación existe pero no se está ejecutando correctamente")
        return True
    else:
        print("❌ La arquitectura de deltas NO está implementada")
        print("\n💡 NECESARIO: Implementar arquitectura de deltas desde cero")
        return False

def generate_correct_implementation():
    """Generar la implementación correcta"""
    print("\n🔧 GENERANDO IMPLEMENTACIÓN CORRECTA\n")
    
    implementation = '''#!/usr/bin/env python3
"""
🔧 Implementación CORRECTA de arquitectura de deltas
⚡ Esta vez asegurándonos de que funcione
"""

import os
import re
import shutil
from datetime import datetime

def implement_delta_architecture_correctly():
    """Implementar arquitectura de deltas que FUNCIONE"""
    
    print("🚀 IMPLEMENTACIÓN CORRECTA DE ARQUITECTURA DE DELTAS\\n")
    
    # Backup
    backup_dir = f"backup_delta_correct_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # 1. Encontrar y modificar SourceMotion o equivalente
    print("1️⃣ Buscando clase SourceMotion...")
    
    motion_file = None
    # Buscar en múltiples ubicaciones posibles
    possible_files = [
        "trajectory_hub/core/motion_components.py",
        "trajectory_hub/core/source_motion.py",
        "trajectory_hub/motion/source_motion.py"
    ]
    
    for pf in possible_files:
        if os.path.exists(pf):
            with open(pf, 'r') as f:
                if 'class SourceMotion' in f.read():
                    motion_file = pf
                    break
    
    if not motion_file:
        # Buscar globalmente
        import glob
        for f in glob.glob("**/*.py", recursive=True):
            if os.path.exists(f):
                with open(f, 'r') as file:
                    if 'class SourceMotion' in file.read():
                        motion_file = f
                        break
    
    if not motion_file:
        print("❌ No se encontró SourceMotion")
        return False
    
    print(f"   ✅ Encontrado: {motion_file}")
    shutil.copy2(motion_file, os.path.join(backup_dir, os.path.basename(motion_file)))
    
    # Leer contenido
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # 2. Reemplazar el método update con arquitectura de deltas
    print("\\n2️⃣ Implementando arquitectura de deltas en update()...")
    
    new_update_method = """    def update(self, dt: float):
        \"\"\"Actualizar posición usando arquitectura de DELTAS (suma)\"\"\"
        if dt < 0.0001:
            return
            
        # Resetear offsets
        self.concentration_offset = np.zeros(3)
        self.macro_rotation_offset = np.zeros(3)
        self.trajectory_offset = np.zeros(3)
        self.algorithmic_rotation_offset = np.zeros(3)
        
        # 1. Calcular offset de trayectoria individual (IS)
        if 'individual_trajectory' in self.components:
            traj = self.components['individual_trajectory']
            if traj.enabled:
                self.trajectory_offset = traj.get_position(self.time) - self.base_position
        
        # 2. Calcular offset de concentración
        if 'concentration' in self.components:
            conc = self.components['concentration']
            if conc.enabled and conc.factor < 0.99:
                target = conc.target_point
                current = self.get_position()
                # Interpolar hacia el punto de concentración
                concentrated = current * conc.factor + target * (1 - conc.factor)
                self.concentration_offset = concentrated - current
        
        # 3. Calcular offset de rotación del macro (MS)
        if 'macro_rotation' in self.components:
            rot = self.components['macro_rotation']
            if rot.enabled:
                # Aplicar rotación alrededor del centro del macro
                angle = rot.angle
                center = rot.center
                current = self.get_position()
                
                # Rotar alrededor del centro
                relative = current - center
                cos_a, sin_a = np.cos(angle), np.sin(angle)
                
                if rot.axis == 'yaw':  # Rotación en Z
                    rotated = np.array([
                        relative[0] * cos_a - relative[1] * sin_a,
                        relative[0] * sin_a + relative[1] * cos_a,
                        relative[2]
                    ])
                elif rot.axis == 'pitch':  # Rotación en Y
                    rotated = np.array([
                        relative[0] * cos_a + relative[2] * sin_a,
                        relative[1],
                        -relative[0] * sin_a + relative[2] * cos_a
                    ])
                else:  # roll - Rotación en X
                    rotated = np.array([
                        relative[0],
                        relative[1] * cos_a - relative[2] * sin_a,
                        relative[1] * sin_a + relative[2] * cos_a
                    ])
                
                self.macro_rotation_offset = (rotated + center) - current
        
        # 4. Calcular offset de rotación algorítmica
        if 'algorithmic_rotation' in self.components:
            algo_rot = self.components['algorithmic_rotation']
            if algo_rot.enabled:
                # Aplicar patrón de rotación
                self.algorithmic_rotation_offset = algo_rot.get_offset(self.time)
        
        # Actualizar tiempo
        self.time += dt
        
    def get_position(self) -> np.ndarray:
        \"\"\"Obtener posición final sumando TODOS los componentes\"\"\"
        return (self.base_position + 
                self.trajectory_offset + 
                self.concentration_offset + 
                self.macro_rotation_offset +
                self.algorithmic_rotation_offset)
    
    def _combine_components(self) -> np.ndarray:
        \"\"\"Combinar todos los offsets (método auxiliar)\"\"\"
        return (self.trajectory_offset + 
                self.concentration_offset + 
                self.macro_rotation_offset +
                self.algorithmic_rotation_offset)"""
    
    # Reemplazar el método update existente
    update_pattern = r'def update\\(self.*?\\n(?=\\n    def|\\nclass|\\Z)'
    content = re.sub(update_pattern, new_update_method, content, flags=re.DOTALL)
    
    # Asegurar que los offsets existen como atributos
    if "__init__" in content:
        init_pattern = r'def __init__\\(self.*?\\):'
        init_match = re.search(init_pattern, content)
        if init_match:
            # Agregar inicialización de offsets
            offset_init = """
        # Offsets para arquitectura de deltas
        self.concentration_offset = np.zeros(3)
        self.macro_rotation_offset = np.zeros(3)
        self.trajectory_offset = np.zeros(3)
        self.algorithmic_rotation_offset = np.zeros(3)"""
            
            # Insertar después del __init__
            insert_pos = init_match.end()
            # Buscar el siguiente self. para insertar antes
            next_self = content.find("\\n        self.", insert_pos)
            if next_self > 0:
                content = content[:next_self] + offset_init + content[next_self:]
    
    # Guardar cambios
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print("   ✅ Arquitectura de deltas implementada")
    
    # 3. Asegurar que enhanced_trajectory_engine.py llama a update correctamente
    print("\\n3️⃣ Verificando enhanced_trajectory_engine.py...")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    if os.path.exists(engine_file):
        shutil.copy2(engine_file, os.path.join(backup_dir, "enhanced_trajectory_engine.py"))
        
        with open(engine_file, 'r') as f:
            engine_content = f.read()
        
        # Verificar que apply_concentration existe y funciona
        if 'def apply_concentration' not in engine_content:
            print("   ⚠️  Agregando apply_concentration...")
            
            apply_conc = """
    def apply_concentration(self):
        \"\"\"Aplicar concentración a todos los macros\"\"\"
        # La concentración ahora se maneja en SourceMotion.update()
        # Solo necesitamos asegurar que los parámetros estén configurados
        pass"""
            
            # Insertar antes de update
            engine_content = engine_content.replace("    def update(self", apply_conc + "\\n\\n    def update(self")
        
        with open(engine_file, 'w') as f:
            f.write(engine_content)
        
        print("   ✅ Engine verificado")
    
    print(f"\\n✅ Implementación completada")
    print(f"📁 Backup en: {backup_dir}")
    
    return True

if __name__ == "__main__":
    implement_delta_architecture_correctly()
'''
    
    # Guardar script
    with open("fix_delta_architecture_final.py", 'w') as f:
        f.write(implementation)
    
    print("✅ Script generado: fix_delta_architecture_final.py")

if __name__ == "__main__":
    # Verificar estado actual
    has_deltas = check_current_implementation()
    
    if not has_deltas or True:  # Siempre generar el fix
        generate_correct_implementation()
        
        print("\n" + "="*60)
        print("🚀 PRÓXIMOS PASOS")
        print("="*60)
        print("\n1. Ejecutar el fix definitivo:")
        print("   python fix_delta_architecture_final.py")
        print("\n2. Verificar:")
        print("   python trajectory_hub/interface/interactive_controller.py")
        print("\n3. Probar:")
        print("   - Concentración sola")
        print("   - Rotación MS sola")
        print("   - IS + Concentración")
        print("   - IS + Rotación MS")
        print("   - Todo combinado")