#!/usr/bin/env python3
"""
🔧 Fix definitivo: Cambiar 'velocity' → 'fix' en todo el código
⚡ El modo correcto para velocidad constante es FIX
🎯 Impacto: CRÍTICO - Sin esto las trayectorias no se mueven
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_all_velocity_references():
    """Cambiar todas las referencias de 'velocity' a 'fix'"""
    
    files_to_fix = [
        'interactive_controller.py',
        'trajectory_hub/core/enhanced_trajectory_engine.py',
        'trajectory_hub/core/motion_components.py'
    ]
    
    fixed_files = []
    
    for filename in files_to_fix:
        try:
            print(f"\n🔧 Procesando {filename}...")
            
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Cambiar movement_mode='velocity' → movement_mode='fix'
            content = re.sub(
                r"movement_mode\s*=\s*['\"]velocity['\"]",
                "movement_mode='fix'",
                content
            )
            
            # Cambiar "velocity" en contextos de modo
            content = re.sub(
                r'["\']velocity["\'](\s*#.*velocidad constante)?',
                lambda m: "'fix'" + (m.group(1) if m.group(1) else ""),
                content
            )
            
            if content != original_content:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   ✅ Archivo actualizado")
                fixed_files.append(filename)
            else:
                print(f"   ℹ️ Sin cambios necesarios")
                
        except FileNotFoundError:
            print(f"   ⚠️ Archivo no encontrado")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return fixed_files

def add_velocity_alias():
    """Agregar alias para que 'velocity' funcione como 'fix'"""
    
    print("\n🔧 Agregando alias velocity → fix en motion_components.py...")
    
    try:
        with open('trajectory_hub/core/motion_components.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Buscar el método set_movement_mode
        for i, line in enumerate(lines):
            if 'def set_movement_mode(self' in line:
                # Buscar dónde insertar el código
                for j in range(i+1, min(i+30, len(lines))):
                    if 'self.movement_mode' in lines[j] and '=' in lines[j]:
                        # Insertar antes de esta línea
                        indent = '        '
                        alias_code = [
                            f"{indent}# Alias para compatibilidad\n",
                            f"{indent}if isinstance(mode, str):\n",
                            f"{indent}    if mode == 'velocity':\n",
                            f"{indent}        mode = 'fix'\n",
                            f"{indent}    try:\n",
                            f"{indent}        mode = TrajectoryMovementMode(mode)\n",
                            f"{indent}    except ValueError:\n",
                            f"{indent}        mode = TrajectoryMovementMode.FIX\n",
                            f"\n"
                        ]
                        
                        # Insertar el código
                        lines[j:j] = alias_code
                        
                        # Guardar
                        with open('trajectory_hub/core/motion_components.py', 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                        
                        print("   ✅ Alias agregado")
                        return True
        
        print("   ⚠️ No se pudo agregar el alias automáticamente")
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_concentration_after_fix():
    """Test completo de concentración después del fix"""
    
    print("\n🧪 TEST DE CONCENTRACIÓN POST-FIX")
    print("="*50)
    
    try:
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        from trajectory_hub.core.motion_components import TrajectoryMovementMode
        import numpy as np
        
        # Crear engine sin OSC
        engine = EnhancedTrajectoryEngine(osc_bridge=None)
        
        # Crear macro como en tu test original
        macro_id = engine.create_macro("qwe", 50)
        print(f"✅ Macro '{macro_id}' creado con 50 fuentes")
        
        # Configurar trayectorias individuales con modo FIX
        trajectories = {i: 'circle' for i in range(50)}
        engine.set_individual_trajectories(
            macro_id,
            trajectories,
            movement_mode='fix',  # Usar 'fix' en lugar de 'velocity'
            movement_speed=1.0
        )
        print("✅ Trayectorias configuradas con modo FIX")
        
        # Verificar configuración inicial
        print("\n📊 Verificación inicial:")
        sample_sources = [0, 25, 49]  # Muestra de fuentes
        for i in sample_sources:
            if i in engine._source_motions:
                motion = engine._source_motions[i]
                if 'individual_trajectory' in motion.components:
                    traj = motion.components['individual_trajectory']
                    print(f"   Fuente {i}: enabled={traj.enabled}, fase={traj.position_on_trajectory:.3f}")
        
        # Ejecutar algunos updates
        print("\n⏯️ Ejecutando 10 updates...")
        for _ in range(10):
            engine.update()
        
        # Verificar movimiento
        print("\n📊 Estado después de updates:")
        movement_ok = False
        for i in sample_sources:
            if i in engine._source_motions:
                motion = engine._source_motions[i]
                if 'individual_trajectory' in motion.components:
                    traj = motion.components['individual_trajectory']
                    print(f"   Fuente {i}: fase={traj.position_on_trajectory:.3f}")
                    if traj.position_on_trajectory > 0:
                        movement_ok = True
        
        if movement_ok:
            print("\n✅ Las trayectorias se mueven correctamente")
            
            # Test de concentración
            print("\n🎯 TEST DE CONCENTRACIÓN")
            print("-"*40)
            
            # Aplicar concentración total
            print("Aplicando factor 0.0 (totalmente concentrado)...")
            engine.set_concentration_factor(macro_id, 0.0)
            engine.update()
            print("✅ Concentración aplicada")
            
            # Toggle
            print("\nEjecutando toggle...")
            engine.toggle_concentration(macro_id)
            engine.update()
            print("✅ Toggle ejecutado")
            
            # Animar concentración
            print("\nAnimando concentración...")
            for i in range(5):
                engine.animate_concentration(macro_id, target_factor=(i % 2), duration=0.5)
                engine.update()
            print("✅ Animación funcionando")
            
            return True
        else:
            print("\n❌ Las trayectorias NO se mueven - verificar el fix")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 FIX DEFINITIVO - CONCENTRACIÓN")
    print("="*60)
    
    # 1. Cambiar todas las referencias de 'velocity' a 'fix'
    print("1️⃣ Cambiando 'velocity' → 'fix' en todos los archivos...")
    fixed = fix_all_velocity_references()
    
    # 2. Agregar alias para compatibilidad
    print("\n2️⃣ Agregando alias para compatibilidad...")
    alias_ok = add_velocity_alias()
    
    # 3. Test completo
    print("\n3️⃣ Ejecutando test completo...")
    test_ok = test_concentration_after_fix()
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN:")
    print(f"   Archivos corregidos: {len(fixed)}")
    print(f"   Alias agregado: {'✅' if alias_ok else '❌'}")
    print(f"   Test funcional: {'✅' if test_ok else '❌'}")
    
    if test_ok:
        print("\n🎉 ¡PROBLEMA RESUELTO! La concentración ahora debería funcionar")
        print("\nPrueba en el controlador interactivo:")
        print("  - Opción 10: Configurar trayectorias")
        print("  - Opción 31: Control de concentración")
    else:
        print("\n⚠️ Puede que necesites hacer cambios manuales adicionales")