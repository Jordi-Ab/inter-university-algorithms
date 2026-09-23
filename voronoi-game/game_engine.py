"""
game_engine.py
==============
Game rules, scoring mechanisms, AI opponents, and economic metrics
for the Six-Center Voronoi Volume Game in the unit square [0, 1]^2.
"""

from typing import List, Dict, Tuple, Optional, Any, Union
import numpy as np
from shapely.geometry import Polygon

try:
    from .voronoi_geometry import compute_bounded_voronoi, summarize_cell_geometry, validate_centers
    from .numerical_integration import (
        avocado_density,
        compute_cell_volumes,
        UNIT_SQUARE_TRUE_VOLUME
    )
except (ImportError, ValueError):
    from voronoi_geometry import compute_bounded_voronoi, summarize_cell_geometry, validate_centers
    from numerical_integration import (
        avocado_density,
        compute_cell_volumes,
        UNIT_SQUARE_TRUE_VOLUME
    )


# ==============================================================================
# 1. Preset Game Configurations
# ==============================================================================

PRESETS: Dict[str, Dict[str, Any]] = {
    "duel_balanced": {
        "name": "Duel: Strategic Balanced",
        "description": "3 centers for Player 1 (Blue) vs 3 centers for Player 2 (Orange) in symmetric competition.",
        "centers": np.array([
            [0.20, 0.25], [0.35, 0.70], [0.80, 0.20],  # Player 1
            [0.25, 0.80], [0.70, 0.75], [0.65, 0.30]   # Player 2
        ]),
        "players": [1, 1, 1, 2, 2, 2]
    },
    "gold_rush": {
        "name": "The Gold Rush (Origin Battle)",
        "description": "Intense competition near the origin (0, 0) where avocado density is highest vs outer territory.",
        "centers": np.array([
            [0.10, 0.12], [0.15, 0.35], [0.38, 0.15],
            [0.45, 0.55], [0.80, 0.30], [0.75, 0.85]
        ]),
        "players": [1, 2, 1, 2, 1, 2]
    },
    "hexagonal_pack": {
        "name": "Hexagonal Market Packing",
        "description": "Evenly distributed spatial market partition (classic Lösch/Christaller central place theory).",
        "centers": np.array([
            [0.25, 0.25], [0.75, 0.25], [0.50, 0.50],
            [0.25, 0.75], [0.75, 0.75], [0.50, 0.90]
        ]),
        "players": [1, 2, 3, 4, 5, 6]
    },
    "hotelling_axis": {
        "name": "Hotelling Diagonal Clustering",
        "description": "Firms clustered along the symmetry axis y = x, competing directly for market indifference boundaries.",
        "centers": np.array([
            [0.15, 0.15], [0.25, 0.30], [0.45, 0.45],
            [0.60, 0.55], [0.75, 0.80], [0.85, 0.85]
        ]),
        "players": [1, 1, 1, 2, 2, 2]
    },
    "perimeter_defense": {
        "name": "Perimeter Fortress vs Center",
        "description": "Firms occupying outer boundaries surrounding an inner central hub.",
        "centers": np.array([
            [0.10, 0.10], [0.90, 0.10], [0.50, 0.50],
            [0.10, 0.90], [0.90, 0.90], [0.50, 0.15]
        ]),
        "players": [1, 2, 3, 4, 5, 6]
    }
}


# ==============================================================================
# 2. Game Engine Class
# ==============================================================================

class VoronoiGame:
    """
    Main state machine and scoring engine for the 6-Center Voronoi Volume Game.
    """

    def __init__(
        self,
        centers: Optional[np.ndarray] = None,
        players: Optional[List[int]] = None,
        mode: str = "duel"
    ):
        """
        Initialize the Voronoi game.

        Parameters
        ----------
        centers : Optional[np.ndarray]
            Array of shape (6, 2). If None, initializes with default balanced duel.
        players : Optional[List[int]]
            Player index for each center (1-indexed). Defaults to [1, 1, 1, 2, 2, 2] for duel.
        mode : str
            Game mode: "duel" (Player 1 vs 2, 3 centers each) or "free_for_all" (6 firms).
        """
        self.mode = mode
        if centers is None:
            default_cfg = PRESETS["duel_balanced"]
            self.centers = default_cfg["centers"].copy()
            self.players = default_cfg["players"].copy()
        else:
            self.centers = validate_centers(centers)
            if players is not None:
                self.players = list(players)
            else:
                self.players = [1, 1, 1, 2, 2, 2] if mode == "duel" else [1, 2, 3, 4, 5, 6]

        self.num_centers = len(self.centers)
        self.cells: List[Polygon] = []
        self.areas = np.zeros(self.num_centers)
        self.volumes = np.zeros(self.num_centers)
        self.area_shares = np.zeros(self.num_centers)
        self.volume_shares = np.zeros(self.num_centers)
        self.value_densities = np.zeros(self.num_centers)
        self.player_scores: Dict[int, Dict[str, float]] = {}
        self.entropy: float = 0.0
        self.gini: float = 0.0

        self.recompute()

    def set_centers(self, centers: np.ndarray, players: Optional[List[int]] = None) -> None:
        """Update center positions and recalculate the board."""
        self.centers = validate_centers(centers)
        if players is not None:
            self.players = list(players)
        self.num_centers = len(self.centers)
        self.recompute()

    def update_center(self, index: int, new_coord: Tuple[float, float]) -> None:
        """Update a single center's coordinate (0-indexed)."""
        x, y = new_coord
        if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
            raise ValueError(f"Coordinates ({x}, {y}) must be in [0, 1]^2.")
        self.centers[index] = [x, y]
        self.centers = validate_centers(self.centers)
        self.recompute()

    def load_preset(self, preset_key: str) -> None:
        """Load a predefined strategic scenario."""
        if preset_key not in PRESETS:
            raise KeyError(f"Unknown preset '{preset_key}'. Choose from: {list(PRESETS.keys())}")
        cfg = PRESETS[preset_key]
        self.centers = cfg["centers"].copy()
        self.players = cfg["players"].copy()
        self.recompute()

    def recompute(self) -> None:
        """
        Recompute Voronoi tessellation, cell areas, integral volumes,
        market shares, and economic welfare metrics.
        """
        self.cells = compute_bounded_voronoi(self.centers)
        self.areas = np.array([float(c.area) for c in self.cells])
        self.volumes = compute_cell_volumes(self.cells, func=avocado_density, order=7)

        total_area = max(1e-12, float(np.sum(self.areas)))
        total_vol = max(1e-12, float(np.sum(self.volumes)))

        self.area_shares = (self.areas / total_area) * 100.0
        self.volume_shares = (self.volumes / total_vol) * 100.0

        # Density yield (avocado volume per unit of physical area)
        with np.errstate(divide="ignore", invalid="ignore"):
            self.value_densities = np.where(self.areas > 1e-12, self.volumes / self.areas, 0.0)

        # Shannon Entropy of Volume Distribution (Kumar & Kumaran 2005)
        # H = -sum p_i * log(p_i)
        p = self.volumes / total_vol
        p = p[p > 1e-14]
        self.entropy = float(-np.sum(p * np.log(p)))

        # Gini Coefficient of Volume Inequality
        v_sorted = np.sort(self.volumes)
        n = len(v_sorted)
        index_arr = np.arange(1, n + 1)
        self.gini = float((2.0 * np.sum(index_arr * v_sorted) - (n + 1) * np.sum(v_sorted)) / (n * np.sum(v_sorted)))

        # Player-aggregated scores
        self.player_scores = {}
        unique_players = sorted(list(set(self.players)))
        for p_id in unique_players:
            idx = [i for i, pl in enumerate(self.players) if pl == p_id]
            p_area = float(np.sum(self.areas[idx]))
            p_vol = float(np.sum(self.volumes[idx]))
            self.player_scores[p_id] = {
                "total_area": p_area,
                "area_share_pct": (p_area / total_area) * 100.0,
                "total_volume": p_vol,
                "volume_share_pct": (p_vol / total_vol) * 100.0,
                "num_centers": len(idx),
                "center_indices": idx
            }

    def get_summary_table(self) -> List[Dict[str, Any]]:
        """
        Return a tabular breakdown of center performance.
        """
        table = []
        for i in range(self.num_centers):
            table.append({
                "Center": i + 1,
                "Player": self.players[i],
                "X": float(self.centers[i, 0]),
                "Y": float(self.centers[i, 1]),
                "Area": float(self.areas[i]),
                "Area Share (%)": float(self.area_shares[i]),
                "Volume": float(self.volumes[i]),
                "Volume Share (%)": float(self.volume_shares[i]),
                "Density (Vol/Area)": float(self.value_densities[i])
            })
        return table

    def get_winner(self) -> Tuple[int, str]:
        """
        Determine the winner based on captured volume.
        
        Returns
        -------
        Tuple[int, str]
            (Winning Player ID, Description message)
        """
        if not self.player_scores:
            return 1, "No scores available."

        best_player = max(self.player_scores.keys(), key=lambda p: self.player_scores[p]["total_volume"])
        best_vol_pct = self.player_scores[best_player]["volume_share_pct"]
        best_area_pct = self.player_scores[best_player]["area_share_pct"]

        if self.mode == "duel":
            other_player = 2 if best_player == 1 else 1
            other_vol_pct = self.player_scores[other_player]["volume_share_pct"]
            margin = best_vol_pct - other_vol_pct
            msg = f"Player {best_player} wins with {best_vol_pct:.2f}% volume (lead of {margin:+.2f}%) [Area: {best_area_pct:.1f}%]!"
        else:
            msg = f"Firm {best_player} leads market with {best_vol_pct:.2f}% volume share!"

        return best_player, msg


# ==============================================================================
# 3. Autonomous Strategic AI Agents
# ==============================================================================

class StrategicAI:
    """
    AI opponent solver for the Voronoi Game.
    Can place a new center or optimize an existing center to maximize volume or area.
    """

    @staticmethod
    def best_move_greedy_volume(
        existing_centers: np.ndarray,
        grid_resolution: int = 40,
        bbox: Tuple[float, float, float, float] = (0.05, 0.95, 0.05, 0.95)
    ) -> Tuple[float, float]:
        """
        Search for the optimal coordinate (x*, y*) that captures the maximum
        incremental volume when added to the current board.
        """
        xmin, xmax, ymin, ymax = bbox
        gx = np.linspace(xmin, xmax, grid_resolution)
        gy = np.linspace(ymin, ymax, grid_resolution)

        best_coord = (0.5, 0.5)
        best_vol = -1.0

        for x in gx:
            for y in gy:
                cand = np.array([x, y])
                # Skip if too close to an existing site
                if np.min(np.linalg.norm(existing_centers - cand, axis=1)) < 0.03:
                    continue

                test_centers = np.vstack([existing_centers, cand])
                cells = compute_bounded_voronoi(test_centers)
                new_cell = cells[-1]
                from numerical_integration import integrate_polygon
                vol = integrate_polygon(new_cell, func=avocado_density, order=5)

                if vol > best_vol:
                    best_vol = vol
                    best_coord = (float(x), float(y))

        return best_coord

    @staticmethod
    def best_move_greedy_area(
        existing_centers: np.ndarray,
        grid_resolution: int = 40,
        bbox: Tuple[float, float, float, float] = (0.05, 0.95, 0.05, 0.95)
    ) -> Tuple[float, float]:
        """
        Search for the coordinate that captures maximum physical land area (Hotelling competition).
        """
        xmin, xmax, ymin, ymax = bbox
        gx = np.linspace(xmin, xmax, grid_resolution)
        gy = np.linspace(ymin, ymax, grid_resolution)

        best_coord = (0.5, 0.5)
        best_area = -1.0

        for x in gx:
            for y in gy:
                cand = np.array([x, y])
                if np.min(np.linalg.norm(existing_centers - cand, axis=1)) < 0.03:
                    continue

                test_centers = np.vstack([existing_centers, cand])
                cells = compute_bounded_voronoi(test_centers)
                area = cells[-1].area

                if area > best_area:
                    best_area = area
                    best_coord = (float(x), float(y))

        return best_coord

    @staticmethod
    def best_move_centroid(game: VoronoiGame) -> Tuple[float, float]:
        """
        Lloyd centroid relaxation move: locates the cell with highest volume/area
        and targets its centroid.
        """
        if not game.cells:
            return (0.5, 0.5)
        largest_idx = int(np.argmax(game.volumes))
        c = game.cells[largest_idx].centroid
        return (float(c.x), float(c.y))
