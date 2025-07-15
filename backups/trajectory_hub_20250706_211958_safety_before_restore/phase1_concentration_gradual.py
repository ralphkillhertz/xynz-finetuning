#!/usr/bin/env python3
"""
🎯 FASE 1: MIGRACIÓN GRADUAL - CONCENTRACIÓN
✅ Primer componente a migrar (menos riesgo)
"""

import os
import shutil
import json
from datetime import datetime
import re

print("=" * 80)
print("🎯 FASE 1: MIGRACIÓN DE CONCENTRACIÓN")
print("=" * 80)

class Phase1Implementation:
    def __init__(self):
        self.backup_dir = f"phase1_backups_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.backup_dir, exist_ok=True)
        self.changes = []
        
    def setup_config(self):
        """Configurar el sistema para modo dual"""
        print("\n1️⃣ CONFIGURANDO MODO DUAL...")
        
        # Crear configuración si no existe
        config_dir = "trajectory_hub/config"
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, "parallel_config.json")
        
        config = {
            "PARALLEL_MODE": False,  # Empieza desactivado
            "COMPONENTS_MIGRATED": [],
            "PHASE": 1,
            "CONCENTRATION_DUAL_MODE": True,  # Activar modo dual para concentration
            "SAFE_MODE": True,
            "LOG_DELTAS": True,  # Para debug
            "ROLLBACK_POINTS": []
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuración creada: {config_path}")
        return config_path
    
    def create_compatibility_layer(self):
        """Crear capa de compatibilidad minimalista"""
        print("\n2️⃣ CREANDO CAPA DE COMPATIBILIDAD...")
        
        compat_code = '''"""
Capa de compatibilidad para transición gradual
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
    
    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"PARALLEL_MODE": False, "CONCENTRATION_DUAL_MODE": False}
    
    def is_component_in_dual_mode(self, component_name):
        """Check if component should use dual mode"""
        return self.config.get(f"{component_name.upper()}_DUAL_MODE", False)
    
    def log_delta(self, component_name, delta_pos, delta_ori=None):
        """Log deltas for debugging"""
        if self.config.get("LOG_DELTAS", False):
            print(f"  [DELTA] {component_name}: pos={delta_pos}")

# Global instance
compat = CompatibilityManager()
'''
        
        compat_path = "trajectory_hub/core/compatibility.py"
        os.makedirs(os.path.dirname(compat_path), exist_ok=True)
        
        with open(compat_path, 'w') as f:
            f.write(compat_code)
        
        print(f"✅ Compatibilidad creada: {compat_path}")
        self.changes.append(("created", compat_path))
        
        return compat_path
    
    def modify_concentration_for_dual_mode(self):
        """Modificar concentration para soportar modo dual"""
        print("\n3️⃣ MODIFICANDO CONCENTRATION PARA MODO DUAL...")
        
        # Buscar archivo de concentration
        concentration_file = None
        for root, dirs, files in os.walk("trajectory_hub"):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                        if 'class Concentration' in content and 'apply' in content:
                            concentration_file = filepath
                            break
                    except:
                        pass
            if concentration_file:
                break
        
        if not concentration_file:
            print("❌ No se encontró archivo de Concentration")
            return False
        
        print(f"✅ Encontrado: {concentration_file}")
        
        # Backup
        backup_path = os.path.join(self.backup_dir, os.path.basename(concentration_file))
        shutil.copy2(concentration_file, backup_path)
        self.changes.append(("backup", concentration_file, backup_path))
        
        # Leer contenido
        with open(concentration_file, 'r') as f:
            content = f.read()
        
        # Agregar import de compatibility
        if 'from trajectory_hub.core.compatibility import compat' not in content:
            import_line = "from trajectory_hub.core.compatibility import compat\n"
            
            # Buscar dónde insertar
            lines = content.split('\n')
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_idx = i + 1
            
            lines.insert(insert_idx, import_line)
            content = '\n'.join(lines)
        
        # Modificar método apply para modo dual
        apply_pattern = r'(def apply\(self.*?\):)(.*?)((?=\n\s{0,4}def|\nclass|\Z))'
        match = re.search(apply_pattern, content, re.DOTALL)
        
        if match:
            original_body = match.group(2)
            
            # Crear versión dual del método
            dual_apply = f'''
    def apply(self, motion):
        """Apply concentration with dual mode support"""
        if not self.enabled:
            return
        
        # Check if we're in dual mode
        if compat.is_component_in_dual_mode('concentration'):
            # DUAL MODE: Calculate delta instead of direct modification
            import numpy as np
            
            # Save initial position
            initial_pos = motion.state.position.copy()
            
            # Calculate concentration effect
            concentrated_pos = self._apply_concentration(motion)
            
            # Calculate delta
            delta = concentrated_pos - initial_pos
            
            # In dual mode, we store the delta for later summation
            if not hasattr(motion, '_position_deltas'):
                motion._position_deltas = []
            
            motion._position_deltas.append(('concentration', delta))
            compat.log_delta('concentration', delta)
            
            # Don't modify position directly in dual mode
            return
        
        # ORIGINAL MODE: Direct modification
{original_body}'''
            
            # Replace apply method
            new_content = content.replace(match.group(0), match.group(1) + dual_apply + match.group(3))
            
            # Save modified file
            with open(concentration_file, 'w') as f:
                f.write(new_content)
            
            print("✅ Concentration modificado para modo dual")
            self.changes.append(("modified", concentration_file))
            
            return True
        
        return False
    
    def create_test_for_phase1(self):
        """Test específico para validar fase 1"""
        print("\n4️⃣ CREANDO TEST DE VALIDACIÓN FASE 1...")
        
        test_code = '''#!/usr/bin/env python3
"""
🧪 TEST FASE 1: Validación de Concentration en modo dual
"""

import sys
import numpy as np
import json

sys.path.insert(0, 'trajectory_hub')

from trajectory_hub.core.compatibility import compat

def test_concentration_dual_mode():
    """Test que concentration funciona en ambos modos"""
    print("\\n🧪 TEST: CONCENTRATION MODO DUAL")
    print("-" * 60)
    
    results = {}
    
    try:
        # Test 1: Modo original
        print("\\n1️⃣ Probando modo ORIGINAL...")
        
        # Asegurar modo original
        compat.config['CONCENTRATION_DUAL_MODE'] = False
        
        from trajectory_hub.interface.interactive_controller import InteractiveController
        controller = InteractiveController()
        
        if 'concentration' in controller.engine.modules:
            conc = controller.engine.modules['concentration']
            conc.enabled = True
            conc.factor = 0.0  # Max concentration
            
            # Get initial positions
            initial_pos = controller.engine._positions[0].copy()
            
            # Update
            controller.engine.update()
            
            # Check movement
            final_pos = controller.engine._positions[0]
            moved = not np.allclose(initial_pos, final_pos)
            
            results['original_mode'] = "✅ PASS" if moved else "❌ FAIL - No movement"
            print(f"   Posición inicial: {initial_pos}")
            print(f"   Posición final: {final_pos}")
            print(f"   Resultado: {results['original_mode']}")
        
        # Test 2: Modo dual
        print("\\n2️⃣ Probando modo DUAL...")
        
        # Activar modo dual
        compat.config['CONCENTRATION_DUAL_MODE'] = True
        compat.load_config()  # Recargar
        
        # Reset positions
        controller = InteractiveController()
        
        if 'concentration' in controller.engine.modules:
            conc = controller.engine.modules['concentration']
            conc.enabled = True
            conc.factor = 0.0
            
            # Check that deltas are being calculated
            motion = controller.engine._source_motions[0]
            
            # Clear any previous deltas
            if hasattr(motion, '_position_deltas'):
                motion._position_deltas = []
            
            # Apply concentration
            conc.apply(motion)
            
            # Check deltas
            has_deltas = hasattr(motion, '_position_deltas') and len(motion._position_deltas) > 0
            
            results['dual_mode_deltas'] = "✅ PASS" if has_deltas else "❌ FAIL - No deltas"
            
            if has_deltas:
                print(f"   Deltas calculados: {len(motion._position_deltas)}")
                for name, delta in motion._position_deltas:
                    print(f"     - {name}: {delta}")
        
        # Test 3: No interferencia con IS
        print("\\n3️⃣ Probando independencia de IS...")
        
        # Desactivar IS, activar concentration
        if 'individual_trajectory' in controller.engine.modules:
            controller.engine.modules['individual_trajectory'].enabled = False
        
        conc.enabled = True
        
        # Should work without IS
        initial = controller.engine._positions[0].copy()
        controller.engine.update()
        final = controller.engine._positions[0]
        
        works_without_is = not np.allclose(initial, final)
        results['independent_of_is'] = "✅ PASS" if works_without_is else "❌ FAIL"
        
    except Exception as e:
        print(f"\\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Resumen
    print("\\n" + "=" * 60)
    print("RESUMEN DE TESTS:")
    
    passed = sum(1 for r in results.values() if "PASS" in str(r))
    total = len(results)
    
    for test, result in results.items():
        print(f"  {test}: {result}")
    
    print(f"\\nRESULTADO: {passed}/{total} tests pasados")
    
    return passed == total

if __name__ == "__main__":
    success = test_concentration_dual_mode()
    
    if success:
        print("\\n✅ FASE 1 COMPLETADA CON ÉXITO")
        print("Concentration funciona en modo dual")
        print("Puedes proceder a la siguiente fase")
    else:
        print("\\n❌ FASE 1 REQUIERE AJUSTES")
        print("Revisa los errores antes de continuar")
'''
        
        test_path = "test_phase1_concentration.py"
        with open(test_path, 'w') as f:
            f.write(test_code)
        os.chmod(test_path, 0o755)
        
        print(f"✅ Test creado: {test_path}")
        return test_path
    
    def create_rollback_phase1(self):
        """Script específico para rollback de fase 1"""
        print("\n5️⃣ CREANDO ROLLBACK DE FASE 1...")
        
        rollback_code = f'''#!/usr/bin/env python3
"""
⏮️ ROLLBACK FASE 1
"""

import os
import shutil

print("⏮️ Revirtiendo cambios de Fase 1...")

# Restaurar desde backups
backup_dir = "{self.backup_dir}"

for file in os.listdir(backup_dir):
    if file.endswith('.py'):
        src = os.path.join(backup_dir, file)
        # Encontrar destino original
        for root, dirs, files in os.walk("trajectory_hub"):
            if file in files:
                dst = os.path.join(root, file)
                print(f"Restaurando: {{dst}}")
                shutil.copy2(src, dst)
                break

# Eliminar archivos creados
files_to_remove = [
    "trajectory_hub/core/compatibility.py",
    "trajectory_hub/config/parallel_config.json"
]

for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
        print(f"Eliminado: {{file}}")

print("✅ Rollback de Fase 1 completado")
'''
        
        with open("rollback_phase1.py", 'w') as f:
            f.write(rollback_code)
        os.chmod("rollback_phase1.py", 0o755)
        
        print("✅ Rollback creado: rollback_phase1.py")

# EJECUTAR FASE 1
print("\n" + "=" * 80)
print("🚀 EJECUTANDO FASE 1: CONCENTRACIÓN")
print("=" * 80)

phase1 = Phase1Implementation()

# 1. Setup
config_path = phase1.setup_config()

# 2. Compatibility
phase1.create_compatibility_layer()

# 3. Modify concentration
success = phase1.modify_concentration_for_dual_mode()

# 4. Create test
test_path = phase1.create_test_for_phase1()

# 5. Create rollback
phase1.create_rollback_phase1()

print("\n" + "=" * 80)
print("📋 RESUMEN FASE 1")
print("=" * 80)

if success:
    print("""
✅ FASE 1 PREPARADA

CAMBIOS REALIZADOS:
1. Sistema de configuración dual creado
2. Capa de compatibilidad implementada
3. Concentration modificado para soportar ambos modos
4. Tests de validación listos
5. Script de rollback disponible

PRÓXIMOS PASOS:
1. Ejecutar: python test_phase1_concentration.py
2. Verificar que ambos modos funcionan
3. Si todo OK, activar modo dual en producción
4. Si hay problemas: python rollback_phase1.py

TIEMPO ESTIMADO: 30-45 minutos de testing

⚠️ IMPORTANTE: No procedas a Fase 2 hasta validar completamente Fase 1
""")
else:
    print("""
❌ FASE 1 REQUIERE ATENCIÓN

Posibles problemas:
- No se encontró el archivo de Concentration
- La estructura del código es diferente a la esperada

Acciones:
1. Verificar ubicación de Concentration
2. Revisar estructura del código
3. Ajustar el script según sea necesario
""")

print("=" * 80)