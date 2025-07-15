#!/usr/bin/env python3
"""
🔧 Fix: Arreglar inicialización de command_processor
⚡ El problema es que está en la misma línea con \\n literal
"""

def fix_init():
    print("🔧 FIX INICIALIZACIÓN COMMAND_PROCESSOR")
    print("=" * 50)
    
    controller_path = "trajectory_hub/interface/interactive_controller.py"
    
    with open(controller_path, 'r') as f:
        content = f.read()
    
    # Buscar la línea problemática
    bad_line = "self.engine.start()  # Iniciar loop\\n        self.command_processor = CommandProcessor(engine)"
    
    if bad_line in content:
        print("❌ Encontrada línea mal formateada")
        print(f"   Actual: {bad_line[:80]}...")
        
        # Reemplazar con formato correcto
        good_lines = """self.engine.start()  # Iniciar loop
        self.command_processor = CommandProcessor(self.engine)"""
        
        content = content.replace(bad_line, good_lines)
        print("\n✅ Reemplazada con:")
        print(good_lines)
        
        # Guardar
        with open(controller_path, 'w') as f:
            f.write(content)
        
        print("\n✅ Inicialización corregida")
    else:
        # Buscar patrón más general
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "engine.start()" in line and "command_processor" in line:
                print(f"❌ Línea problemática {i+1}: {line}")
                # Dividir en dos líneas
                indent = len(line) - len(line.lstrip())
                lines[i] = ' ' * indent + "self.engine.start()  # Iniciar loop"
                lines.insert(i+1, ' ' * indent + "self.command_processor = CommandProcessor(self.engine)")
                
                print("\n✅ Dividida en dos líneas:")
                print(lines[i])
                print(lines[i+1])
                
                # Guardar
                with open(controller_path, 'w') as f:
                    f.write('\n'.join(lines))
                break
    
    print("\n🚀 Ejecuta de nuevo:")
    print("python -m trajectory_hub.interface.interactive_controller")

if __name__ == "__main__":
    fix_init()