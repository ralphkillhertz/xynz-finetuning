#!/usr/bin/env python3
"""
Generador de dataset XYNZ para fine-tuning
Genera 16,500 ejemplos de entrenamiento + 500 de validación
"""
import json
import random
from pathlib import Path

# Configuración
TRAIN_EXAMPLES = 16000
VAL_EXAMPLES = 500
OUTPUT_DIR = Path("dataset/processed/alpaca")

# Categorías y distribución
CATEGORIES = {
    'spatial_positioning': 0.245,      # 24.5%
    'acoustic_parameters': 0.209,      # 20.9%
    'trajectory_mathematics': 0.182,   # 18.2%
    'perceptual_control': 0.155,       # 15.5%
    'mixing_mastering': 0.118,         # 11.8%
    'electroacoustic_composition': 0.091  # 9.1%
}

# Templates por categoría
TEMPLATES = {
    'spatial_positioning': [
        ("Coloca el {} a {} grados azimut, {} grados elevación, {} metros de distancia", 
         "position_source(source='{}', azimuth={}, elevation={}, distance={})"),
        ("Mueve la fuente {} a la posición ({}, {}, {})", 
         "move_source('{}', x={}, y={}, z={})"),
        ("Posiciona {} fuentes en círculo de {} metros de radio",
         "create_circular_formation(sources={}, radius={})"),
        ("Crea una línea de {} fuentes desde ({}, {}, {}) hasta ({}, {}, {})",
         "create_line_formation(count={}, start=({}, {}, {}), end=({}, {}, {}))"),
    ],
    'acoustic_parameters': [
        ("Configura reverberación de {} segundos con {} de difusión",
         "set_reverb(time={}, diffusion={})"),
        ("Ajusta primeras reflexiones a {} ms con atenuación de {} dB",
         "set_early_reflections(delay_ms={}, attenuation_db={})"),
        ("Simula espacio de {}x{}x{} metros con absorción de {}",
         "configure_room(width={}, depth={}, height={}, absorption={})"),
        ("Establece distancia perceptual de {} metros con brillo de {}%",
         "set_perceptual_distance(meters={}, brightness={})"),
    ],
    'trajectory_mathematics': [
        ("Crea trayectoria circular de radio {} a {} revoluciones por minuto",
         "create_circular_trajectory(radius={}, rpm={})"),
        ("Genera espiral de {} vueltas con expansión de {} metros",
         "create_spiral_trajectory(turns={}, expansion={})"),
        ("Dibuja Lissajous con frecuencias {}:{} y fase {}",
         "create_lissajous(freq_x={}, freq_y={}, phase={})"),
        ("Crea movimiento sinusoidal en eje {} con amplitud {} y frecuencia {} Hz",
         "create_sine_motion(axis='{}', amplitude={}, frequency={})"),
    ],
    'perceptual_control': [
        ("Aplica filtro de distancia con corte en {} Hz y resonancia {}",
         "apply_distance_filter(cutoff={}, resonance={})"),
        ("Ajusta brillo espacial al {}% con calidez de {}",
         "set_spatial_brightness(brightness={}, warmth={})"),
        ("Configura doppler con velocidad máxima de {} m/s",
         "configure_doppler(max_velocity={})"),
        ("Establece apertura de fuente a {} grados con foco de {}%",
         "set_source_aperture(degrees={}, focus={})"),
    ],
    'mixing_mastering': [
        ("Balancea {} fuentes con panorama automático cada {} segundos",
         "auto_balance_sources(count={}, interval_seconds={})"),
        ("Aplica compresión espacial con ratio {}:1 y threshold {} dB",
         "apply_spatial_compression(ratio={}, threshold_db={})"),
        ("Crea automatización de {} a {} en {} segundos para parámetro {}",
         "create_automation(from_value={}, to_value={}, duration={}, parameter='{}')"),
        ("Optimiza imagen estéreo con ancho de {}% y profundidad {}%",
         "optimize_stereo_image(width={}, depth={})"),
    ],
    'electroacoustic_composition': [
        ("Espacializa gránulos con densidad {} y dispersión {} grados",
         "spatialize_granular(density={}, dispersion_degrees={})"),
        ("Distribuye espectro en {} bandas con separación de {} grados",
         "distribute_spectrum(bands={}, separation={})"),
        ("Crea nube de {} partículas en espacio de {}m³",
         "create_particle_cloud(count={}, volume_m3={})"),
        ("Aplica morfología espectral {} con profundidad {}%",
         "apply_spectral_morphing(type='{}', depth={})"),
    ]
}

# Valores posibles para rellenar templates
VALUES = {
    'instruments': ['violín', 'piano', 'voz', 'guitarra', 'sintetizador', 'percusión', 'flauta', 'bajo'],
    'axes': ['X', 'Y', 'Z'],
    'morph_types': ['stretch', 'shift', 'freeze', 'smear'],
    'parameters': ['gain', 'position', 'reverb', 'filter']
}

def generate_example(category):
    """Genera un ejemplo para una categoría"""
    template_pair = random.choice(TEMPLATES[category])
    instruction_template, output_template = template_pair
    
    # Generar valores aleatorios según el template
    if category == 'spatial_positioning':
        if "Coloca el" in instruction_template:
            instrument = random.choice(VALUES['instruments'])
            azimuth = random.randint(-180, 180)
            elevation = random.randint(-90, 90)
            distance = round(random.uniform(0.5, 20), 1)
            instruction = instruction_template.format(instrument, azimuth, elevation, distance)
            output = output_template.format(instrument, azimuth, elevation, distance)
        elif "fuentes en círculo" in instruction_template:
            sources = random.randint(3, 12)
            radius = round(random.uniform(1, 10), 1)
            instruction = instruction_template.format(sources, radius)
            output = output_template.format(sources, radius)
        elif "Mueve la fuente" in instruction_template:
            instrument = random.choice(VALUES['instruments'])
            x, y, z = [round(random.uniform(-10, 10), 1) for _ in range(3)]
            instruction = instruction_template.format(instrument, x, y, z)
            output = output_template.format(instrument, x, y, z)
        else:  # línea de fuentes
            count = random.randint(3, 8)
            coords = [round(random.uniform(-10, 10), 1) for _ in range(6)]
            instruction = instruction_template.format(count, *coords)
            output = output_template.format(count, *coords)
            
    elif category == 'acoustic_parameters':
        if "reverberación" in instruction_template:
            time = round(random.uniform(0.5, 5), 1)
            diffusion = round(random.uniform(0.3, 0.9), 2)
            instruction = instruction_template.format(time, diffusion)
            output = output_template.format(time, diffusion)
        elif "reflexiones" in instruction_template:
            delay = random.randint(5, 100)
            atten = random.randint(-20, -3)
            instruction = instruction_template.format(delay, atten)
            output = output_template.format(delay, atten)
        elif "espacio de" in instruction_template:
            dims = [random.randint(5, 50) for _ in range(3)]
            absorption = round(random.uniform(0.1, 0.9), 2)
            instruction = instruction_template.format(*dims, absorption)
            output = output_template.format(*dims, absorption)
        else:  # distancia perceptual
            distance = round(random.uniform(1, 30), 1)
            brightness = random.randint(20, 100)
            instruction = instruction_template.format(distance, brightness)
            output = output_template.format(distance, brightness)
            
    elif category == 'trajectory_mathematics':
        if "circular de radio" in instruction_template:
            radius = round(random.uniform(1, 10), 1)
            rpm = round(random.uniform(0.5, 30), 1)
            instruction = instruction_template.format(radius, rpm)
            output = output_template.format(radius, rpm)
        elif "espiral" in instruction_template:
            turns = random.randint(2, 10)
            expansion = round(random.uniform(0.5, 5), 1)
            instruction = instruction_template.format(turns, expansion)
            output = output_template.format(turns, expansion)
        elif "Lissajous" in instruction_template:
            freq_x = random.randint(1, 7)
            freq_y = random.randint(1, 7)
            phase = round(random.uniform(0, 360), 0)
            instruction = instruction_template.format(freq_x, freq_y, phase)
            output = output_template.format(freq_x, freq_y, phase)
        else:  # sinusoidal
            axis = random.choice(VALUES['axes'])
            amplitude = round(random.uniform(0.5, 5), 1)
            frequency = round(random.uniform(0.1, 5), 1)
            instruction = instruction_template.format(axis, amplitude, frequency)
            output = output_template.format(axis, amplitude, frequency)
            
    elif category == 'perceptual_control':
        if "filtro de distancia" in instruction_template:
            cutoff = random.randint(200, 8000)
            resonance = round(random.uniform(0.5, 4), 1)
            instruction = instruction_template.format(cutoff, resonance)
            output = output_template.format(cutoff, resonance)
        elif "brillo espacial" in instruction_template:
            brightness = random.randint(0, 100)
            warmth = round(random.uniform(0, 1), 2)
            instruction = instruction_template.format(brightness, warmth)
            output = output_template.format(brightness, warmth)
        elif "doppler" in instruction_template:
            velocity = round(random.uniform(1, 50), 1)
            instruction = instruction_template.format(velocity)
            output = output_template.format(velocity)
        else:  # apertura
            degrees = random.randint(0, 180)
            focus = random.randint(0, 100)
            instruction = instruction_template.format(degrees, focus)
            output = output_template.format(degrees, focus)
            
    elif category == 'mixing_mastering':
        if "Balancea" in instruction_template:
            sources = random.randint(4, 16)
            interval = round(random.uniform(0.5, 10), 1)
            instruction = instruction_template.format(sources, interval)
            output = output_template.format(sources, interval)
        elif "compresión espacial" in instruction_template:
            ratio = random.choice([2, 3, 4, 6, 8])
            threshold = random.randint(-30, -10)
            instruction = instruction_template.format(ratio, threshold)
            output = output_template.format(ratio, threshold)
        elif "automatización" in instruction_template:
            from_val = round(random.uniform(0, 1), 2)
            to_val = round(random.uniform(0, 1), 2)
            duration = round(random.uniform(0.5, 10), 1)
            param = random.choice(VALUES['parameters'])
            instruction = instruction_template.format(from_val, to_val, duration, param)
            output = output_template.format(from_val, to_val, duration, param)
        else:  # imagen estéreo
            width = random.randint(50, 150)
            depth = random.randint(50, 150)
            instruction = instruction_template.format(width, depth)
            output = output_template.format(width, depth)
            
    else:  # electroacoustic_composition
        if "gránulos" in instruction_template:
            density = random.randint(10, 1000)
            dispersion = random.randint(30, 360)
            instruction = instruction_template.format(density, dispersion)
            output = output_template.format(density, dispersion)
        elif "espectro" in instruction_template:
            bands = random.randint(4, 32)
            separation = round(random.uniform(5, 45), 1)
            instruction = instruction_template.format(bands, separation)
            output = output_template.format(bands, separation)
        elif "partículas" in instruction_template:
            count = random.randint(50, 5000)
            volume = random.randint(10, 1000)
            instruction = instruction_template.format(count, volume)
            output = output_template.format(count, volume)
        else:  # morfología
            morph_type = random.choice(VALUES['morph_types'])
            depth = random.randint(10, 100)
            instruction = instruction_template.format(morph_type, depth)
            output = output_template.format(morph_type, depth)
    
    return {
        'instruction': instruction,
        'output': output,
        'category': category
    }

def generate_dataset():
    """Genera el dataset completo"""
    print("🎯 Generando dataset XYNZ para fine-tuning...")
    
    # Crear directorio
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generar ejemplos de entrenamiento
    train_examples = []
    for category, percentage in CATEGORIES.items():
        count = int(TRAIN_EXAMPLES * percentage)
        print(f"  - {category}: {count} ejemplos")
        for _ in range(count):
            train_examples.append(generate_example(category))
    
    # Mezclar aleatoriamente
    random.shuffle(train_examples)
    
    # Guardar entrenamiento
    train_file = OUTPUT_DIR / "train.jsonl"
    with open(train_file, 'w', encoding='utf-8') as f:
        for example in train_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"✅ Guardado: {train_file} ({len(train_examples)} ejemplos)")
    
    # Generar ejemplos de validación
    val_examples = []
    for category, percentage in CATEGORIES.items():
        count = int(VAL_EXAMPLES * percentage)
        for _ in range(count):
            val_examples.append(generate_example(category))
    
    random.shuffle(val_examples)
    
    # Guardar validación
    val_file = OUTPUT_DIR / "validation.jsonl"
    with open(val_file, 'w', encoding='utf-8') as f:
        for example in val_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"✅ Guardado: {val_file} ({len(val_examples)} ejemplos)")
    
    print(f"\n📊 Total generado: {len(train_examples) + len(val_examples)} ejemplos")

if __name__ == "__main__":
    generate_dataset()