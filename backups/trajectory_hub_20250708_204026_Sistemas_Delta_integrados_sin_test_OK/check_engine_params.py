import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_engine_init():
    """Verifica los parámetros del constructor del engine"""
    print("🔍 VERIFICANDO PARÁMETROS DEL ENGINE")
    print("=" * 60)
    
    # 1. Buscar en el archivo
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    print(f"📄 Archivo: {engine_path}")
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar __init__
    init_start = content.find("def __init__(")
    if init_start == -1:
        print("❌ No se encontró __init__")
        return
    
    # Extraer la firma completa
    paren_count = 0
    init_end = init_start
    for i in range(init_start, len(content)):
        if content[i] == '(':
            paren_count += 1
        elif content[i] == ')':
            paren_count -= 1
            if paren_count == 0:
                init_end = i + 1
                break
    
    signature = content[init_start:init_end]
    print("\n✅ Firma del constructor encontrada:")
    print("-" * 60)
    # Limpiar y mostrar
    clean_sig = signature.replace('\n', ' ').replace('  ', ' ')
    print(clean_sig)
    
    # 2. Importar y verificar dinámicamente
    print("\n🔍 Verificando dinámicamente...")
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        import inspect
        
        # Obtener firma
        sig = inspect.signature(EnhancedTrajectoryEngine.__init__)
        print("\n📋 Parámetros del constructor:")
        print("-" * 60)
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            default = param.default
            if default == inspect.Parameter.empty:
                default = "REQUERIDO"
            
            print(f"  • {param_name}: {default}")
            
    except Exception as e:
        print(f"❌ Error al importar: {e}")
    
    # 3. Crear test con parámetros correctos
    print("\n💡 EJEMPLO DE USO CORRECTO:")
    print("-" * 60)
    print("engine = EnhancedTrajectoryEngine()  # Sin parámetros")
    print("# O con los parámetros que encuentre arriba")

def test_quick():
    """Test rápido con diferentes combinaciones"""
    print("\n\n🧪 PROBANDO DIFERENTES COMBINACIONES:")
    print("=" * 60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    tests = [
        ("Sin parámetros", {}),
        ("Con fps", {"fps": 60}),
        ("Con n_sources", {"n_sources": 10}),
        ("Con max_sources", {"max_sources": 10}),
    ]
    
    for name, params in tests:
        try:
            engine = EnhancedTrajectoryEngine(**params)
            print(f"✅ {name}: FUNCIONA - {params}")
            # Mostrar algunos atributos
            attrs = ['max_sources', 'fps', '_update_rate', 'n_sources']
            for attr in attrs:
                if hasattr(engine, attr):
                    print(f"   - {attr} = {getattr(engine, attr)}")
            break  # Si funciona, salir
        except Exception as e:
            print(f"❌ {name}: {e}")

if __name__ == "__main__":
    check_engine_init()
    test_quick()