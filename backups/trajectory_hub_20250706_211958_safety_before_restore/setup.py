"""
Setup.py para Trajectory Hub v2.0
"""
from setuptools import setup, find_packages
from pathlib import Path

# Leer README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Leer requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text().splitlines() 
        if line.strip() and not line.startswith("#")
    ]
else:
    requirements = ["numpy>=1.21.0", "scipy>=1.7.0", "python-osc>=1.8.0"]

setup(
    name="trajectory-hub",
    version="2.0.0",
    description="Sistema de Trayectorias 3D Inteligentes para Spat Revolution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ralph Killhertz",
    author_email="ralph@xynz.org",
    url="https://github.com/xynz/trajectory-hub",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0", 
            "mypy>=0.950",
            "flake8>=4.0.0"
        ],
        "numba": ["numba>=0.56.0"],
        "ml": ["scikit-learn>=1.0.0", "tensorflow>=2.8.0"],
        "viz": ["matplotlib>=3.5.0", "plotly>=5.0.0"]
    },
    entry_points={
        "console_scripts": [
            "trajectory-hub=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)
