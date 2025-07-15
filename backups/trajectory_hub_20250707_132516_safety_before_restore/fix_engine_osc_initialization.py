# === fix_engine_osc_initialization.py ===
# 🔧 Fix: Inicializar correctamente el bridge OSC en el engine
# ⚡ El bridge existe pero es None

import os
import re

def fix_engine_osc():
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    print("🔧 ARREGLANDO INICIALIZACIÓN OSC EN ENGINE\n")
    
    # 1. Buscar __init__ del engine
    init_pattern = r'def __init__\(self,[^)]*\):(.*?)(?=\n    def|\Z)'
    
    def fix_init(match):
        init_content = match.group(0)
        
        # Verificar si ya inicializa osc_bridge
        if 'self.osc_bridge = None' in init_content or 'self.osc_bridge = SpatOSCBridge' not in init_content:
            print("   ❌ osc_bridge no se inicializa correctamente")
            
            # Buscar dónde insertar
            if 'self._init_complete = True' in init_content:
                # Insertar antes de init_complete
                init_content = init_content.replace(
                    'self._init_complete = True',
                    '''# Inicializar OSC Bridge
        try:
            from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget
            target = OSCTarget("127.0.0.1", 9000)
            self.osc_bridge = SpatOSCBridge(targets=[target], fps=self.fps)
            print(f"✅ OSC Bridge inicializado: {self.osc_bridge}")
        except Exception as e:
            print(f"❌ Error inicializando OSC: {e}")
            self.osc_bridge = None
        
        self._init_complete = True'''
                )
            else:
                # Añadir al final del __init__
                init_content = init_content.rstrip() + '''
        
        # Inicializar OSC Bridge
        try:
            from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget
            target = OSCTarget("127.0.0.1", 9000)
            self.osc_bridge = SpatOSCBridge(targets=[target], fps=self.fps)
            print(f"✅ OSC Bridge inicializado: {self.osc_bridge}")
        except Exception as e:
            print(f"❌ Error inicializando OSC: {e}")
            self.osc_bridge = None
'''
        
        return init_content
    
    content = re.sub(init_pattern, fix_init, content, flags=re.DOTALL)
    
    # 2. Arreglar create_macro para que use el bridge
    create_pattern = r'(def create_macro\([^)]*\):.*?)(return macro_id)'
    
    def fix_create_macro(match):
        method_content = match.group(1)
        return_line = match.group(2)
        
        # Añadir llamada a create_group si no existe
        if 'self.osc_bridge' not in method_content or 'create_group' not in method_content:
            osc_code = '''
        # Crear grupo en Spat via OSC
        if self.osc_bridge and hasattr(self.osc_bridge, 'create_group'):
            try:
                self.osc_bridge.create_group(macro_id, name)
                
                # Añadir fuentes al grupo
                if hasattr(self.osc_bridge, 'add_source_to_group'):
                    for sid in source_ids:
                        self.osc_bridge.add_source_to_group(sid, name)
                        
            except Exception as e:
                print(f"❌ Error creando grupo OSC: {e}")
        
        '''
            return method_content + osc_code + return_line
        
        return match.group(0)
    
    content = re.sub(create_pattern, fix_create_macro, content, flags=re.DOTALL)
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("✅ Engine actualizado:")
    print("   - OSC Bridge se inicializa en __init__")
    print("   - create_macro envía grupos a Spat")
    
    # Test final
    with open("test_final_osc.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# NO deshabilitar OSC
if 'DISABLE_OSC' in os.environ:
    del os.environ['DISABLE_OSC']

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🧪 TEST FINAL OSC\\n")

print("1. Creando engine...")
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

print(f"\\n2. Verificando OSC:")
print(f"   osc_bridge existe: {engine.osc_bridge is not None}")
if engine.osc_bridge:
    print(f"   Tipo: {type(engine.osc_bridge)}")

print("\\n3. Creando macro 'DemoGroup'...")
macro_id = engine.create_macro("DemoGroup", source_count=3)

print("\\n4. Moviendo fuentes...")
engine.set_macro_concentration(macro_id, 0.5)

for i in range(5):
    engine.step()
    print(f"   Frame {i+1}")

print("\\n✅ VERIFICA EN SPAT OSC MONITOR:")
print("   - /group/new ['DemoGroup']")
print("   - /source/0/group ['DemoGroup']")
print("   - /source/1/group ['DemoGroup']")
print("   - /source/2/group ['DemoGroup']")
print("   - /source/0/xyz [x, y, z] (actualizándose)")
''')

if __name__ == "__main__":
    fix_engine_osc()