# === restore_simple.py ===
import shutil
shutil.copy2("trajectory_hub/core/motion_components.py.backup_20250708_003129", 
             "trajectory_hub/core/motion_components.py")
print("✅ Restaurado a versión con calculate_delta")
