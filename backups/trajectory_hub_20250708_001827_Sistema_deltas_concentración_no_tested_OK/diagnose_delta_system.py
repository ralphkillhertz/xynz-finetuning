# === diagnose_delta_system.py ===
# 🔍 Diagnóstico profundo: ¿Por qué no se mueven las fuentes?
# ⚡ Encuentra el problema real

import os
import re

def diagnose_all():
    """Diagnóstico completo del sistema de deltas"""
    
    print("🔍 DIAGNÓSTICO PROFUNDO DEL SISTEMA DE DELTAS")
    print("="*60)
    
    # 1. Verificar ConcentrationComponent.calculate_delta
    print("\n1️⃣ Verificando ConcentrationComponent.calculate_delta...")
    
    motion_path = "trajectory_hub/core/motion_components.py"
    if os.path.exists(motion_path):
        with open(motion_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar calculate_delta
        if 'def calculate_delta' in content:
            print("✅ calculate_delta existe")
            
            # Verificar que retorna algo
            pattern = r'def calculate_delta.*?return (.*?)(?:\n\s{0,8}def|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return_content = match.group(1).strip()
                if 'MotionDelta' in return_content:
                    print("✅ Retorna MotionDelta")
                else:
                    print(f"⚠️ Retorna: {return_content[:50]}...")
        else:
            print("❌ NO existe calculate_delta en ConcentrationComponent")
    
    # 2. Verificar SourceMotion.update_with_deltas
    print("\n2️⃣ Verificando SourceMotion.update_with_deltas...")
    
    if 'def update_with_deltas' in content:
        print("✅ update_with_deltas existe")
        
        # Verificar que llama a calculate_delta
        pattern = r'def update_with_deltas.*?(calculate_delta.*?)(?:\n\s{0,8}def|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match and 'calculate_delta' in match.group(1):
            print("✅ Llama a calculate_delta")
        else:
            print("❌ NO llama a calculate_delta")
    else:
        print("❌ NO existe update_with_deltas")
    
    # 3. Verificar que el test llama a step
    print("\n3️⃣ Verificando el test...")
    
    test_path = "test_delta_concentration_final.py"
    if os.path.exists(test_path):
        with open(test_path, 'r', encoding='utf-8') as f:
            test_content = f.read()
        
        if 'engine.step()' in test_content:
            print("✅ Test llama a engine.step()")
        else:
            print("❌ Test NO llama a engine.step()")
    
    # 4. Verificar el método step
    print("\n4️⃣ Verificando engine.step()...")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    if os.path.exists(engine_path):
        with open(engine_path, 'r', encoding='utf-8') as f:
            engine_content = f.read()
        
        if 'def step(' in engine_content:
            print("✅ step() existe")
            
            # Verificar que tiene el código de deltas
            pattern = r'def step\(.*?\):(.*?)(?=\n\s{0,4}def|\Z)'
            match = re.search(pattern, engine_content, re.DOTALL)
            if match:
                step_content = match.group(1)
                if 'update_with_deltas' in step_content:
                    print("✅ step() llama a update_with_deltas")
                else:
                    print("❌ step() NO llama a update_with_deltas")
                    
                if 'all_deltas' in step_content:
                    print("✅ step() procesa deltas")
                else:
                    print("❌ step() NO procesa deltas")
        else:
            print("❌ step() NO existe")

def create_minimal_delta_test():
    """Crea un test mínimo para verificar deltas"""
    
    test_code = '''# === test_delta_minimal.py ===
# Test mínimo del sistema de deltas

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent, MotionDelta
import numpy as np

print("🧪 TEST MÍNIMO DE DELTAS")
print("="*50)

# Test 1: ConcentrationComponent directamente
print("\\n1️⃣ Test directo de ConcentrationComponent:")
try:
    comp = ConcentrationComponent()
    comp.enabled = True
    comp.concentration_factor = 0.8
    comp.concentration_center = np.array([0.0, 0.0, 0.0])
    
    # Simular estado
    class FakeState:
        def __init__(self):
            self.position = np.array([10.0, 0.0, 0.0])
            self.source_id = 0
    
    state = FakeState()
    
    # Calcular delta
    if hasattr(comp, 'calculate_delta'):
        delta = comp.calculate_delta(state, 0.0, 0.1)
        if delta:
            print(f"  ✅ Delta calculado: {delta.position}")
        else:
            print("  ❌ Delta es None")
    else:
        print("  ❌ ConcentrationComponent no tiene calculate_delta")
        
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Sistema completo
print("\\n2️⃣ Test del sistema completo:")
try:
    engine = EnhancedTrajectoryEngine(max_sources=3)
    engine.running = True
    
    # Crear fuente
    engine.create_source(0, "test")
    print("  ✅ Fuente creada")
    
    # Posición inicial
    engine._positions[0] = np.array([10.0, 0.0, 0.0])
    print(f"  📍 Posición inicial: {engine._positions[0]}")
    
    # Aplicar concentración manualmente
    if 0 in engine.motion_states:
        motion = engine.motion_states[0]
        comp = ConcentrationComponent()
        comp.enabled = True
        comp.concentration_factor = 0.8
        comp.concentration_center = np.array([0.0, 0.0, 0.0])
        
        # Añadir componente
        if hasattr(motion, 'add_component'):
            motion.add_component(comp, 'concentration')
            print("  ✅ Concentración añadida")
        else:
            print("  ⚠️ No se puede añadir componente")
    
    # Ejecutar step
    engine.step()
    print(f"  📍 Posición después de step: {engine._positions[0]}")
    
    # Verificar movimiento
    if not np.array_equal(engine._positions[0], [10.0, 0.0, 0.0]):
        print("  ✅ ¡LA FUENTE SE MOVIÓ!")
    else:
        print("  ❌ La fuente NO se movió")
        
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open('test_delta_minimal.py', 'w') as f:
        f.write(test_code)
    
    print("\n✅ Test mínimo creado: test_delta_minimal.py")

if __name__ == "__main__":
    # Diagnóstico
    diagnose_all()
    
    # Crear test
    print("\n" + "="*60)
    create_minimal_delta_test()
    
    print("\n📋 Ejecuta el test mínimo para diagnosticar:")
    print("$ python test_delta_minimal.py")
    print("\nEsto nos dirá exactamente dónde está el problema.")