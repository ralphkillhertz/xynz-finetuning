# === diagnose_distance_control.py ===
# 🔍 Diagnóstico profundo del sistema de control de distancias
# ⚡ Identifica dónde está y cómo funciona el control de distancias

import inspect
import ast
import os
from trajectory_hub.core import EnhancedTrajectoryEngine

def diagnose_distance_control():
    """Diagnóstico completo del sistema de control de distancias"""
    
    print("🔍 DIAGNÓSTICO - SISTEMA DE CONTROL DE DISTANCIAS")
    print("=" * 70)
    
    # 1. Verificar métodos relacionados con distancia
    print("\n1️⃣ MÉTODOS EN EnhancedTrajectoryEngine...")
    
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # Buscar métodos con 'distance' o 'concentration'
    distance_methods = []
    concentration_methods = []
    
    for attr_name in dir(engine):
        if 'distance' in attr_name.lower():
            distance_methods.append(attr_name)
        if 'concentrat' in attr_name.lower() or 'converg' in attr_name.lower():
            concentration_methods.append(attr_name)
    
    print(f"\n   📏 Métodos con 'distance': {distance_methods}")
    print(f"   🎯 Métodos con 'concentration/convergent': {concentration_methods}")
    
    # 2. Buscar en el archivo fuente
    print("\n2️⃣ BUSCANDO EN EL CÓDIGO FUENTE...")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar definiciones relacionadas
    import re
    
    # Buscar métodos de distancia
    distance_defs = re.findall(r'def\s+(\w*distance\w*)\s*\(', content, re.IGNORECASE)
    concentration_defs = re.findall(r'def\s+(\w*concentr\w*)\s*\(', content, re.IGNORECASE)
    
    print(f"\n   📄 Definiciones con 'distance' en archivo: {distance_defs}")
    print(f"   📄 Definiciones con 'concentr' en archivo: {concentration_defs}")
    
    # 3. Verificar si hay un controlador de distancias separado
    print("\n3️⃣ BUSCANDO CONTROLADOR DE DISTANCIAS...")
    
    # Buscar archivos relacionados
    core_path = "trajectory_hub/core"
    distance_files = []
    
    for file in os.listdir(core_path):
        if 'distance' in file.lower() or 'concentration' in file.lower():
            distance_files.append(file)
    
    print(f"\n   📁 Archivos relacionados: {distance_files}")
    
    # 4. Verificar si existe distance_controller.py
    distance_controller_file = os.path.join(core_path, "distance_controller.py")
    if os.path.exists(distance_controller_file):
        print("\n   ✅ distance_controller.py EXISTE")
        
        # Ver si tiene la funcionalidad
        with open(distance_controller_file, 'r') as f:
            dc_content = f.read()
        
        # Buscar clases y métodos
        classes = re.findall(r'class\s+(\w+)', dc_content)
        methods = re.findall(r'def\s+(\w+)\s*\(', dc_content)
        
        print(f"   📦 Clases: {classes}")
        print(f"   🔧 Métodos principales: {[m for m in methods if not m.startswith('_')][:10]}")
    
    # 5. Verificar integración con macros
    print("\n4️⃣ VERIFICANDO INTEGRACIÓN CON MACROS...")
    
    # Crear un macro para ver su estructura
    macro = engine.create_macro("test", 2)
    
    print(f"\n   📦 Tipo de macro: {type(macro).__name__}")
    
    # Ver atributos relacionados con concentración/distancia
    if hasattr(macro, '__dict__'):
        relevant_attrs = [attr for attr in macro.__dict__ 
                         if 'concentr' in attr or 'distance' in attr or 'converg' in attr]
        print(f"   🎯 Atributos relevantes del macro: {relevant_attrs}")
    
    # 6. Buscar el método correcto
    print("\n5️⃣ BÚSQUEDA DEL MÉTODO CORRECTO...")
    
    # Buscar set_concentration o similar
    possible_methods = [
        'set_concentration',
        'set_macro_concentration', 
        'apply_concentration',
        'set_convergence',
        'set_distance_mode',
        'set_distance_control'  # El que buscamos
    ]
    
    for method_name in possible_methods:
        if hasattr(engine, method_name):
            print(f"   ✅ ENCONTRADO: {method_name}")
            # Ver la firma
            method = getattr(engine, method_name)
            sig = inspect.signature(method)
            print(f"      Firma: {sig}")
        else:
            # Buscar en el código aunque no esté en el objeto
            if f"def {method_name}" in content:
                print(f"   ⚠️ {method_name} está definido pero no accesible")
    
    # 7. Propuesta de solución
    print("\n6️⃣ ANÁLISIS DE SOLUCIÓN...")
    
    # Ver si hay un patrón de concentración en motion_components
    motion_comp_file = "trajectory_hub/core/motion_components.py"
    if os.path.exists(motion_comp_file):
        with open(motion_comp_file, 'r') as f:
            mc_content = f.read()
        
        if 'ConcentrationComponent' in mc_content:
            print("   ✅ ConcentrationComponent existe en motion_components.py")
            
            # Ver cómo se usa
            concentration_usage = re.findall(r'concentration.*=.*ConcentrationComponent', content, re.IGNORECASE)
            if concentration_usage:
                print(f"   📋 Uso encontrado: {concentration_usage[0]}")

if __name__ == "__main__":
    diagnose_distance_control()