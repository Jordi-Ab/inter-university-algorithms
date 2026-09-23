"""
voronoi_game
============
A pedagogical package for strategic spatial facility placement, bounded Voronoi diagrams,
and high-order numerical avocado volume quadrature over non-uniform demand landscapes.
"""

from .voronoi_geometry import (
    compute_bounded_voronoi,
    compute_delaunay_edges,
    validate_centers,
    summarize_cell_geometry,
    get_polygon_vertices,
)
from .numerical_integration import (
    avocado_density,
    integrate_polygon,
    compute_cell_volumes,
    UNIT_SQUARE_TRUE_VOLUME,
    DENSITY_NORM_CONST,
)
from .game_engine import VoronoiGame, PRESETS, StrategicAI
from .visuals import (
    plot_voronoi_game_2d,
    plot_scoreboard_barchart,
    plot_voronoi_surface_3d,
    plot_dashboard,
    create_interactive_voronoi_widget,
    display_html_game,
    launch_game_in_browser,
)

__all__ = [
    "compute_bounded_voronoi",
    "compute_delaunay_edges",
    "validate_centers",
    "summarize_cell_geometry",
    "get_polygon_vertices",
    "avocado_density",
    "integrate_polygon",
    "compute_cell_volumes",
    "UNIT_SQUARE_TRUE_VOLUME",
    "DENSITY_NORM_CONST",
    "VoronoiGame",
    "PRESETS",
    "StrategicAI",
    "plot_voronoi_game_2d",
    "plot_scoreboard_barchart",
    "plot_voronoi_surface_3d",
    "plot_dashboard",
    "create_interactive_voronoi_widget",
    "display_html_game",
    "launch_game_in_browser",
]
