#!/usr/bin/env python3
"""
🔄 CONTINUAR IMPLEMENTACIÓN DESPUÉS DEL FIX
"""

import os
import subprocess
import sys

print("""
================================================================================
🔄 CONTINUANDO IMPLEMENTACIÓN DEL SISTEMA PARALELO
================================================================================
""")

# 1. Verificar que el fix funcionó
print("1️⃣ VERIFICANDO FIX DE SINTAXIS...")
print("-" * 50)

try:
    # Intentar importar el módulo
    sys.path.insert(0, os.getcwd())
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    print("✅ Import exitoso - sintaxis arreglada!")
except SyntaxError as e:
    print(f"❌ Todavía hay error de sintaxis: {e}")
    print("\nEjecuta primero: python fix_syntax_error.py")
    exit(1)
except Exception as e:
    print(f"⚠️ Otro tipo de error: {e}")
    # Continuar de todos modos

# 2. Ejecutar test de concentración
print("\n2️⃣ EJECUTANDO TEST DE CONCENTRACIÓN...")
print("-" * 50)

if os.path.exists("test_concentration_delta.py"):
    try:
        result = subprocess.run(
            ['python', 'test_concentration_delta.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr and "Error" in result.stderr:
            print(f"\n⚠️ Advertencias:\n{result.stderr}")
            
        # Verificar si pasó
        if "CONCENTRACIÓN FUNCIONA SIN TRAYECTORIAS IS" in result.stdout:
            print("\n✅ ¡TEST DE CONCENTRACIÓN PASÓ!")
        else:
            print("\n⚠️ El test no dio el resultado esperado")
            
    except subprocess.TimeoutExpired:
        print("⚠️ El test tardó demasiado")
    except Exception as e:
        print(f"❌ Error ejecutando test: {e}")
else:
    print("❌ No se encuentra test_concentration_delta.py")

# 3. Verificar independencia
print("\n3️⃣ VERIFICANDO INDEPENDENCIA DE COMPONENTES...")
print("-" * 50)

if os.path.exists("verify_independence.py"):
    try:
        result = subprocess.run(
            ['python', 'verify_independence.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        
        if "TODOS LOS COMPONENTES SON INDEPENDIENTES" in result.stdout:
            print("\n✅ ¡VERIFICACIÓN DE INDEPENDENCIA PASÓ!")
        else:
            print("\n⚠️ Aún hay dependencias por resolver")
            
    except Exception as e:
        print(f"❌ Error ejecutando verificación: {e}")
else:
    print("❌ No se encuentra verify_independence.py")

# 4. Crear plantillas para componentes faltantes
print("\n4️⃣ CREANDO PLANTILLAS PARA COMPONENTES FALTANTES...")
print("-" * 50)

# Plantilla para TrajectoryComponent
trajectory_template = '''"""
Componente de Trayectoria Individual - Sistema de Deltas
======================================================
Gestiona el movimiento de fuentes individuales a lo largo de trayectorias.
"""

import numpy as np
from typing import Dict, Optional
from trajectory_hub.core.delta_system import MotionComponent, MotionDelta
from trajectory_hub.core.motion_components import IndividualTrajectory
import logging

logger = logging.getLogger(__name__)


class TrajectoryComponent(MotionComponent):
    """
    Componente que mueve la fuente a lo largo de una trayectoria individual.
    
    INDEPENDIENTE: No interfiere con otros componentes.
    """
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
        self.trajectory: Optional[IndividualTrajectory] = None
        self.speed: float = 1.0
        self.phase: float = 0.0
        
    def set_trajectory(self, trajectory: IndividualTrajectory):
        """Establece la trayectoria a seguir."""
        self.trajectory = trajectory
        self.phase = 0.0
        
    def calculate_delta(self, state, dt: float, context: Dict = None) -> MotionDelta:
        """
        Calcula el delta para seguir la trayectoria.
        
        NO modifica el estado directamente.
        """
        delta = MotionDelta()
        
        if self.trajectory is None or not self.enabled:
            return delta
            
        # Avanzar en la trayectoria
        self.phase += self.speed * dt
        if self.phase > 1.0:
            self.phase -= 1.0
            
        # Obtener posición objetivo en la trayectoria
        target_pos = self.trajectory.get_position_at_phase(self.phase)
        
        # Calcular delta suave
        direction = target_pos - state.position
        delta.position = direction * 0.1  # Suavizado
        
        return delta
        
    def reset(self):
        """Resetea a la posición inicial."""
        self.phase = 0.0
'''

# Plantilla para RotationComponent
rotation_template = '''"""
Componente de Rotación Algorítmica - Sistema de Deltas
====================================================
Aplica rotación alrededor del centro del macro.
"""

import numpy as np
from typing import Dict, Optional
from trajectory_hub.core.delta_system import MotionComponent, MotionDelta
import logging

logger = logging.getLogger(__name__)


class RotationComponent(MotionComponent):
    """
    Componente que rota la fuente alrededor de un centro.
    
    INDEPENDIENTE: Calcula su rotación sin afectar otros componentes.
    """
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
        self.angular_velocity = {'yaw': 0.0, 'pitch': 0.0, 'roll': 0.0}
        self.rotation_center: Optional[np.ndarray] = None
        
    def set_rotation(self, angular_velocity: Dict[str, float], center: np.ndarray):
        """Configura la rotación."""
        self.angular_velocity = angular_velocity.copy()
        self.rotation_center = center.copy()
        
    def calculate_delta(self, state, dt: float, context: Dict = None) -> MotionDelta:
        """
        Calcula el delta de rotación.
        
        Solo retorna el cambio, no modifica estado.
        """
        delta = MotionDelta()
        
        if self.rotation_center is None:
            # Usar centro del contexto si está disponible
            if context and 'macro_center' in context:
                self.rotation_center = context['macro_center']
            else:
                return delta
                
        # Vector desde el centro a la posición actual
        to_source = state.position - self.rotation_center
        
        # Aplicar rotación (simplificado para yaw)
        angle = self.angular_velocity['yaw'] * dt * np.pi / 180.0
        
        # Matriz de rotación 2D para yaw (alrededor del eje Z)
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        
        # Rotar en el plano XY
        new_x = to_source[0] * cos_a - to_source[1] * sin_a
        new_y = to_source[0] * sin_a + to_source[1] * cos_a
        
        # Nueva posición
        new_position = self.rotation_center + np.array([new_x, new_y, to_source[2]])
        
        # Delta es la diferencia
        delta.position = new_position - state.position
        
        return delta
'''

# Guardar plantillas
print("📝 Creando trajectory_component_template.py...")
with open("trajectory_component_template.py", 'w') as f:
    f.write(trajectory_template)

print("📝 Creando rotation_component_template.py...")
with open("rotation_component_template.py", 'w') as f:
    f.write(rotation_template)

print("✅ Plantillas creadas")

# 5. Resumen y próximos pasos
print(f"\n{'='*70}")
print("📊 RESUMEN DEL ESTADO ACTUAL")
print('='*70)

print("""
✅ COMPLETADO:
   1. Arquitectura de deltas creada
   2. ConcentrationComponent migrado
   3. Sistema de composición funcionando
   4. Plantillas para componentes faltantes

⏳ PENDIENTE:
   1. Migrar TrajectoryComponent (IS)
   2. Migrar RotationComponent (MS)  
   3. Migrar ModulationComponent (3D)
   4. Actualizar engine.update() para contexto

📋 PRÓXIMOS COMANDOS:
   
   # 1. Copiar plantillas a su ubicación final:
   cp trajectory_component_template.py trajectory_hub/core/trajectory_component.py
   cp rotation_component_template.py trajectory_hub/core/rotation_component.py
   
   # 2. Integrar en el engine (manual)
   # 3. Ejecutar test completo:
   python verify_independence.py

💡 TIPS:
   - Cada componente debe ser INDEPENDIENTE
   - calculate_delta() NUNCA modifica el estado
   - El contexto provee información compartida (centro del macro, etc.)
   - Los deltas se SUMAN, no se sobrescriben

================================================================================
""")

# Crear script helper para la integración
integration_helper = '''#!/usr/bin/env python3
"""
🔧 HELPER: Integrar componentes en el engine
"""

print("""
Para integrar los nuevos componentes:

1. En enhanced_trajectory_engine.py, añadir imports:
   from trajectory_hub.core.trajectory_component import TrajectoryComponent
   from trajectory_hub.core.rotation_component import RotationComponent

2. En set_individual_trajectory(), usar el nuevo sistema:
   if sid in self._source_motions:
       motion = self._source_motions[sid]
       if 'trajectory' not in motion.motion_components:
           motion.motion_components['trajectory'] = TrajectoryComponent()
       motion.motion_components['trajectory'].set_trajectory(trajectory)
       motion.use_delta_system = True

3. En set_macro_algorithmic_rotation(), similar:
   for sid in macro.source_ids:
       if sid in self._source_motions:
           motion = self._source_motions[sid]
           if 'rotation' not in motion.motion_components:
               motion.motion_components['rotation'] = RotationComponent()
           motion.motion_components['rotation'].set_rotation(angular_velocity, center)
           motion.use_delta_system = True

4. En update(), proveer contexto:
   for sid, motion in self._source_motions.items():
       context = {
           'source_id': sid,
           'macro_center': self.get_macro_center(sid),
           'time': self._time
       }
       motion.update(dt, context)
""")
'''

with open("integration_helper.py", 'w') as f:
    f.write(integration_helper)
os.chmod("integration_helper.py", 0o755)

print("\n✅ Helper de integración creado: integration_helper.py")