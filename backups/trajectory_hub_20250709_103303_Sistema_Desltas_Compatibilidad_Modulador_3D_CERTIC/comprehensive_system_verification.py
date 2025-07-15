from datetime import datetime
# === comprehensive_system_verification.py ===
# 🔍 Verificación exhaustiva del sistema para certificación
# 👨‍💼 Evaluación de Ingeniero Jefe de Proyecto

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import time
import threading
import json

class SystemVerification:
    """Verificación completa del sistema para certificación profesional"""
    
    def __init__(self):
        self.results = {
            "architecture_tests": {},
            "integration_tests": {},
            "stress_tests": {},
            "compatibility_tests": {},
            "risks_identified": []
        }
    
    def test_1_delta_independence(self):
        """Verificar que los deltas no se interfieren entre sí"""
        print("\n1️⃣ TEST: Independencia de Deltas")
        print("-" * 50)
        
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        macro = engine.create_macro("test", source_count=4)
        
        # Aplicar TODOS los componentes simultáneamente
        engine.set_macro_concentration(f"macro_0_{macro.name}", factor=0.5)
        engine.set_macro_trajectory(f"macro_0_{macro.name}", lambda t: np.array([np.cos(t), np.sin(t), 0]))
        engine.set_macro_rotation(f"macro_0_{macro.name}", speed_x=0.5, speed_y=0.5, speed_z=0.5)
        
        # Verificar primera fuente
        sid = list(macro.source_ids)[0]
        engine.set_individual_trajectory(f"macro_0_{macro.name}", sid, shape="circle", speed=2.0)
        
        # Capturar movimiento durante 2 segundos
        positions = []
        for _ in range(120):  # 2 segundos a 60fps
            engine.update()
            positions.append(engine._positions[sid].copy())
        
        # Análisis
        positions = np.array(positions)
        total_movement = np.linalg.norm(positions[-1] - positions[0])
        path_length = sum(np.linalg.norm(positions[i+1] - positions[i]) for i in range(len(positions)-1))
        
        # Verificar que hay movimiento complejo (no lineal)
        linearity = total_movement / path_length if path_length > 0 else 1.0
        
        result = {
            "passed": linearity < 0.5,
            "total_movement": float(total_movement),
            "path_length": float(path_length),
            "linearity": float(linearity),
            "verdict": "Los deltas se componen correctamente" if linearity < 0.5 else "Posible interferencia"
        }
        
        print(f"   Movimiento total: {total_movement:.3f}")
        print(f"   Longitud de trayectoria: {path_length:.3f}")
        print(f"   Linealidad: {linearity:.3f} (menor = más complejo)")
        print(f"   {'✅ PASS' if result['passed'] else '❌ FAIL'}")
        
        self.results["architecture_tests"]["delta_independence"] = result
        return result["passed"]
    
    def test_2_modulator_compatibility(self):
        """Verificar compatibilidad con modulador 3D"""
        print("\n2️⃣ TEST: Compatibilidad con Modulador 3D")
        print("-" * 50)
        
        try:
            engine = EnhancedTrajectoryEngine(max_sources=5, fps=60, enable_modulator=True)
            
            # Verificar atributos del modulador
            checks = {
                "has_orientation_modulators": hasattr(engine, 'orientation_modulators'),
                "has_enable_modulator": hasattr(engine, 'enable_modulator'),
                "has_create_orientation_modulator": hasattr(engine, 'create_orientation_modulator'),
                "modulators_dict": isinstance(getattr(engine, 'orientation_modulators', None), dict)
            }
            
            # Si existe, intentar crear uno
            if all(checks.values()):
                macro = engine.create_macro("modulator_test", source_count=2)
                sid = list(macro.source_ids)[0]
                
                # Verificar que se puede crear modulador
                if sid in engine.orientation_modulators:
                    checks["modulator_created"] = True
                else:
                    # Intentar crear manualmente
                    try:
                        modulator = engine.create_orientation_modulator(sid)
                        checks["modulator_created"] = modulator is not None
                    except:
                        checks["modulator_created"] = False
            
            result = {
                "passed": all(checks.values()),
                "checks": checks,
                "verdict": "Sistema preparado para modulador 3D" if all(checks.values()) else "Falta integración completa"
            }
            
            for check, status in checks.items():
                print(f"   {check}: {'✅' if status else '❌'}")
            
            print(f"\n   {'✅ PASS' if result['passed'] else '⚠️ PARCIAL'}")
            
        except Exception as e:
            result = {
                "passed": False,
                "error": str(e),
                "verdict": "Modulador 3D no integrado aún"
            }
            print(f"   ⚠️ Modulador no integrado: {e}")
        
        self.results["compatibility_tests"]["modulator_3d"] = result
        return result["passed"]
    
    def test_3_controller_integration(self):
        """Verificar integración con controlador interactivo"""
        print("\n3️⃣ TEST: Integración con Controlador")
        print("-" * 50)
        
        try:
            from trajectory_hub.interface import InteractiveController
            
            # Verificar que se puede crear
            controller = InteractiveController()
            
            # Verificar métodos críticos
            methods = [
                'create_macro',
                'set_macro_trajectory',
                'set_macro_concentration',
                'set_individual_trajectory',
                'apply_preset'
            ]
            
            checks = {}
            for method in methods:
                checks[method] = hasattr(controller, method)
            
            # Verificar engine
            checks["has_engine"] = hasattr(controller, 'engine')
            checks["engine_is_enhanced"] = controller.engine.__class__.__name__ == "EnhancedTrajectoryEngine"
            
            result = {
                "passed": all(checks.values()),
                "checks": checks,
                "verdict": "Controlador listo para integración" if all(checks.values()) else "Necesita actualización"
            }
            
            for check, status in checks.items():
                print(f"   {check}: {'✅' if status else '❌'}")
            
            print(f"\n   {'✅ PASS' if result['passed'] else '❌ FAIL'}")
            
        except Exception as e:
            result = {
                "passed": False,
                "error": str(e),
                "verdict": f"Error al cargar controlador: {e}"
            }
            print(f"   ❌ Error: {e}")
        
        self.results["integration_tests"]["controller"] = result
        return result["passed"]
    
    def test_4_concurrent_operations(self):
        """Test de operaciones concurrentes"""
        print("\n4️⃣ TEST: Operaciones Concurrentes")
        print("-" * 50)
        
        engine = EnhancedTrajectoryEngine(max_sources=20, fps=60)
        errors = []
        
        def create_and_modify(i):
            try:
                macro = engine.create_macro(f"concurrent_{i}", source_count=3)
                engine.set_macro_concentration(f"macro_0_{macro.name}", factor=0.3 + i*0.1)
                engine.set_macro_trajectory(f"macro_0_{macro.name}", lambda t: np.array([i*np.cos(t), i*np.sin(t), 0]))
                for _ in range(10):
                    engine.update()
                    time.sleep(0.001)
            except Exception as e:
                errors.append(f"Thread {i}: {e}")
        
        # Lanzar 5 threads concurrentes
        threads = []
        for i in range(5):
            t = threading.Thread(target=create_and_modify, args=(i,))
            threads.append(t)
            t.start()
        
        # Esperar a que terminen
        for t in threads:
            t.join()
        
        result = {
            "passed": len(errors) == 0,
            "errors": errors,
            "verdict": "Sistema thread-safe" if len(errors) == 0 else "Posibles problemas de concurrencia"
        }
        
        if errors:
            print(f"   ❌ Errores encontrados: {len(errors)}")
            for err in errors[:3]:  # Mostrar máximo 3
                print(f"      - {err}")
        else:
            print(f"   ✅ Sin errores de concurrencia")
        
        self.results["stress_tests"]["concurrency"] = result
        return result["passed"]
    
    def test_5_state_persistence(self):
        """Verificar persistencia de estado"""
        print("\n5️⃣ TEST: Persistencia de Estado")
        print("-" * 50)
        
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        
        # Crear configuración compleja
        macro = engine.create_macro("persistence_test", source_count=4)
        engine.set_macro_concentration(f"macro_0_{macro.name}", factor=0.3)
        engine.set_macro_trajectory(f"macro_0_{macro.name}", lambda t: np.array([np.cos(t), np.sin(t), 0]))
        
        # Actualizar varias veces
        for _ in range(30):
            engine.update()
        
        # Capturar estado
        initial_positions = {sid: engine._positions[sid].copy() for sid in macro.source_ids}
        
        # Verificar que get_state funciona
        try:
            state = engine.get_state()
            has_state = True
            state_complete = all(key in state for key in ['sources', 'macros', 'frame_count'])
        except:
            has_state = False
            state_complete = False
        
        result = {
            "passed": has_state and state_complete,
            "has_get_state": has_state,
            "state_complete": state_complete,
            "verdict": "Sistema con estado persistible" if has_state else "Falta implementar get/set state"
        }
        
        print(f"   get_state(): {'✅' if has_state else '❌'}")
        print(f"   Estado completo: {'✅' if state_complete else '❌'}")
        print(f"\n   {'✅ PASS' if result['passed'] else '⚠️ PARCIAL'}")
        
        self.results["integration_tests"]["persistence"] = result
        return result["passed"]
    
    def identify_risks(self):
        """Identificar riesgos del sistema"""
        print("\n⚠️ ANÁLISIS DE RIESGOS")
        print("-" * 50)
        
        risks = []
        
        # Analizar resultados
        if not self.results["compatibility_tests"].get("modulator_3d", {}).get("passed", False):
            risks.append({
                "level": "MEDIUM",
                "area": "Modulador 3D",
                "description": "Modulador 3D no está completamente integrado",
                "mitigation": "Seguir guía PDF de integración antes de producción"
            })
        
        if not self.results["integration_tests"].get("persistence", {}).get("passed", False):
            risks.append({
                "level": "LOW",
                "area": "Persistencia",
                "description": "Sistema get/set state incompleto",
                "mitigation": "Implementar serialización completa si se requiere guardar sesiones"
            })
        
        if self.results["stress_tests"].get("concurrency", {}).get("errors", []):
            risks.append({
                "level": "HIGH",
                "area": "Concurrencia",
                "description": "Posibles condiciones de carrera en operaciones concurrentes",
                "mitigation": "Añadir locks en operaciones críticas"
            })
        
        # Riesgos generales
        risks.extend([
            {
                "level": "MEDIUM",
                "area": "Escalabilidad",
                "description": "No probado con >100 fuentes simultáneas",
                "mitigation": "Realizar pruebas de carga antes de producción"
            },
            {
                "level": "LOW",
                "area": "Documentación",
                "description": "Documentación de API incompleta",
                "mitigation": "Generar documentación automática con Sphinx"
            }
        ])
        
        self.results["risks_identified"] = risks
        
        for risk in risks:
            print(f"\n   [{risk['level']}] {risk['area']}")
            print(f"   Descripción: {risk['description']}")
            print(f"   Mitigación: {risk['mitigation']}")
        
        return risks
    
    def generate_report(self):
        """Generar reporte de certificación"""
        print("\n" + "="*70)
        print("📋 REPORTE DE CERTIFICACIÓN TÉCNICA")
        print("="*70)
        
        all_tests = []
        for category, tests in self.results.items():
            if category != "risks_identified" and isinstance(tests, dict):
                for test_name, result in tests.items():
                    if isinstance(result, dict) and "passed" in result:
                        all_tests.append(result["passed"])
        
        pass_rate = sum(all_tests) / len(all_tests) if all_tests else 0
        
        certification = {
            "date": datetime.now().isoformat(),
            "engineer": "Chief Project Engineer",
            "project": "Trajectory Hub",
            "version": "1.0-beta",
            "overall_pass_rate": f"{pass_rate*100:.1f}%",
            "certification_status": "APPROVED WITH CONDITIONS" if pass_rate > 0.7 else "NOT READY",
            "results_summary": self.results,
            "final_verdict": {}
        }
        
        # Veredicto final
        if pass_rate >= 0.9:
            certification["final_verdict"] = {
                "status": "✅ CERTIFICADO",
                "notes": "Sistema listo para integración con controlador",
                "conditions": ["Integrar modulador 3D antes de producción"]
            }
        elif pass_rate >= 0.7:
            certification["final_verdict"] = {
                "status": "⚠️ CERTIFICADO CONDICIONAL",
                "notes": "Sistema funcional pero requiere completar integraciones",
                "conditions": self.results["risks_identified"]
            }
        else:
            certification["final_verdict"] = {
                "status": "❌ NO CERTIFICADO",
                "notes": "Sistema requiere más trabajo antes de integración"
            }
        
        # Guardar reporte
        with open("CERTIFICATION_REPORT.json", "w") as f:
            json.dump(certification, f, indent=2)
        
        print(f"\n🏆 RESULTADO FINAL: {certification['final_verdict']['status']}")
        print(f"📊 Tasa de éxito: {certification['overall_pass_rate']}")
        print(f"\n📄 Reporte guardado en: CERTIFICATION_REPORT.json")
        
        return certification

def main():
    """Ejecutar verificación completa"""
    print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA")
    print("👨‍💼 Evaluación de Ingeniero Jefe de Proyecto")
    print("="*70)
    
    verifier = SystemVerification()
    
    # Ejecutar todos los tests
    verifier.test_1_delta_independence()
    verifier.test_2_modulator_compatibility()
    verifier.test_3_controller_integration()
    verifier.test_4_concurrent_operations()
    verifier.test_5_state_persistence()
    
    # Análisis de riesgos
    verifier.identify_risks()
    
    # Generar reporte
    certification = verifier.generate_report()
    
    # Decisión final
    print("\n" + "="*70)
    print("🎯 DECISIÓN DE INGENIERÍA")
    print("="*70)
    
    if certification["final_verdict"]["status"] == "✅ CERTIFICADO":
        print("""
Como Ingeniero Jefe de Proyecto, CERTIFICO que:

1. ✅ La arquitectura de deltas funciona correctamente
2. ✅ Es compatible con el modulador 3D (preparada para integración)
3. ✅ Está lista para integrarse con el controlador

FIRMA: Chief Project Engineer
FECHA: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    else:
        print("\n⚠️ El sistema requiere las siguientes acciones antes de certificación completa:")
        for condition in certification["final_verdict"].get("conditions", []):
            if isinstance(condition, dict):
                print(f"   - [{condition.get('level', 'INFO')}] {condition.get('description', '')}")

if __name__ == "__main__":
    main()