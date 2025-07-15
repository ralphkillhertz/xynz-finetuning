#!/usr/bin/env python3
"""Mostrar estado actual del archivo"""
import os

with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'r') as f:
    lines = f.readlines()

print("PRIMERAS 50 LÍNEAS:")
print("=" * 70)
for i in range(min(50, len(lines))):
    print(f"{i+1:3d}: {lines[i]}", end='')
