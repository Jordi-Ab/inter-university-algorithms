"""
Setup script for inter-university-algorithms.
Provides the voronoi_game package.
"""
from setuptools import setup

setup(
    name="inter-university-algorithms",
    version="0.1.0",
    description="Inter-University Collaborative Algorithms Project: Game Theory, Polygon Integration, and Voronoi Volume Games",
    author="Jordi-Ab",
    packages=["voronoi_game"],
    package_dir={"voronoi_game": "voronoi-game"},
    package_data={
        "voronoi_game": [
            "voronoi_volume_game.html",
            "rhill-voronoi-core.min.js",
        ],
    },
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pandas>=2.0.0",
        "shapely>=2.0.0",
        "matplotlib>=3.7.0",
        "ipywidgets>=8.0.0",
    ],
)
