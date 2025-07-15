#!/usr/bin/env python3
"""
🎯 FASE 1: MIGRACIÓN DE CONCENTRACIÓN (CORREGIDO)
✅ Modifica ConcentrationComponent en motion_components.py
"""

import os
import shutil
import json
from datetime import datetime
import re

print("=" * 80)
print("🎯 FASE 1: MIGRACIÓN DE ConcentrationComponent")
print("=" * 80)

class Phase1ImplementationFixed:
    def __init__(self):
        self.backup_dir = f"phase1_backups_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.backup_dir, exist_ok=True)
        self.changes = []
        
    def analyze_concentration_component(self):
        """Analizar la estructura actual de ConcentrationComponent"""
        print("\n🔍 ANALIZANDO ConcentrationComponent...")
        
        motion_file = "trajectory_hub/core/motion_components.py"
        
        with open(motion_file, 'r') as f:
            content = f.read()
        
        # Extraer la clase ConcentrationComponent
        class_match = re.search(r'class ConcentrationComponent.*?(?=\nclass|\Z)', content, re.DOTALL)
        
        if class_match:
            class_content = class_match.group(0)
            
            # Buscar métodos
            methods = re.findall(r'def (\w+)\(self', class_content)
            print(f"✅ Métodos encontrados: {', '.join(methods)}")
            
            # Verificar si tiene apply
            has_apply = 'apply' in methods
            print(f"✅ Tiene método apply(): {has_apply}")
            
            # Verificar dependencias
            has_is_dependency = 'individual_trajectory' in class_content
            if has_is_dependency:
                print("⚠️ Detectada dependencia de individual_trajectory")
            
            # Guardar para referencia
            analysis_file = os.path.join(self.backup_dir, "concentration_analysis.txt")
            with open(analysis_file, 'w') as f:
                f.write(f"ConcentrationComponent Analysis\n")
                f.write(f"=" * 50 + "\n")
                f.write(f"Methods: {methods}\n")
                f.write(f"Has apply: {has_apply}\n")
                f.write(f"IS dependency: {has_is_dependency}\n")
                f.write(f"\nClass content preview:\n")
                f.write(class_content[:1000] + "...\n")
            
            return True
        
        return False
    
    def setup_config(self):
        """Configurar el sistema para modo dual"""
        print("\n1️⃣ CONFIGURANDO MODO DUAL...")
        
        config_dir = "trajectory_hub/config"
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, "parallel_config.json")
        
        config = {
            "PARALLEL_MODE": False,
            "COMPONENTS_MIGRATED": [],
            "CONCENTRATION_DUAL_MODE": False,  # Empieza desactivado
            "SAFE_MODE": True,
            "LOG_DELTAS": True,
            "PHASE": 1,
            "ROLLBACK_POINTS": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "backup_dir": self.backup_dir,
                    "component": "ConcentrationComponent"
                }
            ]
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuración creada: {config_path}")
        return config_path
    
    def create_compatibility_layer(self):
        """Crear capa de compatibilidad mejorada"""
        print("\n2️⃣ CREANDO CAPA DE COMPATIBILIDAD...")
        
        compat_code = '''"""
Capa de compatibilidad para transición gradual - Phase 1
"""
import json
import os
import numpy as np

class CompatibilityManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.config_path = os.path.join("trajectory_hub", "config", "parallel_config.json")
            self.load_config()
            self.initialized = True
            self.delta_storage = {}  # Store deltas per source
    
    def load_config(self):
        """Load current configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"PARALLEL_MODE": False, "CONCENTRATION_DUAL_MODE": False}
    
    def reload_config(self):
        """Force reload configuration"""
        self.load_config()
    
    def is_concentration_dual_mode(self):
        """Check if concentration should use dual mode"""
        return self.config.get("CONCENTRATION_DUAL_MODE", False)
    
    def store_delta(self, source_id, component_name, position_delta, orientation_delta=None):
        """Store delta for later application"""
        if source_id not in self.delta_storage:
            self.delta_storage[source_id] = []
        
        self.delta_storage[source_id].append({
            'component': component_name,
            'position': position_delta,
            'orientation': orientation_delta
        })
        
        if self.config.get("LOG_DELTAS", False):
            print(f"  [DELTA] Source {source_id} - {component_name}: pos_delta={position_delta}")
    
    def get_deltas(self, source_id):
        """Get all stored deltas for a source"""
        return self.delta_storage.get(source_id, [])
    
    def clear_deltas(self, source_id=None):
        """Clear stored deltas"""
        if source_id is None:
            self.delta_storage.clear()
        elif source_id in self.delta_storage:
            del self.delta_storage[source_id]
    
    def apply_deltas(self, motion):
        """Apply all accumulated deltas to motion"""
        source_id = getattr(motion, 'source_id', 0)
        deltas = self.get_deltas(source_id)
        
        for delta_info in deltas:
            if delta_info['position'] is not None:
                motion.state.position += delta_info['position']
            if delta_info['orientation'] is not None:
                motion.state.orientation += delta_info['orientation']
        
        # Clear after applying
        self.clear_deltas(source_id)

# Global instance
compat = CompatibilityManager()
'''
        
        compat_path = "trajectory_hub/core/compatibility.py"
        with open(compat_path, 'w') as f:
            f.write(compat_code)
        
        print(f"✅ Compatibilidad creada: {compat_path}")
        self.changes.append(("created", compat_path))
        return compat_path
    
    def modify_concentration_component(self):
        """Modificar ConcentrationComponent para modo dual"""
        print("\n3️⃣ MODIFICANDO ConcentrationComponent...")
        
        motion_file = "trajectory_hub/core/motion_components.py"
        
        # Backup
        backup_path = os.path.join(self.backup_dir, "motion_components.py")
        shutil.copy2(motion_file, backup_path)
        print(f"✅ Backup creado: {backup_path}")
        
        # Leer contenido
        with open(motion_file, 'r') as f:
            content = f.read()
        
        # Agregar import de compatibility si no existe
        if 'from trajectory_hub.core.compatibility import compat' not in content:
            # Buscar dónde insertar
            lines = content.split('\n')
            insert_idx = 0
            
            for i, line in enumerate(lines):
                if line.startswith('from trajectory_hub') or (line.startswith('from') and 'trajectory_hub' in line):
                    insert_idx = i + 1
                elif line.startswith('import') and insert_idx == 0:
                    insert_idx = i + 1
            
            lines.insert(insert_idx, 'from trajectory_hub.core.compatibility import compat')
            content = '\n'.join(lines)
            print("✅ Import de compatibility agregado")
        
        # Buscar y modificar el método apply de ConcentrationComponent
        # Primero encontrar la clase
        class_pattern = r'(class ConcentrationComponent.*?)(def apply\(self.*?\):)(.*?)((?=\n    def|\n\nclass|\Z))'
        match = re.search(class_pattern, content, re.DOTALL)
        
        if match:
            # Extraer el cuerpo actual del método apply
            original_apply_body = match.group(3)
            
            # Crear nueva versión con soporte dual
            new_apply = '''
    def apply(self, motion):
        """Apply concentration with dual mode support"""
        if not self.enabled:
            return
        
        # Check if we're in dual mode
        if compat.is_concentration_dual_mode():
            # DUAL MODE: Calculate and store delta
            import numpy as np
            
            # Save initial position
            initial_pos = motion.state.position.copy()
            
            # Calculate concentration effect using existing logic
            target_position = self._calculate_target_position(motion)
            
            if target_position is not None:
                # Calculate vector from current to target
                direction = target_position - initial_pos
                distance = np.linalg.norm(direction)
                
                if distance > 0.001:  # Avoid division by zero
                    # Apply factor and curve
                    strength = self._apply_curve(self.factor)
                    
                    # Calculate delta (how much to move towards target)
                    delta = direction * strength * self.speed
                    
                    # Store delta instead of applying directly
                    compat.store_delta(motion.source_id, 'concentration', delta)
                    
                    # Log for debugging
                    if compat.config.get("LOG_DELTAS", False):
                        print(f"    Concentration delta calculated: {np.linalg.norm(delta):.3f}")
            
            return  # Don't modify position directly in dual mode
        
        # ORIGINAL MODE: Direct modification (existing code)''' + original_apply_body
            
            # Replace the apply method
            new_content = content.replace(
                match.group(0),
                match.group(1) + match.group(2) + new_apply + match.group(4)
            )
            
            # Also need to ensure _calculate_target_position exists
            if '_calculate_target_position' not in new_content:
                # Add helper method
                helper_method = '''
    def _calculate_target_position(self, motion):
        """Calculate target position for concentration"""
        if self.mode == ConcentrationMode.FIXED:
            return self.target
        elif hasattr(self, '_ms_trajectory_position') and self._ms_trajectory_position is not None:
            return self._ms_trajectory_position
        else:
            return self.target
    
    def _apply_curve(self, factor):
        """Apply concentration curve to factor"""
        if self.curve == ConcentrationCurve.LINEAR:
            return factor
        elif self.curve == ConcentrationCurve.SMOOTH:
            return factor * factor * (3 - 2 * factor)
        elif self.curve == ConcentrationCurve.EXPONENTIAL:
            return 1 - np.exp(-3 * factor)
        else:
            return factor
'''
                # Insert before the last method or at the end of class
                class_end = re.search(r'(class ConcentrationComponent.*?)((?=\nclass|\Z))', new_content, re.DOTALL)
                if class_end:
                    new_content = new_content.replace(
                        class_end.group(0),
                        class_end.group(1) + helper_method + class_end.group(2)
                    )
            
            # Ensure numpy is imported
            if 'import numpy as np' not in new_content:
                new_content = 'import numpy as np\n' + new_content
            
            # Save modified file
            with open(motion_file, 'w') as f:
                f.write(new_content)
            
            print("✅ ConcentrationComponent modificado para modo dual")
            self.changes.append(("modified", motion_file))
            
            return True
        else:
            print("❌ No se encontró el método apply en ConcentrationComponent")
            return False
    
    def create_test_suite(self):
        """Test específico para ConcentrationComponent"""
        print("\n4️⃣ CREANDO TEST DE VALIDACIÓN...")
        
        test_code = '''#!/usr/bin/env python3
"""
🧪 TEST FASE 1: ConcentrationComponent Modo Dual
"""

import sys
import numpy as np
import json

sys.path.insert(0, 'trajectory_hub')

from trajectory_hub.core.compatibility import compat
from trajectory_hub.core.motion_components import ConcentrationComponent, ConcentrationMode, MotionState

def test_concentration_modes():
    """Test concentration in both modes"""
    print("\\n🧪 TEST: ConcentrationComponent MODO DUAL")
    print("=" * 60)
    
    results = {}
    
    try:
        # Create mock motion object
        class MockMotion:
            def __init__(self, source_id=0):
                self.source_id = source_id
                self.state = MotionState()
                self.state.position = np.array([5.0, 0.0, 0.0])
        
        # Test 1: Original Mode
        print("\\n1️⃣ TEST MODO ORIGINAL...")
        
        # Ensure original mode
        compat.config['CONCENTRATION_DUAL_MODE'] = False
        
        motion = MockMotion(0)
        concentration = ConcentrationComponent()
        concentration.enabled = True
        concentration.factor = 1.0  # Max concentration
        concentration.target = np.array([0.0, 0.0, 0.0])
        concentration.speed = 0.1
        
        initial_pos = motion.state.position.copy()
        concentration.apply(motion)
        final_pos = motion.state.position
        
        moved = not np.allclose(initial_pos, final_pos)
        results['original_mode'] = "✅ PASS" if moved else "❌ FAIL"
        
        print(f"   Initial: {initial_pos}")
        print(f"   Final: {final_pos}")
        print(f"   Result: {results['original_mode']}")
        
        # Test 2: Dual Mode
        print("\\n2️⃣ TEST MODO DUAL...")
        
        # Activate dual mode
        compat.config['CONCENTRATION_DUAL_MODE'] = True
        
        motion2 = MockMotion(1)
        compat.clear_deltas()  # Clear any previous deltas
        
        initial_pos2 = motion2.state.position.copy()
        concentration.apply(motion2)
        
        # In dual mode, position shouldn't change immediately
        immediate_change = not np.allclose(motion2.state.position, initial_pos2)
        
        # But delta should be stored
        deltas = compat.get_deltas(1)
        has_delta = len(deltas) > 0
        
        results['dual_mode_no_immediate'] = "✅ PASS" if not immediate_change else "❌ FAIL"
        results['dual_mode_stores_delta'] = "✅ PASS" if has_delta else "❌ FAIL"
        
        print(f"   Position unchanged: {not immediate_change}")
        print(f"   Delta stored: {has_delta}")
        if has_delta:
            print(f"   Delta value: {deltas[0]['position']}")
        
        # Test 3: Independence from IS
        print("\\n3️⃣ TEST INDEPENDENCIA DE IS...")
        
        # This tests that concentration works without any IS reference
        motion3 = MockMotion(2)
        concentration.enabled = True
        
        # Should work in both modes without IS
        works_without_is = True
        try:
            concentration.apply(motion3)
        except Exception as e:
            works_without_is = False
            print(f"   Error: {e}")
        
        results['independent_from_is'] = "✅ PASS" if works_without_is else "❌ FAIL"
        
    except Exception as e:
        print(f"\\n❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\\n" + "=" * 60)
    print("RESUMEN DE TESTS:")
    
    passed = sum(1 for r in results.values() if "PASS" in str(r))
    total = len(results)
    
    for test, result in results.items():
        print(f"  {test}: {result}")
    
    print(f"\\nRESULTADO: {passed}/{total} tests pasados")
    
    # Save results
    with open('phase1_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'passed': passed,
            'total': total
        }, f, indent=2)
    
    return passed == total

if __name__ == "__main__":
    from datetime import datetime
    
    success = test_concentration_modes()
    
    if success:
        print("\\n✅ FASE 1 VALIDADA EXITOSAMENTE")
        print("ConcentrationComponent funciona en ambos modos")
        print("\\nPRÓXIMOS PASOS:")
        print("1. Activar modo dual en el controlador")
        print("2. Probar con opción 31 del menú")
        print("3. Si todo OK, proceder a Fase 2")
    else:
        print("\\n❌ FASE 1 REQUIERE REVISIÓN")
        print("Revisa los errores antes de continuar")
'''
        
        test_path = "test_phase1_concentration_fixed.py"
        with open(test_path, 'w') as f:
            f.write(test_code)
        os.chmod(test_path, 0o755)
        
        print(f"✅ Test creado: {test_path}")
        return test_path

# EJECUTAR
print("\n" + "=" * 80)
print("🚀 EJECUTANDO FASE 1 (CORREGIDA)")
print("=" * 80)

phase1 = Phase1ImplementationFixed()

# Analizar primero
if phase1.analyze_concentration_component():
    # Setup
    phase1.setup_config()
    
    # Compatibility
    phase1.create_compatibility_layer()
    
    # Modify
    success = phase1.modify_concentration_component()
    
    # Test
    test_path = phase1.create_test_suite()
    
    if success:
        print("\n" + "=" * 80)
        print("✅ FASE 1 IMPLEMENTADA CORRECTAMENTE")
        print("=" * 80)
        print("""
CAMBIOS REALIZADOS:
1. ConcentrationComponent analizado y respaldado
2. Modo dual implementado en el método apply()
3. Sistema de deltas configurado
4. Tests de validación listos

PRÓXIMOS PASOS:
1. python test_phase1_concentration_fixed.py
2. Verificar que ambos modos funcionan
3. Si todo OK, activar gradualmente en producción

⚠️ IMPORTANTE: El modo dual está DESACTIVADO por defecto
""")
    else:
        print("\n❌ Error al modificar ConcentrationComponent")
else:
    print("\n❌ No se pudo analizar ConcentrationComponent")

print("=" * 80)