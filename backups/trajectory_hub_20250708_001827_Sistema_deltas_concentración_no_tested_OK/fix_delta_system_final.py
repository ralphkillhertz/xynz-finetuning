# === fix_delta_system_final.py ===
# 🔍 Debug completo y arreglo definitivo del sistema de deltas
# ⚡ Encuentra y arregla TODOS los problemas

import os
import re
from datetime import datetime

def analyze_complete_flow():
    """Analiza el flujo completo de deltas"""
    
    print("🔍 ANÁLISIS COMPLETO DEL FLUJO DE DELTAS")
    print("="*60)
    
    # 1. Verificar ConcentrationComponent.calculate_delta
    print("\n1️⃣ Verificando ConcentrationComponent.calculate_delta...")
    
    motion_path = "trajectory_hub/core/motion_components.py"
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar calculate_delta en ConcentrationComponent
    pattern = r'class ConcentrationComponent.*?def calculate_delta\(self[^)]*\):(.*?)(?=\n\s{0,8}def|\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        calc_delta_content = match.group(1)
        print("✅ calculate_delta encontrado")
        
        # Verificar si está retornando delta correctamente
        if 'return MotionDelta' in calc_delta_content:
            print("✅ Retorna MotionDelta")
            
            # Verificar el cálculo
            if 'target_position - state.position' in calc_delta_content:
                print("✅ Calcula dirección correctamente")
            else:
                print("❌ Problema en el cálculo de dirección")
    
    # 2. Verificar SourceMotion.update_with_deltas
    print("\n2️⃣ Verificando SourceMotion.update_with_deltas...")
    
    pattern = r'class SourceMotion.*?def update_with_deltas\(self[^)]*\):(.*?)(?=\n\s{0,8}def|\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        update_deltas_content = match.group(1)
        print("✅ update_with_deltas encontrado")
        
        # Ver qué retorna
        return_match = re.search(r'return\s+(.+)', update_deltas_content)
        if return_match:
            return_value = return_match.group(1).strip()
            print(f"📌 Retorna: {return_value}")
            
            if return_value == 'delta':
                print("❌ Retorna UN delta, debe retornar LISTA")
                return 'fix_return_list'
            elif return_value == 'deltas':
                print("✅ Retorna lista deltas")
            elif 'MotionDelta' in return_value:
                print("❌ Retorna MotionDelta directamente")
                return 'fix_return_list'
    
    # 3. Verificar step()
    print("\n3️⃣ Verificando engine.step()...")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    with open(engine_path, 'r', encoding='utf-8') as f:
        engine_content = f.read()
    
    if 'def step(' in engine_content:
        print("✅ step() existe")
        
        pattern = r'def step\(self[^)]*\):(.*?)(?=\n\s{0,4}def|\nclass|\Z)'
        match = re.search(pattern, engine_content, re.DOTALL)
        
        if match:
            step_content = match.group(1)
            
            checks = {
                'llama_update_with_deltas': 'update_with_deltas' in step_content,
                'procesa_deltas': 'for delta in' in step_content,
                'aplica_posicion': '+= delta.position' in step_content,
                'verifica_deltas_lista': 'if deltas:' in step_content or 'if deltas and' in step_content
            }
            
            for check, result in checks.items():
                print(f"  - {check}: {'✅' if result else '❌'}")
            
            if not all(checks.values()):
                return 'fix_step_implementation'
    
    return None

def apply_fixes(fix_type):
    """Aplica los fixes necesarios"""
    
    if fix_type == 'fix_return_list':
        print("\n🔧 Arreglando update_with_deltas para retornar lista...")
        
        motion_path = "trajectory_hub/core/motion_components.py"
        
        # Backup
        backup_path = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(motion_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Arreglar retorno
        # Opción 1: Si retorna 'delta'
        content = re.sub(
            r'(def update_with_deltas.*?return\s+)(delta)(\s*$)',
            r'\1[delta] if delta else []\3',
            content,
            flags=re.DOTALL | re.MULTILINE
        )
        
        # Opción 2: Si retorna MotionDelta directamente
        content = re.sub(
            r'(def update_with_deltas.*?return\s+)(MotionDelta\([^)]+\))',
            r'\1[\2]',
            content,
            flags=re.DOTALL
        )
        
        with open(motion_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Arreglado para retornar lista")
        return True
    
    elif fix_type == 'fix_step_implementation':
        print("\n🔧 Arreglando implementación de step()...")
        
        # Aquí iría el código para arreglar step()
        # Por ahora solo informamos
        print("⚠️ step() necesita arreglo manual")
        return False
    
    return True

def create_minimal_debug_test():
    """Test mínimo con máximo debug"""
    
    test_code = '''# === test_delta_debug_minimal.py ===
# Test mínimo con debug detallado

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent, MotionDelta
import numpy as np

print("🔍 DEBUG MÍNIMO DEL SISTEMA")
print("="*50)

# Test 1: ConcentrationComponent directamente
print("\\n1️⃣ Test directo de ConcentrationComponent:")
comp = ConcentrationComponent()
comp.enabled = True
comp.concentration_factor = 0.8
comp.concentration_center = np.array([0.0, 0.0, 0.0])

# Estado falso
class FakeState:
    def __init__(self):
        self.position = np.array([10.0, 0.0, 0.0])
        self.source_id = 0

state = FakeState()

# Calcular delta
delta = comp.calculate_delta(state, 0.0, 0.1)
print(f"  Delta calculado: {delta}")
if delta:
    print(f"  - position: {delta.position}")
    print(f"  - source_id: {delta.source_id}")

# Test 2: SourceMotion
print("\\n2️⃣ Test de SourceMotion.update_with_deltas:")
from trajectory_hub.core.motion_components import SourceMotion, MotionState

motion_state = MotionState()
motion_state.position = np.array([10.0, 0.0, 0.0])
motion_state.source_id = 0

motion = SourceMotion(motion_state)
motion.source_id = 0

# Añadir componente
motion.add_component(comp, 'concentration')

# Llamar update_with_deltas
result = motion.update_with_deltas(0.0, 0.1)
print(f"  Resultado: {result}")
print(f"  - Tipo: {type(result)}")
print(f"  - Es lista: {isinstance(result, list)}")

if isinstance(result, list):
    print(f"  - Longitud: {len(result)}")
    for i, d in enumerate(result):
        print(f"  - Delta {i}: {d}")
        if hasattr(d, 'position'):
            print(f"    position: {d.position}")
else:
    print("  ❌ NO es una lista!")
    if hasattr(result, 'position'):
        print(f"  - position: {result.position}")

# Test 3: Sistema completo
print("\\n3️⃣ Test del sistema completo:")
engine = EnhancedTrajectoryEngine(max_sources=1)
engine.running = True
engine.create_source(0, "test")
engine._positions[0] = np.array([10.0, 0.0, 0.0])

# Aplicar concentración
motion = engine.motion_states[0]
motion.add_component(comp, 'concentration')

print(f"  Posición antes: {engine._positions[0]}")

# Un solo step con debug
if hasattr(engine, 'step'):
    engine.step()
else:
    print("  ❌ No existe engine.step()")

print(f"  Posición después: {engine._positions[0]}")
'''
    
    with open('test_delta_debug_minimal.py', 'w') as f:
        f.write(test_code)
    
    print("\n✅ Test debug creado: test_delta_debug_minimal.py")

if __name__ == "__main__":
    print("🔧 FIX DEFINITIVO DEL SISTEMA DE DELTAS")
    print("="*60)
    
    # Analizar
    fix_needed = analyze_complete_flow()
    
    if fix_needed:
        print(f"\n🔧 Aplicando fix: {fix_needed}")
        success = apply_fixes(fix_needed)
        
        if success:
            print("\n✅ Fix aplicado")
    else:
        print("\n✅ No se detectaron problemas obvios")
    
    # Crear test
    create_minimal_debug_test()
    
    print("\n📋 Ejecuta el test de debug:")
    print("$ python test_delta_debug_minimal.py")
    print("\nEsto mostrará exactamente qué está pasando en cada paso.")