#!/usr/bin/env python3
"""
🔬 ANÁLISIS SIMPLE: Por qué no funciona la concentración
📋 Adaptado a la versión del 5 de julio
"""

import os
import sys
import numpy as np

os.environ['PYTHONPATH'] = os.getcwd()
sys.path.insert(0, os.getcwd())

def analyze():
    print("🔍 ANÁLISIS DE CONCENTRACIÓN - VERSIÓN BASE")
    print("=" * 60)
    
    try:
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    except ImportError as e:
        print(f"❌ Error importando: {e}")
        return
    
    # 1. CREAR MACRO SIMPLE
    print("\n1️⃣ CREANDO MACRO SIMPLE")
    engine = EnhancedTrajectoryEngine(max_sources=4)
    
    # Verificar que tenemos el método create_macro
    if not hasattr(engine, 'create_macro'):
        print("❌ No existe create_macro()")
        return
    
    macro_id = engine.create_macro("test", source_count=4)
    print(f"✅ Macro creado: {macro_id}")
    
    # Posiciones iniciales
    positions_before = engine._positions[:4].copy()
    print(f"\n📍 Posiciones iniciales:")
    for i, pos in enumerate(positions_before):
        print(f"   Fuente {i}: {pos}")
    
    # 2. VERIFICAR SET_MACRO_CONCENTRATION
    print("\n2️⃣ APLICANDO CONCENTRACIÓN")
    
    if hasattr(engine, 'set_macro_concentration'):
        print("✅ set_macro_concentration existe")
        engine.set_macro_concentration(macro_id, 0.5)
        
        # Verificar si se guardó
        if hasattr(engine, '_macros') and macro_id in engine._macros:
            macro = engine._macros[macro_id]
            factor = getattr(macro, 'concentration_factor', None)
            print(f"   Factor guardado: {factor}")
        else:
            print("❌ No se puede verificar el factor")
    else:
        print("❌ NO existe set_macro_concentration")
        return
    
    # 3. BUSCAR MÉTODO DE ACTUALIZACIÓN
    print("\n3️⃣ BUSCANDO MÉTODO DE ACTUALIZACIÓN")
    
    update_method = None
    
    if hasattr(engine, 'step'):
        print("✅ engine.step() existe")
        update_method = 'step'
    elif hasattr(engine, 'update'):
        print("✅ engine.update() existe")
        update_method = 'update'
    else:
        print("❌ No hay step() ni update()")
        
        # Buscar otros métodos
        methods = [m for m in dir(engine) if not m.startswith('_') and callable(getattr(engine, m))]
        print(f"\n📋 Métodos públicos disponibles:")
        for m in methods[:10]:
            print(f"   - {m}")
        return
    
    # 4. EJECUTAR ACTUALIZACIÓN
    print(f"\n4️⃣ EJECUTANDO {update_method}()")
    
    # Ejecutar varios frames
    for i in range(10):
        try:
            if update_method == 'step':
                engine.step()
            else:
                engine.update(1/60.0)
        except Exception as e:
            print(f"❌ Error en frame {i}: {e}")
            break
    
    # Verificar movimiento
    positions_after = engine._positions[:4]
    movements = []
    
    print(f"\n📍 Posiciones después de 10 frames:")
    for i in range(4):
        movement = np.linalg.norm(positions_after[i] - positions_before[i])
        movements.append(movement)
        print(f"   Fuente {i}: {positions_after[i]} (movió {movement:.4f})")
    
    # 5. DIAGNÓSTICO
    print("\n5️⃣ DIAGNÓSTICO")
    print("-" * 40)
    
    if sum(movements) > 0.01:
        print("✅ HAY MOVIMIENTO - La concentración funciona")
    else:
        print("❌ NO HAY MOVIMIENTO - La concentración NO funciona")
        
        # Buscar por qué
        print("\n🔍 BUSCANDO LA CAUSA...")
        
        # Verificar si hay código de concentración
        engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
        if os.path.exists(engine_file):
            with open(engine_file, 'r') as f:
                content = f.read()
            
            # Buscar referencias a concentración
            if 'concentration_factor' in content:
                print("✅ El código contiene 'concentration_factor'")
                
                # Ver dónde se usa
                lines = content.split('\n')
                uses = []
                
                for i, line in enumerate(lines):
                    if 'concentration_factor' in line and 'def' not in line:
                        # Contexto: método que lo contiene
                        for j in range(i, max(0, i-50), -1):
                            if 'def ' in lines[j]:
                                method = lines[j].strip()
                                uses.append((method, i+1, line.strip()))
                                break
                
                if uses:
                    print(f"\n📍 Usos de concentration_factor:")
                    for method, line_no, line in uses[:3]:
                        print(f"   {method}")
                        print(f"   L{line_no}: {line[:60]}...")
                else:
                    print("⚠️ concentration_factor existe pero no se usa")
            else:
                print("❌ El código NO contiene 'concentration_factor'")
        
        # Problema más probable
        print("\n💡 CAUSA PROBABLE:")
        print("La concentración está definida pero NO está conectada")
        print("al sistema de actualización de posiciones.")
        
        print("\n🔧 SOLUCIÓN NECESARIA:")
        print("1. Agregar lógica de concentración en step() o update()")
        print("2. Calcular dirección hacia el centro del macro")
        print("3. Mover las fuentes gradualmente")

def check_implementation():
    """Verificar qué falta implementar"""
    
    print("\n\n6️⃣ VERIFICACIÓN DE IMPLEMENTACIÓN")
    print("=" * 60)
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_file):
        print("❌ No se encuentra el archivo del engine")
        return
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar componentes clave
    components = {
        'create_macro': 'def create_macro' in content,
        'set_macro_concentration': 'def set_macro_concentration' in content,
        'step': 'def step' in content,
        'update': 'def update' in content,
        '_apply_concentration': 'def _apply_concentration' in content,
        'concentration_logic': 'concentration_factor' in content and ('step' in content or 'update' in content)
    }
    
    print("📋 COMPONENTES NECESARIOS:")
    for comp, exists in components.items():
        status = "✅" if exists else "❌"
        print(f"   {status} {comp}")
    
    # Si falta la lógica, mostrar ejemplo
    if not components['concentration_logic']:
        print("\n🔧 CÓDIGO FALTANTE (ejemplo):")
        print("""
def step(self):
    # ... código existente ...
    
    # Aplicar concentración a macros
    for macro_id, macro in self._macros.items():
        if hasattr(macro, 'concentration_factor') and macro.concentration_factor > 0:
            # Calcular centro del macro
            positions = [self._positions[sid] for sid in macro.source_ids]
            center = np.mean(positions, axis=0)
            
            # Mover cada fuente hacia el centro
            for sid in macro.source_ids:
                direction = center - self._positions[sid]
                movement = direction * macro.concentration_factor * 0.01
                self._positions[sid] += movement
    
    # ... resto del código ...
""")

def main():
    analyze()
    check_implementation()
    
    print("\n" + "="*60)
    print("🎯 RESUMEN")
    print("="*60)
    print("\nLa concentración no funciona porque:")
    print("1. El método set_macro_concentration() guarda el factor")
    print("2. PERO step()/update() no usa ese factor")
    print("3. Falta la lógica que mueve las fuentes hacia el centro")
    print("\n✅ La solución es simple: agregar ~10 líneas en step()")

if __name__ == "__main__":
    main()