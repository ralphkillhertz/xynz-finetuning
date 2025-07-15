# === fix_test_trajectory_api.py ===
import numpy as np

# Fix the test to use correct API
test_file = "test_7_deltas_final.py"

with open(test_file, 'r') as f:
    content = f.read()

# Replace incorrect API calls
replacements = [
    (
        'engine.set_macro_trajectory(macro1.name, shape="circle", speed=2.0)',
        '''# Crear función de trayectoria circular
    def circle_trajectory(t):
        radius = 3.0
        return np.array([radius * np.cos(t * 2.0), radius * np.sin(t * 2.0), 0.0])
    
    engine.set_macro_trajectory(macro1.name, circle_trajectory)'''
    ),
    (
        'engine.set_individual_trajectory(test_source, shape="spiral", \n                                     shape_params={"radius": 2.0, "height": 1.0})',
        '''# Crear función de trayectoria espiral
    def spiral_trajectory(t):
        radius = 2.0 * (1 + 0.1 * t)
        height = t * 0.5
        return np.array([radius * np.cos(t * 3), radius * np.sin(t * 3), height])
    
    engine.set_individual_trajectory(test_source, spiral_trajectory)'''
    )
]

for old, new in replacements:
    content = content.replace(old, new)

# Add numpy import if not present
if "import numpy as np" not in content:
    content = content.replace("import math", "import math\nimport numpy as np")

with open(test_file, 'w') as f:
    f.write(content)

print("✅ Test actualizado con API correcta de trayectorias")