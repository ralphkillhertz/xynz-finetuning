# === fix_duplicate_params.py ===
# 🔧 Fix: Eliminar parámetros duplicados flotantes
# ⚡ Líneas 534-536 no pertenecen a ninguna función

import os

def fix_duplicate_params():
    """Eliminar líneas de parámetros duplicadas"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_dup_params', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Identificando líneas problemáticas...")
    
    # Mostrar contexto
    print("\n📋 Contexto alrededor de línea 534:")
    for i in range(max(0, 525), min(len(lines), 545)):
        if i < len(lines):
            marker = ">>>" if i in [533, 534, 535] else "   "
            print(f"{marker} {i+1}: {lines[i].rstrip()}")
    
    # Eliminar líneas problemáticas
    lines_to_remove = []
    for i in range(len(lines)):
        line = lines[i].strip()
        # Identificar líneas sueltas de parámetros
        if (line.startswith('shape:') or 
            line.startswith('movement_mode:') or
            (line.endswith(',') and 'shape_params' in line and i > 520)):
            # Verificar si no está dentro de una definición de función
            if i > 0 and not lines[i-1].strip().startswith('def '):
                lines_to_remove.append(i)
                print(f"❌ Marcando para eliminar línea {i+1}: {line[:50]}...")
    
    # También buscar la línea 534 específicamente
    if 533 < len(lines) and 'shape: str, shape_params: dict = None,' in lines[533]:
        if 533 not in lines_to_remove:
            lines_to_remove.append(533)
        if 534 < len(lines):
            lines_to_remove.append(534)
        if 535 < len(lines) and '"""Configura' in lines[535]:
            lines_to_remove.append(535)
    
    # Eliminar en orden inverso para no afectar índices
    print(f"\n✅ Eliminando {len(lines_to_remove)} líneas problemáticas...")
    for i in sorted(lines_to_remove, reverse=True):
        if i < len(lines):
            print(f"   Eliminando línea {i+1}: {lines[i].strip()[:50]}...")
            del lines[i]
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo limpiado")

def final_test():
    """Test final del sistema"""
    print("\n🧪 Test final...")
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        print("✅ Import exitoso!")
        
        # Crear engine
        engine = EnhancedTrajectoryEngine(n_sources=10)
        print("✅ Engine creado")
        
        # Test rápido de deltas
        print("\n🚀 Test rápido del sistema de deltas:")
        
        # Crear macro
        macro = engine.create_macro("test", source_count=4)
        print(f"✅ Macro creado: {macro.name}")
        
        # Aplicar concentración
        engine.apply_concentration("test", concentration_factor=0.8)
        print("✅ Concentración aplicada")
        
        # Update
        for i in range(3):
            engine.update()
        
        # Verificar posiciones
        moved = False
        for sid in range(4):
            if sid in engine._positions:
                pos = engine._positions[sid]
                if abs(pos[0]) > 0.1 or abs(pos[1]) > 0.1:
                    moved = True
                    print(f"✅ Fuente {sid} movida a: {pos[:2]}")
        
        if moved:
            print("\n🎉 ¡SISTEMA DE DELTAS FUNCIONANDO!")
        else:
            print("\n⚠️ Las fuentes no se movieron")
            
        # Test completo
        print("\n📊 Ejecutando test completo...")
        import subprocess
        result = subprocess.run(['python', 'test_delta_100.py'], 
                              capture_output=True, text=True, timeout=15)
        
        # Mostrar solo resumen
        if result.stdout:
            lines = result.stdout.split('\n')
            for line in lines[-20:]:  # Últimas 20 líneas
                if any(word in line for word in ['RESUMEN', '%', 'funcional', 'Error']):
                    print(line)
                    
    except SyntaxError as e:
        print(f"❌ Todavía hay sintaxis error en línea {e.lineno}")
        print(f"   {e.text}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)[:200]}")

if __name__ == "__main__":
    print("🔧 FIXING DUPLICATE PARAMETERS")
    print("=" * 60)
    
    fix_duplicate_params()
    final_test()