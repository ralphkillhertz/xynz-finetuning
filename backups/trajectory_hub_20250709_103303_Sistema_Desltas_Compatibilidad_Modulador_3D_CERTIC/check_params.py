# === check_params.py ===
from trajectory_hub.core import EnhancedTrajectoryEngine
import inspect

# Ver la firma del constructor
sig = inspect.signature(EnhancedTrajectoryEngine.__init__)
print("Constructor signature:")
print(f"EnhancedTrajectoryEngine{sig}")

# Ver los parámetros con sus valores por defecto
print("\nParámetros:")
for name, param in sig.parameters.items():
    if name != 'self':
        if param.default != inspect.Parameter.empty:
            print(f"  {name} = {param.default}")
        else:
            print(f"  {name} (required)")