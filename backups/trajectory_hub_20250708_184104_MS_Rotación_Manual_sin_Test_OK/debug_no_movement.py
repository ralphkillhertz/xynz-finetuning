# === debug_no_movement.py ===
# 🔍 Debug: Por qué no hay movimiento en rotaciones
# ⚡ Rastrear el flujo completo de deltas

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import math

print("🔍 DEBUG: Por qué no hay movimiento")
print("=" * 60)

# Crear engine mínimo
engine = EnhancedTrajectoryEngine(max_sources=1, fps=60, enable_modulator=False)

# Una sola fuente
sid = 0
engine._active_sources[sid] = True
engine._positions[sid] = np.array([3.0, 0.0, 0.0])

# Crear macro
macro_name = engine.create_macro("square", source_count=1)
print(f"✅ Macro creado: {macro_name}")

# Verificar motion_states
print(f"\n🔍 Motion states existe para fuente {sid}: {sid in engine.motion_states}")
if sid in engine.motion_states:
    motion = engine.motion_states[sid]
    print(f"   Active components: {list(motion.active_components.keys())}")

# Configurar rotación
print("\n🔧 Configurando rotación 90°...")
engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi/2,
    interpolation_speed=0.5
)

# Verificar que se configuró
if sid in engine.motion_states:
    motion = engine.motion_states[sid]
    if 'manual_macro_rotation' in motion.active_components:
        comp = motion.active_components['manual_macro_rotation']
        print(f"✅ Componente configurado:")
        print(f"   - enabled: {comp.enabled}")
        print(f"   - target_yaw: {comp.target_yaw:.3f}")
        print(f"   - center: {comp.center}")
    else:
        print("❌ NO se agregó manual_macro_rotation")

# Ahora vamos a rastrear un update paso a paso
print("\n⚙️ Rastreando engine.update() paso a paso...")

# Guardar posición inicial
pos_inicial = engine._positions[sid].copy()
print(f"\nPosición inicial: {pos_inicial}")

# Monkey patch para debug
original_update = engine.update
update_called = False
motion_update_called = False
delta_calculated = False
delta_applied = False

def debug_engine_update(self):
    global update_called, motion_update_called, delta_applied
    update_called = True
    print("\n   [ENGINE] update() llamado")
    
    # Verificar sincronización
    for source_id in range(self.max_sources):
        if self._active_sources[source_id] and source_id in self.motion_states:
            old_state_pos = self.motion_states[source_id].state.position.copy()
            self.motion_states[source_id].state.position = self._positions[source_id].copy()
            print(f"   [ENGINE] State sincronizado: {old_state_pos} → {self._positions[source_id]}")
    
    # Llamar al update original
    original_update()
    
    # Ver si cambió la posición
    if not np.array_equal(pos_inicial, self._positions[sid]):
        delta_applied = True
        print(f"   [ENGINE] Posición cambió: {pos_inicial} → {self._positions[sid]}")
    else:
        print(f"   [ENGINE] Posición NO cambió")

# Monkey patch motion.update
if sid in engine.motion_states:
    motion = engine.motion_states[sid]
    original_motion_update = motion.update
    
    def debug_motion_update(self, current_time, dt):
        global motion_update_called
        motion_update_called = True
        print(f"\n   [MOTION] update() llamado con dt={dt}")
        
        # Llamar al original
        result = original_motion_update(current_time, dt)
        
        print(f"   [MOTION] update() retornó: {result}")
        return result
    
    motion.update = lambda ct, dt: debug_motion_update(motion, ct, dt)

# Monkey patch calculate_delta
if sid in engine.motion_states and 'manual_macro_rotation' in engine.motion_states[sid].active_components:
    comp = engine.motion_states[sid].active_components['manual_macro_rotation']
    original_calc_delta = comp.calculate_delta
    
    def debug_calc_delta(self, state, current_time, dt):
        global delta_calculated
        delta_calculated = True
        print(f"\n   [DELTA] calculate_delta llamado")
        print(f"   [DELTA] state.position: {state.position}")
        print(f"   [DELTA] current_yaw: {self.current_yaw:.3f}")
        
        delta = original_calc_delta(state, current_time, dt)
        
        if delta:
            print(f"   [DELTA] Delta calculado: {delta.position}")
            print(f"   [DELTA] Magnitud: {np.linalg.norm(delta.position):.6f}")
        else:
            print(f"   [DELTA] Delta es None")
        
        return delta
    
    comp.calculate_delta = lambda s, ct, dt: debug_calc_delta(comp, s, ct, dt)

# Aplicar monkey patches
engine.update = lambda: debug_engine_update(engine)

# Ejecutar UN update
print("\n🔄 Ejecutando UN engine.update()...")
engine.update()

# Resumen
print("\n" + "=" * 60)
print("📊 RESUMEN DE RASTREO:")
print(f"   - engine.update() llamado: {'✅' if update_called else '❌'}")
print(f"   - motion.update() llamado: {'✅' if motion_update_called else '❌'}")
print(f"   - calculate_delta() llamado: {'✅' if delta_calculated else '❌'}")
print(f"   - Posición cambió: {'✅' if delta_applied else '❌'}")

# Verificar manualmente
print("\n🧪 Verificación manual del sistema de deltas:")

# Ver si hay un método update_with_deltas
if sid in engine.motion_states:
    motion = engine.motion_states[sid]
    if hasattr(motion, 'update_with_deltas'):
        print("   - motion.update_with_deltas existe: ✅")
        
        # Llamarlo manualmente
        deltas = motion.update_with_deltas(0.0, 1/60.0)
        print(f"   - update_with_deltas retornó: {deltas}")
        
        if deltas:
            print(f"   - Número de deltas: {len(deltas)}")
            for i, d in enumerate(deltas):
                if d:
                    print(f"     Delta {i}: {d.position if hasattr(d, 'position') else d}")
    else:
        print("   - motion.update_with_deltas NO existe: ❌")

# Verificar si engine procesa deltas
print("\n🔍 Verificando procesamiento de deltas en engine:")
import inspect
engine_update_code = inspect.getsource(engine.__class__.update)
if "calculate_delta" in engine_update_code or "motion.update" in engine_update_code:
    print("   - engine.update() menciona deltas o motion.update: ✅")
    
    # Ver qué hace con el resultado
    if "motion.update(" in engine_update_code:
        # Buscar qué hace después
        lines = engine_update_code.split('\n')
        for i, line in enumerate(lines):
            if "motion.update(" in line:
                print(f"   - Línea con motion.update: {line.strip()}")
                # Ver las siguientes líneas
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip():
                        print(f"     Siguiente: {lines[j].strip()}")
else:
    print("   - engine.update() NO procesa deltas: ❌")

print("\n💡 Diagnóstico completado")