# === quick_check_trajectory_params.py ===
import inspect
from trajectory_hub.core import EnhancedTrajectoryEngine

# Check set_macro_trajectory signature
try:
    engine = EnhancedTrajectoryEngine()
    sig = inspect.signature(engine.set_macro_trajectory)
    print("set_macro_trajectory signature:")
    print(f"set_macro_trajectory{sig}")
except Exception as e:
    print(f"Error: {e}")