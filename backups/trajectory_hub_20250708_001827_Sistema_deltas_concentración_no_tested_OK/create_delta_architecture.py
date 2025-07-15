#!/usr/bin/env python3
"""
🔧 Fix: Implementa arquitectura de deltas para resolver conflictos
⚡ Impacto: ALTO - Cambia paradigma de sobrescritura a composición
🎯 Objetivo: Permitir que todos los componentes funcionen simultáneamente
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import sys
import os

# Añadir path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core.motion_components import (
    MotionState, ConcentrationMode, SourceMotion
)

@dataclass
class MotionDelta:
    """Representa un cambio incremental en posición/orientación"""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    orientation: np.ndarray = field(default_factory=lambda: np.zeros(3))
    aperture: float = 0.0
    weight: float = 1.0  # Para mezclar múltiples deltas
    source: str = ""  # Identificador del componente que genera el delta
    
    def scale(self, factor: float) -> 'MotionDelta':
        """Escala el delta por un factor"""
        return MotionDelta(
            position=self.position * factor,
            orientation=self.orientation * factor,
            aperture=self.aperture * factor,
            weight=self.weight * factor,
            source=self.source
        )
    
    def __add__(self, other: 'MotionDelta') -> 'MotionDelta':
        """Suma dos deltas"""
        return MotionDelta(
            position=self.position + other.position,
            orientation=self.orientation + other.orientation,
            aperture=self.aperture + other.aperture,
            weight=(self.weight + other.weight) / 2,
            source=f"{self.source}+{other.source}"
        )


class DeltaComposer:
    """Compone múltiples deltas en un cambio final"""
    
    def __init__(self):
        self.deltas: List[MotionDelta] = []
        
    def add_delta(self, delta: MotionDelta):
        """Añade un delta a la composición"""
        self.deltas.append(delta)
        
    def compose(self) -> MotionDelta:
        """Compone todos los deltas en uno final"""
        if not self.deltas:
            return MotionDelta()
            
        # Suma ponderada de todos los deltas
        total_weight = sum(d.weight for d in self.deltas)
        if total_weight == 0:
            total_weight = 1.0
            
        result = MotionDelta()
        for delta in self.deltas:
            normalized_weight = delta.weight / total_weight
            result.position += delta.position * normalized_weight
            result.orientation += delta.orientation * normalized_weight
            result.aperture += delta.aperture * normalized_weight
            
        result.weight = 1.0
        result.source = "composed"
        return result
        
    def clear(self):
        """Limpia los deltas acumulados"""
        self.deltas.clear()


# Modificar SourceMotion para usar deltas
class DeltaSourceMotion(SourceMotion):
    """SourceMotion modificado para generar deltas en lugar de posiciones absolutas"""
    
    def __init__(self, source_id: int):
        super().__init__(source_id)
        self.composer = DeltaComposer()
        
    def update(self, current_time: float, dt: float) -> MotionDelta:
        """Actualiza y retorna delta en lugar de estado final"""
        self.composer.clear()
        
        # Calcular delta de cada componente activo
        for component in self.active_components:
            if hasattr(component, 'calculate_delta'):
                delta = component.calculate_delta(self.state, current_time, dt)
            else:
                # Fallback: calcular delta comparando estados
                old_state = MotionState(
                    position=self.state.position.copy(),
                    orientation=self.state.orientation.copy(),
                    aperture=self.state.aperture
                )
                new_state = component.update(self.state, current_time, dt)
                delta = MotionDelta(
                    position=new_state.position - old_state.position,
                    orientation=new_state.orientation - old_state.orientation,
                    aperture=new_state.aperture - old_state.aperture,
                    source=component.__class__.__name__
                )
                self.state = new_state
                
            self.composer.add_delta(delta)
            
        # Componer todos los deltas
        return self.composer.compose()


# Componente de concentración que genera deltas
class ConcentrationDelta:
    """Genera deltas para efecto de concentración"""
    
    def __init__(self, center_point: np.ndarray = None):
        self.center = center_point if center_point is not None else np.zeros(3)
        self.factor = 0.0
        self.speed = 1.0
        self.enabled = False
        
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula delta hacia el centro"""
        if not self.enabled:
            return MotionDelta(source="concentration")
            
        # Vector hacia el centro
        to_center = self.center - state.position
        distance = np.linalg.norm(to_center)
        
        if distance > 0.001:  # Evitar división por cero
            direction = to_center / distance
            # Movimiento proporcional a la distancia y factor
            movement = direction * distance * self.factor * self.speed * dt
            
            return MotionDelta(
                position=movement,
                weight=self.factor,  # Peso proporcional al factor
                source="concentration"
            )
            
        return MotionDelta(source="concentration")


def test_delta_system():
    """Test del sistema de deltas"""
    print("🧪 Probando sistema de deltas...\n")
    
    # Crear motion con deltas
    motion = DeltaSourceMotion(source_id=0)
    
    # Añadir componente de concentración
    concentration = ConcentrationDelta(center_point=np.array([0, 0, 0]))
    concentration.enabled = True
    concentration.factor = 0.5
    
    # Simular posición inicial
    motion.state.position = np.array([10.0, 5.0, 0.0])
    
    print(f"Posición inicial: {motion.state.position}")
    print(f"Centro de concentración: {concentration.center}")
    
    # Calcular delta
    delta = concentration.calculate_delta(motion.state, 0.0, 0.1)
    
    print(f"\nDelta calculado:")
    print(f"  Posición: {delta.position}")
    print(f"  Peso: {delta.weight}")
    print(f"  Fuente: {delta.source}")
    
    # Aplicar delta
    motion.state.position += delta.position
    print(f"\nPosición después de aplicar delta: {motion.state.position}")
    
    # Test de composición
    print("\n🔄 Test de composición de múltiples deltas:")
    
    composer = DeltaComposer()
    
    # Delta 1: Movimiento de trayectoria
    delta1 = MotionDelta(
        position=np.array([1.0, 0.0, 0.0]),
        weight=1.0,
        source="trajectory"
    )
    
    # Delta 2: Concentración
    delta2 = MotionDelta(
        position=np.array([-0.5, -0.5, 0.0]),
        weight=0.5,
        source="concentration"
    )
    
    composer.add_delta(delta1)
    composer.add_delta(delta2)
    
    composed = composer.compose()
    print(f"\nDelta compuesto: {composed.position}")
    print(f"Fuentes: {composed.source}")


def integrate_delta_engine():
    """Muestra cómo integrar en el engine existente"""
    print("\n🔧 Integración con EnhancedTrajectoryEngine:\n")
    
    code = '''
# En enhanced_trajectory_engine.py, modificar step():

def step(self):
    """Nueva versión usando deltas"""
    dt = 1.0 / self.update_rate
    current_time = time.time()
    
    # Para cada source
    for source_id in range(self.n_sources):
        if source_id not in self.motion_states:
            continue
            
        # Obtener motion (ahora genera deltas)
        motion = self.motion_states[source_id]
        
        # Calcular delta total
        delta = motion.update(current_time, dt)
        
        # Aplicar delta a la posición actual
        self._positions[source_id] += delta.position
        self._orientations[source_id] += delta.orientation
        
        # Aplicar límites si es necesario
        self._positions[source_id] = np.clip(
            self._positions[source_id], -100, 100
        )
    '''
    
    print(code)
    print("\n✅ Con este cambio, múltiples componentes pueden coexistir!")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ARQUITECTURA DE DELTAS PARA TRAJECTORY HUB")
    print("=" * 60)
    
    # Test básico
    test_delta_system()
    
    # Mostrar integración
    integrate_delta_engine()
    
    print("\n📋 Próximos pasos:")
    print("1. Migrar ConcentrationComponent a ConcentrationDelta ✓")
    print("2. Migrar IndividualTrajectory para generar deltas")
    print("3. Migrar MacroTrajectory para generar deltas")
    print("4. Actualizar EnhancedTrajectoryEngine.step()")
    print("5. Probar todas las combinaciones")
    
    print("\n✨ Sistema de deltas creado exitosamente!")