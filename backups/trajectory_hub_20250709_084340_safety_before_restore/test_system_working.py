# === test_system_working.py ===
# 🎯 Test completo con la estructura correcta del sistema
# ⚡ Basado en el diagnóstico real

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import time

class SystemTest:
    def __init__(self):
        self.engine = EnhancedTrajectoryEngine(max_sources=20, fps=60)
        self.results = {"passed": 0, "failed": 0}
        
    def test_concentration(self):
        """Test concentración con estructura correcta"""
        print("\n1️⃣ TEST: Concentración")
        print("-" * 40)
        
        try:
            # Crear macro (crea fuentes automáticamente)
            macro_name = self.engine.create_macro("test_conc", 4, formation='square', spacing=5.0)
            print(f"✅ Macro creado: {macro_name}")
            
            # Obtener posiciones iniciales
            macro = self.engine._macros[macro_name]
            source_ids = list(macro.source_ids)  # Convertir set a lista
            
            initial_positions = {}
            for sid in source_ids:
                initial_positions[sid] = self.engine._positions[sid].copy()
                print(f"   Fuente {sid}: {initial_positions[sid]}")
            
            # Aplicar concentración
            self.engine.set_macro_concentration(macro_name, 0.5)
            
            # Simular
            for _ in range(30):
                self.engine.update()
            
            # Verificar movimiento
            moved = 0
            for sid in source_ids:
                initial = initial_positions[sid]
                final = self.engine._positions[sid]
                dist = np.linalg.norm(final - initial)
                if dist > 0.1:
                    moved += 1
            
            if moved >= 2:
                print(f"✅ Concentración funciona: {moved}/{len(source_ids)} fuentes se movieron")
                self.results["passed"] += 1
            else:
                print(f"❌ Concentración falló: solo {moved}/{len(source_ids)} se movieron")
                self.results["failed"] += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results["failed"] += 1
    
    def test_individual_trajectory(self):
        """Test trayectorias individuales"""
        print("\n2️⃣ TEST: Trayectorias Individuales")
        print("-" * 40)
        
        try:
            # Crear nuevo macro
            macro_name = self.engine.create_macro("test_traj", 3, formation='line', spacing=3.0)
            macro = self.engine._macros[macro_name]
            source_ids = list(macro.source_ids)
            
            # Configurar trayectorias usando el método correcto
            shapes = ['circle', 'spiral', 'figure8']
            configured = 0
            
            for i, shape in enumerate(shapes):
                if i < len(source_ids):
                    try:
                        # Usar el índice dentro del macro, no el source_id global
                        self.engine.set_individual_trajectory(
                            macro_name,
                            i,  # índice 0, 1, 2
                            shape,
                            shape_params={'radius': 2.0},
                            movement_mode='fix',
                            speed=2.0
                        )
                        print(f"✅ {shape} configurado para índice {i}")
                        configured += 1
                    except Exception as e:
                        print(f"❌ Error configurando {shape}: {e}")
            
            # Simular movimiento
            initial_positions = {sid: self.engine._positions[sid].copy() for sid in source_ids}
            
            for _ in range(60):
                self.engine.update()
            
            # Verificar movimiento
            moved = 0
            for sid in source_ids:
                dist = np.linalg.norm(self.engine._positions[sid] - initial_positions[sid])
                if dist > 0.5:
                    moved += 1
                    print(f"   Fuente {sid} se movió {dist:.2f} unidades")
            
            if moved >= 2:
                print(f"✅ Trayectorias funcionan: {moved}/{len(source_ids)} en movimiento")
                self.results["passed"] += 1
            else:
                print(f"❌ Pocas fuentes en movimiento: {moved}/{len(source_ids)}")
                self.results["failed"] += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results["failed"] += 1
    
    def test_rotations(self):
        """Test rotaciones macro"""
        print("\n3️⃣ TEST: Rotaciones Macro")
        print("-" * 40)
        
        try:
            # Crear macro en formación línea
            macro_name = self.engine.create_macro("test_rot", 3, formation='line', spacing=3.0)
            
            # Esperar estabilización
            for _ in range(5):
                self.engine.update()
            
            # Obtener posición inicial de primera fuente
            macro = self.engine._macros[macro_name]
            sid = list(macro.source_ids)[0]
            initial_pos = self.engine._positions[sid].copy()
            
            # Aplicar rotación algorítmica
            self.engine.set_macro_rotation(macro_name, speed_x=0, speed_y=1.0, speed_z=0)
            
            # Simular
            for _ in range(30):
                self.engine.update()
            
            # Verificar rotación
            final_pos = self.engine._positions[sid]
            angle_change = np.arctan2(final_pos[1], final_pos[0]) - np.arctan2(initial_pos[1], initial_pos[0])
            
            if abs(angle_change) > 0.1:
                print(f"✅ Rotación detectada: {np.degrees(angle_change):.1f}°")
                self.results["passed"] += 1
            else:
                print(f"❌ Sin rotación significativa")
                self.results["failed"] += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results["failed"] += 1
    
    def test_orientation_modulation(self):
        """Test modulador de orientación"""
        print("\n4️⃣ TEST: Modulador de Orientación")
        print("-" * 40)
        
        try:
            # Crear macro
            macro_name = self.engine.create_macro("test_orient", 3, formation='triangle')
            
            # Aplicar preset de orientación
            self.engine.apply_orientation_preset(macro_name, "respiración_suave", intensity=0.8)
            
            # Verificar que se crearon los moduladores
            macro = self.engine._macros[macro_name]
            modulators_created = 0
            
            for sid in macro.source_ids:
                if sid in self.engine.orientation_modulators:
                    modulators_created += 1
            
            if modulators_created > 0:
                print(f"✅ Moduladores creados: {modulators_created}/{len(macro.source_ids)}")
                self.results["passed"] += 1
            else:
                print(f"❌ No se crearon moduladores")
                self.results["failed"] += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results["failed"] += 1
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        print("🚀 TEST COMPLETO DEL SISTEMA")
        print("=" * 60)
        print(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Ejecutar tests
        self.test_concentration()
        self.test_individual_trajectory()
        self.test_rotations()
        self.test_orientation_modulation()
        
        # Resumen
        print("\n" + "=" * 60)
        print("📊 RESUMEN")
        print("=" * 60)
        total = self.results["passed"] + self.results["failed"]
        print(f"✅ Pasados: {self.results['passed']}")
        print(f"❌ Fallados: {self.results['failed']}")
        
        if total > 0:
            success_rate = (self.results['passed'] / total) * 100
            print(f"📈 Tasa de éxito: {success_rate:.1f}%")
            
            if success_rate >= 75:
                print("\n🎉 SISTEMA OPERATIVO - Listo para MCP Server")
            elif success_rate >= 50:
                print("\n⚠️ SISTEMA PARCIALMENTE OPERATIVO")
            else:
                print("\n❌ SISTEMA NECESITA ATENCIÓN")
        
        return self.results["failed"] == 0

if __name__ == "__main__":
    tester = SystemTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ PRÓXIMO PASO: Implementar MCP Server")
        print("   Ejecutar: python create_mcp_server_base.py")