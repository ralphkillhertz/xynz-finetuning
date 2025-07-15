# 🔧 Fix: Activar comunicación OSC con Spat
# ⚡ Diagnosticar y arreglar el envío de mensajes

print("🔧 Diagnosticando comunicación OSC...")

# 1. Descomentar la línea del target en el controller
controller_file = "trajectory_hub/interface/interactive_controller.py"
with open(controller_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Descomentar la línea
content = content.replace(
    "# engine.osc_bridge.add_target(target)  # TODO: Verificar inicialización",
    "engine.osc_bridge.add_target(target)"
)

# Guardar
with open(controller_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Target OSC reactivado")

# 2. Verificar que el engine esté llamando a _send_osc_update
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
with open(engine_file, 'r', encoding='utf-8') as f:
    engine_content = f.read()

# Buscar si existe _send_osc_update
if "_send_osc_update" not in engine_content:
    print("⚠️ Falta método _send_osc_update")
    
    # Añadirlo antes del último método o al final de la clase
    osc_method = '''
    def _send_osc_update(self):
        """Envía actualizaciones OSC de todas las fuentes activas"""
        if not hasattr(self, 'osc_bridge') or self.osc_bridge is None:
            return
            
        for source_id in self._active_sources:
            if source_id in self._positions:
                pos = self._positions[source_id]
                
                # Enviar posición
                self.osc_bridge.send_position(
                    source_id=source_id,
                    x=float(pos[0]),
                    y=float(pos[1]),
                    z=float(pos[2])
                )
                
                # Enviar orientación si existe
                if hasattr(self, '_orientations') and source_id in self._orientations:
                    orient = self._orientations[source_id]
                    self.osc_bridge.send_orientation(
                        source_id=source_id,
                        yaw=float(orient.get('yaw', 0)),
                        pitch=float(orient.get('pitch', 0)),
                        roll=float(orient.get('roll', 0))
                    )
    '''
    
    # Insertar antes del último def o al final
    last_def = engine_content.rfind("\n    def ")
    if last_def > 0:
        engine_content = engine_content[:last_def] + osc_method + engine_content[last_def:]
    else:
        # Añadir al final de la clase
        engine_content = engine_content.rstrip() + "\n" + osc_method
    
    # Guardar
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.write(engine_content)
    
    print("✅ Método _send_osc_update añadido")

# 3. Verificar que update() llame a _send_osc_update
if "def update" in engine_content:
    # Buscar el método update
    update_start = engine_content.find("def update")
    if update_start > 0:
        # Buscar dónde insertar la llamada (al final del método)
        # Buscar el siguiente def para saber dónde termina update
        next_def = engine_content.find("\n    def ", update_start + 10)
        if next_def > 0:
            # Insertar antes del siguiente método
            insert_pos = engine_content.rfind("\n", update_start, next_def)
            if "_send_osc_update" not in engine_content[update_start:next_def]:
                new_call = "\n        # Enviar actualizaciones OSC\n        self._send_osc_update()\n"
                engine_content = engine_content[:insert_pos] + new_call + engine_content[insert_pos:]
                
                with open(engine_file, 'w', encoding='utf-8') as f:
                    f.write(engine_content)
                    
                print("✅ Llamada a _send_osc_update añadida en update()")

# 4. Crear test rápido
test_script = '''# === test_osc_quick.py ===
# Test rápido de comunicación OSC

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.spat_osc_bridge import OSCTarget
import time

print("🧪 TEST RÁPIDO DE OSC")
print("=" * 50)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=30)

# Configurar OSC
target = OSCTarget(host="127.0.0.1", port=9000, name="Spat_Test")
engine.osc_bridge.add_target(target)

print(f"✅ Target OSC configurado: {target.name}")

# Crear un macro simple
engine.create_macro("test", source_count=3)
print("✅ Macro 'test' creado con 3 fuentes")

# Mover las fuentes
print("\\n📡 Enviando posiciones...")
for i in range(10):
    # Actualizar engine
    engine.update()
    
    # Mostrar progreso
    print(f"  Frame {i+1}/10 enviado")
    time.sleep(0.1)

stats = engine.osc_bridge.get_stats()
print(f"\\n📊 Mensajes enviados: {stats.get('messages_sent', 0)}")
print("\\n✅ Test completado - Verifica en Spat")
'''

with open("test_osc_quick.py", 'w') as f:
    f.write(test_script)

print("\n✅ Script de test creado: test_osc_quick.py")
print("\n🚀 Comandos:")
print("1. Reinicia el controlador:")
print("   python -m trajectory_hub.interface.interactive_controller")
print("\n2. O ejecuta el test rápido:")
print("   python test_osc_quick.py")