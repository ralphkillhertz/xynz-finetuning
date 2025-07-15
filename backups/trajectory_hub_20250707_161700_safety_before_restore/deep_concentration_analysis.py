#!/usr/bin/env python3
"""
🔬 ANÁLISIS PROFUNDO: Concentración en Macros
📋 Objetivo: Entender por qué un macro sin movimiento no ejecuta concentración
🎯 Método: Rastrear todo el flujo desde creación hasta movimiento
"""

import os
import sys
import numpy as np
from datetime import datetime

# Configurar para análisis
os.environ['PYTHONPATH'] = os.getcwd()
sys.path.insert(0, os.getcwd())

def analyze_concentration_flow():
    """Analizar paso a paso el flujo de concentración"""
    
    print("🔬 ANÁLISIS PROFUNDO DE CONCENTRACIÓN")
    print("=" * 70)
    
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # 1. CREAR ENGINE Y MACRO
    print("\n1️⃣ CREACIÓN DE ENGINE Y MACRO")
    print("-" * 50)
    
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
    print(f"✅ Engine creado con {engine.max_sources} fuentes")
    
    # Verificar estado inicial
    print(f"\n📊 Estado inicial del engine:")
    print(f"   - _time: {engine._time}")
    print(f"   - _frame_count: {engine._frame_count}")
    print(f"   - running: {engine.running}")
    
    # Crear macro
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=4.0)
    print(f"\n✅ Macro creado: {macro_id}")
    
    # 2. VERIFICAR ESTRUCTURA DEL MACRO
    print("\n2️⃣ ESTRUCTURA DEL MACRO")
    print("-" * 50)
    
    if macro_id in engine._macros:
        macro = engine._macros[macro_id]
        print(f"✅ Macro encontrado en engine._macros")
        print(f"   - source_ids: {getattr(macro, 'source_ids', 'NO TIENE')}")
        print(f"   - concentration_factor: {getattr(macro, 'concentration_factor', 'NO TIENE')}")
        print(f"   - Tipo: {type(macro)}")
        print(f"   - Atributos: {[a for a in dir(macro) if not a.startswith('_')]}")
    else:
        print(f"❌ Macro NO encontrado en engine._macros")
        return
    
    # 3. APLICAR CONCENTRACIÓN
    print("\n3️⃣ APLICAR CONCENTRACIÓN")
    print("-" * 50)
    
    print("Llamando set_macro_concentration(macro_id, 0.5)...")
    engine.set_macro_concentration(macro_id, 0.5)
    
    # Verificar que se aplicó
    macro = engine._macros[macro_id]
    print(f"✅ concentration_factor después: {getattr(macro, 'concentration_factor', 'NO TIENE')}")
    
    # 4. ANALIZAR MÉTODO STEP
    print("\n4️⃣ ANÁLISIS DEL MÉTODO STEP")
    print("-" * 50)
    
    # Verificar que step existe
    if hasattr(engine, 'step'):
        print("✅ engine.step() existe")
        
        # Analizar el código de step
        import inspect
        try:
            step_code = inspect.getsource(engine.step)
            print("\n📜 Código de step():")
            print("-" * 30)
            # Mostrar solo las primeras líneas relevantes
            lines = step_code.split('\n')[:20]
            for i, line in enumerate(lines):
                if 'concentration' in line.lower() or 'macro' in line:
                    print(f"L{i}: {line}")
        except:
            print("❌ No se pudo obtener el código de step()")
    else:
        print("❌ engine.step() NO existe")
        # Buscar update
        if hasattr(engine, 'update'):
            print("⚠️ Pero engine.update() SÍ existe")
    
    # 5. EJECUTAR UN FRAME Y RASTREAR
    print("\n5️⃣ EJECUCIÓN DE UN FRAME")
    print("-" * 50)
    
    # Guardar posiciones iniciales
    initial_positions = engine._positions[:4].copy()
    print(f"Posiciones iniciales: {initial_positions}")
    
    # Intentar ejecutar step
    try:
        if hasattr(engine, 'step'):
            result = engine.step()
            print("✅ step() ejecutado")
            if result:
                print(f"   Resultado: {type(result)}")
        elif hasattr(engine, 'update'):
            engine.update(1/60)
            print("✅ update() ejecutado")
    except Exception as e:
        print(f"❌ Error ejecutando step/update: {e}")
    
    # Verificar cambios
    final_positions = engine._positions[:4]
    movement = np.sum(np.abs(final_positions - initial_positions))
    print(f"\nPosiciones finales: {final_positions}")
    print(f"Movimiento total: {movement}")
    
    # 6. BUSCAR DÓNDE SE APLICA LA CONCENTRACIÓN
    print("\n6️⃣ BÚSQUEDA DE APLICACIÓN DE CONCENTRACIÓN")
    print("-" * 50)
    
    # Buscar en el código dónde se usa concentration_factor
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    if os.path.exists(engine_file):
        with open(engine_file, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        concentration_lines = []
        
        for i, line in enumerate(lines):
            if 'concentration_factor' in line and 'def' not in line:
                concentration_lines.append((i+1, line.strip()))
        
        print(f"Encontradas {len(concentration_lines)} líneas con 'concentration_factor':")
        for line_no, line in concentration_lines[:5]:
            print(f"   L{line_no}: {line}")
    
    # 7. DIAGNÓSTICO
    print("\n7️⃣ DIAGNÓSTICO")
    print("-" * 50)
    
    problems = []
    
    if not hasattr(engine, 'step'):
        problems.append("step() no existe - el controlador no puede ejecutar frames")
    
    if movement == 0:
        problems.append("No hay movimiento - la concentración no se está aplicando")
    
    if not hasattr(macro, 'concentration_factor'):
        problems.append("El macro no tiene concentration_factor")
    
    # Buscar si step() tiene código de concentración
    if hasattr(engine, 'step'):
        step_code = inspect.getsource(engine.step)
        if 'concentration' not in step_code.lower():
            problems.append("step() no contiene código de concentración")
    
    if problems:
        print("❌ PROBLEMAS ENCONTRADOS:")
        for p in problems:
            print(f"   - {p}")
    else:
        print("✅ No se encontraron problemas obvios")
    
    # 8. POSIBLES CAUSAS
    print("\n8️⃣ ANÁLISIS DE CAUSAS PROBABLES")
    print("-" * 50)
    
    print("CAUSA 1: step() no llama al código de concentración")
    print("   - El método step() puede existir pero no incluir la lógica")
    print("   - La concentración puede estar en update() pero no en step()")
    
    print("\nCAUSA 2: La concentración requiere otro componente activo")
    print("   - Puede necesitar que haya una trayectoria activa")
    print("   - Puede estar condicionada a otro estado")
    
    print("\nCAUSA 3: El factor de concentración no se guarda correctamente")
    print("   - set_macro_concentration() puede no estar guardando el valor")
    print("   - El macro puede resetearse después")
    
    print("\nCAUSA 4: Error en el cálculo de posiciones")
    print("   - La fórmula puede estar mal")
    print("   - El dt puede ser 0 o muy pequeño")

def create_minimal_test():
    """Crear test mínimo para verificar"""
    
    print("\n\n9️⃣ TEST MÍNIMO DE VERIFICACIÓN")
    print("=" * 70)
    
    test_code = '''
# Test mínimo de concentración
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

engine = EnhancedTrajectoryEngine(max_sources=4)
macro_id = engine.create_macro("test", source_count=4)

# Verificar estructura
macro = engine._macros[macro_id]
print(f"Macro tipo: {type(macro)}")
print(f"Tiene concentration_factor: {hasattr(macro, 'concentration_factor')}")

# Aplicar concentración
engine.set_macro_concentration(macro_id, 0.8)
print(f"Factor aplicado: {getattr(macro, 'concentration_factor', 'NO TIENE')}")

# Buscar dónde se ejecuta
if hasattr(engine, 'step'):
    print("✅ Tiene step()")
    # Ver si step llama a algo más
    import inspect
    code = inspect.getsource(engine.step)
    if 'update' in code:
        print("   step() llama a update()")
    if 'concentration' in code.lower():
        print("   step() contiene lógica de concentración")
else:
    print("❌ NO tiene step()")
    
# Intentar movimiento manual
if hasattr(engine, '_apply_concentration'):
    print("✅ Tiene _apply_concentration()")
elif hasattr(engine, 'apply_concentration'):
    print("✅ Tiene apply_concentration()")
else:
    print("❌ No tiene método de aplicar concentración")
'''
    
    print(test_code)

def main():
    analyze_concentration_flow()
    create_minimal_test()
    
    print("\n" + "="*70)
    print("🎯 CONCLUSIÓN")
    print("=" * 70)
    print("\nLa concentración probablemente no funciona porque:")
    print("1. step() no incluye la lógica de concentración")
    print("2. La lógica está en update() pero el controlador llama a step()")
    print("3. Falta conectar set_macro_concentration() con el sistema de movimiento")
    print("\n💡 SOLUCIÓN PROPUESTA:")
    print("Implementar step() que:")
    print("1. Llame a update() si existe")
    print("2. Aplique la concentración después")
    print("3. Devuelva el estado para el controlador")

if __name__ == "__main__":
    main()