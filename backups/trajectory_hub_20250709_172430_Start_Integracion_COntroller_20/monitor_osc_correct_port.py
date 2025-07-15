from pythonosc import dispatcher, osc_server
import threading
import time

print("🎧 MONITOR OSC - Puerto 9000")
print("="*60)

message_count = 0
last_messages = []

def message_handler(address, *args):
    """Capturar TODOS los mensajes OSC"""
    global message_count, last_messages
    
    message_count += 1
    
    # Guardar últimos mensajes
    last_messages.append((address, args))
    if len(last_messages) > 10:
        last_messages.pop(0)
    
    # Mostrar mensajes de posición
    if 'position' in address or 'xyz' in address or '/source' in address:
        if len(args) >= 3:
            print(f"✅ 3D [{message_count}]: {address} → x={args[0]:.2f}, y={args[1]:.2f}, z={args[2]:.2f}")
        elif len(args) == 2:
            print(f"❌ 2D [{message_count}]: {address} → x={args[0]:.2f}, y={args[1]:.2f} (NO Z!)")
        else:
            print(f"❓ [{message_count}]: {address} → {args}")
    elif message_count % 10 == 0:  # Mostrar cada 10 mensajes para ver actividad
        print(f"📡 {message_count} mensajes recibidos...")

# Configurar dispatcher para capturar TODO
disp = dispatcher.Dispatcher()
disp.set_default_handler(message_handler)

# Crear servidor en puerto 9000
try:
    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9000), disp)
    print("✅ Escuchando en 127.0.0.1:9000")
except:
    print("❌ Error: Puerto 9000 en uso")
    print("Probando puerto alternativo 9001...")
    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9001), disp)
    print("✅ Escuchando en 127.0.0.1:9001")

print("\n📋 INSTRUCCIONES:")
print("1. En otra terminal, ejecuta el programa")
print("2. Crea un macro con formación sphere")
print("3. Verás si se envían 2 o 3 coordenadas")
print("4. Presiona Ctrl+C para terminar\n")

# Thread para mostrar resumen cada 5 segundos
def show_summary():
    while True:
        time.sleep(5)
        if last_messages:
            print(f"\n📊 Últimos mensajes únicos:")
            unique_addresses = set(msg[0] for msg in last_messages)
            for addr in unique_addresses:
                msgs = [m for m in last_messages if m[0] == addr]
                if msgs:
                    latest = msgs[-1]
                    print(f"  {addr}: {len(latest[1])} valores")

summary_thread = threading.Thread(target=show_summary, daemon=True)
summary_thread.start()

try:
    server.serve_forever()
except KeyboardInterrupt:
    print(f"\n\n📊 RESUMEN FINAL:")
    print(f"Total mensajes: {message_count}")
    if last_messages:
        print("\nÚltimos mensajes:")
        for addr, args in last_messages[-5:]:
            print(f"  {addr}: {args}")