#!/usr/bin/env python3
"""
🧪 Test simple: Ver qué sources se envían
"""

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import time

def test():
    print("🧪 TEST OSC SIMPLE")
    print("=" * 50)
    
    engine = EnhancedTrajectoryEngine()
    
    # Interceptar el método update para ver qué pasa
    original_update = engine.update
    calls = []
    
    def debug_update(dt):
        # Contar sources procesadas
        active = len(engine._active_sources)
        calls.append(active)
        
        # Ver si hay algún límite
        if hasattr(engine, '_positions'):
            print(f"\n🔍 Update: {active} sources activas, {len(engine._positions)} positions")
        
        return original_update(dt)
    
    engine.update = debug_update
    engine.start()
    
    # Crear 3 macros
    print("\n1️⃣ Creando 3 macros...")
    for i in range(3):
        engine.create_macro(f"test_{i}", 8, "circle", 3.0)
        print(f"   Macro {i+1}: {len(engine._active_sources)} sources totales")
    
    # Esperar un poco
    print("\n2️⃣ Esperando 2 segundos...")
    time.sleep(2)
    
    engine.stop()
    
    print(f"\n📊 ANÁLISIS:")
    print(f"   Updates realizados: {len(calls)}")
    if calls:
        print(f"   Sources procesadas: {calls[0]} → {calls[-1]}")
    
    # Verificar positions
    if hasattr(engine, '_positions'):
        print(f"   Positions en engine: {len(engine._positions)}")
        print(f"   Sources activas: {len(engine._active_sources)}")
        
        if len(engine._positions) < len(engine._active_sources):
            print("\n❌ PROBLEMA: Hay menos positions que sources activas")

if __name__ == "__main__":
    test()