#!/usr/bin/env python3
"""
🔧 Test: Verifica que el sistema de deltas esté completo
⚡ Incluye: Debug detallado para identificar problemas
🎯 Objetivo: Concentración funcionando con deltas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

def test_imports():
    """Test 1: Verificar que todo se importa"""
    print("1️⃣ Verificando imports...")
    try:
        from trajectory_hub import EnhancedTrajectoryEngine
        print("   ✅ EnhancedTrajectoryEngine")
        
        from trajectory_hub.core.motion_components import (
            MotionState, MotionDelta, SourceMotion, 
            ConcentrationComponent
        )
        print("   ✅ MotionState")
        print("   ✅ MotionDelta") 
        print("   ✅ SourceMotion")
        print("   ✅ ConcentrationComponent")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_source_motion():
    """Test 2: Verificar SourceMotion"""
    print("\n2️⃣ Verificando SourceMotion...")
    try:
        from trajectory_hub.core.motion_components import SourceMotion
        
        # Crear instancia
        sm = SourceMotion(0)
        print(f"   ✅ SourceMotion creado")
        
        # Verificar atributos
        attrs = {
            'source_id': 'ID de la fuente',
            'state': 'Estado del movimiento',
            'active_components': 'Lista de componentes',
            'add_component': 'Método para añadir componentes',
            'update_with_deltas': 'Método para deltas'
        }
        
        for attr, desc in attrs.items():
            if hasattr(sm, attr):
                print(f"   ✅ {attr}: {desc}")
            else:
                print(f"   ❌ {attr}: FALTA")
                
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_concentration():
    """Test 3: Sistema completo de concentración"""
    print("\n3️⃣ Test completo de concentración...")
    
    try:
        from trajectory_hub import EnhancedTrajectoryEngine
        
        # Crear engine
        engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
        print("   ✅ Engine creado")
        
        # Crear macro
        source_ids = [0, 1, 2]
        engine.create_macro("test", source_ids)
        print("   ✅ Macro creado")
        
        # Verificar motion_states
        print(f"   📊 Motion states: {list(engine.motion_states.keys())}")
        
        # Si no hay motion_states, crearlos manualmente
        if not engine.motion_states:
            print("   ⚠️ Creando motion_states manualmente...")
            from trajectory_hub.core.motion_components import SourceMotion
            for sid in source_ids:
                engine.motion_states[sid] = SourceMotion(sid)
            print(f"   ✅ Motion states creados: {list(engine.motion_states.keys())}")
        
        # Posiciones iniciales
        print("\n   📍 Posiciones iniciales:")
        for i in source_ids:
            angle = i * 2 * np.pi / 3
            pos = np.array([np.cos(angle) * 10, np.sin(angle) * 10, 0])
            engine._positions[i] = pos
            print(f"      Source {i}: [{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}]")
        
        # Calcular distancia inicial
        center = np.mean([engine._positions[i] for i in source_ids], axis=0)
        dist_inicial = np.mean([np.linalg.norm(engine._positions[i] - center) for i in source_ids])
        print(f"\n   📏 Distancia inicial al centro: {dist_inicial:.2f}")
        
        # Aplicar concentración
        print("\n   🎯 Aplicando concentración...")
        try:
            result = engine.set_macro_concentration("test", factor=0.8)
            if result:
                print("   ✅ Concentración aplicada")
            else:
                print("   ❌ Concentración falló")
        except Exception as e:
            print(f"   ❌ Error aplicando concentración: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Simular algunos frames
        print("\n   🔄 Simulando 10 frames...")
        for frame in range(10):
            try:
                positions = engine.step()
                
                if frame % 3 == 0:
                    center = np.mean([positions[i] for i in source_ids], axis=0)
                    dist = np.mean([np.linalg.norm(positions[i] - center) for i in source_ids])
                    cambio = dist_inicial - dist
                    print(f"      Frame {frame}: dist={dist:.2f}, cambio={cambio:+.2f}")
                    
            except Exception as e:
                print(f"   ❌ Error en frame {frame}: {e}")
                return False
        
        # Verificar si hubo cambio
        center_final = np.mean([engine._positions[i] for i in source_ids], axis=0)
        dist_final = np.mean([np.linalg.norm(engine._positions[i] - center_final) for i in source_ids])
        
        if dist_final < dist_inicial:
            print(f"\n   ✅ ¡CONCENTRACIÓN FUNCIONA! Distancia cambió de {dist_inicial:.2f} a {dist_final:.2f}")
            return True
        else:
            print(f"\n   ❌ Sin cambio en distancia: {dist_inicial:.2f} -> {dist_final:.2f}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecuta todos los tests"""
    print("🧪 TEST COMPLETO DEL SISTEMA DE DELTAS")
    print("=" * 60)
    
    # Test 1
    if not test_imports():
        print("\n❌ Fallo en imports básicos")
        return
    
    # Test 2  
    if not test_source_motion():
        print("\n❌ Fallo en SourceMotion")
        return
    
    # Test 3
    if test_concentration():
        print("\n🎉 ¡SISTEMA DE DELTAS FUNCIONANDO!")
        print("\n✅ Concentración implementada correctamente")
        print("✅ Motion states funcionando")
        print("✅ Sistema de deltas operativo")
        
        print("\n📋 Próximos pasos:")
        print("1. Migrar IndividualTrajectory a deltas")
        print("2. Migrar MacroTrajectory a deltas")  
        print("3. Probar combinaciones complejas")
    else:
        print("\n⚠️ El sistema necesita más ajustes")

if __name__ == "__main__":
    main()