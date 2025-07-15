import os
import re

def find_osc_config():
    """Buscar dónde se configura el destino OSC"""
    print("🔍 BUSCANDO CONFIGURACIÓN OSC")
    print("="*60)
    
    # Buscar archivos con configuración
    config_patterns = [
        r'host\s*=\s*["\']([^"\']+)["\']',
        r'osc_host\s*=\s*["\']([^"\']+)["\']',
        r'192\.168\.\d+\.\d+',
        r'127\.0\.0\.1',
        r'localhost'
    ]
    
    for root, dirs, files in os.walk("trajectory_hub"):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    for pattern in config_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            print(f"\n📄 {filepath}")
                            for match in set(matches):
                                print(f"  → {match}")
                            
                            # Mostrar contexto
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if 'host' in line and '=' in line:
                                    print(f"  L{i+1}: {line.strip()}")
                except:
                    pass

if __name__ == "__main__":
    find_osc_config()