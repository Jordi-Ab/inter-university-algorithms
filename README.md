# Inter-University Collaborative Algorithms Project

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Jordi-Ab/inter-university-algorithms/main)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)

This repository hosts collaborative implementations developed jointly across partner universities. The project explores algorithmic game theory, computational geometry, and scientific computing through three core assignments.

Students and collaborators can run and interact with all code directly in their browsers with **zero local installation, zero account creation, and zero logins** via **MyBinder**.

---

## 🚀 Quick Launch Matrix

Click any **Binder** badge to launch an interactive JupyterLab session directly in your browser:

| Module | Topic | Interactive Binder Environment | Colab (Optional) |
| :--- | :--- | :--- | :--- |
| **1. Gale–Roth–Shapley** | Two-Sided Matching & Game Theory | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Jordi-Ab/inter-university-algorithms/main?labpath=gale-roth-shapley%2FThe_Gale_Roth_Shapley_1_1_Stable_Matching_Algorithm.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Jordi-Ab/inter-university-algorithms/blob/main/gale-roth-shapley/The_Gale_Roth_Shapley_1_1_Stable_Matching_Algorithm.ipynb) |
| **2. Polygon Integration** | Quadrature & Computational Geometry | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Jordi-Ab/inter-university-algorithms/main?labpath=polygon-integration%2FNumerical_Integration_over_Polygons_Visual_Guide.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Jordi-Ab/inter-university-algorithms/blob/main/polygon-integration/Numerical_Integration_over_Polygons_Visual_Guide.ipynb) |
| **3. Voronoi Volume Game** | Spatial Partitioning & Game Solvers | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Jordi-Ab/inter-university-algorithms/main?labpath=voronoi-game) | *(Coming soon)* |

---

## 📚 Modules Overview

### 1. Gale–Shapley & Roth–Peranson Matching ([`/gale-roth-shapley`](gale-roth-shapley/))
* Implementation and analysis of two-sided matching markets with preferences.
* Focuses on stability, student-optimal strategies, and extensions for market clearing (e.g., residency/school match constraints).
* Includes validation routines, blocking pair detection, and automated test suites.

### 2. Numerical Integration over Arbitrary Polygons ([`/polygon-integration`](polygon-integration/))
* Quadrature routines and numerical methods evaluated over complex 2D planar domains.
* Covers domain triangulation/partitioning, Green's theorem transformations, and accuracy benchmarks.
* Compares numerical convergence against analytical solutions for irregular polygon boundaries.

### 3. Voronoi Volume Game ([`/voronoi-game`](voronoi-game/))
* Strategic generator/site placement game based on Voronoi cell partitioning and volume maximization.
* Features game simulation, heuristic/greedy agent solvers, and interactive territory visualization using `shapely` and `scipy.spatial`.

---

## 💻 Running the Code

### Option A: MyBinder (Recommended for Students — Zero Signup)
1. Click any of the **Binder** badges above.
2. An interactive JupyterLab environment will build and launch in your browser automatically.
3. Open any `.ipynb` notebook and run cells interactively.
> **Note for students:** Binder sessions are ephemeral. If your session is idle for more than 10–15 minutes, the server shuts down. Make sure to download your completed work locally via **File → Download** (`.ipynb`).

### Option B: Local Environment (Optional)
If you prefer running locally on your own computer:

```bash
git clone https://github.com/Jordi-Ab/inter-university-algorithms.git
cd inter-university-algorithms
pip install -r .binder/requirements.txt
jupyter lab
```
