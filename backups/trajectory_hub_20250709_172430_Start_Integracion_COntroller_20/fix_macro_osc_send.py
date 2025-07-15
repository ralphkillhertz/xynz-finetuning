import numpy as np

def fix_macro_creation():
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Buscar el método create_macro
    import re
    pattern = r'(def create_macro\(self.*?\n)(.*?)(return macro)'
    
    def replacer(match):
        header = match.group(1)
        body = match.group(2)
        return_line = match.group(3)
        
        # Añadir envío OSC al final del método
        new_send = '''
        # Enviar posiciones iniciales a Spat
        if self.osc_bridge:
            for i, sid in enumerate(source_ids):
                if sid in self._positions:
                    self.osc_bridge.send_position(sid, self._positions[sid])
                    # También enviar nombre
                    self.osc_bridge.send_source_name(sid, f"{name}_{i}")
        '''
        
        # Insertar antes del return
        return header + body + new_send + "\n        " + return_line
    
    # Aplicar fix
    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    if "# Enviar posiciones iniciales a Spat" not in content:
        # Backup
        import shutil
        from datetime import datetime
        backup = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(file_path, backup)
        print(f"✅ Backup: {backup}")
        
        # Escribir
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        print("✅ Fix aplicado: posiciones se enviarán a Spat al crear macro")
    else:
        print("⚠️ Fix ya aplicado")
    
    # Crear test
    test_code = '''# Test rápido
from trajectory_hub import EnhancedTrajectoryEngine

engine = EnhancedTrajectoryEngine(max_sources=10, fps=30)
macro = engine.create_macro("test_visible", 5, formation="circle")
print("✅ Macro creado - verifica en Spat")

# Forzar update para asegurar
engine.update(0.033)
print("✅ Update forzado")
'''
    
    with open("test_macro_visible.py", "w") as f:
        f.write(test_code)
    
    print("🚀 Ejecuta: python test_macro_visible.py")

if __name__ == "__main__":
    fix_macro_creation()