# === test_spat_group_formats.py ===
# 🔧 Test: Probar diferentes formatos OSC para crear grupos
# ⚡ Según diferentes versiones de Spat

from pythonosc import udp_client
import time

print("🧪 PROBANDO FORMATOS OSC PARA GRUPOS EN SPAT\n")

client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

print("FORMATO 1: /group/new [nombre]")
client.send_message("/group/new", ["TestGrupo1"])
time.sleep(0.5)

print("\nFORMATO 2: /source/group/new [nombre]")
client.send_message("/source/group/new", ["TestGrupo2"])
time.sleep(0.5)

print("\nFORMATO 3: /source/group/add [id, nombre]")
client.send_message("/source/group/add", [1, "TestGrupo3"])
time.sleep(0.5)

print("\nFORMATO 4: /spat/source/group/new [nombre]")
client.send_message("/spat/source/group/new", ["TestGrupo4"])
time.sleep(0.5)

print("\nFORMATO 5: /source/1/group/new [nombre]")
client.send_message("/source/1/group/new", ["TestGrupo5"])
time.sleep(0.5)

print("\nFORMATO 6: Crear y asignar por separado")
client.send_message("/group/add", ["TestGrupo6"])
time.sleep(0.2)
client.send_message("/source/1/group", ["TestGrupo6"])

print("\n✅ VERIFICA EN SPAT:")
print("   1. ¿Cuál formato creó grupos?")
print("   2. ¿Cuál es el comando correcto?")
print("\n📋 Revisa también la documentación de tu versión de Spat")