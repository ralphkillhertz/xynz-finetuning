#!/usr/bin/env python3
# 🧪 Test: Verificar que TODAS las sources sean visibles
# ⚡ Crea 3 macros de 10 sources cada uno = 30 sources total

import time
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge

def test_all_sources():
    print("\n🧪 TEST TODAS LAS SOURCES VISIBLES")
    print("=" * 60)
    
    # Crear engine y OSC
    engine = EnhancedTrajectoryEngine()
    engine.osc_bridge = SpatOSCBridge()
    print("✅ Sistema inicializado")
    
    # Iniciar engine
    engine.start()
    print("✅ Engine iniciado - Loop activo\n")
    
    # Crear 3 macros de 10 sources cada uno
    formations = ['circle', 'line', 'grid']
    total_sources = 0
    
    for i, formation in enumerate(formations):
        print(f"\n🎯 Creando Macro {i+1} ({formation}) con 10 sources...")
        result = engine.create_macro(
            name=f"test_{formation}",
            source_count=10,
            formation=formation,
            spacing=3.0
        )
        total_sources += 10
        print(f"   ✅ {result}")
        print(f"   📊 Total sources: {total_sources}")
        time.sleep(0.5)
    
    # Esperar y verificar
    print(f"\n📡 Enviando {total_sources} sources a Spat...")
    print("   Deberías ver sources 1-30 en Spat")
    print("\n⏰ Esperando 5 segundos...")
    
    for i in range(5):
        time.sleep(1)
        print(f"   {5-i}...")
    
    # Detener
    engine.stop()
    print("\n✅ Test completado")
    print(f"📊 Resumen:")
    print(f"   - Macros creados: {len(formations)}")
    print(f"   - Sources totales: {total_sources}")
    print(f"   - Sources activas: {len(engine._active_sources)}")
    print("\n🎯 Verifica en Spat que aparezcan TODAS las 30 sources")

if __name__ == "__main__":
    test_all_sources()