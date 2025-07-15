# === fix_engine_constructor.py ===
# 🔧 Fix: Corregir constructor de EnhancedTrajectoryEngine
# ⚡ Impacto: CRÍTICO - Arregla toda la inicialización

import os
import re

def fix_constructor():
    """Corrige el constructor del engine"""
    
    print("🔧 CORRIGIENDO CONSTRUCTOR DE EnhancedTrajectoryEngine\n")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Buscar el constructor actual
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la clase y su constructor
    print("🔍 Buscando constructor actual...")
    
    # Patrón para encontrar el __init__ actual (mal)
    bad_init_pattern = r'def __init__\(self, name: str, source_ids: List\[int\]\):'
    
    if re.search(bad_init_pattern, content):
        print("❌ Constructor incorrecto encontrado, reemplazando...")
        
        # Constructor correcto
        correct_init = '''def __init__(self, max_sources: int = 64, fps: int = 60, 
                 use_legacy_mode: bool = False,
                 enable_modulator: bool = True):'''
        
        # Reemplazar
        content = re.sub(bad_init_pattern, correct_init, content)
        
        # También buscar y corregir el cuerpo del __init__ si es necesario
        # Buscar las líneas después del __init__
        init_body_pattern = r'(def __init__.*?:)\s*\n(.*?)(?=\n    def|\n\nclass|\Z)'
        
        def fix_init_body(match):
            header = match.group(1)
            body = match.group(2)
            
            # Si el cuerpo parece ser el incorrecto (menciona self.name o self.source_ids como params)
            if 'self.name = name' in body or 'self.source_ids = source_ids' in body:
                print("📝 Reemplazando cuerpo del constructor...")
                
                new_body = '''        """Inicializa el motor de trayectorias mejorado"""
        self.max_sources = max_sources
        self.fps = fps
        self.use_legacy_mode = use_legacy_mode
        self.enable_modulator = enable_modulator
        
        # Arrays de posiciones y velocidades
        self._positions = np.zeros((max_sources, 3))
        self._velocities = np.zeros((max_sources, 3))
        
        # Estados de movimiento
        self.motion_states = {}
        
        # Sistema de macros
        self._macros = {}
        self._macro_counter = 0
        
        # Bridge OSC
        self.osc_bridge = SpatOSCBridge()
        
        # Contadores
        self._frame_count = 0
        self._time = 0.0
        
        # Sistema de modulación
        self.orientation_modulators = {}
        self._last_orientations = {}
        self._last_apertures = {}
        self._orientation_update_threshold = 0.01
        self._aperture_update_threshold = 0.01
        
        # Parámetros globales del modulador
        self.global_modulator_intensity = 1.0
        self.global_modulator_preset = None
        
        print(f"✅ Engine inicializado: {max_sources} fuentes, {fps} FPS")'''
                
                return header + '\n' + new_body
            else:
                return match.group(0)
        
        content = re.sub(init_body_pattern, fix_init_body, content, flags=re.DOTALL)
        
        # Guardar
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Constructor corregido")
    else:
        print("⚠️ No se encontró el constructor incorrecto")
        
        # Buscar cualquier __init__
        any_init = re.search(r'def __init__\([^)]+\):', content)
        if any_init:
            print(f"📋 Constructor actual: {any_init.group(0)}")
    
    # Crear test simple
    print("\n📝 Creando test de verificación...")
    
    test_code = '''# === test_engine_fixed.py ===
# 🧪 Test del engine corregido

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("\\n🔧 TEST: Engine con constructor corregido\\n")

# Test 1: Crear con valores por defecto
print("1️⃣ Creando con valores por defecto...")
try:
    engine1 = EnhancedTrajectoryEngine()
    print("✅ Éxito con valores por defecto")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Crear con max_sources
print("\\n2️⃣ Creando con max_sources=8...")
try:
    engine2 = EnhancedTrajectoryEngine(max_sources=8)
    print("✅ Éxito con max_sources")
    print(f"   Posiciones shape: {engine2._positions.shape}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Crear macro y rotar
print("\\n3️⃣ Creando macro y aplicando rotación...")
try:
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60, enable_modulator=False)
    macro_id = engine.create_macro("test", 4)
    
    # Configurar posiciones
    positions = [[1,0,0], [-1,0,0], [0,1,0], [0,-1,0]]
    for i, sid in enumerate(list(engine._macros[macro_id].source_ids)[:4]):
        engine._positions[sid] = np.array(positions[i])
    
    # Aplicar rotación
    engine.set_macro_rotation(macro_id, 0, 1.0, 0)
    
    # Simular
    for _ in range(30):
        engine.update()
    
    print("✅ ¡TODO FUNCIONANDO!")
    print("\\n🎉 SISTEMA LISTO PARA USAR")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open("test_engine_fixed.py", "w") as f:
        f.write(test_code)
    
    print("✅ Test creado")

if __name__ == "__main__":
    fix_constructor()
    print("\n🚀 Ejecutando test...")
    os.system("python test_engine_fixed.py")