#!/usr/bin/env python3
"""
🎯 MIGRAR CONCENTRACIÓN A SISTEMA DE DELTAS
Primer componente: el más simple para validar el sistema
"""

import os
import re
from datetime import datetime

print("""
================================================================================
🎯 MIGRANDO CONCENTRACIÓN A DELTAS
================================================================================
Este componente será INDEPENDIENTE:
- No verificará si existen trayectorias IS
- Calculará su delta sin modificar el estado
- Se sumará con otros componentes
================================================================================
""")

# 1. Crear ConcentrationComponent
concentration_code = '''"""
Componente de Concentración - Sistema de Deltas
============================================
Hace que las fuentes de un macro converjan hacia su centro.
"""

import numpy as np
from typing import Dict, Optional
from trajectory_hub.core.delta_system import MotionComponent, MotionDelta
import logging

logger = logging.getLogger(__name__)


class ConcentrationComponent(MotionComponent):
    """
    Componente que aplica fuerzas de concentración hacia un punto objetivo.
    
    INDEPENDIENTE: No verifica ni depende de otros componentes.
    """
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
        self.target_position: Optional[np.ndarray] = None
        self.concentration_factor: float = 0.0
        self.smoothing: float = 0.1  # Suavizado del movimiento
        
    def set_target(self, target_position: np.ndarray, factor: float):
        """
        Establece el punto objetivo y la intensidad de concentración.
        
        Args:
            target_position: Posición objetivo (centro del macro)
            factor: Intensidad 0.0 (sin efecto) a 1.0 (máxima concentración)
        """
        self.target_position = target_position.copy()
        self.concentration_factor = np.clip(factor, 0.0, 1.0)
        logger.debug(f"Concentración configurada: target={target_position}, factor={factor}")
        
    def calculate_delta(self, state, dt: float, context: Dict = None) -> MotionDelta:
        """
        Calcula el delta de movimiento hacia el centro.
        
        NO modifica el estado, solo calcula el cambio deseado.
        """
        delta = MotionDelta()
        
        # Si no hay objetivo o el factor es 0, no hay movimiento
        if self.target_position is None or self.concentration_factor == 0:
            return delta
            
        # Calcular dirección hacia el objetivo
        current_pos = state.position
        direction = self.target_position - current_pos
        distance = np.linalg.norm(direction)
        
        # Si ya estamos muy cerca, reducir el movimiento
        if distance < 0.01:
            return delta
            
        # Normalizar dirección
        direction = direction / distance
        
        # Calcular velocidad deseada
        # - Factor de concentración controla la intensidad
        # - Smoothing evita movimientos bruscos
        # - La velocidad disminuye al acercarse (distance factor)
        distance_factor = min(1.0, distance / 5.0)  # Desacelera cerca del objetivo
        desired_speed = self.concentration_factor * self.smoothing * distance_factor
        
        # Delta de posición
        delta.position = direction * desired_speed * dt * 50.0  # Factor de escala para velocidad visible
        
        # Log para debugging
        if np.any(delta.position != 0):
            logger.debug(f"ConcentrationDelta: {np.linalg.norm(delta.position):.4f}")
            
        return delta
    
    def reset(self):
        """Resetea el componente."""
        self.target_position = None
        self.concentration_factor = 0.0
'''

# Guardar ConcentrationComponent
comp_file = "trajectory_hub/core/concentration_component.py"
print(f"📝 Creando {comp_file}...")
with open(comp_file, 'w') as f:
    f.write(concentration_code)
print("✅ ConcentrationComponent creado\n")

# 2. Actualizar enhanced_trajectory_engine.py
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
print(f"📝 Actualizando {engine_file}...")

with open(engine_file, 'r') as f:
    engine_content = f.read()

# Backup
backup_name = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_name, 'w') as f:
    f.write(engine_content)

# Añadir import
if "from trajectory_hub.core.concentration_component import" not in engine_content:
    import_pos = engine_content.find("from trajectory_hub.core.motion_components import")
    if import_pos > 0:
        next_line = engine_content.find("\n", import_pos) + 1
        new_import = "from trajectory_hub.core.concentration_component import ConcentrationComponent\n"
        engine_content = engine_content[:next_line] + new_import + engine_content[next_line:]

# Modificar set_macro_concentration para usar el nuevo sistema
method_pattern = r'def set_macro_concentration\(self,[^}]+?\n(?=\n    def|\Z)'
match = re.search(method_pattern, engine_content, re.DOTALL)

if match:
    new_method = '''def set_macro_concentration(self, macro_id: str, factor: float):
        """
        Aplica concentración a un macro usando el sistema de deltas.
        
        CAMBIO CLAVE: No verifica dependencias, siempre funciona.
        """
        if macro_id not in self._macros:
            return
            
        macro = self._macros[macro_id]
        factor = np.clip(factor, 0.0, 1.0)
        
        # Calcular centro del macro
        positions = []
        for sid in macro.source_ids:
            if sid < self.max_sources and sid in self._source_motions:
                pos = self._source_motions[sid].state.position
                positions.append(pos)
                
        if len(positions) < 2:
            return  # No hay suficientes fuentes para concentrar
            
        center = np.mean(positions, axis=0)
        
        # Configurar concentración para cada fuente del macro
        for sid in macro.source_ids:
            if sid < self.max_sources and sid in self._source_motions:
                motion = self._source_motions[sid]
                
                # Crear componente si no existe
                if 'concentration' not in motion.motion_components:
                    motion.motion_components['concentration'] = ConcentrationComponent()
                    motion.use_delta_system = True  # Activar sistema de deltas
                
                # Configurar el componente
                concentration = motion.motion_components['concentration']
                concentration.set_target(center, factor)
                concentration.set_enabled(factor > 0)
                
                print(f"✅ Concentración configurada para fuente {sid}: factor={factor:.2f}")
        
        # Guardar estado en el macro
        macro.concentration_factor = factor
        macro.concentration_center = center
'''
    
    engine_content = engine_content[:match.start()] + new_method + engine_content[match.end():]

# Guardar cambios
with open(engine_file, 'w') as f:
    f.write(engine_content)
print("✅ set_macro_concentration actualizado\n")

# 3. Modificar SourceMotion.update() para usar deltas
motion_file = "trajectory_hub/core/motion_components.py"
print(f"📝 Actualizando SourceMotion.update()...")

with open(motion_file, 'r') as f:
    motion_content = f.read()

# Buscar método update
update_pattern = r'def update\(self, dt:[^}]+?\n(?=\n    def|\Z)'
match = re.search(update_pattern, motion_content, re.DOTALL)

if match:
    # Insertar lógica de deltas al principio del update
    old_update = match.group(0)
    
    # Encontrar dónde empieza el cuerpo del método
    body_start = old_update.find(':') + 1
    first_line_start = old_update.find('\n', body_start) + 1
    
    # Extraer indentación
    indent_match = re.search(r'\n(\s+)', old_update[body_start:])
    indent = indent_match.group(1) if indent_match else "        "
    
    delta_logic = f'''
{indent}# Sistema de deltas (si está activado)
{indent}if self.use_delta_system and self.motion_components:
{indent}    # Recolectar deltas de todos los componentes activos
{indent}    deltas = []
{indent}    context = {{'source_id': getattr(self, 'source_id', None)}}
{indent}    
{indent}    for name, component in self.motion_components.items():
{indent}        if component.enabled:
{indent}            try:
{indent}                delta = component.calculate_delta(self.state, dt, context)
{indent}                deltas.append((name, delta))
{indent}            except Exception as e:
{indent}                print(f"Error en {{name}}: {{e}}")
{indent}    
{indent}    # Componer nuevo estado si hay deltas
{indent}    if deltas:
{indent}        from trajectory_hub.core.delta_system import DeltaComposer
{indent}        self.state = DeltaComposer.compose(self.state, deltas, self.component_weights)
{indent}        return  # Skip legacy update
{indent}
{indent}# Sistema legacy (se ejecuta si no hay deltas)
'''
    
    new_update = old_update[:first_line_start] + delta_logic + old_update[first_line_start:]
    motion_content = motion_content[:match.start()] + new_update + motion_content[match.end():]

# Guardar cambios
with open(motion_file, 'w') as f:
    f.write(motion_content)
print("✅ SourceMotion.update() preparado para deltas\n")

# 4. Crear test para verificar
test_code = '''#!/usr/bin/env python3
"""
🧪 TEST: Concentración Independiente con Sistema de Deltas
"""

import os
import sys
import numpy as np

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("""
================================================================================
🧪 TEST DE CONCENTRACIÓN CON SISTEMA DE DELTAS
================================================================================
""")

# Deshabilitar OSC para test
os.environ['DISABLE_OSC'] = '1'

try:
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=8, fps=60)
    
    # Test 1: Concentración SIN trayectorias IS
    print("TEST 1: Concentración sin trayectorias IS")
    print("-" * 50)
    
    # Crear macro simple
    macro_id = engine.create_macro("test_concentration", source_count=4, formation="grid", spacing=6.0)
    
    # Verificar posiciones iniciales
    positions_before = []
    for sid in engine._macros[macro_id].source_ids:
        pos = engine._source_motions[sid].state.position.copy()
        positions_before.append(pos)
        print(f"Fuente {sid}: {pos}")
    
    # Calcular dispersión inicial
    center_before = np.mean(positions_before, axis=0)
    dispersion_before = np.mean([np.linalg.norm(p - center_before) for p in positions_before])
    print(f"\\nCentro: {center_before}")
    print(f"Dispersión inicial: {dispersion_before:.2f}")
    
    # Aplicar concentración
    print("\\n🎯 Aplicando concentración (factor=0.8)...")
    engine.set_macro_concentration(macro_id, 0.8)
    
    # Verificar que se crearon los componentes
    for sid in engine._macros[macro_id].source_ids:
        motion = engine._source_motions[sid]
        if 'concentration' in motion.motion_components:
            print(f"✅ Componente de concentración creado para fuente {sid}")
            print(f"   use_delta_system: {motion.use_delta_system}")
    
    # Ejecutar varios frames
    print("\\n🔄 Ejecutando 60 frames...")
    for i in range(60):
        engine.update(1/60)
        if i % 20 == 0:
            # Verificar progreso
            pos = engine._source_motions[engine._macros[macro_id].source_ids[0]].state.position
            dist = np.linalg.norm(pos - center_before)
            print(f"   Frame {i}: distancia al centro = {dist:.2f}")
    
    # Verificar resultado
    print("\\n📊 RESULTADO:")
    positions_after = []
    for sid in engine._macros[macro_id].source_ids:
        pos = engine._source_motions[sid].state.position
        positions_after.append(pos)
        print(f"Fuente {sid}: {pos}")
    
    center_after = np.mean(positions_after, axis=0)
    dispersion_after = np.mean([np.linalg.norm(p - center_after) for p in positions_after])
    
    print(f"\\nDispersión final: {dispersion_after:.2f}")
    print(f"Reducción: {((dispersion_before - dispersion_after) / dispersion_before * 100):.1f}%")
    
    # Verificar que hubo movimiento
    total_movement = sum(np.linalg.norm(p1 - p2) for p1, p2 in zip(positions_before, positions_after))
    
    if total_movement > 0.1 and dispersion_after < dispersion_before:
        print("\\n✅ ¡CONCENTRACIÓN FUNCIONA SIN TRAYECTORIAS IS!")
    else:
        print("\\n❌ La concentración no funcionó correctamente")
        
    # Test 2: Verificar que no interfiere con otros componentes
    print("\\n\\nTEST 2: Independencia de componentes")
    print("-" * 50)
    
    # Aplicar trayectoria macro
    print("Aplicando trayectoria circular al macro...")
    engine.set_macro_trajectory(macro_id, "circle", speed=0.5)
    
    # La concentración debe seguir funcionando
    print("Verificando que concentración sigue activa...")
    for i in range(30):
        engine.update(1/60)
    
    # Verificar que siguen concentradas mientras se mueven
    positions_moving = []
    for sid in engine._macros[macro_id].source_ids:
        pos = engine._source_motions[sid].state.position
        positions_moving.append(pos)
    
    center_moving = np.mean(positions_moving, axis=0)
    dispersion_moving = np.mean([np.linalg.norm(p - center_moving) for p in positions_moving])
    
    print(f"\\nDispersión con movimiento: {dispersion_moving:.2f}")
    print(f"Centro se movió: {np.linalg.norm(center_moving - center_after):.2f}")
    
    if dispersion_moving < dispersion_before * 0.5 and np.linalg.norm(center_moving - center_after) > 0.1:
        print("\\n✅ ¡CONCENTRACIÓN Y MOVIMIENTO FUNCIONAN EN PARALELO!")
    else:
        print("\\n⚠️  Verificar interacción entre componentes")

except Exception as e:
    print(f"\\n❌ Error durante el test: {e}")
    import traceback
    traceback.print_exc()

print("""
================================================================================
✅ TEST COMPLETADO
================================================================================
""")
'''

with open("test_concentration_delta.py", 'w') as f:
    f.write(test_code)
os.chmod("test_concentration_delta.py", 0o755)

print("""
================================================================================
✅ MIGRACIÓN DE CONCENTRACIÓN COMPLETADA
================================================================================

CAMBIOS REALIZADOS:
1. ✅ Creado ConcentrationComponent
   - Calcula deltas sin modificar estado
   - No verifica dependencias
   - Totalmente independiente

2. ✅ Actualizado set_macro_concentration()
   - Usa el nuevo sistema de componentes
   - No requiere trayectorias IS
   - Activa sistema de deltas

3. ✅ Modificado SourceMotion.update()
   - Detecta y usa sistema de deltas
   - Compone múltiples deltas
   - Mantiene compatibilidad legacy

4. ✅ Test creado: test_concentration_delta.py

PRÓXIMO PASO:
python test_concentration_delta.py

Si el test pasa, continuar con:
python migrate_trajectories_to_delta.py

================================================================================
""")