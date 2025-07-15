# === verify_is_rotations_implementation.py ===
# 🔍 Verificar qué rotaciones IS están implementadas
# ⚡ Inspección de clases disponibles

import inspect
from trajectory_hub.core import motion_components

def verify_is_rotation_classes():
    """Verificar qué clases de rotación IS existen"""
    
    print("🔍 VERIFICACIÓN: ROTACIONES IS IMPLEMENTADAS")
    print("=" * 60)
    
    # 1. Buscar clases de rotación
    print("\n1️⃣ CLASES EN motion_components:")
    print("-" * 40)
    
    classes = []
    for name in dir(motion_components):
        obj = getattr(motion_components, name)
        if inspect.isclass(obj):
            classes.append(name)
    
    # Filtrar clases relacionadas con rotación individual
    rotation_classes = [c for c in classes if 'Individual' in c and 'Rotation' in c]
    
    print("   Clases de rotación individual encontradas:")
    for cls_name in rotation_classes:
        print(f"   - {cls_name}")
    
    # 2. Verificar IndividualRotation
    print("\n2️⃣ VERIFICANDO IndividualRotation:")
    print("-" * 40)
    
    if hasattr(motion_components, 'IndividualRotation'):
        cls = motion_components.IndividualRotation
        sig = inspect.signature(cls.__init__)
        print(f"   ✅ Existe")
        print(f"   Parámetros: {sig}")
        print(f"   Tipo: Rotación algorítmica continua")
    else:
        print("   ❌ No existe")
    
    # 3. Verificar ManualIndividualRotation
    print("\n3️⃣ VERIFICANDO ManualIndividualRotation:")
    print("-" * 40)
    
    if hasattr(motion_components, 'ManualIndividualRotation'):
        cls = motion_components.ManualIndividualRotation
        sig = inspect.signature(cls.__init__)
        print(f"   ✅ Existe")
        print(f"   Parámetros: {sig}")
        
        # Crear instancia de prueba
        try:
            # Intentar con diferentes parámetros
            test = cls()  # Sin parámetros
            print("   Acepta: Sin parámetros")
        except Exception as e:
            print(f"   Error sin params: {e}")
            
        try:
            test = cls(yaw=0, pitch=0, roll=0)
            print("   Acepta: yaw, pitch, roll")
        except Exception as e:
            print(f"   Error con yaw/pitch/roll: {e}")
    else:
        print("   ❌ No existe")
    
    # 4. Verificar métodos del engine
    print("\n4️⃣ MÉTODOS DE ROTACIÓN IS EN ENGINE:")
    print("-" * 40)
    
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    engine = EnhancedTrajectoryEngine(max_sources=1)
    
    methods = []
    for name in dir(engine):
        if 'individual' in name.lower() and 'rotation' in name.lower():
            methods.append(name)
    
    print("   Métodos encontrados:")
    for method in methods:
        sig = inspect.signature(getattr(engine, method))
        print(f"   - {method}: {sig}")
    
    # 5. Conclusión
    print("\n" + "=" * 60)
    print("📊 CONCLUSIÓN:")
    
    has_algo = 'IndividualRotation' in rotation_classes
    has_manual = 'ManualIndividualRotation' in rotation_classes
    
    print(f"   Rotación algorítmica IS: {'✅ IMPLEMENTADA' if has_algo else '❌ NO IMPLEMENTADA'}")
    print(f"   Rotación manual IS: {'✅ IMPLEMENTADA' if has_manual else '❌ NO IMPLEMENTADA'}")
    
    if not has_manual:
        print("\n💡 La rotación manual IS parece NO estar implementada.")
        print("   Solo tenemos la rotación algorítmica (continua).")
        print("\n📝 Para completar el sistema necesitaríamos:")
        print("   1. Implementar ManualIndividualRotation con calculate_delta")
        print("   2. Añadir método set_manual_individual_rotation al engine")
    
    return has_algo, has_manual

if __name__ == "__main__":
    verify_is_rotation_classes()