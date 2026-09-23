# Module 3: Voronoi Volume Game
### Spatial Competition, Non-Uniform Demand & Six-Center Quadrature in the First Quadrant

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Jordi-Ab/inter-university-algorithms/main?labpath=voronoi-game%2FThe_Voronoi_Volume_Game.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Jordi-Ab/inter-university-algorithms/blob/main/voronoi-game/The_Voronoi_Volume_Game.ipynb)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)

## Overview
This module explores strategic facility location and spatial market partitioning under non-uniform economic resource density (inspired by the seminar presentation *"A Voronoï volume game for the avocados"* by Dr. José Daniel López-Barrientos):
- **Continuous Density Landscape**: Evaluates the bivariate density distribution:
  $$f(x, y) = \frac{\sqrt{3}}{4\pi} \exp\left(-\frac{x^2 - xy + y^2}{2}\right)$$
  over the unit square in the first quadrant $[0, 1] \times [0, 1]$ with its peak situated at the origin $(0, 0)$.
- **Six-Center Voronoi Diagram**: Partitions the market into 6 irregular convex polygon catchment cells using exact halfplane clipping.
- **High-Order Polygon Quadrature**: Applies Duffy-transformed tensor Gauss–Legendre cubature over triangle simplices to calculate exact captured volumes in $< 1$ ms with error $< 10^{-13}$.
- **Game Theoretic Solvers & Economic Metrics**: Analyzes 1v1 duels (3 vs 3 centers), 6-firm free-for-all markets, greedy volume vs area AI solvers, Shannon entropy, and Gale–Roth–Shapley stability.
- **Interactive Visual Analytics**: Interactive `ipywidgets` dashboard with live 2D market map, 3D terrain slices, and comparative volume vs area scoreboards.

---

## 🧱 Modular Architecture (Clean Helper Modules)
To keep the educational notebook clean, uncluttered, and pedagogical, the underlying algorithms are separated into specialized helper modules:
1. **[`voronoi_geometry.py`](voronoi_geometry.py)**: Bounded halfplane clipping in $[0, 1]^2$, Delaunay triangulation dual graph extraction, and polygon geometry summaries.
2. **[`numerical_integration.py`](numerical_integration.py)**: Vectorized avocado density distribution, simplicial Duffy Gauss–Legendre quadrature, and polygon cubature.
3. **[`game_engine.py`](game_engine.py)**: Core `VoronoiGame` class, scoring rules, preset scenarios (`"duel_balanced"`, `"gold_rush"`, `"hexagonal_pack"`), Shannon entropy, Gini index, and autonomous AI solvers.
4. **[`visuals.py`](visuals.py)**: 2D market maps with contour overlays, 3D density surface plots, scoreboard bar charts, and interactive `ipywidgets` dashboard.
5. **[`test_voronoi_game.py`](test_voronoi_game.py)**: Automated test suite validating geometry, numerical integration precision, game state, and plotting.

---

## 🕹️ Interactive Web Application
- **[`voronoi_volume_game.html`](voronoi_volume_game.html)**: Standalone, 60-FPS HTML5 Canvas game replicating the reference game at [`cfbrasz.github.io`](https://cfbrasz.github.io/VoronoiColoring.html). Features:
  * Live avocado density heatmap background of $f(x, y)$ with $(0, 0)$ peak highlighted.
  * Turn-based 6-center match (3 Red vs 3 Blue) with mouse click-to-place and active preview.
  * Dual real-time scoreboard comparing **Captured Avocado Volume** against **Land Area**.
  * Play against computer (Volume-maximizing AI or Area-maximizing AI).
  * Direct clipboard export: click "Copy Coordinates" to paste your match into the Python notebook.

---

## 📓 Notebooks
- **[`The_Voronoi_Volume_Game.ipynb`](The_Voronoi_Volume_Game.ipynb)**: Complete visual walkthrough, mathematical derivations, embedded interactive web canvas, AI simulation, and student exploration challenges.

---

## 🚀 Running the Code

### Option A: MyBinder (Recommended for Students)
Click the **Launch Binder** badge above to launch an interactive JupyterLab environment directly in your browser with zero installation.

### Option B: Local Testing
Run the automated test suite locally:
```bash
python voronoi-game/test_voronoi_game.py
```
Launch JupyterLab:
```bash
jupyter lab voronoi-game/The_Voronoi_Volume_Game.ipynb
```
