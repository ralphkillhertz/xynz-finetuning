#!/usr/bin/env python3
"""
integrate_concentration.py - Integra automáticamente el sistema de concentración
Este script aplica todos los cambios necesarios en los archivos del proyecto
"""

import os
import re
import shutil
from datetime import datetime

class ConcentrationIntegrator:
    def __init__(self):
        self.changes_made = []
        self.backups = []
        
    def backup_file(self, filepath):
        """Crear backup de un archivo"""
        if os.path.exists(filepath):
            backup_name = f"{filepath}.backup_concentration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(filepath, backup_name)
            self.backups.append(backup_name)
            return backup_name
        return None
        
    def integrate_motion_components(self):
        """Integrar ConcentrationComponent en motion_components.py"""
        print("\n1️⃣ INTEGRANDO EN motion_components.py...")
        
        filepath = "trajectory_hub/core/motion_components.py"
        if not os.path.exists(filepath):
            print(f"   ❌ No se encuentra {filepath}")
            return False
            
        # Backup
        self.backup_file(filepath)
        
        # Leer archivo
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. Agregar imports
        if "from enum import Enum" not in content:
            # Agregar después de los imports numpy
            import_pos = content.find("import numpy as np")
            if import_pos != -1:
                import_pos = content.find("\n", import_pos) + 1
                content = content[:import_pos] + "from enum import Enum\n" + content[import_pos:]
                
        # 2. Agregar enums de concentración
        concentration_enums = '''
# Enums para el sistema de concentración
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
'''
        
        # Insertar antes de la primera clase Component
        if "class ConcentrationMode" not in content:
            class_pos = content.find("class MotionComponent")
            if class_pos != -1:
                content = content[:class_pos] + concentration_enums + "\n" + content[class_pos:]
                
        # 3. Agregar ConcentrationComponent
        concentration_component = '''
class ConcentrationComponent(MotionComponent):
    """
    Componente que maneja la concentración/dispersión de fuentes
    Se aplica como último paso después de todos los demás movimientos
    """
    
    def __init__(self):
        super().__init__("concentration")
        
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
        self.include_macro_trajectory = True
        self.attenuate_rotations = True
        self.attenuate_modulations = True
        self.concentration_order = "uniform"
        
        # Cache
        self._macro_center = np.zeros(3)
        self._source_distances = {}
        
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        """Actualizar el componente de concentración"""
        if not self.enabled:
            return state
            
        # Actualizar animación
        if self.animation_active:
            self.animation_elapsed += dt
            progress = min(self.animation_elapsed / self.animation_duration, 1.0)
            
            # Aplicar curva
            curved_progress = self._apply_curve(progress, self.animation_curve)
            
            # Interpolar factor
            self.factor = self.animation_start_factor + \\
                         (self.animation_target_factor - self.animation_start_factor) * curved_progress
            
            if progress >= 1.0:
                self.animation_active = False
                
        # No hacer nada si completamente disperso
        if abs(self.factor - 1.0) < 0.001:
            return state
            
        # Calcular punto objetivo
        if self.mode == ConcentrationMode.FOLLOW_MACRO:
            target = self._macro_center + self.target_point
        else:
            target = self.target_point
            
        # Aplicar concentración
        concentration_strength = 1.0 - self.factor
        state.position = self._lerp(state.position, target, concentration_strength)
        
        # Atenuar velocidad
        state.velocity *= self.factor
        
        # Atenuar orientación si está habilitado
        if self.attenuate_rotations:
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
        """Establecer factor inmediatamente"""
        self.factor = max(0.0, min(1.0, factor))
        self.animation_active = False
        self.enabled = True
        
    def update_macro_center(self, center: np.ndarray):
        """Actualizar centro del macro"""
        self._macro_center = center.copy()
        
    def _lerp(self, a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
        """Interpolación lineal"""
        return a + (b - a) * t
        
    def _apply_curve(self, t: float, curve: ConcentrationCurve) -> float:
        """Aplicar curva de animación"""
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
'''
        
        # Insertar al final del archivo
        if "class ConcentrationComponent" not in content:
            content = content.rstrip() + "\n\n" + concentration_component + "\n"
            
        # 4. Actualizar SourceMotion.__init__
        init_search = "self.components\['environmental_forces'\] = EnvironmentalForces()"
        if init_search in content:
            init_pos = content.find(init_search)
            if init_pos != -1:
                init_pos = content.find("\n", init_pos) + 1
                add_component = "        self.components['concentration'] = ConcentrationComponent()\n"
                if "self.components['concentration']" not in content:
                    content = content[:init_pos] + add_component + content[init_pos:]
                    
        # 5. Actualizar SourceMotion.update para incluir concentración al final
        update_search = "# Aplicar fuerzas ambientales"
        if update_search in content:
            # Buscar el final del método update
            update_pos = content.find(update_search)
            if update_pos != -1:
                # Buscar el return state
                return_pos = content.find("return self.state", update_pos)
                if return_pos != -1:
                    concentration_update = '''
        # Concentración se aplica como último paso
        if 'concentration' in self.components:
            self.state = self.components['concentration'].update(
                self.state, current_time, dt
            )
        
        '''
                    if "# Concentración se aplica como último paso" not in content:
                        content = content[:return_pos] + concentration_update + content[return_pos:]
                        
        # Guardar archivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("   ✅ ConcentrationComponent integrado")
        self.changes_made.append("motion_components.py: Added ConcentrationComponent")
        return True
        
    def integrate_engine_methods(self):
        """Integrar métodos en enhanced_trajectory_engine.py"""
        print("\n2️⃣ INTEGRANDO EN enhanced_trajectory_engine.py...")
        
        filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
        if not os.path.exists(filepath):
            print(f"   ❌ No se encuentra {filepath}")
            return False
            
        # Backup
        self.backup_file(filepath)
        
        # Leer archivo
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Agregar imports necesarios
        if "ConcentrationMode" not in content:
            # Buscar el import de motion_components
            import_search = "from trajectory_hub.core.motion_components import"
            import_pos = content.find(import_search)
            if import_pos != -1:
                # Encontrar el final del import
                paren_pos = content.find(")", import_pos)
                if paren_pos != -1:
                    # Agregar las nuevas clases
                    content = content[:paren_pos] + ",\n    ConcentrationComponent, ConcentrationMode, ConcentrationCurve" + content[paren_pos:]
                    
        # Métodos de concentración
        concentration_methods = '''
    # =========== SISTEMA DE CONCENTRACIÓN ===========
    
    def set_macro_concentration(self, macro_id: str, factor: float, 
                               duration: float = 0.0, mode: str = "fixed_point",
                               target_point: Optional[np.ndarray] = None) -> bool:
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
            Modo: "fixed_point", "follow_macro", "dynamic"
        target_point : np.ndarray, optional
            Punto objetivo (por defecto centro del macro)
            
        Returns
        -------
        bool
            True si se aplicó correctamente
        """
        macro = self._macros.get(macro_id)
        if not macro:
            logger.error(f"Macro {macro_id} no encontrado")
            return False
            
        # Calcular punto objetivo si no se especifica
        if target_point is None:
            positions = []
            for sid in macro.source_ids:
                if sid in self._source_motions:
                    positions.append(self._source_motions[sid].state.position)
            
            if positions:
                target_point = np.mean(positions, axis=0)
            else:
                target_point = np.zeros(3)
                
        # Configurar concentración para cada fuente
        for sid in macro.source_ids:
            if sid not in self._source_motions:
                continue
                
            motion = self._source_motions[sid]
            
            # Obtener o crear componente
            if 'concentration' not in motion.components:
                motion.components['concentration'] = ConcentrationComponent()
                
            concentration = motion.components['concentration']
            
            # Configurar parámetros
            concentration.target_point = target_point
            concentration.mode = ConcentrationMode[mode.upper().replace(" ", "_")]
            
            # Configurar atenuación
            concentration.include_macro_trajectory = not (mode == "follow_macro")
            
            # Aplicar
            if duration > 0:
                concentration.start_animation(factor, duration)
            else:
                concentration.set_factor(factor)
                
        # Guardar estado en macro
        macro.concentration_active = (factor < 1.0)
        macro.concentration_point = target_point
        
        logger.info(f"Concentración establecida para {macro_id}: factor={factor}")
        return True
        
    def animate_macro_concentration(self, macro_id: str, target_factor: float,
                                   duration: float = 2.0, 
                                   curve: str = "ease_in_out") -> bool:
        """Animar transición de concentración"""
        macro = self._macros.get(macro_id)
        if not macro:
            return False
            
        # Convertir string a enum
        curve_enum = ConcentrationCurve[curve.upper().replace(" ", "_")]
        
        for sid in macro.source_ids:
            if sid in self._source_motions:
                concentration = self._source_motions[sid].components.get('concentration')
                if concentration:
                    concentration.animation_curve = curve_enum
                    
        return self.set_macro_concentration(macro_id, target_factor, duration)
        
    def get_macro_concentration_state(self, macro_id: str) -> Dict:
        """Obtener estado actual de concentración"""
        macro = self._macros.get(macro_id)
        if not macro or not macro.source_ids:
            return {"error": "Macro no encontrado"}
            
        # Obtener del primer source
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
        
    def toggle_macro_concentration(self, macro_id: str) -> bool:
        """Alternar entre concentrado y disperso"""
        state = self.get_macro_concentration_state(macro_id)
        if state.get("error"):
            return False
            
        current_factor = state.get("factor", 1.0)
        target_factor = 0.0 if current_factor > 0.5 else 1.0
        
        return self.animate_macro_concentration(macro_id, target_factor, 2.0)
        
    def set_concentration_parameters(self, macro_id: str, **params) -> bool:
        """Configurar parámetros avanzados de concentración"""
        macro = self._macros.get(macro_id)
        if not macro:
            return False
            
        for sid in macro.source_ids:
            if sid in self._source_motions:
                concentration = self._source_motions[sid].components.get('concentration')
                if concentration:
                    for key, value in params.items():
                        if hasattr(concentration, key):
                            setattr(concentration, key, value)
                            
        return True
'''
        
        # Insertar antes del final de la clase
        class_end = content.rfind("\nclass ")
        if class_end == -1:
            class_end = len(content)
            
        # Buscar un buen lugar para insertar (después de otros métodos)
        insert_pos = content.rfind("        return True", 0, class_end)
        if insert_pos != -1:
            insert_pos = content.find("\n", insert_pos) + 1
            
            if "def set_macro_concentration" not in content:
                content = content[:insert_pos] + concentration_methods + content[insert_pos:]
                
        # Guardar archivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("   ✅ Métodos de concentración agregados")
        self.changes_made.append("enhanced_trajectory_engine.py: Added concentration methods")
        return True
        
    def integrate_controller_menu(self):
        """Integrar menú en interactive_controller.py"""
        print("\n3️⃣ INTEGRANDO EN interactive_controller.py...")
        
        filepath = "trajectory_hub/interface/interactive_controller.py"
        if not os.path.exists(filepath):
            print(f"   ❌ No se encuentra {filepath}")
            return False
            
        # Backup
        self.backup_file(filepath)
        
        # Leer archivo
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. Agregar opción al menú principal
        menu_search = "30. 💠 Control de Modulador de Orientación"
        if menu_search in content and "31. 🎯 Control de Concentración" not in content:
            menu_pos = content.find(menu_search)
            if menu_pos != -1:
                menu_pos = content.find("\n", menu_pos) + 1
                content = content[:menu_pos] + "            print(\"31. 🎯 Control de Concentración\")\n" + content[menu_pos:]
                
        # 2. Agregar handler para opción 31
        handler_search = 'elif choice == "30":'
        if handler_search in content and 'elif choice == "31":' not in content:
            handler_pos = content.find(handler_search)
            if handler_pos != -1:
                # Buscar el final del bloque elif
                next_elif = content.find('\n            elif choice', handler_pos + 1)
                if next_elif == -1:
                    next_elif = content.find('\n            else:', handler_pos)
                if next_elif != -1:
                    handler_code = '''
            elif choice == "31":
                await self.concentration_control_menu()
'''
                    content = content[:next_elif] + handler_code + content[next_elif:]
                    
        # 3. Agregar método del menú de concentración
        concentration_menu = '''
    async def concentration_control_menu(self):
        """Control de concentración de fuentes (Opción 31)"""
        print("\\n" + "="*50)
        print("🎯 CONTROL DE CONCENTRACIÓN DE FUENTES")
        print("="*50)
        
        # Seleccionar macro
        macro_list = [(name, id) for name, id in self.macros.items()]
        if not macro_list:
            print("\\n❌ No hay macros disponibles")
            return
            
        print("\\nMacros disponibles:")
        for i, (name, _) in enumerate(macro_list, 1):
            print(f"{i}. {name}")
            
        idx = await self._get_int("Seleccionar macro: ", 1, len(macro_list))
        macro_name, macro_id = macro_list[idx - 1]
        
        while True:
            # Obtener estado
            state = self.engine.get_macro_concentration_state(macro_id)
            if "error" in state:
                print(f"\\n❌ {state['error']}")
                break
                
            factor = state.get("factor", 1.0)
            
            print(f"\\n📍 Macro: {macro_name}")
            print(f"📊 Factor: {factor:.2f} {'[Concentrado]' if factor < 0.5 else '[Disperso]'}")
            print(f"🎬 Animando: {'Sí' if state.get('animating') else 'No'}")
            print(f"📌 Modo: {state.get('mode', 'fixed_point')}")
            
            print("\\nOpciones:")
            print("1. Establecer factor (0-1)")
            print("2. Animar concentración")
            print("3. Toggle (concentrar/dispersar)")
            print("4. Configurar modo")
            print("5. Presets rápidos")
            print("0. Volver")
            
            option = await self._get_input("\\nOpción: ")
            
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
                print("\\nCurvas disponibles:")
                for i, c in enumerate(curves, 1):
                    print(f"{i}. {c}")
                curve_idx = await self._get_int("Seleccionar curva: ", 1, len(curves))
                
                self.engine.animate_macro_concentration(
                    macro_id, target, duration, curves[curve_idx-1]
                )
                print(f"✅ Animación iniciada")
                
            elif option == "3":
                self.engine.toggle_macro_concentration(macro_id)
                print("✅ Toggle ejecutado")
                
            elif option == "4":
                print("\\nModos disponibles:")
                print("1. Punto fijo")
                print("2. Seguir macro")
                
                mode_idx = await self._get_int("Seleccionar modo: ", 1, 2)
                mode = ["fixed_point", "follow_macro"][mode_idx-1]
                
                self.engine.set_macro_concentration(macro_id, factor, 0, mode)
                print(f"✅ Modo establecido: {mode}")
                
            elif option == "5":
                print("\\nPresets:")
                print("1. Explosión (dispersar en 0.5s)")
                print("2. Implosión (concentrar en 0.5s)")
                print("3. Pulso (toggle rápido)")
                print("4. Convergencia dramática (3s)")
                
                preset = await self._get_int("Seleccionar preset: ", 1, 4)
                
                if preset == 1:
                    self.engine.animate_macro_concentration(macro_id, 1.0, 0.5, "ease_out")
                elif preset == 2:
                    self.engine.animate_macro_concentration(macro_id, 0.0, 0.5, "ease_in")
                elif preset == 3:
                    self.engine.toggle_macro_concentration(macro_id)
                elif preset == 4:
                    self.engine.animate_macro_concentration(macro_id, 0.0, 3.0, "exponential")
                    
                print("✅ Preset aplicado")
'''
        
        # Insertar al final de la clase
        if "async def concentration_control_menu" not in content:
            # Buscar el final de la clase
            class_end = content.rfind("\n\nif __name__")
            if class_end == -1:
                class_end = len(content)
                
            content = content[:class_end] + "\n" + concentration_menu + content[class_end:]
            
        # Guardar archivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("   ✅ Menú de concentración agregado")
        self.changes_made.append("interactive_controller.py: Added concentration menu")
        return True
        
    def create_test_script(self):
        """Crear script de prueba"""
        print("\n4️⃣ CREANDO SCRIPT DE PRUEBA...")
        
        test_script = '''#!/usr/bin/env python3
"""
test_concentration.py - Prueba del sistema de concentración
"""

import asyncio
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

async def test_concentration():
    print("🧪 TEST DEL SISTEMA DE CONCENTRACIÓN\\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    
    # Crear macro de prueba
    print("1. Creando macro con 10 fuentes...")
    macro_id = engine.create_macro("test_concentration", 10, 
                                   formation="circle", spacing=2.0)
    
    # Configurar movimiento
    print("2. Configurando trayectorias...")
    engine.set_macro_trajectory(macro_id, "circle", size=5.0)
    engine.set_trajectory_mode(macro_id, "fix", speed=1.0)
    
    # Test concentración inmediata
    print("\\n3. Test concentración inmediata (factor 0.5)")
    engine.set_macro_concentration(macro_id, 0.5)
    
    # Actualizar algunos frames
    for _ in range(30):
        engine.update()
        
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   ✓ Factor: {state['factor']}")
    print(f"   ✓ Habilitado: {state['enabled']}")
    
    # Test animación
    print("\\n4. Test animación (0.5 → 0.0 en 2s)")
    engine.animate_macro_concentration(macro_id, 0.0, 2.0)
    
    # Simular 2 segundos
    for i in range(120):
        engine.update()
        if i % 60 == 0:
            state = engine.get_macro_concentration_state(macro_id)
            print(f"   - {i/60}s: factor={state['factor']:.2f}")
            
    # Test toggle
    print("\\n5. Test toggle")
    engine.toggle_macro_concentration(macro_id)
    
    for _ in range(120):
        engine.update()
        
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   ✓ Factor después de toggle: {state['factor']}")
    
    print("\\n✅ TESTS COMPLETADOS")

if __name__ == "__main__":
    asyncio.run(test_concentration())
'''
        
        with open("test_concentration.py", 'w', encoding='utf-8') as f:
            f.write(test_script)
            
        print("   ✅ test_concentration.py creado")
        self.changes_made.append("Created test_concentration.py")
        return True
        
    def run_integration(self):
        """Ejecutar la integración completa"""
        print("="*60)
        print("🚀 INTEGRACIÓN AUTOMÁTICA DEL SISTEMA DE CONCENTRACIÓN")
        print("="*60)
        
        success = True
        
        # Ejecutar cada paso
        success &= self.integrate_motion_components()
        success &= self.integrate_engine_methods()
        success &= self.integrate_controller_menu()
        success &= self.create_test_script()
        
        print("\n" + "="*60)
        
        if success:
            print("✅ INTEGRACIÓN COMPLETADA EXITOSAMENTE")
            print("\nCambios realizados:")
            for change in self.changes_made:
                print(f"   - {change}")
                
            print("\nBackups creados:")
            for backup in self.backups:
                print(f"   - {backup}")
                
            print("\nPróximos pasos:")
            print("1. Ejecutar: python fix_concentration_update.py")
            print("2. Ejecutar: python test_concentration.py")
            print("3. Usar opción 31 en el controlador interactivo")
        else:
            print("❌ Hubo errores durante la integración")
            print("   Revisa los mensajes anteriores")
            
        return success

def main():
    integrator = ConcentrationIntegrator()
    integrator.run_integration()

if __name__ == "__main__":
    main()