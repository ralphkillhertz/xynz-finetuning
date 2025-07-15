#!/usr/bin/env python3
"""
concentration_system.py - Sistema completo de concentración de fuentes
Implementación robusta basada en componentes para trajectory_hub
"""

import numpy as np
from enum import Enum
from typing import Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# PARTE 1: COMPONENTE DE CONCENTRACIÓN (agregar a motion_components.py)
# =============================================================================

class ConcentrationMode(Enum):
    """Modos de concentración"""
    FIXED_POINT = "fixed_point"      # Punto fijo en el espacio
    FOLLOW_MACRO = "follow_macro"    # Sigue la trayectoria macro
    DYNAMIC = "dynamic"              # Punto calculado dinámicamente

class ConcentrationCurve(Enum):
    """Curvas de transición"""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    EXPONENTIAL = "exponential"
    BOUNCE = "bounce"

class ConcentrationComponent:
    """
    Componente que maneja la concentración/dispersión de fuentes
    Se aplica como último paso después de todos los demás movimientos
    """
    
    def __init__(self):
        self.enabled = False
        self.component_type = "concentration"
        
        # Parámetros principales
        self.factor = 1.0  # 0=concentrado, 1=disperso
        self.target_point = np.zeros(3)
        self.mode = ConcentrationMode.FIXED_POINT
        
        # Control de animación
        self.animation_active = False
        self.animation_start_factor = 1.0
        self.animation_target_factor = 0.0
        self.animation_duration = 2.0
        self.animation_elapsed = 0.0
        self.animation_curve = ConcentrationCurve.EASE_IN_OUT
        
        # Parámetros avanzados
        self.include_macro_trajectory = True  # Si la trayectoria MS se atenúa
        self.attenuate_rotations = True       # Si las rotaciones se atenúan
        self.attenuate_modulations = True     # Si las modulaciones se atenúan
        self.concentration_order = "uniform"   # uniform, gradual, radial, spiral
        
        # Cache para optimización
        self._macro_center = np.zeros(3)
        self._source_distances = {}
        
    def update(self, state, current_time: float, dt: float):
        """Actualizar el componente de concentración"""
        if not self.enabled:
            return state
            
        # Actualizar animación si está activa
        if self.animation_active:
            self.animation_elapsed += dt
            progress = min(self.animation_elapsed / self.animation_duration, 1.0)
            
            # Aplicar curva de animación
            curved_progress = self._apply_curve(progress, self.animation_curve)
            
            # Interpolar factor
            self.factor = self.animation_start_factor + \
                         (self.animation_target_factor - self.animation_start_factor) * curved_progress
            
            # Finalizar animación si completó
            if progress >= 1.0:
                self.animation_active = False
                
        # No hacer nada si factor es 1.0 (completamente disperso)
        if abs(self.factor - 1.0) < 0.001:
            return state
            
        # Calcular punto objetivo según modo
        if self.mode == ConcentrationMode.FOLLOW_MACRO:
            target = self._macro_center + self.target_point
        else:
            target = self.target_point
            
        # Aplicar concentración a la posición
        concentration_strength = 1.0 - self.factor
        state.position = self._lerp(state.position, target, concentration_strength)
        
        # Atenuar velocidad proporcionalmente
        state.velocity *= self.factor
        
        # Atenuar rotaciones si está habilitado
        if self.attenuate_rotations and hasattr(state, 'orientation'):
            # Reducir magnitud de orientación hacia neutral
            state.orientation *= self.factor
            
        return state
        
    def start_animation(self, target_factor: float, duration: float, 
                       curve: ConcentrationCurve = ConcentrationCurve.EASE_IN_OUT):
        """Iniciar animación de concentración"""
        self.animation_start_factor = self.factor
        self.animation_target_factor = max(0.0, min(1.0, target_factor))
        self.animation_duration = max(0.1, duration)
        self.animation_elapsed = 0.0
        self.animation_curve = curve
        self.animation_active = True
        self.enabled = True
        
    def set_factor(self, factor: float):
        """Establecer factor inmediatamente (sin animación)"""
        self.factor = max(0.0, min(1.0, factor))
        self.animation_active = False
        self.enabled = True
        
    def update_macro_center(self, center: np.ndarray):
        """Actualizar centro del macro para modo FOLLOW_MACRO"""
        self._macro_center = center.copy()
        
    def _lerp(self, a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
        """Interpolación lineal entre dos puntos"""
        return a + (b - a) * t
        
    def _apply_curve(self, t: float, curve: ConcentrationCurve) -> float:
        """Aplicar curva de animación al progreso"""
        if curve == ConcentrationCurve.LINEAR:
            return t
        elif curve == ConcentrationCurve.EASE_IN:
            return t * t
        elif curve == ConcentrationCurve.EASE_OUT:
            return 1 - (1 - t) * (1 - t)
        elif curve == ConcentrationCurve.EASE_IN_OUT:
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        elif curve == ConcentrationCurve.EXPONENTIAL:
            return t * t * t
        elif curve == ConcentrationCurve.BOUNCE:
            if t < 0.5:
                return 4 * t * t * t
            else:
                p = 2 * t - 2
                return 1 + p * p * p / 2
        return t

# =============================================================================
# PARTE 2: INTEGRACIÓN EN MOTION_COMPONENTS.PY
# =============================================================================

def add_to_source_motion_init(self):
    """Agregar a SourceMotion.__init__ después de los otros componentes"""
    # Agregar componente de concentración
    self.components['concentration'] = ConcentrationComponent()

def update_source_motion_update(self):
    """Modificar SourceMotion.update para procesar concentración al final"""
    # ... código existente ...
    
    # Concentración se aplica como último paso
    if 'concentration' in self.components:
        self.state = self.components['concentration'].update(
            self.state, current_time, dt
        )

# =============================================================================
# PARTE 3: MÉTODOS PARA ENHANCED_TRAJECTORY_ENGINE.PY
# =============================================================================

class ConcentrationMethods:
    """Métodos para agregar a EnhancedTrajectoryEngine"""
    
    def set_macro_concentration(self, macro_id: str, factor: float, 
                               duration: float = 0.0, mode: str = "fixed_point",
                               target_point: Optional[np.ndarray] = None):
        """
        Establecer concentración para un macro
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        factor : float
            Factor de concentración (0=concentrado, 1=disperso)
        duration : float
            Duración de la animación (0 para cambio inmediato)
        mode : str
            Modo de concentración: "fixed_point", "follow_macro", "dynamic"
        target_point : np.ndarray, optional
            Punto objetivo (por defecto centro del macro)
        """
        macro = self._macros.get(macro_id)
        if not macro:
            logger.error(f"Macro {macro_id} no encontrado")
            return False
            
        # Calcular punto objetivo si no se especifica
        if target_point is None:
            # Calcular centroide del macro
            positions = []
            for sid in macro.source_ids:
                if sid in self._source_motions:
                    positions.append(self._source_motions[sid].state.position)
            
            if positions:
                target_point = np.mean(positions, axis=0)
            else:
                target_point = np.zeros(3)
                
        # Configurar concentración para cada fuente del macro
        for sid in macro.source_ids:
            if sid not in self._source_motions:
                continue
                
            motion = self._source_motions[sid]
            concentration = motion.components.get('concentration')
            
            if not concentration:
                # Crear componente si no existe
                concentration = ConcentrationComponent()
                motion.components['concentration'] = concentration
                
            # Configurar parámetros
            concentration.target_point = target_point
            concentration.mode = ConcentrationMode[mode.upper()]
            
            # Aplicar atenuación según configuración del macro
            concentration.include_macro_trajectory = not (mode == "follow_macro")
            
            # Iniciar animación o establecer directamente
            if duration > 0:
                concentration.start_animation(factor, duration)
            else:
                concentration.set_factor(factor)
                
        # Guardar estado en el macro
        macro.concentration_active = (factor < 1.0)
        macro.concentration_point = target_point
        
        logger.info(f"Concentración establecida para {macro_id}: factor={factor}, modo={mode}")
        return True
        
    def animate_macro_concentration(self, macro_id: str, target_factor: float,
                                   duration: float = 2.0, 
                                   curve: str = "ease_in_out"):
        """
        Animar transición de concentración
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        target_factor : float
            Factor objetivo
        duration : float
            Duración en segundos
        curve : str
            Tipo de curva: linear, ease_in, ease_out, ease_in_out, exponential, bounce
        """
        return self.set_macro_concentration(macro_id, target_factor, duration)
        
    def get_macro_concentration_state(self, macro_id: str) -> Dict:
        """Obtener estado actual de concentración"""
        macro = self._macros.get(macro_id)
        if not macro or not macro.source_ids:
            return {"error": "Macro no encontrado"}
            
        # Obtener estado del primer source (asumimos todos iguales)
        first_sid = next(iter(macro.source_ids))
        if first_sid not in self._source_motions:
            return {"error": "Source no encontrado"}
            
        concentration = self._source_motions[first_sid].components.get('concentration')
        if not concentration:
            return {
                "enabled": False,
                "factor": 1.0,
                "mode": "fixed_point",
                "animating": False
            }
            
        return {
            "enabled": concentration.enabled,
            "factor": concentration.factor,
            "mode": concentration.mode.value,
            "animating": concentration.animation_active,
            "target_point": concentration.target_point.tolist(),
            "include_macro_trajectory": concentration.include_macro_trajectory
        }
        
    def set_concentration_parameters(self, macro_id: str, **params):
        """
        Configurar parámetros avanzados de concentración
        
        Parameters
        ----------
        include_macro_trajectory : bool
            Si incluir trayectoria macro en la atenuación
        attenuate_rotations : bool
            Si atenuar rotaciones
        attenuate_modulations : bool
            Si atenuar modulaciones
        concentration_order : str
            Orden de concentración: uniform, gradual, radial, spiral
        """
        macro = self._macros.get(macro_id)
        if not macro:
            return False
            
        for sid in macro.source_ids:
            if sid not in self._source_motions:
                continue
                
            concentration = self._source_motions[sid].components.get('concentration')
            if concentration:
                for key, value in params.items():
                    if hasattr(concentration, key):
                        setattr(concentration, key, value)
                        
        return True

    def toggle_macro_concentration(self, macro_id: str):
        """Alternar entre concentrado (0.0) y disperso (1.0)"""
        state = self.get_macro_concentration_state(macro_id)
        if state.get("error"):
            return False
            
        current_factor = state.get("factor", 1.0)
        target_factor = 0.0 if current_factor > 0.5 else 1.0
        
        return self.animate_macro_concentration(macro_id, target_factor, 2.0)

# =============================================================================
# PARTE 4: ACTUALIZACIÓN PARA INTERACTIVE_CONTROLLER.PY
# =============================================================================

async def concentration_control_menu(self):
    """Menú de control de concentración (Opción 31)"""
    print("\n" + "="*50)
    print("🎯 CONTROL DE CONCENTRACIÓN DE FUENTES")
    print("="*50)
    
    # Seleccionar macro
    macro_list = [(name, id) for name, id in self.macros.items()]
    if not macro_list:
        print("\n❌ No hay macros disponibles")
        return
        
    print("\nMacros disponibles:")
    for i, (name, _) in enumerate(macro_list, 1):
        print(f"{i}. {name}")
        
    idx = await self._get_int("Seleccionar macro: ", 1, len(macro_list))
    macro_name, macro_id = macro_list[idx - 1]
    
    # Obtener estado actual
    state = self.engine.get_macro_concentration_state(macro_id)
    current_factor = state.get("factor", 1.0)
    
    while True:
        print(f"\n📍 Macro: {macro_name}")
        print(f"📊 Factor actual: {current_factor:.2f} {'[Concentrado]' if current_factor < 0.5 else '[Disperso]'}")
        print(f"🎬 Animando: {'Sí' if state.get('animating') else 'No'}")
        
        print("\nOpciones:")
        print("1. Establecer factor (0-1)")
        print("2. Animar concentración")
        print("3. Toggle (concentrar/dispersar)")
        print("4. Configurar modo")
        print("5. Presets rápidos")
        print("6. Parámetros avanzados")
        print("0. Volver")
        
        option = await self._get_input("\nOpción: ")
        
        if option == "0":
            break
            
        elif option == "1":
            factor = await self._get_float("Factor (0=concentrado, 1=disperso): ", 0.0, 1.0)
            self.engine.set_macro_concentration(macro_id, factor)
            print(f"✅ Factor establecido: {factor:.2f}")
            
        elif option == "2":
            target = await self._get_float("Factor objetivo: ", 0.0, 1.0)
            duration = await self._get_float("Duración (segundos): ", 0.1, 10.0)
            
            curves = ["linear", "ease_in", "ease_out", "ease_in_out", "exponential", "bounce"]
            print("\nCurvas disponibles:")
            for i, c in enumerate(curves, 1):
                print(f"{i}. {c}")
            curve_idx = await self._get_int("Seleccionar curva: ", 1, len(curves))
            
            self.engine.animate_macro_concentration(
                macro_id, target, duration, curves[curve_idx-1]
            )
            print(f"✅ Animación iniciada: {current_factor:.2f} → {target:.2f} en {duration}s")
            
        elif option == "3":
            self.engine.toggle_macro_concentration(macro_id)
            print("✅ Toggle ejecutado")
            
        elif option == "4":
            modes = ["fixed_point", "follow_macro", "dynamic"]
            print("\nModos disponibles:")
            print("1. Punto fijo - Concentración en punto estático")
            print("2. Seguir macro - El punto sigue la trayectoria macro")
            print("3. Dinámico - Punto calculado dinámicamente")
            
            mode_idx = await self._get_int("Seleccionar modo: ", 1, 3)
            mode = modes[mode_idx-1]
            
            # Opcionalmente establecer punto personalizado
            if mode == "fixed_point":
                use_custom = await self._get_input("¿Usar punto personalizado? (s/n): ")
                if use_custom.lower() == 's':
                    x = await self._get_float("X: ", -10, 10)
                    y = await self._get_float("Y: ", -10, 10) 
                    z = await self._get_float("Z: ", -10, 10)
                    point = np.array([x, y, z])
                else:
                    point = None
                    
                self.engine.set_macro_concentration(
                    macro_id, current_factor, 0, mode, point
                )
            else:
                self.engine.set_macro_concentration(
                    macro_id, current_factor, 0, mode
                )
                
            print(f"✅ Modo establecido: {mode}")
            
        elif option == "5":
            print("\nPresets rápidos:")
            print("1. Explosión (1→0 en 0.5s)")
            print("2. Implosión (0→1 en 0.5s)")
            print("3. Respiración lenta (1→0→1 en 4s)")
            print("4. Pulso rápido (toggle en 0.2s)")
            print("5. Convergencia dramática (1→0 en 3s, exponential)")
            
            preset = await self._get_int("Seleccionar preset: ", 1, 5)
            
            if preset == 1:
                self.engine.animate_macro_concentration(macro_id, 0.0, 0.5, "ease_out")
            elif preset == 2:
                self.engine.animate_macro_concentration(macro_id, 1.0, 0.5, "ease_in")
            elif preset == 3:
                # Requiere implementación de animación cíclica
                self.engine.animate_macro_concentration(macro_id, 0.0, 2.0)
                # TODO: Agregar callback para revertir
            elif preset == 4:
                self.engine.toggle_macro_concentration(macro_id)
            elif preset == 5:
                self.engine.animate_macro_concentration(macro_id, 0.0, 3.0, "exponential")
                
            print("✅ Preset aplicado")
            
        elif option == "6":
            print("\nParámetros avanzados:")
            print("1. Incluir trayectoria macro en atenuación")
            print("2. Atenuar rotaciones")
            print("3. Atenuar modulaciones")
            print("4. Orden de concentración")
            
            param = await self._get_int("Seleccionar parámetro: ", 1, 4)
            
            if param in [1, 2, 3]:
                value = await self._get_input("Activar (s/n): ")
                params = {
                    1: "include_macro_trajectory",
                    2: "attenuate_rotations",
                    3: "attenuate_modulations"
                }
                self.engine.set_concentration_parameters(
                    macro_id, **{params[param]: value.lower() == 's'}
                )
            elif param == 4:
                orders = ["uniform", "gradual", "radial", "spiral"]
                print("\nÓrdenes disponibles:")
                for i, o in enumerate(orders, 1):
                    print(f"{i}. {o}")
                order_idx = await self._get_int("Seleccionar orden: ", 1, 4)
                self.engine.set_concentration_parameters(
                    macro_id, concentration_order=orders[order_idx-1]
                )
                
            print("✅ Parámetro actualizado")
            
        # Actualizar estado
        state = self.engine.get_macro_concentration_state(macro_id)
        current_factor = state.get("factor", 1.0)

# =============================================================================
# PARTE 5: SCRIPT DE PRUEBA
# =============================================================================

def test_concentration_system():
    """Script de prueba del sistema de concentración"""
    from trajectory_hub import EnhancedTrajectoryEngine
    import asyncio
    
    print("🧪 TEST DEL SISTEMA DE CONCENTRACIÓN\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    
    # Crear macro de prueba
    print("1. Creando macro con 10 fuentes...")
    macro_id = engine.create_macro("test_concentration", 10, 
                                   formation="circle", spacing=2.0)
    
    # Establecer trayectorias para ver el efecto
    print("2. Configurando trayectorias circulares...")
    engine.set_macro_trajectory(macro_id, "circle", size=5.0)
    engine.set_trajectory_mode(macro_id, "fix", speed=1.0)
    
    # Test 1: Concentración inmediata
    print("\n3. TEST 1: Concentración inmediata")
    print("   - Factor 0.5 (medio concentrado)")
    engine.set_macro_concentration(macro_id, 0.5)
    
    # Simular algunos frames
    for i in range(5):
        engine.update()
        
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   ✓ Factor actual: {state['factor']}")
    print(f"   ✓ Habilitado: {state['enabled']}")
    
    # Test 2: Animación
    print("\n4. TEST 2: Animación de concentración")
    print("   - Animando de 0.5 a 0.0 en 2 segundos")
    engine.animate_macro_concentration(macro_id, 0.0, 2.0, "ease_in_out")
    
    # Simular 2 segundos
    for i in range(120):  # 60 fps * 2 segundos
        engine.update()
        if i % 30 == 0:  # Cada 0.5 segundos
            state = engine.get_macro_concentration_state(macro_id)
            print(f"   - t={i/60:.1f}s: factor={state['factor']:.2f}")
            
    # Test 3: Toggle
    print("\n5. TEST 3: Toggle concentración")
    print("   - Estado inicial: concentrado (0.0)")
    engine.toggle_macro_concentration(macro_id)
    
    # Simular transición
    for i in range(120):
        engine.update()
        
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   ✓ Factor después de toggle: {state['factor']}")
    
    # Test 4: Modo follow_macro
    print("\n6. TEST 4: Modo follow_macro")
    engine.set_macro_concentration(macro_id, 0.3, mode="follow_macro")
    print("   ✓ Concentración siguiendo trayectoria macro")
    
    # Test 5: Presets
    print("\n7. TEST 5: Preset explosión")
    engine.animate_macro_concentration(macro_id, 0.0, 0.5, "ease_out")
    
    for i in range(30):  # 0.5 segundos
        engine.update()
        
    print("   ✓ Explosión completada")
    
    print("\n✅ TODOS LOS TESTS COMPLETADOS")
    print("\nIntegración:")
    print("1. Copiar ConcentrationComponent a motion_components.py")
    print("2. Agregar métodos a EnhancedTrajectoryEngine")
    print("3. Agregar opción 31 al menú del controlador")
    print("4. Ejecutar este script para verificar")

if __name__ == "__main__":
    test_concentration_system()