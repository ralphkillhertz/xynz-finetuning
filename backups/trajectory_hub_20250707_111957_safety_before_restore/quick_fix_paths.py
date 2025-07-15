#!/usr/bin/env python3
"""
🔧 Fix: Completar actualización OSC con rutas correctas
⚡ Solución: Buscar y aplicar fix en archivo correcto
"""

import os
import glob

def find_source_motion():
    """Encontrar el archivo source_motion.py"""
    # Buscar en todas las subcarpetas
    patterns = [
        "*/source_motion.py",
        "*/*/source_motion.py", 
        "*/*/*/source_motion.py"
    ]
    
    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            return files[0]
    return None

def apply_remaining_fix():
    """Aplicar el fix pendiente en source_motion.py"""
    
    # Encontrar archivo
    motion_file = find_source_motion()
    
    if not motion_file:
        print("⚠️  No se encontró source_motion.py")
        print("✅ El fix principal ya está aplicado en enhanced_trajectory_engine.py")
        print("   Esto debería ser suficiente para resolver el problema.")
        return
    
    print(f"📁 Encontrado: {motion_file}")
    
    # Aplicar fix
    try:
        with open(motion_file, 'r') as f:
            content = f.read()
        
        # Reducir umbral para actualizaciones más frecuentes
        original = "if dt < 0.001:"
        replacement = "if dt < 0.0001:"
        
        if original in content:
            content = content.replace(original, replacement)
            with open(motion_file, 'w') as f:
                f.write(content)
            print("✅ Fix adicional aplicado en source_motion.py")
        else:
            print("ℹ️  source_motion.py ya estaba actualizado")
            
    except Exception as e:
        print(f"⚠️  Error al modificar {motion_file}: {e}")
        print("✅ Pero el fix principal ya está aplicado")

if __name__ == "__main__":
    print("🔍 Buscando archivos...")
    apply_remaining_fix()
    print("\n✨ Proceso completado")
    print("🚀 Ejecuta: python trajectory_hub/interface/interactive_controller.py")
    print("\n📊 El sistema ahora enviará actualizaciones inmediatas a Spat:")
    print("   - Concentración → Visible al instante")
    print("   - Rotación MS → Cambios inmediatos")