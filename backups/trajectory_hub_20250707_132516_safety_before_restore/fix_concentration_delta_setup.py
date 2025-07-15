# === fix_concentration_delta_setup.py ===
# 🔧 Fix: Configurar correctamente sistema de deltas para concentración
# ⚡ Impacto: CRÍTICO - Sin esto los deltas no funcionan

import os
import re

def fix_concentration_setup():
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Backup
    import datetime
    backup_name = f"{engine_file}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_name, 'w') as f:
        f.write(content)
    
    # Buscar set_macro_concentration
    method_pattern = r'def set_macro_concentration\(self, macro_id: str, factor: float\):[^}]+?(?=\n    def|\nclass|\Z)'
    
    # Nuevo método que configura correctamente el sistema de deltas
    new_method = '''def set_macro_concentration(self, macro_id: str, factor: float):
        """Establecer factor de concentración para un macro."""
        if macro_id not in self._macros:
            print(f"❌ Macro '{macro_id}' no existe")
            return
            
        macro = self._macros[macro_id]
        macro.concentration_factor = max(0.0, min(1.0, factor))
        
        print(f"✅ Concentración de '{macro_id}' establecida a {macro.concentration_factor:.2f}")
        
        # Configurar sistema de deltas si está disponible
        if hasattr(self, 'use_delta_system') and self.use_delta_system:
            try:
                from trajectory_hub.core.concentration_component import ConcentrationComponent
                
                # Calcular centro del macro
                positions = []
                for sid in macro.source_ids:
                    if sid < self.max_sources and sid in self._source_motions:
                        positions.append(self._source_motions[sid].state.position.copy())
                
                if positions:
                    import numpy as np
                    center = np.mean(positions, axis=0)
                    
                    # Configurar cada fuente con ConcentrationComponent
                    for sid in macro.source_ids:
                        if sid in self._source_motions:
                            motion = self._source_motions[sid]
                            
                            # Activar sistema de deltas en el SourceMotion
                            motion.use_delta_system = True
                            
                            # Crear componente de concentración
                            concentration = ConcentrationComponent(
                                target_position=center,
                                factor=factor
                            )
                            
                            # Añadir o actualizar componente
                            motion.motion_components['concentration'] = concentration
                            
                            print(f"   ✅ ConcentrationComponent añadido a fuente {sid}")
                            
            except ImportError:
                print("   ⚠️ ConcentrationComponent no disponible")
        
        # Actualizar estado de macros
        self._update_macro_states()'''
    
    # Reemplazar el método
    content = re.sub(method_pattern, new_method, content, flags=re.DOTALL)
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("✅ set_macro_concentration actualizado para:")
    print("   - Activar use_delta_system en cada SourceMotion")
    print("   - Crear y añadir ConcentrationComponent")
    print("   - Calcular centro correcto del macro")
    
    # Test actualizado
    with open("test_concentration_delta.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST CONCENTRACIÓN CON DELTAS\\n")

# Crear engine con sistema de deltas
engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
engine.use_delta_system = True

# Crear macro
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

# Posiciones iniciales
print("📍 Posiciones iniciales:")
for i in range(2):
    print(f"   Fuente {i}: {engine._positions[i]}")

# Configurar concentración
print("\\n🎯 Configurando concentración...")
engine.set_macro_concentration(macro_id, 0.5)

# Verificar configuración
if 0 in engine._source_motions:
    motion = engine._source_motions[0]
    print(f"\\n🔍 SourceMotion[0]:")
    print(f"   use_delta_system: {motion.use_delta_system}")
    print(f"   Componentes: {list(motion.motion_components.keys())}")

# Actualizar varias veces
print("\\n🔄 Actualizando 10 frames...")
for i in range(10):
    engine.update(0.016)
    if i == 0 or i == 9:
        print(f"\\n📍 Frame {i+1}:")
        for j in range(2):
            print(f"   Fuente {j}: {engine._positions[j]}")

# Verificar movimiento
center = np.mean([engine._positions[0], engine._positions[1]], axis=0)
dist_to_center = np.linalg.norm(engine._positions[0] - center)
print(f"\\n📊 Resultado:")
print(f"   Centro: {center}")
print(f"   Distancia al centro: {dist_to_center:.4f}")

if dist_to_center < 1.8:  # Debería ser < 2.0 si hay concentración
    print("\\n✅ ¡CONCENTRACIÓN FUNCIONA!")
else:
    print("\\n❌ No hay concentración")
''')
    
    print("\n🚀 Ejecuta: python test_concentration_delta.py")

if __name__ == "__main__":
    fix_concentration_setup()