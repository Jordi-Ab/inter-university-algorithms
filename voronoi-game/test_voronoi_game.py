"""
test_voronoi_game.py
====================
Test suite for the Voronoi Volume Game modules:
- Geometry partitioning & clipping
- High-precision numerical quadrature
- Game state, metrics & AI solver
- Visual dashboard rendering
"""

import sys
import os
import time
import numpy as np

# Ensure voronoi-game directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voronoi_geometry import (
    compute_bounded_voronoi,
    compute_delaunay_edges,
    validate_centers,
    summarize_cell_geometry
)
from numerical_integration import (
    avocado_density,
    integrate_triangle,
    integrate_polygon,
    compute_cell_volumes,
    UNIT_SQUARE_TRUE_VOLUME,
    DENSITY_NORM_CONST
)
from game_engine import VoronoiGame, PRESETS, StrategicAI
from visuals import (
    plot_voronoi_game_2d,
    plot_scoreboard_barchart,
    plot_voronoi_surface_3d,
    plot_dashboard
)
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless test runner
import matplotlib.pyplot as plt


def test_geometry_partition():
    print("[1/5] Testing Computational Geometry & Partitioning...")
    # Test with random points in unit square
    np.random.seed(42)
    pts = np.random.uniform(0.1, 0.9, size=(6, 2))
    cells = compute_bounded_voronoi(pts)

    assert len(cells) == 6, f"Expected 6 cells, got {len(cells)}"
    total_area = sum(c.area for c in cells)
    assert abs(total_area - 1.0) < 1e-10, f"Total area should be 1.0, got {total_area:.12f}"

    # Verify each cell is convex and valid
    for i, c in enumerate(cells):
        assert c.is_valid, f"Cell {i} is invalid"
        assert not c.is_empty, f"Cell {i} is empty"
        assert c.area > 0.01, f"Cell {i} has unexpectedly small area {c.area}"

    # Test Delaunay triangulation dual
    edges = compute_delaunay_edges(pts)
    assert len(edges) >= 5, f"Expected at least 5 Delaunay edges, got {len(edges)}"
    print(f"   [OK] 6 cells partition [0, 1]^2 with total area = {total_area:.10f} and {len(edges)} Delaunay edges.")


def test_avocado_density_and_quadrature():
    print("[2/5] Testing Avocado Density Function & Simplicial Quadrature...")
    # Peak value at origin
    f_peak = avocado_density(0.0, 0.0)
    assert abs(f_peak - DENSITY_NORM_CONST) < 1e-15, f"Peak mismatch: {f_peak} vs {DENSITY_NORM_CONST}"

    # Test quadrature on the unit square directly
    from shapely.geometry import box
    unit_box = box(0.0, 0.0, 1.0, 1.0)
    vol_box = integrate_polygon(unit_box, func=avocado_density, order=7)
    diff = abs(vol_box - UNIT_SQUARE_TRUE_VOLUME)
    assert diff < 1e-10, f"Unit box volume error {diff:.2e} exceeded tolerance."
    print(f"   [OK] Unit square integral matches reference: {vol_box:.12f} (diff = {diff:.2e}).")

    # Test cell volumes sum to unit square volume
    pts = PRESETS["duel_balanced"]["centers"]
    cells = compute_bounded_voronoi(pts)
    vols = compute_cell_volumes(cells, func=avocado_density, order=7)
    sum_vols = float(np.sum(vols))
    diff_sum = abs(sum_vols - UNIT_SQUARE_TRUE_VOLUME)
    assert diff_sum < 1e-10, f"Sum of cell volumes {sum_vols:.12f} differs from true volume ({diff_sum:.2e})."
    print(f"   [OK] Sum of 6 Voronoi cell volumes: {sum_vols:.12f} (diff = {diff_sum:.2e}).")


def test_game_engine():
    print("[3/5] Testing Game Engine & Scenarios...")
    game = VoronoiGame(mode="duel")
    winner_id, winner_msg = game.get_winner()
    assert winner_id in [1, 2], f"Invalid winner id {winner_id}"
    assert "wins" in winner_msg or "volume" in winner_msg

    table = game.get_summary_table()
    assert len(table) == 6, f"Expected 6 rows in summary table, got {len(table)}"
    assert abs(sum(r["Area Share (%)"] for r in table) - 100.0) < 1e-6
    assert abs(sum(r["Volume Share (%)"] for r in table) - 100.0) < 1e-6

    # Test all presets load and recompute cleanly
    for pkey in PRESETS:
        game.load_preset(pkey)
        assert len(game.cells) == 6
        assert abs(np.sum(game.areas) - 1.0) < 1e-10
        assert game.entropy > 0.0
        assert 0.0 <= game.gini <= 1.0

    print("   [OK] Game state, scoring, table generation, and all presets validated.")


def test_ai_solvers():
    print("[4/5] Testing AI Opponents...")
    existing = np.array([
        [0.2, 0.2], [0.8, 0.2], [0.5, 0.5], [0.2, 0.8], [0.8, 0.8]
    ])
    # Greedy Volume
    t0 = time.perf_counter()
    best_vol_pt = StrategicAI.best_move_greedy_volume(existing, grid_resolution=25)
    t1 = time.perf_counter()
    assert 0.0 <= best_vol_pt[0] <= 1.0 and 0.0 <= best_vol_pt[1] <= 1.0
    print(f"   [OK] Greedy Volume AI picked {best_vol_pt} in {(t1-t0)*1000:.1f} ms.")

    # Greedy Area
    best_area_pt = StrategicAI.best_move_greedy_area(existing, grid_resolution=25)
    assert 0.0 <= best_area_pt[0] <= 1.0 and 0.0 <= best_area_pt[1] <= 1.0
    print(f"   [OK] Greedy Area AI picked {best_area_pt}.")


def test_visual_rendering():
    print("[5/5] Testing Visual Dashboards & Plot Exports...")
    game = VoronoiGame()
    
    # 2D plot
    fig2d, ax2d = plt.subplots(figsize=(6, 6))
    plot_voronoi_game_2d(game, show_delaunay=True, ax=ax2d)
    plt.close(fig2d)

    # Scoreboard
    fig_sb, ax_sb = plt.subplots(figsize=(7, 4))
    plot_scoreboard_barchart(game, ax=ax_sb)
    plt.close(fig_sb)

    # 3D plot
    fig_3d = plot_voronoi_surface_3d(game, resolution=30)
    plt.close(fig_3d)

    # Full dashboard
    fig_dash = plot_dashboard(game, show_delaunay=True)
    out_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_dashboard_preview.png")
    fig_dash.savefig(out_img, dpi=100)
    plt.close(fig_dash)
    assert os.path.exists(out_img), "Dashboard preview image was not created."
    print(f"   [OK] Visual plots rendered cleanly; preview saved to {out_img}.")


if __name__ == "__main__":
    print("=" * 65)
    print("Running Automated Test Suite for Voronoi Volume Game")
    print("=" * 65)
    t_start = time.perf_counter()
    test_geometry_partition()
    test_avocado_density_and_quadrature()
    test_game_engine()
    test_ai_solvers()
    test_visual_rendering()
    t_total = time.perf_counter() - t_start
    print("=" * 65)
    print(f"ALL TESTS PASSED SUCCESSFULLY in {t_total:.2f} seconds!")
    print("=" * 65)
