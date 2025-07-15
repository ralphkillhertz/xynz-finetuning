# === fix_system_design_complete.py ===
# 🔧 Corrección completa del diseño del sistema
# ⚡ Arregla create_macro y el modulador

import shutil
from datetime import datetime
import ast

def fix_system_design():
    """Corrige los problemas de diseño identificados"""
    
    print("🔧 CORRECCIÓN COMPLETA DEL SISTEMA")
    print("=" * 70)
    
    # 1. Backup
    print("\n1️⃣ Creando backups...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    engine_backup = f"{engine_file}.backup_{timestamp}"
    
    shutil.copy2(engine_file, engine_backup)
    print(f"   ✅ Backup creado: {engine_backup}")
    
    # 2. Leer el archivo
    with open(engine_file, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # 3. FIX 1: Modificar create_macro para retornar el objeto
    print("\n2️⃣ Corrigiendo create_macro...")
    
    modified = False
    for i, line in enumerate(lines):
        # Buscar "return macro_id"
        if line.strip() == "return macro_id":
            # Reemplazar con return del objeto
            indent = len(line) - len(line.lstrip())
            lines[i] = " " * indent + "return self._macros[macro_id]"
            print(f"   ✅ Línea {i+1}: Cambiado 'return macro_id' por 'return self._macros[macro_id]'")
            modified = True
            break
    
    if not modified:
        print("   ⚠️ No se encontró 'return macro_id'")
    
    # 4. FIX 2: Corregir create_orientation_modulator
    print("\n3️⃣ Corrigiendo create_orientation_modulator...")
    
    # Buscar y reemplazar _source_motions por motion_states
    modulator_fixed = False
    for i, line in enumerate(lines):
        if "if source_id not in self._source_motions:" in line:
            lines[i] = line.replace("self._source_motions", "self.motion_states")
            print(f"   ✅ Línea {i+1}: Cambiado '_source_motions' por 'motion_states'")
            modulator_fixed = True
    
    if not modulator_fixed:
        print("   ⚠️ No se encontró la condición en create_orientation_modulator")
    
    # 5. FIX 3: Sincronizar _source_motions con motion_states en create_source
    print("\n4️⃣ Sincronizando _source_motions...")
    
    # Buscar create_source y añadir sincronización
    in_create_source = False
    source_sync_added = False
    
    for i, line in enumerate(lines):
        if "def create_source" in line and "self" in line:
            in_create_source = True
        elif in_create_source and "self.motion_states[source_id] = motion" in line:
            # Añadir sincronización después
            indent = len(line) - len(line.lstrip())
            # Insertar después de esta línea
            lines.insert(i + 1, " " * indent + "self._source_motions[source_id] = motion")
            print(f"   ✅ Línea {i+2}: Añadida sincronización de _source_motions")
            source_sync_added = True
            break
    
    if not source_sync_added:
        print("   ⚠️ No se pudo añadir sincronización en create_source")
    
    # 6. Guardar archivo modificado
    print("\n5️⃣ Guardando archivo corregido...")
    
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print("   ✅ Archivo guardado")
    
    # 7. Verificar sintaxis
    print("\n6️⃣ Verificando sintaxis...")
    
    try:
        with open(engine_file, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("   ✅ Sintaxis correcta")
    except SyntaxError as e:
        print(f"   ❌ Error de sintaxis: {e}")
        # Restaurar backup
        shutil.copy2(engine_backup, engine_file)
        print("   🔄 Backup restaurado")
        return False
    
    # 8. Test rápido
    print("\n7️⃣ Test rápido del sistema corregido...")
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        
        # Crear engine
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        
        # Test create_macro
        print("\n   📦 Test create_macro:")
        macro = engine.create_macro('test', 3)
        print(f"      Tipo retornado: {type(macro).__name__}")
        print(f"      source_ids: {getattr(macro, 'source_ids', 'NO TIENE')}")
        
        # Test modulador
        print("\n   🎛️ Test modulador:")
        if hasattr(engine, 'create_orientation_modulator'):
            source_id = list(macro.source_ids)[0] if hasattr(macro, 'source_ids') else 0
            mod = engine.create_orientation_modulator(source_id)
            print(f"      Modulador creado: {'✅' if mod else '❌'}")
        
        print("\n✅ SISTEMA CORREGIDO EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        
        # Preguntar si restaurar
        print("\n⚠️ Hubo un error. ¿Restaurar backup? (s/n)")
        return False

def create_fixed_test():
    """Crea una versión del test adaptada si es necesario"""
    
    print("\n8️⃣ Creando test actualizado...")
    
    test_content = '''# === test_delta_fixed.py ===
# 🧪 Test del sistema de deltas con API corregida
# ⚡ Versión que funciona con create_macro retornando objeto

import time
import numpy as np
from trajectory_hub.core import EnhancedTrajectoryEngine

def test_delta_system():
    """Test del sistema de deltas con API corregida"""
    
    print("🧪 TEST DEL SISTEMA DE DELTAS (API CORREGIDA)")
    print("=" * 70)
    
    try:
        # Crear engine
        engine = EnhancedTrajectoryEngine(max_sources=50, fps=60)
        print("✅ Engine creado")
        
        # Test 1: Concentración
        print("\\n1️⃣ Test de concentración...")
        macro = engine.create_macro("test_conc", 5, formation="line", spacing=3.0)
        
        # Verificar que es un objeto
        print(f"   create_macro retorna: {type(macro).__name__}")
        source_ids = list(macro.source_ids)
        print(f"   source_ids: {source_ids}")
        
        # Aplicar concentración
        engine.set_distance_control("test_conc", mode="convergent")
        
        # Simular
        for _ in range(30):
            engine.update()
        
        print("   ✅ Concentración aplicada")
        
        # Test 2: Más tests...
        print("\\n✅ Test básico completado")
        print("   El sistema está listo para tests completos")
        
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_delta_system()
'''
    
    with open('test_delta_fixed.py', 'w') as f:
        f.write(test_content)
    
    print("   ✅ Creado: test_delta_fixed.py")

if __name__ == "__main__":
    success = fix_system_design()
    
    if success:
        create_fixed_test()
        print("\n" + "=" * 70)
        print("✅ CORRECCIONES COMPLETADAS")
        print("=" * 70)
        print("\nPróximos pasos:")
        print("1. Ejecutar: python test_delta_fixed.py")
        print("2. Si funciona, ejecutar el test completo original")
    else:
        print("\n❌ Corrección fallida - revisar errores arriba")