#!/usr/bin/env python3
"""
test_modulator_integration.py - Prueba completa del sistema de modulación 3D
VERSIÓN CORREGIDA
"""
import asyncio
import time
import numpy as np
from typing import List, Dict
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Imports del proyecto
from trajectory_hub import EnhancedTrajectoryEngine, SpatOSCBridge, OSCTarget
from trajectory_hub.core.motion_components import AdvancedOrientationModulation


class ModulatorIntegrationTest:
    """Clase para probar la integración completa del modulador"""
    
    def __init__(self, osc_host: str = "127.0.0.1", osc_port: int = 9000):
        """Inicializar sistema de pruebas"""
        # Crear motor con modulador habilitado
        self.engine = EnhancedTrajectoryEngine(
            max_sources=50,  # Corregido
            fps=120,         # Corregido
            enable_modulator=True
        )
        
        # Configurar OSC
        self.osc_bridge = SpatOSCBridge(
            targets=[OSCTarget(osc_host, osc_port, name="Spat")],
            fps=120,
            source_offset=1
        )
        
        self.engine.set_osc_bridge(self.osc_bridge)
        
        # Estado de la prueba
        self.test_results = {}
        self.running = False
        
    def test_basic_modulation(self):
        """Test 1: Modulación básica en una fuente"""
        print("\n🧪 TEST 1: Modulación Básica")
        print("-" * 50)
        
        try:
            # Crear macro con una sola fuente
            macro_id = self.engine.create_macro(
                name="test_single",
                source_count=1,
                formation="point"
            )
            
            # Aplicar preset de respiración
            success = self.engine.apply_orientation_preset(
                macro_id,
                "respiración_suave",
                intensity=1.0
            )
            
            if success:
                print("✅ Preset aplicado correctamente")
                
                # Obtener la primera fuente del macro
                macro = self.engine._macros[macro_id]
                first_source_id = next(iter(macro.source_ids))
                
                # Verificar que el modulador existe
                modulator = self.engine.orientation_modulators.get(first_source_id)
                if modulator and modulator.enabled:
                    print("✅ Modulador creado y activo")
                    print(f"   - Forma: {modulator.modulation_shape}")
                    print(f"   - Velocidad: {modulator.lfo_frequency} Hz")
                    print(f"   - Intensidad: {modulator.intensity}")
                    self.test_results["basic_modulation"] = "PASSED"
                else:
                    print("❌ Modulador no encontrado o inactivo")
                    self.test_results["basic_modulation"] = "FAILED"
            else:
                print("❌ Error aplicando preset")
                self.test_results["basic_modulation"] = "FAILED"
                
        except Exception as e:
            print(f"❌ Error en test: {e}")
            self.test_results["basic_modulation"] = "ERROR"
            
    def test_multi_source_modulation(self):
        """Test 2: Modulación en múltiples fuentes con desfase"""
        print("\n🧪 TEST 2: Modulación Multi-Fuente")
        print("-" * 50)
        
        try:
            # Crear macro con 10 fuentes
            macro_id = self.engine.create_macro(
                name="test_multi",
                source_count=10,
                formation="line",
                spacing=1.0
            )
            
            # Aplicar preset con desfase temporal
            self.engine.apply_orientation_preset(
                macro_id,
                "lissajous_complejo",
                intensity=0.8,
                time_offset_spread=0.2
            )
            
            # Verificar moduladores
            macro = self.engine._macros[macro_id]
            source_list = list(macro.source_ids)
            
            all_active = True
            for i, sid in enumerate(source_list):
                mod = self.engine.orientation_modulators.get(sid)
                if mod:
                    expected_offset = i * 0.2
                    if abs(mod.time_offset - expected_offset) < 0.01:
                        print(f"✅ Fuente {sid}: offset = {mod.time_offset:.2f}s")
                    else:
                        print(f"❌ Fuente {sid}: offset incorrecto")
                        all_active = False
                else:
                    print(f"❌ Fuente {sid}: sin modulador")
                    all_active = False
                    
            self.test_results["multi_source_modulation"] = "PASSED" if all_active else "FAILED"
            
        except Exception as e:
            print(f"❌ Error en test: {e}")
            self.test_results["multi_source_modulation"] = "ERROR"
            
    def test_preset_interpolation(self):
        """Test 3: Interpolación entre presets"""
        print("\n🧪 TEST 3: Interpolación de Presets")
        print("-" * 50)
        
        try:
            # Crear macro
            macro_id = self.engine.create_macro(
                name="test_interp",
                source_count=1,
                formation="point"
            )
            
            # Obtener la primera fuente
            macro = self.engine._macros[macro_id]
            first_source_id = next(iter(macro.source_ids))
            
            # Obtener valores de dos presets
            modulator = self.engine.create_orientation_modulator(first_source_id)
            
            # Aplicar primer preset
            modulator.apply_preset("respiración_suave")
            lfo1 = modulator.lfo_frequency
            aperture1 = modulator.aperture_base
            
            # Aplicar segundo preset
            modulator.apply_preset("nervioso_aleatorio")
            lfo2 = modulator.lfo_frequency
            aperture2 = modulator.aperture_base
            
            # Interpolar al 50%
            self.engine.interpolate_orientation_presets(
                macro_id,
                "respiración_suave",
                "nervioso_aleatorio",
                0.5
            )
            
            # Verificar interpolación
            expected_lfo = (lfo1 + lfo2) / 2
            expected_aperture = (aperture1 + aperture2) / 2
            
            if abs(modulator.lfo_frequency - expected_lfo) < 0.01:
                print(f"✅ LFO interpolado correctamente: {modulator.lfo_frequency:.2f} Hz")
                self.test_results["preset_interpolation"] = "PASSED"
            else:
                print(f"❌ LFO incorrecto: esperado {expected_lfo:.2f}, obtenido {modulator.lfo_frequency:.2f}")
                self.test_results["preset_interpolation"] = "FAILED"
                
        except Exception as e:
            print(f"❌ Error en test: {e}")
            self.test_results["preset_interpolation"] = "ERROR"
            
    def test_osc_transmission(self):
        """Test 4: Verificar transmisión OSC de orientaciones"""
        print("\n🧪 TEST 4: Transmisión OSC")
        print("-" * 50)
        
        try:
            # Crear macro
            macro_id = self.engine.create_macro(
                name="test_osc",
                source_count=3,
                formation="triangle",
                spacing=2.0
            )
            
            # Aplicar modulación activa
            self.engine.apply_orientation_preset(
                macro_id,
                "rotación_mecánica",
                intensity=1.0
            )
            
            # Ejecutar algunas actualizaciones
            print("Enviando actualizaciones OSC...")
            for i in range(10):
                self.engine.update(1/120.0)
                time.sleep(0.05)
                
            # Verificar estadísticas OSC
            stats = self.osc_bridge.get_stats()
            
            print(f"\n📊 Estadísticas OSC:")
            print(f"   - Mensajes enviados: {stats['messages_sent']}")
            print(f"   - Orientaciones enviadas: {stats['parameters_sent']['orientations']}")
            print(f"   - Aperturas enviadas: {stats['parameters_sent']['apertures']}")
            print(f"   - Errores: {stats['messages_failed']}")
            
            if stats['parameters_sent']['orientations'] > 0:
                print("✅ Orientaciones transmitidas correctamente")
                self.test_results["osc_transmission"] = "PASSED"
            else:
                print("❌ No se enviaron orientaciones")
                self.test_results["osc_transmission"] = "FAILED"
                
        except Exception as e:
            print(f"❌ Error en test: {e}")
            self.test_results["osc_transmission"] = "ERROR"
            
    def test_combined_movement(self):
        """Test 5: Movimiento combinado (trayectoria + modulación)"""
        print("\n🧪 TEST 5: Movimiento Combinado")
        print("-" * 50)
        
        try:
            # Crear macro con trayectoria y modulación
            macro_id = self.engine.create_macro(
                name="test_combined",
                source_count=5,
                formation="circle",
                spacing=1.5
            )
            
            # Configurar trayectoria circular del macro
            def circular_trajectory(t):
                return np.array([
                    5.0 * np.cos(t),
                    5.0 * np.sin(t),
                    0.0
                ])
                
            # Crear una función de trayectoria que incluya la velocidad
            def trajectory_with_speed(t):
                # t ya viene escalado por la velocidad del motor
                return circular_trajectory(t * 0.2)
                
            self.engine.set_macro_trajectory(
                macro_id,
                trajectory_with_speed
            )
            
            # Aplicar modulación de orientación
            self.engine.apply_orientation_preset(
                macro_id,
                "flotación_oceánica",
                intensity=0.7
            )
            
            print("✅ Configuración aplicada:")
            print("   - Trayectoria: circular (r=5.0)")
            print("   - Modulación: flotación oceánica")
            print("   - Combinación: las fuentes giran en círculo mientras modulan su orientación")
            
            # Verificar estados
            macro = self.engine._macros[macro_id]
            if macro.trajectory_component and macro.trajectory_component.enabled:
                print("✅ Trayectoria activa")
            else:
                print("❌ Trayectoria no configurada")
                
            modulator_active = all(
                sid in self.engine.orientation_modulators and 
                self.engine.orientation_modulators[sid].enabled
                for sid in macro.source_ids
            )
            
            if modulator_active:
                print("✅ Moduladores activos")
                self.test_results["combined_movement"] = "PASSED"
            else:
                print("❌ Moduladores inactivos")
                self.test_results["combined_movement"] = "FAILED"
                
        except Exception as e:
            print(f"❌ Error en test: {e}")
            self.test_results["combined_movement"] = "ERROR"
            
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        print("\n" + "="*60)
        print("🧪 SUITE DE PRUEBAS - INTEGRACIÓN DEL MODULADOR 3D")
        print("="*60)
        
        # Ejecutar tests
        self.test_basic_modulation()
        self.test_multi_source_modulation()
        self.test_preset_interpolation()
        self.test_osc_transmission()
        self.test_combined_movement()
        
        # Resumen
        print("\n" + "="*60)
        print("📊 RESUMEN DE RESULTADOS")
        print("="*60)
        
        passed = sum(1 for r in self.test_results.values() if r == "PASSED")
        failed = sum(1 for r in self.test_results.values() if r == "FAILED")
        errors = sum(1 for r in self.test_results.values() if r == "ERROR")
        
        for test_name, result in self.test_results.items():
            icon = "✅" if result == "PASSED" else "❌"
            print(f"{icon} {test_name}: {result}")
            
        print(f"\nTotal: {passed} pasados, {failed} fallidos, {errors} errores")
        
        if failed == 0 and errors == 0:
            print("\n🎉 ¡Todos los tests pasaron! El modulador está listo para usar.")
        else:
            print("\n⚠️  Algunos tests fallaron. Revisa la configuración.")
            
    async def run_live_demo(self, duration: float = 30.0):
        """Demo en vivo del sistema completo"""
        print("\n" + "="*60)
        print("🎭 DEMO EN VIVO - SISTEMA DE MODULACIÓN 3D")
        print("="*60)
        
        # Crear escena compleja
        scenes = [
            {
                "name": "bandada_nerviosa",
                "sources": 15,
                "formation": "circle",  # sphere no existe, usar circle
                "preset": "nervioso_aleatorio",
                "trajectory": "random_walk",
                "color": "🔴"
            },
            {
                "name": "orbita_cosmica",
                "sources": 10,
                "formation": "circle",
                "preset": "espiral_cósmica",
                "trajectory": "circular",
                "color": "🔵"
            },
            {
                "name": "respiracion_central",
                "sources": 5,
                "formation": "grid",  # point no existe, usar grid
                "preset": "respiración_suave",
                "trajectory": "static",
                "color": "🟢"
            }
        ]
        
        print("\nCreando escena...")
        
        for scene in scenes:
            # Crear macro
            macro_id = self.engine.create_macro(
                name=scene["name"],
                source_count=scene["sources"],
                formation=scene["formation"],
                spacing=1.0
            )
            
            # Aplicar preset
            self.engine.apply_orientation_preset(
                macro_id,
                scene["preset"],
                intensity=1.0,
                time_offset_spread=0.1
            )
            
            # Configurar trayectoria si no es estática
            if scene["trajectory"] == "circular":
                def circular_traj(t):
                    return np.array([3.0 * np.cos(t), 3.0 * np.sin(t), 0.0])
                self.engine.set_macro_trajectory(macro_id, circular_traj, speed=0.1)
            elif scene["trajectory"] == "random_walk":
                # Random walk se maneja diferente
                pass
                
            print(f"{scene['color']} {scene['name']}: {scene['sources']} fuentes")
            
        print(f"\n🎬 Ejecutando demo por {duration} segundos...")
        print("Observa los movimientos en Spat Revolution")
        print("\nPresiona Ctrl+C para detener antes")
        
        # Ejecutar demo
        self.running = True
        start_time = time.time()
        update_interval = 1.0 / 120.0  # 120 FPS
        
        try:
            while self.running and (time.time() - start_time) < duration:
                # Actualizar motor
                self.engine.update(update_interval)
                
                # Mostrar progreso
                elapsed = time.time() - start_time
                progress = elapsed / duration
                bar = "█" * int(progress * 40) + "░" * int((1-progress) * 40)
                print(f"\r[{bar}] {elapsed:.1f}s / {duration}s", end="", flush=True)
                
                # Control de timing preciso
                await asyncio.sleep(update_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Demo detenida por el usuario")
        
        print("\n✅ Demo completada")
        
        # Mostrar estadísticas finales
        stats = self.osc_bridge.get_stats()
        print(f"\n📊 Estadísticas finales:")
        print(f"   - Total mensajes OSC: {stats['messages_sent']:,}")
        print(f"   - Tasa promedio: {stats['message_rate']:.1f} msg/s")
        print(f"   - Orientaciones enviadas: {stats['parameters_sent']['orientations']:,}")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test de integración del modulador 3D"
    )
    parser.add_argument(
        "--host", 
        default="127.0.0.1",
        help="Host OSC de Spat Revolution"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9000,
        help="Puerto OSC de Spat Revolution"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Ejecutar demo en vivo después de los tests"
    )
    parser.add_argument(
        "--demo-duration",
        type=float,
        default=30.0,
        help="Duración de la demo en segundos"
    )
    
    args = parser.parse_args()
    
    # Crear tester
    tester = ModulatorIntegrationTest(args.host, args.port)
    
    # Ejecutar tests
    tester.run_all_tests()
    
    # Demo opcional
    if args.demo:
        asyncio.run(tester.run_live_demo(args.demo_duration))
        
    print("\n✨ Prueba completada")


if __name__ == "__main__":
    main()