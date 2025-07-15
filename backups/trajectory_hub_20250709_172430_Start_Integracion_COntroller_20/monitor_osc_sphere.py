
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
print("Presiona Ctrl+C para terminar\n")

# Ejecutar
server.serve_forever()
