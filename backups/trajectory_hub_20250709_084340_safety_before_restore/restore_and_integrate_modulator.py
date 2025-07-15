# === restore_and_integrate_modulator.py ===
# 🔧 Restaura backup limpio y añade modulador 3D
# ⚡ Solución definitiva al problema de sintaxis

import shutil
import os
import ast
from datetime import datetime

def restore_and_integrate():
    """Restaura backup y añade funcionalidad del modulador"""
    
    print("🔧 RESTAURACIÓN Y INTEGRACIÓN DEL MODULADOR 3D")
    print("=" * 70)
    
    # 1. Hacer backup del archivo actual dañado
    current_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    damaged_backup = f"{current_file}.damaged_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\n📁 Guardando archivo dañado como backup...")
    shutil.copy2(current_file, damaged_backup)
    print(f"   ✅ Guardado: {damaged_backup}")
    
    # 2. Restaurar el backup limpio
    clean_backup = "trajectory_hub/core/enhanced_trajectory_engine.py.backup_20250708_140157"
    
    print(f"\n🔄 Restaurando backup limpio...")
    if not os.path.exists(clean_backup):
        print(f"   ❌ Error: No se encuentra el backup {clean_backup}")
        return False
    
    shutil.copy2(clean_backup, current_file)
    print(f"   ✅ Restaurado: {clean_backup} ({os.path.getsize(clean_backup):,} bytes)")
    
    # 3. Verificar sintaxis del archivo restaurado
    print("\n🧪 Verificando sintaxis del archivo restaurado...")
    try:
        with open(current_file, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("   ✅ Sintaxis correcta!")
    except SyntaxError as e:
        print(f"   ❌ Error de sintaxis: {e}")
        return False
    
    # 4. Añadir imports necesarios para el modulador
    print("\n📝 Añadiendo imports para el modulador...")
    
    with open(current_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar dónde insertar el import
    import_added = False
    for i, line in enumerate(lines):
        if line.startswith('from trajectory_hub.core.motion_components import'):
            # Verificar si ya tiene AdvancedOrientationModulation
            if 'AdvancedOrientationModulation' not in line:
                # Añadir al final del import existente
                if line.strip().endswith(')'):
                    lines[i] = line.rstrip()[:-1] + ',\n    AdvancedOrientationModulation\n)\n'
                    import_added = True
                    print("   ✅ Import añadido a línea existente")
                    break
    
    if not import_added:
        # Buscar otro lugar para añadir
        for i, line in enumerate(lines):
            if line.startswith('import') or line.startswith('from'):
                continue
            elif line.strip() and not line.startswith('#'):
                # Insertar antes de la primera línea de código
                lines.insert(i, 'from trajectory_hub.core.motion_components import AdvancedOrientationModulation\n')
                import_added = True
                print(f"   ✅ Import añadido en línea {i+1}")
                break
    
    # 5. Añadir atributos del modulador en __init__
    print("\n📝 Añadiendo atributos del modulador en __init__...")
    
    init_found = False
    for i, line in enumerate(lines):
        if 'def __init__' in line and 'self' in line:
            # Buscar el final del __init__
            j = i + 1
            indent = '        '  # Asumiendo indentación estándar
            
            # Buscar una buena ubicación (después de otros atributos)
            while j < len(lines) and lines[j].strip():
                if 'self._' in lines[j] or 'self.' in lines[j]:
                    last_attr_line = j
                j += 1
            
            # Insertar después del último atributo
            if 'last_attr_line' in locals():
                insert_pos = last_attr_line + 1
                modulator_attrs = [
                    f"{indent}# Sistema de modulación de orientación\n",
                    f"{indent}self.enable_modulator = enable_modulator\n",
                    f"{indent}self.orientation_modulators = {{}}  # Dict[int, AdvancedOrientationModulation]\n",
                    f"{indent}self.global_modulator_intensity = 1.0\n",
                    f"{indent}self.global_modulator_preset = None\n",
                    f"{indent}self._last_orientations = {{}}\n",
                    f"{indent}self._orientation_update_threshold = 0.01  # radianes\n",
                    f"{indent}self._last_apertures = {{}}\n",
                    f"{indent}self._aperture_update_threshold = 0.01\n",
                    "\n"
                ]
                
                # Verificar si enable_modulator está en los parámetros
                init_line = lines[i]
                if 'enable_modulator' not in init_line:
                    # Añadir parámetro
                    if ')' in init_line:
                        lines[i] = init_line.rstrip()[:-2] + ',\n                 enable_modulator: bool = True):\n'
                        print("   ✅ Parámetro enable_modulator añadido")
                
                # Insertar atributos
                for attr in reversed(modulator_attrs):
                    lines.insert(insert_pos, attr)
                
                init_found = True
                print("   ✅ Atributos del modulador añadidos")
                break
    
    # 6. Guardar archivo modificado
    print("\n💾 Guardando archivo modificado...")
    with open(current_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("   ✅ Archivo guardado")
    
    # 7. Verificar sintaxis final
    print("\n🧪 Verificación final de sintaxis...")
    try:
        with open(current_file, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("   ✅ ¡Sintaxis perfecta!")
        
        # Test de importación
        print("\n🧪 Test de importación...")
        try:
            from trajectory_hub.core import EnhancedTrajectoryEngine
            print("   ✅ Importación exitosa")
            
            # Test de creación
            engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=True)
            print("   ✅ Engine creado con modulador habilitado")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error de importación: {e}")
            return False
            
    except SyntaxError as e:
        print(f"   ❌ Error de sintaxis: {e}")
        return False

def create_modulator_methods():
    """Crea archivo con los métodos del modulador para añadir manualmente"""
    
    print("\n📝 Creando archivo con métodos del modulador...")
    
    methods_content = '''# === MÉTODOS DEL MODULADOR 3D PARA AÑADIR A enhanced_trajectory_engine.py ===
# Copiar estos métodos dentro de la clase EnhancedTrajectoryEngine

    def create_orientation_modulator(self, source_id: int) -> Optional['AdvancedOrientationModulation']:
        """Crea un modulador de orientación para una fuente"""
        if not self.enable_modulator:
            return None
            
        if source_id not in self.motion_states:
            logger.warning(f"No se puede crear modulador para fuente inexistente: {source_id}")
            return None
            
        modulator = AdvancedOrientationModulation()
        self.orientation_modulators[source_id] = modulator
        
        logger.info(f"Modulador de orientación creado para fuente {source_id}")
        return modulator
        
    def apply_orientation_preset(self, macro_name: str, preset_name: str, 
                               intensity: float = 1.0, time_offset_spread: float = 0.0):
        """Aplica un preset de modulación a todas las fuentes de un macro"""
        if macro_name not in self._macros:
            logger.warning(f"Macro no encontrado: {macro_name}")
            return
            
        macro = self._macros[macro_name]
        source_ids = list(macro.source_ids)
        
        for i, source_id in enumerate(source_ids):
            if source_id not in self.orientation_modulators:
                self.create_orientation_modulator(source_id)
                
            modulator = self.orientation_modulators.get(source_id)
            if modulator:
                modulator.apply_preset(preset_name)
                modulator.intensity = intensity
                
                # Aplicar desfase temporal si se especifica
                if time_offset_spread > 0:
                    modulator.time_offset = i * time_offset_spread
                    
        logger.info(f"Preset '{preset_name}' aplicado a macro '{macro_name}' con intensidad {intensity}")
        
    def set_orientation_intensity(self, macro_name: str, intensity: float):
        """Ajusta la intensidad de modulación para un macro (0.0 a 1.0)"""
        if macro_name not in self._macros:
            return
            
        intensity = max(0.0, min(1.0, intensity))
        macro = self._macros[macro_name]
        
        for source_id in macro.source_ids:
            if source_id in self.orientation_modulators:
                self.orientation_modulators[source_id].intensity = intensity
                
        logger.info(f"Intensidad de modulación ajustada a {intensity} para macro '{macro_name}'")
'''
    
    with open('modulator_methods_to_add.py', 'w', encoding='utf-8') as f:
        f.write(methods_content)
    
    print("   ✅ Archivo creado: modulator_methods_to_add.py")
    print("   📋 Contiene los métodos principales del modulador")
    print("   📋 Añadir manualmente después de verificar que todo funciona")

if __name__ == "__main__":
    success = restore_and_integrate()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ RESTAURACIÓN COMPLETADA CON ÉXITO")
        print("=" * 70)
        print("\n📋 SIGUIENTE PASO:")
        print("   1. Verificar que el sistema básico funcione")
        print("   2. Añadir los métodos del modulador del archivo 'modulator_methods_to_add.py'")
        print("   3. Seguir la guía de integración del modulador")
        
        create_modulator_methods()
    else:
        print("\n❌ La restauración encontró problemas")
        print("   Revisar los mensajes de error arriba")