from trajectory_hub.interface.interactive_controller import InteractiveController
from trajectory_hub import EnhancedTrajectoryEngine

# Verificar que el menú tiene sphere
with open("trajectory_hub/interface/interactive_controller.py", "r") as f:
    content = f.read()
    if "6. sphere" in content:
        print("✅ '6. sphere' está en el archivo")
    else:
        print("❌ '6. sphere' NO está en el archivo")
        
    # Contar cuántas veces aparece sphere
    count = content.count("sphere")
    print(f"📊 'sphere' aparece {count} veces en el archivo")
