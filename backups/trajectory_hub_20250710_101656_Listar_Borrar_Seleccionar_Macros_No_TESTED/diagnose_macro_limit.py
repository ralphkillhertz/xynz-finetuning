# === diagnose_macro_limit.py ===
#!/usr/bin/env python3
"""
🔍 Diagnóstico: ¿Por qué solo 2 macros?
"""

def diagnose():
    print("🔍 DIAGNÓSTICO LÍMITE DE MACROS")
    print("=" * 50)
    
    # 1. Verificar configuración
    print("\n1️⃣ Verificando config.py...")
    with open("trajectory_hub/config.py", 'r') as f:
        config_content = f.read()
        if "n_sources" in config_content:
            for line in config_content.split('\n'):
                if "n_sources" in line and not line.strip().startswith('#'):
                    print(f"   → {line.strip()}")
    
    # 2. Verificar engine
    print("\n2️⃣ Verificando engine...")
    with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'r') as f:
        engine_content = f.read()
        
    # Buscar límites
    print("\n3️⃣ Buscando límites de sources...")
    
    # Verificar inicialización
    if "_active_sources" in engine_content:
        print("   ✅ _active_sources encontrado")
        
    # Buscar ID generation
    for line in engine_content.split('\n'):
        if "source_id" in line and ("=" in line or "+" in line):
            print(f"   ID: {line.strip()[:80]}...")
    
    print("\n4️⃣ Teoría del problema:")
    print("   - IDs de sources podrían estar colisionando")
    print("   - Límite hardcodeado en algún lugar")
    print("   - Sources anteriores no se liberan")
    
    # Quick fix suggestion
    print("\n💡 Solución probable:")
    print("   Los IDs de las sources deben ser únicos")
    print("   Verificar que cada macro use IDs diferentes")

if __name__ == "__main__":
    diagnose()