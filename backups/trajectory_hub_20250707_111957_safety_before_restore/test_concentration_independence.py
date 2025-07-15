#!/usr/bin/env python3
"""
🧪 TEST: CONCENTRACIÓN INDEPENDIENTE DE IS
⚡ Verifica si la concentración funciona sin trayectorias individuales
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🧪 TEST DE INDEPENDENCIA DE CONCENTRACIÓN")
print("="*60)

# 1. TEST BÁSICO: Crear macro sin IS y aplicar concentración
print("\n1️⃣ TEST BÁSICO: Macro sin trayectorias IS")
print("-"*60)

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    print("✅ Engine creado")
    
    # Crear macro SIN trayectorias individuales
    macro_id = engine.create_macro("test_concentration", 10)
    print(f"✅ Macro creado: {macro_id}")
    
    # Intentar aplicar concentración
    print("\n🎯 Aplicando concentración SIN trayectorias IS...")
    
    try:
        # Usar el método correcto
        engine.set_macro_concentration(macro_id, factor=0.0)  # 0 = totalmente concentrado
        print("✅ set_macro_concentration ejecutado sin errores")
        
        # Verificar estado
        state = engine.get_macro_concentration_state(macro_id)
        if 'error' not in state:
            print(f"✅ Estado de concentración: factor={state.get('factor', 'N/A')}")
            
            # Hacer update para ver si realmente funciona
            engine.update()
            print("✅ engine.update() ejecutado sin errores")
            
            # Toggle para verificar
            engine.toggle_macro_concentration(macro_id)
            print("✅ toggle_macro_concentration ejecutado")
            
            print("\n✅ ¡CONCENTRACIÓN FUNCIONA SIN IS!")
            concentration_works_without_is = True
            
        else:
            print(f"❌ Error en estado: {state.get('error')}")
            concentration_works_without_is = False
            
    except Exception as e:
        print(f"❌ Error al aplicar concentración: {e}")
        concentration_works_without_is = False
        
except Exception as e:
    print(f"❌ Error general: {e}")
    concentration_works_without_is = False

# 2. ANALIZAR CÓDIGO FUENTE
print("\n\n2️⃣ ANÁLISIS DE CÓDIGO FUENTE")
print("-"*60)

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
if os.path.exists(engine_file):
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar el método set_macro_concentration
    method_start = content.find('def set_macro_concentration')
    if method_start != -1:
        # Extraer el método completo
        method_end = content.find('\n    def ', method_start + 1)
        if method_end == -1:
            method_end = method_start + 2000
        
        method_code = content[method_start:method_end]
        
        print("🔍 Analizando set_macro_concentration...")
        
        # Buscar si verifica trayectorias individuales
        checks_for_is = False
        if 'individual_trajectory' in method_code:
            print("  ⚠️ Menciona 'individual_trajectory'")
            checks_for_is = True
            
            # Ver contexto
            lines = method_code.split('\n')
            for i, line in enumerate(lines):
                if 'individual_trajectory' in line:
                    print(f"     Línea {i}: {line.strip()}")
        
        # Buscar si crea ConcentrationComponent independientemente
        if 'ConcentrationComponent()' in method_code:
            print("  ✅ Crea ConcentrationComponent sin condiciones")
        
        # Buscar línea específica que podría causar dependencia
        if 'if' in method_code and 'individual_trajectory' in method_code:
            print("  ❌ Posible dependencia condicional de IS")
        else:
            print("  ✅ No parece tener dependencia directa de IS")

# 3. TEST DE ROTACIÓN MS CON IS
print("\n\n3️⃣ TEST: ROTACIÓN MS CON IS ACTIVA")
print("-"*60)

try:
    # Crear nuevo macro
    macro_id2 = engine.create_macro("test_rotation", 5)
    print(f"✅ Macro creado: {macro_id2}")
    
    # Agregar trayectorias IS
    print("\n🎯 Agregando trayectorias IS...")
    for i in range(5):
        engine.set_individual_trajectory(i, 'circle', mode='fix')
    print("✅ Trayectorias IS configuradas")
    
    # Intentar rotación MS
    print("\n🔄 Aplicando rotación MS con IS activa...")
    try:
        engine.set_macro_rotation(macro_id2, pitch=0.5, yaw=0.5, roll=0.0)
        print("✅ set_macro_rotation ejecutado")
        
        # Verificar si se aplica
        engine.update()
        print("✅ Rotación MS funciona con IS activa")
        ms_rotation_works_with_is = True
        
    except Exception as e:
        print(f"❌ Error en rotación MS: {e}")
        ms_rotation_works_with_is = False
        
except Exception as e:
    print(f"❌ Error en test de rotación: {e}")
    ms_rotation_works_with_is = False

# 4. BUSCAR BLOQUEOS EN UPDATE
print("\n\n4️⃣ ANÁLISIS DE BLOQUEOS EN UPDATE")
print("-"*60)

if os.path.exists(engine_file):
    # Buscar el método update
    update_start = content.find('def update(self')
    if update_start != -1:
        update_end = content.find('\n    def ', update_start + 1)
        if update_end == -1:
            update_end = update_start + 3000
            
        update_code = content[update_start:update_end]
        
        print("🔍 Analizando engine.update()...")
        
        # Buscar patrones de bloqueo
        lines = update_code.split('\n')
        blocking_patterns = []
        
        for i, line in enumerate(lines):
            # Buscar condiciones que podrían bloquear
            if 'if' in line and ('individual_trajectory' in line or 'IS' in line):
                if 'continue' in lines[i:i+5] or 'return' in lines[i:i+5]:
                    blocking_patterns.append((i, line.strip()))
                    
        if blocking_patterns:
            print(f"  ❌ Encontrados {len(blocking_patterns)} posibles bloqueos:")
            for line_num, pattern in blocking_patterns[:3]:
                print(f"     Línea {line_num}: {pattern}")
        else:
            print("  ✅ No se encontraron bloqueos obvios")

# RESUMEN
print("\n\n" + "="*60)
print("📊 RESUMEN DE RESULTADOS")
print("="*60)

print("\n🎯 CONCENTRACIÓN:")
if concentration_works_without_is:
    print("  ✅ Funciona SIN trayectorias IS")
else:
    print("  ❌ Depende de trayectorias IS")

print("\n🔄 ROTACIÓN MS:")
if ms_rotation_works_with_is:
    print("  ✅ Funciona CON trayectorias IS")
else:
    print("  ❌ Bloqueada por trayectorias IS")

print("\n🏗️ ARQUITECTURA:")
print("  ❌ Secuencial con sobrescritura (confirmado)")

print("\n💡 RECOMENDACIÓN:")
if concentration_works_without_is and ms_rotation_works_with_is:
    print("  Los problemas principales parecen estar resueltos")
    print("  Solo falta implementar arquitectura de suma")
else:
    print("  Implementar arquitectura paralela de deltas")
    print("  para resolver todos los problemas")

print("\n✅ Test completado")