# === fix_test_complete.py ===
import fileinput

# Fix the test file completely
fixes = 0

for line in fileinput.input('test_7_deltas_final.py', inplace=True):
    # Fix macro references - use the actual macro names with prefix
    if 'engine.set_macro_trajectory(macro1.name' in line:
        line = line.replace('macro1.name', '"macro_0_test_group_1"')
        fixes += 1
    elif 'engine.set_macro_rotation(macro2.name' in line:
        line = line.replace('macro2.name', '"macro_1_test_group_2"')
        fixes += 1
    elif 'engine.set_manual_macro_rotation(macro1.name' in line:
        line = line.replace('macro1.name', '"macro_0_test_group_1"')
        fixes += 1
    elif 'engine.set_individual_trajectory(test_source, spiral_trajectory)' in line:
        line = '    engine.set_individual_trajectory(test_source, "spiral", speed=1.0)\n'
        fixes += 1
    elif 'def spiral_trajectory(t):' in line:
        # Skip the function definition
        continue
    elif 'radius = 2.0 * (1 + 0.1 * t)' in line:
        continue
    elif 'height = t * 0.5' in line:
        continue
    elif 'return np.array([radius * np.cos(t * 3), radius * np.sin(t * 3), height])' in line:
        continue
    
    print(line, end='')

print(f"✅ {fixes} correcciones aplicadas")