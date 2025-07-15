# === check_motion_components.py ===
# 🔧 Verifica el estado de motion_components.py
# ⚡ Diagnóstico rápido

import os
import re

def check_motion_components():
    """Verifica qué clases están en motion_components.py"""
    
    motion_path = "trajectory_hub/core/motion_components.py"
    
    if not os.path.exists(motion_path):
        print("❌ No se encuentra motion_components.py")
        return
    
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 VERIFICANDO motion_components.py")
    print("="*60)
    
    # Buscar todas las clases
    class_pattern = r'^class\s+(\w+)'
    classes = re.findall(class_pattern, content, re.MULTILINE)
    
    print(f"\n📋 Clases encontradas ({len(classes)}):")
    for cls in classes:
        print(f"   - {cls}")
    
    # Verificar ConcentrationComponent específicamente
    if 'ConcentrationComponent' in classes:
        print("\n✅ ConcentrationComponent EXISTE")
    else:
        print("\n❌ ConcentrationComponent NO EXISTE")
    
    # Buscar backups
    print("\n🔍 Buscando backups:")
    backup_dir = os.path.dirname(motion_path)
    backups = []
    for file in os.listdir(backup_dir):
        if file.startswith('motion_components.py.backup_'):
            backups.append(file)
    
    if backups:
        backups.sort(reverse=True)  # Más reciente primero
        print(f"   Encontrados {len(backups)} backups:")
        for backup in backups[:5]:  # Mostrar últimos 5
            print(f"   - {backup}")
        
        # Sugerir restauración
        latest_backup = os.path.join(backup_dir, backups[0])
        print(f"\n📌 Para restaurar el backup más reciente:")
        print(f"$ cp '{latest_backup}' '{motion_path}'")
    
    # Verificar sintaxis
    print("\n🔍 Verificando sintaxis:")
    try:
        compile(content, motion_path, 'exec')
        print("   ✅ Sintaxis correcta")
    except SyntaxError as e:
        print(f"   ❌ Error de sintaxis: {e}")
        print(f"      Línea {e.lineno}: {e.text}")

if __name__ == "__main__":
    check_motion_components()