# === test_import_direct.py ===
import sys
print("\n🔍 TEST DE IMPORT DIRECTO\n")

# Intentar import directo desde core
try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    print("✅ Import directo exitoso")
    
    # Ver la firma del constructor
    import inspect
    sig = inspect.signature(EnhancedTrajectoryEngine.__init__)
    print(f"\n📋 Firma del constructor: {sig}")
    
    # Intentar crear instancia
    print("\n🧪 Intentando crear instancia...")
    try:
        engine = EnhancedTrajectoryEngine(max_sources=4)
        print("✅ Creado con max_sources")
    except Exception as e:
        print(f"❌ Error con max_sources: {e}")
        
        # Ver qué tipo de error es
        print(f"   Tipo de error: {type(e).__name__}")
        
        # Si es error de argumentos, mostrar qué espera
        if "missing" in str(e) or "unexpected" in str(e):
            print("\n💡 Parece que hay un conflicto de clases")
            
            # Ver todas las clases EnhancedTrajectoryEngine
            print("\n🔎 Buscando todas las clases con ese nombre...")
            import trajectory_hub.core
            for name in dir(trajectory_hub.core):
                obj = getattr(trajectory_hub.core, name)
                if "Engine" in name:
                    print(f"   - {name}: {type(obj)}")
                    
except ImportError as e:
    print(f"❌ Error de import: {e}")
    
# También probar el import normal
print("\n4️⃣ Import normal desde trajectory_hub:")
try:
    from trajectory_hub import EnhancedTrajectoryEngine as Engine2
    print("✅ Import normal exitoso")
    
    # Comparar si son la misma clase
    try:
        if 'EnhancedTrajectoryEngine' in locals() and Engine2 is not EnhancedTrajectoryEngine:
            print("⚠️ ¡CONFLICTO! Son clases diferentes")
            print(f"   Clase 1: {EnhancedTrajectoryEngine}")
            print(f"   Clase 2: {Engine2}")
    except:
        pass
        
except Exception as e:
    print(f"❌ Error: {e}")
