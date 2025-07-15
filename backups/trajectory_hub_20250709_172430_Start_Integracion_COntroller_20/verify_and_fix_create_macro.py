import re

def verify_and_fix():
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Buscar create_macro
    print("🔍 Buscando método create_macro...")
    
    # Encontrar el método completo
    pattern = r'(def create_macro\(self[^:]+:\s*\n)((?:.*?\n)*?)(\s+return macro)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    
    if not match:
        print("❌ No se encontró create_macro")
        return
    
    method_body = match.group(2)
    
    # Verificar si ya tiene send_position
    if "send_position" in method_body:
        print("✅ Ya tiene send_position")
        # Verificar si está dentro del if self.osc_bridge
        if "if self.osc_bridge" in method_body:
            print("✅ Está dentro del if correcto")
        else:
            print("⚠️ send_position existe pero podría no estar en el lugar correcto")
    else:
        print("❌ NO tiene send_position - aplicando fix...")
        
        # Insertar justo antes del return
        osc_send_code = '''
        # Enviar posiciones iniciales a Spat
        if self.osc_bridge:
            for i, sid in enumerate(source_ids):
                if sid < len(self._positions):
                    self.osc_bridge.send_position(sid, self._positions[sid])
                    # También enviar nombre
                    self.osc_bridge.send_source_name(sid, f"{name}_{i}")
            print(f"📡 Enviadas {len(source_ids)} posiciones a Spat")
'''
        
        # Reemplazar
        new_content = content.replace(
            match.group(0),
            match.group(1) + method_body + osc_send_code + match.group(3)
        )
        
        # Backup y escribir
        import shutil
        from datetime import datetime
        backup = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(file_path, backup)
        print(f"✅ Backup: {backup}")
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        print("✅ Fix aplicado correctamente")
    
    # Test inmediato
    print("\n🧪 Test inmediato:")
    test_code = '''from trajectory_hub import EnhancedTrajectoryEngine

engine = EnhancedTrajectoryEngine(max_sources=10, fps=30)
print("Stats antes:", engine.osc_bridge.get_stats()['messages_sent'])

macro = engine.create_macro("test_fix", 5, formation="circle")

stats = engine.osc_bridge.get_stats()
print(f"Stats después: {stats['messages_sent']} mensajes")
print(f"✅ Posiciones enviadas: {stats['parameters_sent']['positions']}")
print(f"✅ Nombres enviados: {stats['parameters_sent']['names']}")
'''
    
    with open("test_create_macro_osc.py", "w") as f:
        f.write(test_code)
    
    print("\n🚀 Ejecuta: python test_create_macro_osc.py")

if __name__ == "__main__":
    verify_and_fix()