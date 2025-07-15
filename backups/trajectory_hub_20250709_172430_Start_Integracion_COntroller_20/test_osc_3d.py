import os
import re

def test_osc_3d():
    """Verificar si OSC envía coordenada Z"""
    print("🧪 TEST OSC 3D")
    print("="*60)
    
    # Buscar en OSCManager o donde se envíen las posiciones
    osc_files = [
        "trajectory_hub/bridges/osc_bridge.py",
        "trajectory_hub/core/osc_manager.py",
        "trajectory_hub/utils/osc_sender.py"
    ]
    
    for filepath in osc_files:
        if os.path.exists(filepath):
            print(f"\n📄 Analizando: {filepath}")
            
            with open(filepath, 'r') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Buscar métodos que envíen posiciones
            for i, line in enumerate(lines):
                if 'send' in line and ('position' in line or 'xyz' in line or '/source' in line):
                    print(f"\nL{i+1}: {line.strip()}")
                    
                    # Ver contexto
                    for j in range(max(0, i-5), min(len(lines), i+5)):
                        if 'send' in lines[j] or 'position' in lines[j] or 'args' in lines[j]:
                            print(f"  {j+1}: {lines[j]}")
    
    # Buscar en engine cómo envía posiciones
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        print(f"\n\n📄 En ENGINE:")
        
        with open(engine_file, 'r') as f:
            content = f.read()
        
        # Buscar send_position o similar
        position_sends = re.findall(r'.*send.*position.*', content, re.IGNORECASE)
        
        for match in position_sends[:5]:
            print(f"  {match.strip()}")
        
        # Buscar específicamente qué coordenadas envía
        osc_patterns = [
            r'osc.*send.*\([^)]+\)',
            r'send_message.*position',
            r'/source/\d+/xyz.*args'
        ]
        
        for pattern in osc_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"\n  Patrón '{pattern}':")
                for match in matches[:3]:
                    print(f"    {match}")

def create_osc_monitor():
    """Crear monitor para ver qué se envía por OSC"""
    
    monitor_content = '''
# === monitor_osc_sphere.py ===
import time
from pythonosc import dispatcher, osc_server
import threading

print("🎧 MONITOR OSC - Escuchando mensajes de posición")
print("="*60)

positions_received = []

def position_handler(address, *args):
    """Capturar mensajes de posición"""
    positions_received.append((address, args))
    
    # Mostrar si tiene 3 coordenadas
    if len(args) >= 3:
        print(f"✅ 3D: {address} → x={args[0]:.2f}, y={args[1]:.2f}, z={args[2]:.2f}")
    else:
        print(f"❌ 2D: {address} → {args}")

# Configurar dispatcher
disp = dispatcher.Dispatcher()
disp.map("/source/*/xyz", position_handler)
disp.map("/source/*/position", position_handler)
disp.map("/track/*/xyz", position_handler)

# Crear servidor
server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9999), disp)

print("Escuchando en puerto 9999...")
print("Crea un macro con sphere en otra terminal")
print("Presiona Ctrl+C para terminar\\n")

# Ejecutar
server.serve_forever()
'''
    
    with open("monitor_osc_sphere.py", 'w') as f:
        f.write(monitor_content)
    
    print("\n✅ Monitor creado: monitor_osc_sphere.py")

if __name__ == "__main__":
    test_osc_3d()
    create_osc_monitor()
    
    print("\n\n💡 PARA MONITOREAR OSC:")
    print("1. En una terminal: python monitor_osc_sphere.py")
    print("2. En otra: ejecuta el programa y crea sphere")
    print("3. Verás si se envían 2 o 3 coordenadas")