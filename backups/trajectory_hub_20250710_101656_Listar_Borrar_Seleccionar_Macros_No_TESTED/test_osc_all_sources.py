#!/usr/bin/env python3
"""
🧪 Test: Verificar envío OSC de todas las sources
"""

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import time

def test_osc():
    print("🧪 TEST OSC TODAS LAS SOURCES")
    print("=" * 50)
    
    engine = EnhancedTrajectoryEngine()
    engine.start()
    
    # Crear 3 macros para tener 24 sources
    print("\n1️⃣ Creando 3 macros (24 sources total)...")
    
    for i in range(3):
        engine.create_macro(
            name=f"test_macro_{i}",
            source_count=8,
            formation="circle",
            spacing=3.0 + i  # Diferentes radios para distinguir
        )
        print(f"   ✅ Macro {i+1} creado")
    
    print(f"\n📊 Sources activas: {len(engine._active_sources)}")
    print(f"   IDs: {sorted(engine._active_sources)}")
    
    # Verificar qué se está enviando
    print("\n2️⃣ Monitoreando OSC por 5 segundos...")
    print("   (Verifica en Spat cuántas sources aparecen)")
    
    # Contar mensajes OSC
    start_time = time.time()
    msg_count = 0
    unique_ids = set()
    
    # Modificar temporalmente para contar
    original_send = engine.osc_bridge.send_source_position
    
    def counting_send(source_id, x, y, z):
        nonlocal msg_count, unique_ids
        msg_count += 1
        unique_ids.add(source_id)
        return original_send(source_id, x, y, z)
    
    engine.osc_bridge.send_source_position = counting_send
    
    # Esperar 5 segundos
    time.sleep(5)
    
    # Restaurar
    engine.osc_bridge.send_source_position = original_send
    
    elapsed = time.time() - start_time
    print(f"\n📊 RESULTADOS:")
    print(f"   Mensajes OSC enviados: {msg_count}")
    print(f"   Sources únicas enviadas: {len(unique_ids)}")
    print(f"   IDs enviados: {sorted(unique_ids)}")
    print(f"   Frecuencia: {msg_count/elapsed:.1f} msgs/seg")
    
    if len(unique_ids) < len(engine._active_sources):
        print(f"\n❌ PROBLEMA: Solo {len(unique_ids)} de {len(engine._active_sources)} sources se envían")
        missing = sorted(engine._active_sources - unique_ids)
        print(f"   Sources NO enviadas: {missing}")
    else:
        print(f"\n✅ Todas las sources se están enviando")
    
    engine.stop()

if __name__ == "__main__":
    test_osc()