"""
visuals.py
==========
Visualization helpers and interactive widget dashboards for the
Six-Center Voronoi Volume Game in the unit square [0, 1]^2.
"""

from typing import Optional, Tuple, List, Dict, Any
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D
from shapely.geometry import Polygon

try:
    from .voronoi_geometry import get_polygon_vertices, compute_delaunay_edges
    from .numerical_integration import avocado_density, DENSITY_NORM_CONST
    from .game_engine import VoronoiGame, PRESETS, StrategicAI
except (ImportError, ValueError):
    from voronoi_geometry import get_polygon_vertices, compute_delaunay_edges
    from numerical_integration import avocado_density, DENSITY_NORM_CONST
    from game_engine import VoronoiGame, PRESETS, StrategicAI


# ==============================================================================
# Color Palettes & Aesthetic Theme
# ==============================================================================

# Palette for 2-player duel (Player 1 = Blue shades, Player 2 = Amber/Coral shades)
DUEL_COLORS = {
    1: {"fill": "#3B82F6", "edge": "#1D4ED8", "badge": "#2563EB", "name": "Player 1 (Blue)"},
    2: {"fill": "#F59E0B", "edge": "#B45309", "badge": "#D97706", "name": "Player 2 (Orange)"}
}

# Distinct palette for 6-Firm Free-For-All
FIRM_COLORS = [
    {"fill": "#3B82F6", "edge": "#1D4ED8", "badge": "#2563EB", "name": "Firm A"},
    {"fill": "#F59E0B", "edge": "#B45309", "badge": "#D97706", "name": "Firm B"},
    {"fill": "#10B981", "edge": "#047857", "badge": "#059669", "name": "Firm C"},
    {"fill": "#8B5CF6", "edge": "#6D28D9", "badge": "#7C3AED", "name": "Firm D"},
    {"fill": "#EF4444", "edge": "#B91C1C", "badge": "#DC2626", "name": "Firm E"},
    {"fill": "#06B6D4", "edge": "#0E7490", "badge": "#0891B2", "name": "Firm F"},
]

# Custom gentle avocado density colormap (cream to deep avocado green)
AVOCADO_CMAP = LinearSegmentedColormap.from_list(
    "avocado_harvest",
    ["#F7FEE7", "#ECFCCB", "#D9F99D", "#A3E635", "#65A30D", "#3F6212", "#14532D"],
    N=256
)


# ==============================================================================
# 1. 2D Strategic Market Map
# ==============================================================================

def plot_voronoi_game_2d(
    game: VoronoiGame,
    show_delaunay: bool = False,
    show_density_contours: bool = True,
    show_cell_labels: bool = True,
    title: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
    figsize: Tuple[int, int] = (8, 8)
) -> plt.Axes:
    """
    Plot 2D Voronoi partition over the avocado value density field.

    Parameters
    ----------
    game : VoronoiGame
        Current game instance.
    show_delaunay : bool
        Whether to overlay the Delaunay triangulation dual graph.
    show_density_contours : bool
        Whether to render background contours of f(x, y).
    show_cell_labels : bool
        Whether to print volume share % annotations inside cells.
    title : Optional[str]
        Plot title.
    ax : Optional[plt.Axes]
        Matplotlib axis.

    Returns
    -------
    plt.Axes
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, dpi=120)

    # 1. Background density heatmap & contours
    res = 160
    x_lin = np.linspace(0.0, 1.0, res)
    y_lin = np.linspace(0.0, 1.0, res)
    X, Y = np.meshgrid(x_lin, y_lin)
    Z = avocado_density(X, Y)

    if show_density_contours:
        c_fill = ax.contourf(X, Y, Z, levels=18, cmap=AVOCADO_CMAP, alpha=0.45, zorder=1)
        c_lines = ax.contour(X, Y, Z, levels=10, colors="#4D7C0F", alpha=0.30, linewidths=0.7, zorder=2)
        ax.clabel(c_lines, inline=True, fontsize=7, fmt="%.3f")

    # 2. Origin peak marker
    ax.scatter([0.0], [0.0], s=140, color="#CA8A04", marker="*", edgecolor="#78350F", linewidth=1.5, zorder=6)
    ax.annotate(
        f"Peak Origin (0, 0)\nf_max = {DENSITY_NORM_CONST:.3f}",
        xy=(0.02, 0.03),
        fontsize=8,
        fontweight="bold",
        color="#78350F",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#FEF08A", edgecolor="#CA8A04", alpha=0.85),
        zorder=7
    )

    # 3. Voronoi cells
    for i, cell in enumerate(game.cells):
        if cell.is_empty:
            continue

        p_id = game.players[i]
        if game.mode == "duel":
            cfg = DUEL_COLORS.get(p_id, DUEL_COLORS[1])
        else:
            cfg = FIRM_COLORS[i % len(FIRM_COLORS)]

        verts = get_polygon_vertices(cell)
        poly_patch = patches.Polygon(
            verts,
            closed=True,
            facecolor=cfg["fill"],
            edgecolor=cfg["edge"],
            linewidth=2.0,
            alpha=0.38,
            zorder=3
        )
        ax.add_patch(poly_patch)

        # Center point marker
        cx, cy = game.centers[i]
        ax.scatter([cx], [cy], s=110, facecolor=cfg["badge"], edgecolor="#FFFFFF", linewidth=1.5, zorder=5)
        ax.text(
            cx, cy + 0.028,
            f"C{i+1}",
            fontsize=9,
            fontweight="bold",
            color="#1E293B",
            ha="center",
            va="bottom",
            zorder=6,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="#FFFFFF", edgecolor="#CBD5E1", alpha=0.85)
        )

        # Cell label (Volume and Area share)
        if show_cell_labels:
            centroid = cell.centroid
            ax.text(
                centroid.x, centroid.y - 0.015,
                f"Vol: {game.volume_shares[i]:.1f}%\nArea: {game.area_shares[i]:.1f}%",
                fontsize=7.5,
                fontweight="semibold",
                color="#0F172A",
                ha="center",
                va="center",
                zorder=4,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFFFFF", edgecolor="none", alpha=0.65)
            )

    # 4. Delaunay triangulation dual graph
    if show_delaunay:
        edges = compute_delaunay_edges(game.centers)
        for u, v in edges:
            p_u = game.centers[u]
            p_v = game.centers[v]
            ax.plot([p_u[0], p_v[0]], [p_u[1], p_v[1]], linestyle="--", color="#DC2626", linewidth=1.3, alpha=0.75, zorder=4)

    # 5. Styling and boundaries
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_aspect("equal")
    ax.set_xlabel("x (Market Dimension 1)", fontsize=10, fontweight="semibold")
    ax.set_ylabel("y (Market Dimension 2)", fontsize=10, fontweight="semibold")
    ax.grid(True, linestyle=":", alpha=0.4, color="#94A3B8")

    # Bounding box border
    unit_box = patches.Rectangle((0, 0), 1, 1, linewidth=2.2, edgecolor="#0F172A", facecolor="none", zorder=8)
    ax.add_patch(unit_box)

    if title is None:
        winner_id, winner_msg = game.get_winner()
        title = f"Voronoi Volume Game (6 Centers)\n{winner_msg}"
    ax.set_title(title, fontsize=11, fontweight="bold", pad=10)

    return ax


# ==============================================================================
# 2. Scoreboard & Market Share Analytics Bar Chart
# ==============================================================================

def plot_scoreboard_barchart(
    game: VoronoiGame,
    figsize: Tuple[int, int] = (8, 4.5),
    ax: Optional[plt.Axes] = None
) -> plt.Axes:
    """
    Plot comparative bar chart of Volume Share (%) vs Area Share (%) for each center.
    Highlights the economic divergence between physical land area and captured avocado value.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, dpi=120)

    indices = np.arange(game.num_centers)
    bar_width = 0.35

    # Colors for centers
    bar_colors = []
    for i in range(game.num_centers):
        if game.mode == "duel":
            p_id = game.players[i]
            bar_colors.append(DUEL_COLORS[p_id]["fill"])
        else:
            bar_colors.append(FIRM_COLORS[i % len(FIRM_COLORS)]["fill"])

    rects1 = ax.bar(indices - bar_width/2, game.volume_shares, bar_width, label="Volume Share (%) [Avocados]", color=bar_colors, alpha=0.9, edgecolor="#0F172A", linewidth=0.8)
    rects2 = ax.bar(indices + bar_width/2, game.area_shares, bar_width, label="Area Share (%) [Land]", color="#94A3B8", alpha=0.5, hatch="//", edgecolor="#475569", linewidth=0.8)

    ax.set_ylabel("Market Share (%)", fontsize=10, fontweight="semibold")
    ax.set_title("Market Catchment Comparison: Captured Volume vs Physical Area", fontsize=11, fontweight="bold", pad=8)
    ax.set_xticks(indices)
    ax.set_xticklabels([f"C{i+1} (P{game.players[i]})" for i in range(game.num_centers)], fontsize=9, fontweight="semibold")
    ax.set_ylim(0, max(np.max(game.volume_shares), np.max(game.area_shares)) * 1.25)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=9)

    # Value annotations on top of bars
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=7.5, fontweight="bold")

    return ax


# ==============================================================================
# 3. 3D Surface & Voronoi Prism Plot
# ==============================================================================

def plot_voronoi_surface_3d(
    game: VoronoiGame,
    resolution: int = 60,
    figsize: Tuple[int, int] = (9, 7)
) -> plt.Figure:
    """
    3D perspective plot showing the avocado density function f(x, y)
    with Voronoi cell boundaries projected on the surface.
    """
    fig = plt.figure(figsize=figsize, dpi=120)
    ax = fig.add_subplot(111, projection="3d")

    x = np.linspace(0, 1, resolution)
    y = np.linspace(0, 1, resolution)
    X, Y = np.meshgrid(x, y)
    Z = avocado_density(X, Y)

    # Plot 3D surface
    surf = ax.plot_surface(X, Y, Z, cmap=AVOCADO_CMAP, alpha=0.75, edgecolor="none", rstride=2, cstride=2)

    # Project Voronoi cell boundaries onto 3D surface
    for i, cell in enumerate(game.cells):
        if cell.is_empty:
            continue
        verts = get_polygon_vertices(cell)
        # Close loop
        verts_closed = np.vstack([verts, verts[0]])
        zv = avocado_density(verts_closed[:, 0], verts_closed[:, 1])

        p_id = game.players[i]
        edge_col = DUEL_COLORS[p_id]["edge"] if game.mode == "duel" else FIRM_COLORS[i % len(FIRM_COLORS)]["edge"]

        # 3D line on surface
        ax.plot(verts_closed[:, 0], verts_closed[:, 1], zv + 0.002, color=edge_col, linewidth=2.0)
        # Baseline footprint on floor z = 0
        ax.plot(verts_closed[:, 0], verts_closed[:, 1], np.zeros_like(zv), color="#94A3B8", linestyle=":", linewidth=1.0)

        # Plot site marker in 3D
        cx, cy = game.centers[i]
        cz = avocado_density(cx, cy)
        ax.scatter([cx], [cy], [cz + 0.005], s=70, color=edge_col, edgecolor="#FFFFFF", linewidth=1.2)
        ax.text(cx, cy, cz + 0.015, f"C{i+1}", fontsize=8, fontweight="bold")

    ax.set_xlabel("X (Market 1)", fontsize=9, labelpad=6)
    ax.set_ylabel("Y (Market 2)", fontsize=9, labelpad=6)
    ax.set_zlabel("Density f(x, y)", fontsize=9, labelpad=6)
    ax.set_title("3D Avocado Density Surface & Voronoi Cell Partitions", fontsize=11, fontweight="bold", pad=12)
    ax.view_init(elev=34, azim=-55)

    return fig


# ==============================================================================
# 4. Comprehensive Dashboard View
# ==============================================================================

def plot_dashboard(
    game: VoronoiGame,
    show_delaunay: bool = False,
    figsize: Tuple[int, int] = (15, 6)
) -> plt.Figure:
    """
    Combined 2-panel dashboard:
    Left: 2D Strategic Market Map with density contours & cells.
    Right: Market Share & Density Scoreboard.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, dpi=120, gridspec_kw={"width_ratios": [1.1, 1.0]})
    plot_voronoi_game_2d(game, show_delaunay=show_delaunay, ax=ax1)
    plot_scoreboard_barchart(game, ax=ax2)
    plt.tight_layout()
    return fig


# ==============================================================================
# 5. Interactive Widget Dashboard (ipywidgets)
# ==============================================================================

def create_interactive_voronoi_widget(initial_preset: str = "duel_balanced"):
    """
    Create an interactive ipywidgets control panel for student experimentation.
    Allows real-time slider manipulation of all 6 centers, preset loading,
    Delaunay dual toggling, and instant AI opponent moves.
    """
    import ipywidgets as widgets
    from IPython.display import display, clear_output

    game = VoronoiGame()
    if initial_preset in PRESETS:
        game.load_preset(initial_preset)

    # 1. Preset dropdown
    preset_dropdown = widgets.Dropdown(
        options=[(v["name"], k) for k, v in PRESETS.items()],
        value=initial_preset,
        description="Scenario:",
        style={"description_width": "initial"},
        layout=widgets.Layout(width="280px")
    )

    # 2. Mode selector
    mode_toggle = widgets.RadioButtons(
        options=[("1v1 Duel (3 vs 3)", "duel"), ("6 Firms (Free-for-All)", "free_for_all")],
        value=game.mode,
        description="Mode:",
        style={"description_width": "initial"},
        layout=widgets.Layout(width="280px")
    )

    # 3. Checkbox toggles
    delaunay_check = widgets.Checkbox(value=False, description="Show Delaunay Dual", indent=False)
    density_check = widgets.Checkbox(value=True, description="Show Density Contours", indent=False)

    # 4. Sliders for each of the 6 centers
    sliders_x = []
    sliders_y = []
    for i in range(6):
        sx = widgets.FloatSlider(
            value=float(game.centers[i, 0]), min=0.01, max=0.99, step=0.01,
            description=f"C{i+1} x:",
            continuous_update=False,
            style={"description_width": "45px"},
            layout=widgets.Layout(width="180px")
        )
        sy = widgets.FloatSlider(
            value=float(game.centers[i, 1]), min=0.01, max=0.99, step=0.01,
            description=f"y:",
            continuous_update=False,
            style={"description_width": "20px"},
            layout=widgets.Layout(width="150px")
        )
        sliders_x.append(sx)
        sliders_y.append(sy)

    # 5. Action Buttons
    ai_btn = widgets.Button(
        description="AI Move: Greedy Volume",
        button_style="info",
        icon="bolt",
        layout=widgets.Layout(width="200px")
    )

    output_area = widgets.Output()

    def update_view(*args):
        with output_area:
            clear_output(wait=True)
            # Read current sliders into centers array
            new_pts = np.array([[sliders_x[i].value, sliders_y[i].value] for i in range(6)])
            game.mode = mode_toggle.value
            game.set_centers(new_pts)
            fig = plot_dashboard(game, show_delaunay=delaunay_check.value)
            plt.show()

    def on_preset_change(change):
        pkey = change["new"]
        if pkey in PRESETS:
            cfg = PRESETS[pkey]
            for i in range(6):
                sliders_x[i].value = float(cfg["centers"][i, 0])
                sliders_y[i].value = float(cfg["centers"][i, 1])
            update_view()

    def on_ai_click(b):
        # AI replaces Center 6 with the optimal greedy volume coordinate
        best_coord = StrategicAI.best_move_greedy_volume(game.centers[:5])
        sliders_x[5].value = round(best_coord[0], 2)
        sliders_y[5].value = round(best_coord[1], 2)
        update_view()

    preset_dropdown.observe(on_preset_change, names="value")
    mode_toggle.observe(update_view, names="value")
    delaunay_check.observe(update_view, names="value")
    density_check.observe(update_view, names="value")
    ai_btn.on_click(on_ai_click)

    for i in range(6):
        sliders_x[i].observe(update_view, names="value")
        sliders_y[i].observe(update_view, names="value")

    # Layout assembling
    row1 = widgets.HBox([preset_dropdown, mode_toggle, widgets.VBox([delaunay_check, density_check]), ai_btn])
    p1_sliders = widgets.VBox([widgets.HTML("<b>Player 1 Centers (Blue):</b>")] + [widgets.HBox([sliders_x[i], sliders_y[i]]) for i in range(3)])
    p2_sliders = widgets.VBox([widgets.HTML("<b>Player 2 Centers (Orange):</b>")] + [widgets.HBox([sliders_x[i], sliders_y[i]]) for i in range(3, 6)])
    slider_box = widgets.HBox([p1_sliders, p2_sliders], layout=widgets.Layout(margin="10px 0 10px 0"))

    ui = widgets.VBox([row1, slider_box, output_area])
    update_view()
    return ui


# ==============================================================================
# 6. Universal HTML Game Display & Browser Launcher (VS Code, JupyterLab, Colab, Binder)
# ==============================================================================

def launch_game_in_browser(filename: str = "voronoi_volume_game.html") -> str:
    """
    Open the standalone HTML5 Voronoi Volume Game directly in the user's default web browser.
    Guarantees 60-FPS canvas rendering, bypasses all Jupyter/VS Code iframe restrictions,
    and allows direct clipboard coordinate copying back into Python.
    """
    import os
    import webbrowser

    candidate_paths = [
        filename,
        os.path.join("voronoi-game", filename),
        os.path.join("..", "voronoi-game", filename),
        os.path.join(os.path.dirname(__file__), filename)
    ]
    file_path = None
    for cp in candidate_paths:
        if os.path.exists(cp):
            file_path = os.path.abspath(cp)
            break
            
    if file_path is None:
        raise FileNotFoundError(f"Could not locate '{filename}' in search paths: {candidate_paths}")

    file_url = f"file:///{file_path.replace(os.sep, '/')}"
    webbrowser.open_new_tab(file_url)
    print(f"🚀 Opened game in web browser: {file_url}")
    return file_url


def display_html_game(filename: str = "voronoi_volume_game.html", width: str = "100%", height: int = 860) -> None:
    """
    Display the standalone HTML5 Voronoi Volume Game inside any notebook environment
    (VS Code Notebook Editor, JupyterLab, Classic Notebook, Google Colab, or MyBinder).
    
    Includes a direct browser launch button and uses an in-memory srcdoc iframe to bypass
    local file path / webview CORS restrictions.
    """
    import html
    import os
    from IPython.display import HTML, display

    # Resolve file path across different working directories
    candidate_paths = [
        filename,
        os.path.join("voronoi-game", filename),
        os.path.join("..", "voronoi-game", filename),
        os.path.join(os.path.dirname(__file__), filename)
    ]
    
    file_path = None
    for cp in candidate_paths:
        if os.path.exists(cp):
            file_path = os.path.abspath(cp)
            break
            
    if file_path is None:
        raise FileNotFoundError(f"Could not locate '{filename}' in search paths: {candidate_paths}")

    with open(file_path, "r", encoding="utf-8") as f:
        raw_html = f.read()

    file_url = f"file:///{file_path.replace(os.sep, '/')}"
    escaped_html = html.escape(raw_html)

    banner_markup = f'''
<div style="display: flex; align-items: center; justify-content: space-between; background: #1E293B; border: 1px solid #334155; border-radius: 10px; padding: 12px 18px; margin-bottom: 12px; font-family: 'Segoe UI', system-ui, sans-serif;">
    <div>
        <div style="font-weight: 700; color: #F8FAFC; font-size: 14px; display: flex; align-items: center; gap: 8px;">
            <span>🥑</span> 3D Voronoi Volume Game (HTML5 Interactive Canvas)
        </div>
        <div style="font-size: 12px; color: #94A3B8; margin-top: 3px;">
            Click on canvas below to place seeds, or open in a dedicated browser tab for full 60-FPS rendering.
        </div>
    </div>
    <a href="{file_url}" target="_blank" 
       style="display: inline-flex; align-items: center; gap: 6px; background: #22C55E; color: #0F172A; font-weight: 700; font-size: 13px; padding: 8px 16px; border-radius: 8px; text-decoration: none; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.3); white-space: nowrap;">
       🚀 Open in Full Browser Window
    </a>
</div>
'''

    iframe_markup = (
        f'<iframe srcdoc="{escaped_html}" width="{width}" height="{height}" '
        f'style="border: 1px solid #334155; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3); background: #0F172A;" '
        f'sandbox="allow-scripts allow-popups"></iframe>'
    )
    display(HTML(banner_markup + iframe_markup))
