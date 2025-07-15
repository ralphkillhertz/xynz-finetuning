# === fix_delta_certification.py ===
# 🎯 Correcciones SOLO para certificar deltas
# ⚡ Ignorando controlador como solicitado

import os
import shutil
from datetime import datetime

print("🔧 CORRECCIÓN PARA CERTIFICACIÓN DE DELTAS")
print("=" * 60)

# Backup
backup_dir = f"backup_delta_cert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(backup_dir, exist_ok=True)

# 1. Fix valores extremos en motion_components.py
motion_file = "trajectory_hub/core/motion_components.py"
shutil.copy2(motion_file, os.path.join(backup_dir, "motion_components.py"))

with open(motion_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar IndividualTrajectory y limitar el calculate_delta
import re

# Encontrar el método calculate_delta en IndividualTrajectory
pattern = r'(class IndividualTrajectory.*?def calculate_delta.*?return MotionDelta.*?\))'

def fix_individual_trajectory(match):
    class_content = match.group(0)
    # Reemplazar el return para añadir límites
    class_content = re.sub(
        r'delta = self\._calculate_position_on_trajectory\(\) - state\.position',
        r'''delta = self._calculate_position_on_trajectory() - state.position
        # Limitar delta para evitar valores extremos
        delta = np.clip(delta, -10.0, 10.0)''',
        class_content
    )
    return class_content

content = re.sub(pattern, fix_individual_trajectory, content, flags=re.DOTALL)

# 2. Fix concentration_factor
content = content.replace('self.concentration_factor', 'self.factor')
content = content.replace('.concentration_factor', '.factor')

with open(motion_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ motion_components.py corregido")

# 3. Fix datetime en verification
verif_file = "comprehensive_system_verification.py"
shutil.copy2(verif_file, os.path.join(backup_dir, "comprehensive_system_verification.py"))

with open(verif_file, 'r', encoding='utf-8') as f:
    verif_content = f.read()

if 'from datetime import datetime' not in verif_content:
    verif_content = "from datetime import datetime\n" + verif_content

with open(verif_file, 'w', encoding='utf-8') as f:
    f.write(verif_content)
print("✅ comprehensive_system_verification.py corregido")

print(f"\n📁 Backups en: {backup_dir}")
print("🚀 Ejecuta: python comprehensive_system_verification.py")