# 🔧 Fix: Asegurar que osc_bridge se inicializa correctamente
# ⚡ Diagnosticar y arreglar la inicialización

print("🔧 Verificando inicialización de osc_bridge...")

# 1. Verificar el __init__ del engine
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar dónde se inicializa osc_bridge
if "self.osc_bridge = SpatOSCBridge()" in content:
    print("✅ osc_bridge se está inicializando")
    
    # Verificar que el import esté correcto
    if "from .spat_osc_bridge import SpatOSCBridge" not in content:
        print("⚠️ Falta el import de SpatOSCBridge")
        
        # Añadir import al principio con los otros imports
        import_line = "from .spat_osc_bridge import SpatOSCBridge"
        
        # Buscar dónde están los otros imports
        import_section_end = content.find("\n\n\nclass")
        if import_section_end == -1:
            import_section_end = content.find("\n\nclass")
        
        if import_section_end > 0:
            content = content[:import_section_end] + f"\n{import_line}" + content[import_section_end:]
        else:
            # Añadir después de los primeros imports
            first_class = content.find("class ")
            content = import_line + "\n\n" + content
        
        # Guardar
        with open(engine_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Import añadido")

# 2. Añadir debug al __init__ para ver qué pasa
init_index = content.find("self.osc_bridge = SpatOSCBridge()")
if init_index > 0:
    # Añadir print de debug
    debug_line = '\n        logger.info("Inicializando OSC bridge...")'
    
    # Buscar si ya existe el debug
    if 'logger.info("Inicializando OSC bridge' not in content:
        content = content[:init_index] + debug_line + "\n        " + content[init_index:]
        
        # También añadir verificación después
        after_init = init_index + len("self.osc_bridge = SpatOSCBridge()")
        verify_line = '\n        logger.info(f"OSC bridge inicializado: {self.osc_bridge is not None}")'
        content = content[:after_init] + verify_line + content[after_init:]
        
        # Guardar
        with open(engine_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Debug añadido")

# 3. Crear test con más información
test_debug = '''# === test_osc_debug.py ===
# Test con información de debug

import logging
logging.basicConfig(level=logging.DEBUG)

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.spat_osc_bridge import OSCTarget

print("🧪 TEST DEBUG OSC")
print("=" * 50)

try:
    # Crear engine
    print("1. Creando engine...")
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=30)
    print(f"   ✅ Engine creado")
    
    # Verificar osc_bridge
    print(f"2. Verificando osc_bridge...")
    print(f"   - osc_bridge existe: {hasattr(engine, 'osc_bridge')}")
    print(f"   - osc_bridge es None: {getattr(engine, 'osc_bridge', 'NO EXISTE') is None}")
    
    if hasattr(engine, 'osc_bridge') and engine.osc_bridge is not None:
        print(f"   ✅ osc_bridge inicializado correctamente")
        
        # Configurar OSC
        target = OSCTarget(host="127.0.0.1", port=9000, name="Spat_Test")
        engine.osc_bridge.add_target(target)
        print(f"3. ✅ Target OSC añadido")
        
        # Test básico
        engine.osc_bridge.send_position(1, 1.0, 2.0, 3.0)
        print(f"4. ✅ Mensaje de prueba enviado")
    else:
        print("   ❌ osc_bridge no está inicializado")
        
except Exception as e:
    print(f"\\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''

with open("test_osc_debug.py", 'w') as f:
    f.write(test_debug)

print("\n✅ Test de debug creado: test_osc_debug.py")
print("\n🚀 Ejecuta el test de debug:")
print("   python test_osc_debug.py")