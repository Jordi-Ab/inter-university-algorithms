# Module 2: Numerical Integration over Arbitrary Polygons

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Jordi-Ab/inter-university-algorithms/main?labpath=polygon-integration%2FNumerical_Integration_over_Polygons_Visual_Guide.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Jordi-Ab/inter-university-algorithms/blob/main/polygon-integration/Numerical_Integration_over_Polygons_Visual_Guide.ipynb)

## Overview
Quadrature routines and numerical methods evaluated over complex 2D planar domains:
- **Domain Triangulation & Partitioning**: Decomposing polygons into simplices for standard Gauss–Legendre quadrature rules.
- **Green's Theorem Transformations**: Transforming area/volume integrals over 2D polygons into line integrals along boundary edges.
- **8-Node Spline Finite Elements (Li et al. 2009)**: Implementing quadrilateral spline cubature rules based on diagonal intersection partitioning and boundary nodes.
- **Visual Analytics & Benchmarks**: Comparing convergence and error orders between triangular Gauss rules and quadrilateral spline elements on exponential peaks and conical surfaces.

## Notebooks
- [`Numerical_Integration_over_Polygons_Visual_Guide.ipynb`](Numerical_Integration_over_Polygons_Visual_Guide.ipynb): Visual guide, step-by-step geometric explanations, 3D terrain plots, and benchmark comparisons.
