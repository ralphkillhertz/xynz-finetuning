# === fix_all_array_comparisons_final.py ===
# 🔧 Fix: Encontrar y corregir TODAS las comparaciones de arrays
# ⚡ Impacto: ALTO - Resuelve error definitivamente
# 🎯 Tiempo: 30 seg

import re
from pathlib import Path
import numpy as np

def fix_all_array_comparisons():
    """Encuentra y corrige TODAS las comparaciones problemáticas con arrays"""
    
    file_path = Path("trajectory_hub/core/motion_components.py")
    
    # Backup
    backup_path = file_path.with_suffix(f'.backup_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}')
    
    try:
        import pandas as pd
    except:
        import datetime
        backup_path = file_path.with_suffix(f'.backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}')
    
    content = file_path.read_text()
    original = content
    
    # Patrones a buscar y reemplazar
    replacements = [
        # Patrón 1: abs(x) > valor or abs(y) > valor or abs(z) > valor
        (r'(abs\([^)]+\)\s*>\s*[\d.]+)\s+or\s+(abs\([^)]+\)\s*>\s*[\d.]+)\s+or\s+(abs\([^)]+\)\s*>\s*[\d.]+)',
         r'any([\1, \2, \3])'),
        
        # Patrón 2: (condición) or (condición) or (condición)
        (r'\((abs\([^)]+\)\s*>\s*[\d.]+)\)\s+or\s+\((abs\([^)]+\)\s*>\s*[\d.]+)\)\s+or\s+\((abs\([^)]+\)\s*>\s*[\d.]+)\)',
         r'any([\1, \2, \3])'),
         
        # Patrón 3: valor == 0 or valor == 0 or valor == 0
        (r'([a-zA-Z_][a-zA-Z0-9_]*\s*==\s*0)\s+or\s+([a-zA-Z_][a-zA-Z0-9_]*\s*==\s*0)\s+or\s+([a-zA-Z_][a-zA-Z0-9_]*\s*==\s*0)',
         r'any([\1, \2, \3])'),
         
        # Patrón 4: self.algo > 0 and self.algo > 0
        (r'(self\.[a-zA-Z_][a-zA-Z0-9_]*\s*>\s*0)\s+and\s+(self\.[a-zA-Z_][a-zA-Z0-9_]*\s*>\s*0)',
         r'all([\1, \2])'),
    ]
    
    changes = []
    for pattern, replacement in replacements:
        matches = list(re.finditer(pattern, content))
        for match in reversed(matches):  # Reemplazar de atrás hacia adelante
            old_text = match.group(0)
            new_text = re.sub(pattern, replacement, old_text)
            content = content[:match.start()] + new_text + content[match.end():]
            
            # Encontrar número de línea
            line_num = content[:match.start()].count('\n') + 1
            changes.append((line_num, old_text, new_text))
    
    # Buscar específicamente en MacroRotation
    if "class MacroRotation" in content:
        # Encontrar el bloque de la clase
        class_start = content.find("class MacroRotation")
        class_end = content.find("\nclass ", class_start + 1)
        if class_end == -1:
            class_end = len(content)
        
        class_content = content[class_start:class_end]
        
        # Buscar cualquier uso de 'or' o 'and' con variables que podrían ser arrays
        problematic_patterns = [
            r'if\s+[^:]+\s+or\s+[^:]+:',
            r'if\s+[^:]+\s+and\s+[^:]+:',
            r'=\s*[^=]+\s+or\s+[^=\n]+',
            r'=\s*[^=]+\s+and\s+[^=\n]+',
        ]
        
        for pattern in problematic_patterns:
            for match in re.finditer(pattern, class_content):
                line = match.group(0)
                if any(x in line for x in ['speed', 'position', 'velocity', 'rotation', 'angle']):
                    line_start = class_start + match.start()
                    line_num = content[:line_start].count('\n') + 1
                    print(f"⚠️  Línea {line_num} puede tener problema: {line.strip()}")
    
    if content != original:
        # Guardar backup
        file_path.write_text(original)
        file_path.rename(backup_path)
        
        # Guardar archivo corregido
        file_path.write_text(content)
        
        print(f"✅ Backup creado: {backup_path}")
        print(f"\n📝 {len(changes)} cambios realizados:")
        for line_num, old, new in changes[:5]:  # Mostrar primeros 5
            print(f"   Línea {line_num}:")
            print(f"   Antes:   {old[:60]}...")
            print(f"   Después: {new[:60]}...")
        
        if len(changes) > 5:
            print(f"   ... y {len(changes) - 5} cambios más")
    else:
        print("❌ No se encontraron más comparaciones problemáticas")
        print("\n🔍 Buscando en calculate_delta de MacroRotation...")
        
        # Debug específico
        if "class MacroRotation" in content:
            print("\n📋 Método calculate_delta encontrado")
            # Extraer y mostrar el método para inspección manual
            calc_start = content.find("def calculate_delta", class_start)
            if calc_start > 0:
                calc_end = content.find("\n    def ", calc_start + 1)
                if calc_end == -1:
                    calc_end = content.find("\nclass ", calc_start)
                print("Revisar manualmente las líneas del método calculate_delta")

if __name__ == "__main__":
    fix_all_array_comparisons()