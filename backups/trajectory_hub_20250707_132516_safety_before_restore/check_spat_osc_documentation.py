#!/usr/bin/env python3
from pythonosc import udp_client
import time

print("🔍 VERIFICANDO FORMATO OSC SEGÚN DOCUMENTACIÓN SPAT\n")

client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

# Según la documentación, algunos comandos requieren inicialización
print("1. PROBANDO COMANDOS DE INICIALIZACIÓN:")

# Posible necesidad de definir número de fuentes primero
print("   /source/count [10]")
client.send_message("/source/count", [10])
time.sleep(0.5)

# O tal vez
print("   /spat/source/count [10]")
client.send_message("/spat/source/count", [10])
time.sleep(0.5)

print("\n2. PROBANDO CREAR GRUPO CON DIFERENTES SINTAXIS:")

# Formato con ID numérico
print("   /group/1/name ['Grupo1']")
client.send_message("/group/1/name", ["Grupo1"])
time.sleep(0.5)

# Formato con create
print("   /group/create ['Grupo2']")
client.send_message("/group/create", ["Grupo2"])
time.sleep(0.5)

# Formato con define
print("   /group/define [1, 'Grupo3']")
client.send_message("/group/define", [1, "Grupo3"])
time.sleep(0.5)

print("\n3. ASIGNACIÓN DIRECTA SIN CREAR:")
# Tal vez Spat crea grupos automáticamente al asignar
print("   /source/1/group ['AutoGrupo']")
client.send_message("/source/1/group", ["AutoGrupo"])
time.sleep(0.5)

print("\n4. FORMATO DE LISTA DE FUENTES:")
# Algunos sistemas requieren definir el grupo con sus fuentes
print("   /group/set ['ListaGrupo', 1, 2, 3]")
client.send_message("/group/set", ["ListaGrupo", 1, 2, 3])

print("\n✅ REVISA EN SPAT:")
print("   - ¿Algún grupo se creó?")
print("   - ¿Qué mensajes se reconocen?")
print("\n💡 ALTERNATIVA:")
print("   Si nada funciona, crea los grupos manualmente en Spat")
print("   y usa solo /source/X/group para asignar fuentes")
