# === fix_update_mismatch.py ===
# 🔧 Fix: Arreglar discrepancia entre engine.update() y SourceMotion.update()
# ⚡ Impacto: ALTO - Sistema de deltas funcionará

import os
import re

def fix_update_signatures():
    """Arreglar las firmas de update para que sean compatibles"""
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Backup
    import datetime
    backup_name = f"{engine_file}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_name, 'w') as f:
        f.write(content)
    
    # Buscar y modificar update()
    # Cambiar def update(self) -> Dict[str, Any]:
    # Por def update(self, dt: float = None) -> Dict[str, Any]:
    pattern = r'(\s*)def update\(self\) -> Dict\[str, Any\]:'
    replacement = r'\1def update(self, dt: float = None) -> Dict[str, Any]:'
    
    new_content = re.sub(pattern, replacement, content)
    
    # Añadir lógica para usar dt y llamar a SourceMotion.update
    if "def update(self, dt: float = None)" in new_content:
        # Buscar dónde insertar el código
        update_start = new_content.find("def update(self, dt: float = None)")
        # Buscar el siguiente return
        return_pos = new_content.find("return {", update_start)
        
        # Insertar antes del return
        insert_code = """
        # Usar dt proporcionado o self.dt
        if dt is None:
            dt = self.dt
        
        # Obtener tiempo actual
        current_time = getattr(self, '_time', 0.0)
        self._time = current_time + dt
        
        # Actualizar todos los SourceMotion con sistema de deltas
        if hasattr(self, 'use_delta_system') and self.use_delta_system:
            for sid, motion in self._source_motions.items():
                if sid < self.max_sources:
                    # Llamar con firma correcta
                    pos, orient, aperture = motion.update(current_time, dt)
                    self._positions[sid] = pos
                    self._orientations[sid] = orient
                    self._apertures[sid] = aperture
        
        """
        
        # Insertar el código
        new_content = new_content[:return_pos] + insert_code + new_content[return_pos:]
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.write(new_content)
    
    print("✅ engine.update() modificado para:")
    print("   - Aceptar dt opcional")
    print("   - Llamar SourceMotion.update(time, dt) correctamente")
    print("   - Actualizar positions, orientations y apertures")
    
    # Crear test rápido
    with open("test_update_fix.py", 'w') as f:
        f.write("""#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.concentration_component import ConcentrationComponent
import numpy as np

print("🧪 TEST UPDATE FIX")

# Crear engine con sistema de deltas
engine = EnhancedTrajectoryEngine(n_sources=4, update_rate=60)
engine.use_delta_system = True

# Crear macro
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

# Configurar concentración
if hasattr(engine, 'set_macro_concentration'):
    engine.set_macro_concentration(macro_id, 0.5)
    print("✅ Concentración configurada")

# Posiciones iniciales
print(f"\\nPosiciones iniciales:")
print(f"  Fuente 0: {engine._positions[0]}")
print(f"  Fuente 1: {engine._positions[1]}")

# Llamar update con dt
print("\\n🔄 Llamando engine.update(0.016)...")
result = engine.update(0.016)

# Verificar movimiento
print(f"\\nPosiciones después de update:")
print(f"  Fuente 0: {engine._positions[0]}")
print(f"  Fuente 1: {engine._positions[1]}")

# Calcular movimiento
movement = np.linalg.norm(engine._positions[0] - np.array([-2., 0., 0.]))
if movement > 0.001:
    print(f"\\n✅ ¡FUNCIONA! Movimiento detectado: {movement:.4f}")
else:
    print(f"\\n❌ Sin movimiento: {movement:.6f}")
""")
    
    print("\n📋 Para probar:")
    print("   python test_update_fix.py")

if __name__ == "__main__":
    fix_update_signatures()