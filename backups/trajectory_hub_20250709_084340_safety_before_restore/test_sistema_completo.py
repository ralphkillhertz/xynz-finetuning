# === test_sistema_completo.py ===
# 🎯 Test exhaustivo del sistema completo
# ⚡ Verifica TODOS los componentes al 100%

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import math
import time
from datetime import datetime

class TestSistemaCompleto:
    def __init__(self):
        self.engine = None
        self.results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "components": {}
        }
        
    def setup(self):
        """Configurar engine para tests"""
        print("🔧 Configurando sistema...")
        self.engine = EnhancedTrajectoryEngine(max_sources=20, fps=60)
        
        # Deshabilitar OSC si existe
        if hasattr(self.engine, 'osc_bridge') and self.engine.osc_bridge:
            self.engine.osc_bridge.enabled = False
            
        print("✅ Sistema configurado\n")
        
    def test_concentration_component(self):
        """Test 1: ConcentrationComponent"""
        print("1️⃣ TEST: ConcentrationComponent")
        print("-" * 60)
        
        try:
            # Crear macro con 4 fuentes
            positions = [[2,0,0], [0,2,0], [-2,0,0], [0,-2,0]]
            source_ids = []
            
            for i, pos in enumerate(positions):
                sid = self.engine.create_source(i)
                self.engine._positions[i] = np.array(pos)
                if i in self.engine.motion_states:
                    self.engine.motion_states[i].state.position = np.array(pos)
                source_ids.append(i)
                
            # Crear macro
            self.engine.create_macro("test_concentration", source_ids)
            
            # Aplicar concentración
            initial_distance = np.mean([np.linalg.norm(self.engine._positions[i]) for i in source_ids])
            self.engine.set_macro_concentration("test_concentration", 0.5)
            
            # Simular
            for _ in range(30):
                self.engine.update()
                
            # Verificar
            final_distance = np.mean([np.linalg.norm(self.engine._positions[i]) for i in source_ids])
            
            if final_distance < initial_distance * 0.6:
                print(f"✅ Concentración exitosa: {initial_distance:.2f} → {final_distance:.2f}")
                self.results["tests_passed"] += 1
                self.results["components"]["ConcentrationComponent"] = "✅ FUNCIONAL"
            else:
                print(f"❌ Concentración falló: {initial_distance:.2f} → {final_distance:.2f}")
                self.results["tests_failed"] += 1
                self.results["components"]["ConcentrationComponent"] = "❌ FALLO"
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results["tests_failed"] += 1
            self.results["components"]["ConcentrationComponent"] = f"❌ ERROR: {str(e)}"
            
        print()
        
    def test_individual_trajectory(self):
        """Test 2: IndividualTrajectory"""
        print("2️⃣ TEST: IndividualTrajectory")
        print("-" * 60)
        
        try:
            # Limpiar fuentes anteriores
            self.engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
            
            # Test cada forma
            shapes = ['circle', 'spiral', 'figure8']
            all_passed = True
            
            for shape in shapes:
                sid = self.engine.create_source(len(shapes))
                initial_pos = [3.0, 0.0, 0.0]
                self.engine._positions[sid] = np.array(initial_pos)
                
                # Configurar trayectoria
                self.engine.set_individual_trajectory(
                    sid,
                    trajectory_type=shape,
                    shape_params={'radius': 2.0},
                    movement_speed=1.0
                )
                
                # Simular movimiento
                for _ in range(60):  # 1 segundo
                    self.engine.update()
                    
                # Verificar movimiento
                final_pos = self.engine._positions[sid]
                distance_moved = np.linalg.norm(final_pos - initial_pos)
                
                if distance_moved > 0.5:
                    print(f"   ✅ {shape}: movió {distance_moved:.2f} unidades")
                else:
                    print(f"   ❌ {shape}: solo movió {distance_moved:.2f} unidades")
                    all_passed = False
                    
            if all_passed:
                self.results["tests_passed"] += 1
                self.results["components"]["IndividualTrajectory"] = "✅ FUNCIONAL"
            else:
                self.results["tests_failed"] += 1
                self.results["components"]["IndividualTrajectory"] = "❌ FALLO"
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results["tests_failed"] += 1
            self.results["components"]["IndividualTrajectory"] = f"❌ ERROR: {str(e)}"
            
        print()
        
    def test_macro_trajectory(self):
        """Test 3: MacroTrajectory"""
        print("3️⃣ TEST: MacroTrajectory")
        print("-" * 60)
        
        try:
            # Crear nuevo macro
            self.engine.create_macro("test_macro_traj", 4, formation='line')
            
            # Configurar trayectoria macro
            self.engine.set_macro_trajectory("test_macro_traj", "circle", speed=1.0)
            
            # Obtener centroide inicial
            positions = [self.engine._positions[i] for i in range(4)]
            initial_centroid = np.mean(positions, axis=0)
            
            # Simular
            for _ in range(60):
                self.engine.update()
                
            # Verificar movimiento del centroide
            final_positions = [self.engine._positions[i] for i in range(4)]
            final_centroid = np.mean(final_positions, axis=0)
            centroid_movement = np.linalg.norm(final_centroid - initial_centroid)
            
            if centroid_movement > 1.0:
                print(f"✅ Macro trajectory movió centroide: {centroid_movement:.2f} unidades")
                self.results["tests_passed"] += 1
                self.results["components"]["MacroTrajectory"] = "✅ FUNCIONAL"
            else:
                print(f"❌ Macro trajectory movimiento insuficiente: {centroid_movement:.2f}")
                self.results["tests_failed"] += 1
                self.results["components"]["MacroTrajectory"] = "❌ FALLO"
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results["tests_failed"] += 1
            self.results["components"]["MacroTrajectory"] = f"❌ ERROR: {str(e)}"
            
        print()
        
    def test_macro_rotation(self):
        """Test 4: MacroRotation (algorítmica)"""
        print("4️⃣ TEST: MacroRotation (algorítmica)")
        print("-" * 60)
        
        try:
            # Crear macro
            self.engine.create_macro("test_rotation", 3, formation='line')
            
            # Configurar rotación algorítmica
            self.engine.set_macro_rotation("test_rotation", speed_x=0, speed_y=1.0, speed_z=0)
            
            # Posición inicial de la primera fuente
            initial_pos = self.engine._positions[0].copy()
            
            # Simular
            for _ in range(30):
                self.engine.update()
                
            # Verificar rotación
            final_pos = self.engine._positions[0]
            angle_change = math.atan2(final_pos[1], final_pos[0]) - math.atan2(initial_pos[1], initial_pos[0])
            
            if abs(angle_change) > 0.1:
                print(f"✅ Rotación algorítmica: {math.degrees(angle_change):.1f}°")
                self.results["tests_passed"] += 1
                self.results["components"]["MacroRotation"] = "✅ FUNCIONAL"
            else:
                print(f"❌ Sin rotación significativa: {math.degrees(angle_change):.1f}°")
                self.results["tests_failed"] += 1
                self.results["components"]["MacroRotation"] = "❌ FALLO"
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results["tests_failed"] += 1
            self.results["components"]["MacroRotation"] = f"❌ ERROR: {str(e)}"
            
        print()
        
    def test_manual_macro_rotation(self):
        """Test 5: ManualMacroRotation"""
        print("5️⃣ TEST: ManualMacroRotation")
        print("-" * 60)
        
        try:
            # Crear macro en formación
            self.engine.create_macro("test_manual", 4, formation='square')
            
            # Configurar rotación manual 45°
            self.engine.set_manual_macro_rotation(
                "test_manual",
                yaw=math.pi/4,  # 45 grados
                interpolation_speed=0.3
            )
            
            # Simular
            for _ in range(30):
                self.engine.update()
                
            # Verificar ángulo
            pos = self.engine._positions[0]
            angle = math.degrees(math.atan2(pos[1], pos[0]))
            
            if 40 < angle < 50:
                print(f"✅ Rotación manual a {angle:.1f}° (objetivo 45°)")
                self.results["tests_passed"] += 1
                self.results["components"]["ManualMacroRotation"] = "✅ FUNCIONAL"
            else:
                print(f"❌ Ángulo incorrecto: {angle:.1f}° (esperado ~45°)")
                self.results["tests_failed"] += 1
                self.results["components"]["ManualMacroRotation"] = "❌ FALLO"
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results["tests_failed"] += 1
            self.results["components"]["ManualMacroRotation"] = f"❌ ERROR: {str(e)}"
            
        print()
        
    def test_individual_rotation(self):
        """Test 6: IndividualRotation (algorítmica)"""
        print("6️⃣ TEST: IndividualRotation (algorítmica)")
        print("-" * 60)
        
        try:
            # Crear fuente individual
            sid = self.engine.create_source(10)
            self.engine._positions[sid] = np.array([3.0, 0.0, 0.0])
            if sid in self.engine.motion_states:
                self.engine.motion_states[sid].state.position = np.array([3.0, 0.0, 0.0])
            
            # Configurar rotación algorítmica
            self.engine.set_individual_rotation(sid, speed_y=2.0)  # Rápida
            
            # Simular
            for _ in range(30):
                self.engine.update()
                
            # Verificar
            pos = self.engine._positions[sid]
            angle = math.degrees(math.atan2(pos[1], pos[0]))
            
            if abs(angle) > 30:
                print(f"✅ Rotación individual: {angle:.1f}°")
                self.results["tests_passed"] += 1
                self.results["components"]["IndividualRotation"] = "✅ FUNCIONAL"
            else:
                print(f"❌ Rotación insuficiente: {angle:.1f}°")
                self.results["tests_failed"] += 1
                self.results["components"]["IndividualRotation"] = "❌ FALLO"
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results["tests_failed"] += 1
            self.results["components"]["IndividualRotation"] = f"❌ ERROR: {str(e)}"
            
        print()
        
    def test_manual_individual_rotation(self):
        """Test 7: ManualIndividualRotation"""
        print("7️⃣ TEST: ManualIndividualRotation")
        print("-" * 60)
        
        try:
            # Crear fuente
            sid = self.engine.create_source(11)
            self.engine._positions[sid] = np.array([3.0, 0.0, 0.0])
            if sid in self.engine.motion_states:
                self.engine.motion_states[sid].state.position = np.array([3.0, 0.0, 0.0])
            
            # Configurar rotación manual 90°
            self.engine.set_manual_individual_rotation(
                sid,
                yaw=math.pi/2,
                interpolation_speed=0.3
            )
            
            # Simular más frames
            for _ in range(40):
                self.engine.update()
                
            # Verificar
            pos = self.engine._positions[sid]
            angle = math.degrees(math.atan2(pos[1], pos[0]))
            
            if 20 < angle < 100:  # Rango amplio porque la interpolación es gradual
                print(f"✅ Rotación manual individual: {angle:.1f}°")
                self.results["tests_passed"] += 1
                self.results["components"]["ManualIndividualRotation"] = "✅ FUNCIONAL"
            else:
                print(f"❌ Ángulo fuera de rango: {angle:.1f}°")
                self.results["tests_failed"] += 1
                self.results["components"]["ManualIndividualRotation"] = "❌ FALLO"
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results["tests_failed"] += 1
            self.results["components"]["ManualIndividualRotation"] = f"❌ ERROR: {str(e)}"
            
        print()
        
    def test_combined_movements(self):
        """Test 8: Movimientos combinados (prueba de no interferencia)"""
        print("8️⃣ TEST: Movimientos combinados")
        print("-" * 60)
        
        try:
            # Crear macro con trayectorias individuales Y rotación macro
            self.engine.create_macro("combined", 3, formation='triangle')
            
            # Configurar trayectorias individuales
            for i in range(3):
                self.engine.set_individual_trajectory(
                    i,
                    trajectory_type='circle',
                    shape_params={'radius': 0.5},
                    movement_speed=2.0
                )
            
            # Configurar trayectoria macro
            self.engine.set_macro_trajectory("combined", "spiral", speed=0.5)
            
            # Configurar rotación macro
            self.engine.set_macro_rotation("combined", speed_y=0.5)
            
            # Aplicar concentración parcial
            self.engine.set_macro_concentration("combined", 0.7)
            
            # Simular
            initial_positions = [self.engine._positions[i].copy() for i in range(3)]
            
            for _ in range(60):
                self.engine.update()
                
            # Verificar que todos se movieron
            all_moved = True
            for i in range(3):
                movement = np.linalg.norm(self.engine._positions[i] - initial_positions[i])
                if movement < 0.5:
                    all_moved = False
                    print(f"   ❌ Fuente {i} movimiento insuficiente: {movement:.2f}")
                else:
                    print(f"   ✅ Fuente {i} movió: {movement:.2f} unidades")
                    
            if all_moved:
                print("✅ Movimientos combinados sin interferencia")
                self.results["tests_passed"] += 1
                self.results["components"]["CombinedMovements"] = "✅ FUNCIONAL"
            else:
                print("❌ Interferencia detectada en movimientos combinados")
                self.results["tests_failed"] += 1
                self.results["components"]["CombinedMovements"] = "❌ FALLO"
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results["tests_failed"] += 1
            self.results["components"]["CombinedMovements"] = f"❌ ERROR: {str(e)}"
            
        print()
        
    def generate_report(self):
        """Generar reporte final"""
        print("=" * 80)
        print("📊 REPORTE FINAL DEL SISTEMA")
        print("=" * 80)
        
        print(f"\n📈 MÉTRICAS:")
        print(f"   Tests pasados: {self.results['tests_passed']}")
        print(f"   Tests fallados: {self.results['tests_failed']}")
        print(f"   Tasa de éxito: {(self.results['tests_passed'] / (self.results['tests_passed'] + self.results['tests_failed']) * 100):.1f}%")
        
        print(f"\n🔍 ESTADO DE COMPONENTES:")
        for component, status in self.results["components"].items():
            print(f"   {component:.<35} {status}")
            
        print(f"\n🎯 VEREDICTO FINAL:")
        if self.results['tests_failed'] == 0:
            print("   ✅ SISTEMA 100% FUNCIONAL - TODOS LOS TESTS PASARON")
            print("   🎉 ¡El sistema de deltas está completamente operativo!")
        else:
            print(f"   ⚠️ SISTEMA CON {self.results['tests_failed']} FALLOS")
            print("   📝 Revisar componentes marcados con ❌")
            
        # Guardar reporte
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_results": self.results,
            "system_status": "OPERATIONAL" if self.results['tests_failed'] == 0 else "NEEDS_ATTENTION"
        }
        
        import json
        with open("test_sistema_completo_report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"\n💾 Reporte guardado en: test_sistema_completo_report.json")
        
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        print("🚀 INICIANDO TEST COMPLETO DEL SISTEMA")
        print("=" * 80)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        self.setup()
        
        # Ejecutar cada test
        self.test_concentration_component()
        self.test_individual_trajectory()
        self.test_macro_trajectory()
        self.test_macro_rotation()
        self.test_manual_macro_rotation()
        self.test_individual_rotation()
        self.test_manual_individual_rotation()
        self.test_combined_movements()
        
        # Generar reporte
        self.generate_report()


if __name__ == "__main__":
    tester = TestSistemaCompleto()
    tester.run_all_tests()