#!/usr/bin/env python3
from pythonosc import udp_client
from pythonosc import osc_message_builder

print("🧪 TEST OSC SIMPLE Y DIRECTO\n")

# Cliente OSC directo
client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

print("1. Enviando /group/new...")
client.send_message("/group/new", ["TestGroup"])
print("   ✅ Enviado")

print("\n2. Enviando fuentes al grupo...")
for i in range(1, 4):
    client.send_message(f"/source/{i}/group", ["TestGroup"])
    print(f"   ✅ Fuente {i} → TestGroup")

print("\n✅ VERIFICA EN SPAT OSC MONITOR")
print("   Si ves los mensajes, el problema está en el bridge")
print("   Si NO ves nada, verifica:")
print("   - Puerto 9000 correcto")
print("   - Spat está recibiendo OSC")
