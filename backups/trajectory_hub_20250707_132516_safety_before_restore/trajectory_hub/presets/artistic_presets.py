"""
artistic_presets.py - Presets artísticos para el sistema de trayectorias
Versión corregida y optimizada con validación de errores
"""
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Presets artísticos principales
ARTISTIC_PRESETS = {
    "Bandada al atardecer": {
        "description": "Movimiento suave y orgánico como pájaros al atardecer",
        "macros": [
            {"name": "Bandada_Principal", "sources": 30, "behavior": "flock", "formation": "circle"},
            {"name": "Bandada_Secundaria", "sources": 15, "behavior": "flock", "formation": "circle"}
        ],
        "trajectories": {
            "Bandada_Principal": "figure8",
            "Bandada_Secundaria": "circle"
        },
        "distances": {
            "Bandada_Principal": "media",
            "Bandada_Secundaria": "cercana"
        },
        "deformations": {
            "Bandada_Principal": [("breathing", 6.0, 1.0)],
            "Bandada_Secundaria": [("breathing", 4.0, 0.5)]
        },
        "interactions": [
            ("following", "Bandada_Secundaria", "Bandada_Principal", 5.0)
        ]
    },
    
    "Constelación dinámica": {
        "description": "Puntos luminosos en rotación con atracción gravitacional",
        "macros": [
            {"name": "Núcleo", "sources": 5, "behavior": "rigid", "formation": "circle"},
            {"name": "Satélites", "sources": 20, "behavior": "elastic", "formation": "spiral"}
        ],
        "trajectories": {
            "Núcleo": "lissajous",
            "Satélites": "spiral"
        },
        "distances": {
            "Núcleo": "focus",
            "Satélites": "expansiva"
        },
        "deformations": {
            "Núcleo": [("chaotic", "lorenz", 0.1)],
            "Satélites": [("force_field", "vortex", 2.0)]
        },
        "interactions": [
            ("orbit", "Satélites", "Núcleo", 8.0, 2.0)
        ]
    },
    
    "Océano de partículas": {
        "description": "Ondas y corrientes en un mar de fuentes sonoras",
        "macros": [
            {"name": "Corriente_1", "sources": 25, "behavior": "flock", "formation": "line"},
            {"name": "Corriente_2", "sources": 25, "behavior": "flock", "formation": "line"}
        ],
        "trajectories": {
            "Corriente_1": "circle",
            "Corriente_2": "circle"
        },
        "distances": {
            "Corriente_1": "lejana",
            "Corriente_2": "lejana"
        },
        "deformations": {
            "Corriente_1": [("wave", "traveling", 3.0, 1.5)],
            "Corriente_2": [("wave", "traveling", 3.0, 1.5)]
        },
        "interactions": [
            ("mutual_force", "Corriente_1", "Corriente_2", "repulsion", 2.0)
        ]
    },
    
    "Enjambre cuántico": {
        "description": "Partículas que oscilan entre orden y caos",
        "macros": [
            {"name": "Quantum_Core", "sources": 40, "behavior": "swarm", "formation": "spiral"}
        ],
        "trajectories": {
            "Quantum_Core": "lissajous"
        },
        "distances": {
            "Quantum_Core": "media"
        },
        "deformations": {
            "Quantum_Core": [
                ("chaotic", "rossler", 0.2),
                ("wave", "breathing", 3.0, 0.8)
            ]
        },
        "interactions": []
    },
    
    "Catedral sonora": {
        "description": "Arquitectura acústica con pilares y bóvedas",
        "macros": [
            {"name": "Pilares", "sources": 12, "behavior": "rigid", "formation": "grid"},
            {"name": "Bóveda", "sources": 20, "behavior": "elastic", "formation": "circle"}
        ],
        "trajectories": {
            "Pilares": "line",
            "Bóveda": "circle"
        },
        "distances": {
            "Pilares": "media",
            "Bóveda": "lejana"
        },
        "deformations": {
            "Pilares": [("wave", "standing", 8.0, 0.3)],
            "Bóveda": [("breathing", 12.0, 2.0)]
        },
        "interactions": []
    },
    
    "Galaxia en espiral": {
        "description": "Sistema galáctico con brazos espirales dinámicos",
        "macros": [
            {"name": "Centro_Galáctico", "sources": 8, "behavior": "rigid", "formation": "circle"},
            {"name": "Brazo_Espiral_1", "sources": 25, "behavior": "elastic", "formation": "spiral"},
            {"name": "Brazo_Espiral_2", "sources": 25, "behavior": "elastic", "formation": "spiral"}
        ],
        "trajectories": {
            "Centro_Galáctico": "lissajous",
            "Brazo_Espiral_1": "spiral",
            "Brazo_Espiral_2": "spiral"
        },
        "distances": {
            "Centro_Galáctico": "cercana",
            "Brazo_Espiral_1": "expansiva",
            "Brazo_Espiral_2": "expansiva"
        },
        "deformations": {
            "Centro_Galáctico": [("chaotic", "lorenz", 0.05)],
            "Brazo_Espiral_1": [("wave", "traveling", 2.0, 1.0)],
            "Brazo_Espiral_2": [("wave", "traveling", 2.0, 1.0)]
        },
        "interactions": [
            ("orbit", "Brazo_Espiral_1", "Centro_Galáctico", 10.0, 1.5),
            ("orbit", "Brazo_Espiral_2", "Centro_Galáctico", 10.0, -1.5)
        ]
    },
    
    "Jardín zen sonoro": {
        "description": "Paisaje minimalista con movimientos contemplativos",
        "macros": [
            {"name": "Piedras", "sources": 5, "behavior": "rigid", "formation": "grid"},
            {"name": "Arena", "sources": 30, "behavior": "flock", "formation": "circle"}
        ],
        "trajectories": {
            "Piedras": "circle",
            "Arena": "circle"
        },
        "distances": {
            "Piedras": "focus",
            "Arena": "media"
        },
        "deformations": {
            "Piedras": [("breathing", 20.0, 0.2)],
            "Arena": [("wave", "ripple", 0.5, 0.3)]
        },
        "interactions": [
            ("mutual_force", "Arena", "Piedras", "repulsion", 1.0)
        ]
    },
    
    "Tormenta eléctrica": {
        "description": "Energía caótica con relámpagos y truenos espaciales",
        "macros": [
            {"name": "Núcleo_Tormenta", "sources": 15, "behavior": "swarm", "formation": "spiral"},
            {"name": "Relámpagos", "sources": 10, "behavior": "elastic", "formation": "line"}
        ],
        "trajectories": {
            "Núcleo_Tormenta": "lissajous",
            "Relámpagos": "line"
        },
        "distances": {
            "Núcleo_Tormenta": "media",
            "Relámpagos": "muy_lejana"
        },
        "deformations": {
            "Núcleo_Tormenta": [
                ("chaotic", "chen", 0.3),
                ("force_field", "vortex", 3.0)
            ],
            "Relámpagos": [("wave", "pulse", 0.2, 5.0)]
        },
        "interactions": []
    },
    
    # Presets adicionales para demos rápidos
    "Demo Básico": {
        "description": "Configuración simple para pruebas rápidas",
        "macros": [
            {"name": "Grupo_Demo", "sources": 10, "behavior": "flock", "formation": "circle"}
        ],
        "trajectories": {
            "Grupo_Demo": "circle"
        },
        "distances": {
            "Grupo_Demo": "personal"
        },
        "deformations": {
            "Grupo_Demo": [("breathing", 4.0, 1.0)]
        },
        "interactions": []
    },
    
    "Minimalista": {
        "description": "Configuración minimalista con pocas fuentes",
        "macros": [
            {"name": "Esencia", "sources": 5, "behavior": "rigid", "formation": "line"}
        ],
        "trajectories": {
            "Esencia": "line"
        },
        "distances": {
            "Esencia": "íntima"
        },
        "deformations": {
            "Esencia": [("breathing", 8.0, 0.3)]
        },
        "interactions": []
    }
}

# Funciones de trayectoria predefinidas con manejo de errores
def safe_trajectory_function(func, default_func=None):
    """Wrapper para funciones de trayectoria con manejo de errores"""
    def wrapper(t):
        try:
            return func(t)
        except Exception as e:
            logger.warning(f"Error en función de trayectoria: {e}")
            if default_func:
                return default_func(t)
            return np.array([0, 0, 0])  # Punto de origen como fallback
    return wrapper

# Funciones básicas
_circle_func = lambda t: np.array([5*np.cos(t*0.3), 5*np.sin(t*0.3), 0])
_figure8_func = lambda t: np.array([5*np.sin(t*0.5), 5*np.sin(t*0.5)*np.cos(t*0.5), 0])
_spiral_func = lambda t: np.array([(3+0.1*t)*np.cos(t*0.5), (3+0.1*t)*np.sin(t*0.5), 0.2*t])
_lissajous_func = lambda t: np.array([5*np.sin(3*t*0.2), 5*np.sin(4*t*0.2+np.pi/4), 2*np.sin(5*t*0.2)])
_line_func = lambda t: np.array([8*np.sin(t*0.3), 0, 0])
_vertical_orbit_func = lambda t: np.array([5*np.cos(t*0.4), 0, 5*np.sin(t*0.4)])

TRAJECTORY_FUNCTIONS = {
    "circle": safe_trajectory_function(_circle_func),
    "figure8": safe_trajectory_function(_figure8_func, _circle_func),
    "spiral": safe_trajectory_function(_spiral_func, _circle_func),
    "lissajous": safe_trajectory_function(_lissajous_func, _circle_func),
    "line": safe_trajectory_function(_line_func, _circle_func),
    "vertical_orbit": safe_trajectory_function(_vertical_orbit_func, _circle_func),
    
    # Funciones adicionales
    "helix": safe_trajectory_function(
        lambda t: np.array([3*np.cos(t*0.5), 3*np.sin(t*0.5), 0.5*t % 10]),
        _circle_func
    ),
    "infinity": safe_trajectory_function(
        lambda t: np.array([8*np.cos(t*0.3), 4*np.sin(2*t*0.3), 0]),
        _circle_func
    ),
    "wave": safe_trajectory_function(
        lambda t: np.array([t*0.5 % 20 - 10, 3*np.sin(t*0.8), 0]),
        _line_func
    )
}

# Composiciones temporales predefinidas
TEMPORAL_COMPOSITIONS = {
    "Danza de las esferas": {
        "description": "Inspirada en la música de las esferas de Kepler",
        "duration": "5 minutos",
        "dynamics": "Crescendo gradual con clímax al minuto 3",
        "timeline": [
            {"time": 0, "action": "load_preset", "preset": "Galaxia en espiral"},
            {"time": 30, "action": "change_speed", "target": "all", "speed": 0.5},
            {"time": 90, "action": "trigger_concentration", "target": "all", "duration": 10},
            {"time": 180, "action": "change_behavior", "target": "all", "behavior": "swarm"},
            {"time": 240, "action": "trigger_dispersion", "target": "all", "duration": 20}
        ]
    },
    
    "Migración": {
        "description": "Simula el movimiento migratorio de aves",
        "duration": "8 minutos",
        "dynamics": "Oleadas de movimiento con pausas contemplativas",
        "timeline": [
            {"time": 0, "action": "load_preset", "preset": "Bandada al atardecer"},
            {"time": 60, "action": "change_distance", "target": "all", "distance": "muy_lejana"},
            {"time": 120, "action": "pause_movement", "target": "Bandada_Secundaria"},
            {"time": 180, "action": "resume_movement", "target": "Bandada_Secundaria"},
            {"time": 240, "action": "change_formation", "target": "all", "formation": "line"},
            {"time": 360, "action": "change_distance", "target": "all", "distance": "íntima"}
        ]
    },
    
    "Cosmos emergente": {
        "description": "Creación progresiva del universo sonoro",
        "duration": "10 minutos",
        "dynamics": "De la nada al todo, con explosiones de creatividad",
        "timeline": [
            {"time": 0, "action": "load_preset", "preset": "Demo Básico"},
            {"time": 120, "action": "load_preset", "preset": "Constelación dinámica"},
            {"time": 300, "action": "load_preset", "preset": "Galaxia en espiral"},
            {"time": 480, "action": "load_preset", "preset": "Océano de partículas"},
            {"time": 600, "action": "trigger_concentration", "target": "all", "duration": 60}
        ]
    },
    
    "Contemplación zen": {
        "description": "Viaje meditativo a través de paisajes sonoros",
        "duration": "15 minutos", 
        "dynamics": "Minimalista, evolución muy lenta y contemplativa",
        "timeline": [
            {"time": 0, "action": "load_preset", "preset": "Jardín zen sonoro"},
            {"time": 300, "action": "change_speed", "target": "all", "speed": 0.3},
            {"time": 600, "action": "change_distance", "target": "all", "distance": "íntima"},
            {"time": 900, "action": "load_preset", "preset": "Minimalista"}
        ]
    }
}

# Configuraciones de estilo para generación aleatoria
STYLE_CONFIGS = {
    "Orgánico": {
        "behaviors": ["flock", "elastic"],
        "formations": ["circle", "spiral"],
        "source_range": {"simple": (5, 15), "medium": (10, 30), "complex": (20, 50)},
        "trajectories": ["circle", "figure8", "spiral"],
        "deformations": ["breathing", "wave"],
        "preferred_distances": ["media", "cercana", "expansiva"]
    },
    
    "Geométrico": {
        "behaviors": ["rigid", "elastic"],
        "formations": ["grid", "line", "circle"],
        "source_range": {"simple": (4, 10), "medium": (8, 20), "complex": (15, 30)},
        "trajectories": ["line", "circle", "lissajous"],
        "deformations": ["wave", "force_field"],
        "preferred_distances": ["focus", "media", "lejana"]
    },
    
    "Caótico": {
        "behaviors": ["swarm", "flock"],
        "formations": ["spiral", "circle"],
        "source_range": {"simple": (10, 20), "medium": (15, 40), "complex": (30, 60)},
        "trajectories": ["lissajous", "spiral"],
        "deformations": ["chaotic", "force_field"],
        "preferred_distances": ["media", "expansiva", "muy_lejana"]
    },
    
    "Minimalista": {
        "behaviors": ["rigid", "elastic"],
        "formations": ["line", "circle"],
        "source_range": {"simple": (3, 8), "medium": (5, 12), "complex": (8, 15)},
        "trajectories": ["line", "circle"],
        "deformations": ["breathing"],
        "preferred_distances": ["íntima", "focus", "cercana"]
    },
    
    "Maximalista": {
        "behaviors": ["flock", "swarm", "elastic"],
        "formations": ["spiral", "circle", "grid"],
        "source_range": {"simple": (20, 50), "medium": (30, 70), "complex": (50, 100)},
        "trajectories": ["lissajous", "spiral", "figure8"],
        "deformations": ["chaotic", "wave", "force_field"],
        "preferred_distances": ["expansiva", "muy_lejana", "envolvente"]
    },
    
    "Experimental": {
        "behaviors": ["swarm", "elastic"],
        "formations": ["spiral", "grid"],
        "source_range": {"simple": (8, 20), "medium": (15, 35), "complex": (25, 60)},
        "trajectories": ["helix", "infinity", "wave", "lissajous"],
        "deformations": ["chaotic", "force_field", "wave"],
        "preferred_distances": ["media", "lejana", "expansiva"]
    },
    
    "Demo": {
        "behaviors": ["flock", "rigid"],
        "formations": ["circle", "line"],
        "trajectories": ["circle", "spiral"],
        "source_range": {"simple": (5, 15), "medium": (10, 25), "complex": (20, 50)},
        "preferred_distances": ["personal", "social"],
        "deformations": ["breathing"]
    }
}

# Funciones de validación
def validate_preset(preset_name: str) -> bool:
    """Validar que un preset existe y es válido"""
    if preset_name not in ARTISTIC_PRESETS:
        return False
        
    preset = ARTISTIC_PRESETS[preset_name]
    
    # Validar estructura básica
    required_keys = ["description", "macros", "trajectories", "distances", "deformations", "interactions"]
    if not all(key in preset for key in required_keys):
        logger.error(f"Preset {preset_name} tiene estructura inválida")
        return False
        
    # Validar que hay al menos un macro
    if not preset["macros"]:
        logger.error(f"Preset {preset_name} no tiene macros")
        return False
        
    return True

def get_available_presets() -> list:
    """Obtener lista de presets disponibles y válidos"""
    valid_presets = []
    for preset_name in ARTISTIC_PRESETS.keys():
        if validate_preset(preset_name):
            valid_presets.append(preset_name)
    return valid_presets

def get_trajectory_function(name: str):
    """Obtener función de trayectoria por nombre"""
    return TRAJECTORY_FUNCTIONS.get(name, TRAJECTORY_FUNCTIONS["circle"])

def get_preset_info(preset_name: str) -> dict:
    """Obtener información detallada de un preset"""
    if preset_name not in ARTISTIC_PRESETS:
        return {}
        
    preset = ARTISTIC_PRESETS[preset_name]
    
    # Calcular estadísticas
    total_sources = sum(macro["sources"] for macro in preset["macros"])
    macro_count = len(preset["macros"])
    has_interactions = len(preset["interactions"]) > 0
    
    return {
        "name": preset_name,
        "description": preset["description"],
        "total_sources": total_sources,
        "macro_count": macro_count,
        "has_interactions": has_interactions,
        "complexity": "Simple" if total_sources < 20 else "Media" if total_sources < 50 else "Compleja"
    }

# Configuración del módulo
__all__ = [
    'ARTISTIC_PRESETS',
    'TRAJECTORY_FUNCTIONS', 
    'TEMPORAL_COMPOSITIONS',
    'STYLE_CONFIGS',
    'validate_preset',
    'get_available_presets',
    'get_trajectory_function',
    'get_preset_info'
]

# Validar presets al importar
if __name__ == "__main__":
    print("Validando presets artísticos...")
    valid_count = 0
    total_count = len(ARTISTIC_PRESETS)
    
    for preset_name in ARTISTIC_PRESETS:
        if validate_preset(preset_name):
            valid_count += 1
            print(f"✅ {preset_name}")
        else:
            print(f"❌ {preset_name}")
            
    print(f"\nValidación completada: {valid_count}/{total_count} presets válidos")
    
    # Validar funciones de trayectoria
    print("\nValidando funciones de trayectoria...")
    for name, func in TRAJECTORY_FUNCTIONS.items():
        try:
            result = func(1.0)  # Probar con t=1.0
            if isinstance(result, np.ndarray) and len(result) == 3:
                print(f"✅ {name}")
            else:
                print(f"❌ {name} - resultado inválido")
        except Exception as e:
            print(f"❌ {name} - error: {e}")
            
    print("Validación de presets completada.")