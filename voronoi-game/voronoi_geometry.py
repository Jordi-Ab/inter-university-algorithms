"""
voronoi_geometry.py
===================
Computational geometry utilities for the Voronoi Volume Game.
Handles bounded Voronoi diagram generation, clipping to the unit square [0, 1]^2,
Delaunay triangulation dual graphs, and polygon geometric attributes.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from scipy.spatial import Delaunay
from shapely.geometry import Polygon, box, LineString


def validate_centers(
    centers: np.ndarray,
    bbox: Tuple[float, float, float, float] = (0.0, 1.0, 0.0, 1.0),
    min_dist: float = 1e-4
) -> np.ndarray:
    """
    Validate that centers are within the specified bounding box and non-degenerate.

    Parameters
    ----------
    centers : np.ndarray
        Array of shape (N, 2) representing site coordinates.
    bbox : Tuple[float, float, float, float]
        (xmin, xmax, ymin, ymax) of the domain.
    min_dist : float
        Minimum allowable Euclidean distance between any two distinct centers.

    Returns
    -------
    np.ndarray
        Validated floating-point array of shape (N, 2).
    """
    pts = np.asarray(centers, dtype=float)
    if pts.ndim != 2 or pts.shape[1] != 2:
        raise ValueError(f"Centers must have shape (N, 2), got {pts.shape}")
    
    xmin, xmax, ymin, ymax = bbox
    for i, (x, y) in enumerate(pts):
        if not (xmin <= x <= xmax and ymin <= y <= ymax):
            raise ValueError(
                f"Center {i+1} at ({x:.4f}, {y:.4f}) is outside bounding box [{xmin}, {xmax}] x [{ymin}, {ymax}]."
            )
            
    n = len(pts)
    for i in range(n):
        for j in range(i + 1, n):
            d = np.linalg.norm(pts[i] - pts[j])
            if d < min_dist:
                raise ValueError(
                    f"Centers {i+1} and {j+1} are too close (distance {d:.2e} < {min_dist})."
                )
                
    return pts


def compute_bounded_voronoi(
    centers: np.ndarray,
    bbox: Tuple[float, float, float, float] = (0.0, 1.0, 0.0, 1.0)
) -> List[Polygon]:
    """
    Compute bounded Voronoi cells for points inside a rectangular domain.
    
    Each cell is constructed deterministically by intersecting the bounding box
    with the halfplanes formed by the perpendicular bisectors to all other sites:
        H_{i,j} = { x in R^2 : ||x - P_i|| <= ||x - P_j|| }
        
    This approach is unconditionally robust, handles arbitrary configurations,
    boundary points, and produces exact polygon cells.

    Parameters
    ----------
    centers : np.ndarray
        Array of shape (N, 2) containing site coordinates.
    bbox : Tuple[float, float, float, float]
        (xmin, xmax, ymin, ymax) defining the bounding rectangle. Default is [0, 1]^2.

    Returns
    -------
    List[Polygon]
        List of shapely Polygon objects, one for each input site in the same order.
    """
    pts = validate_centers(centers, bbox=bbox)
    xmin, xmax, ymin, ymax = bbox
    domain_poly = box(xmin, ymin, xmax, ymax)
    diag = np.sqrt((xmax - xmin)**2 + (ymax - ymin)**2)
    big_m = 50.0 * max(1.0, diag)

    cells: List[Polygon] = []
    n_pts = len(pts)

    for i in range(n_pts):
        p = pts[i]
        cell_poly = domain_poly
        
        for j in range(n_pts):
            if i == j:
                continue
            q = pts[j]
            
            # Midpoint and normal pointing from q toward p
            mid = (p + q) / 2.0
            normal = p - q
            norm_len = np.linalg.norm(normal)
            if norm_len < 1e-14:
                continue
            normal_unit = normal / norm_len
            tangent_unit = np.array([-normal_unit[1], normal_unit[0]])

            # Construct half-plane polygon containing p
            hp_poly = Polygon([
                mid - big_m * tangent_unit,
                mid + big_m * tangent_unit,
                mid + big_m * tangent_unit + big_m * normal_unit,
                mid - big_m * tangent_unit + big_m * normal_unit
            ])

            cell_poly = cell_poly.intersection(hp_poly)

        cells.append(cell_poly)

    return cells


def compute_delaunay_edges(centers: np.ndarray) -> List[Tuple[int, int]]:
    """
    Compute unique edges of the Delaunay triangulation dual graph for the centers.

    Parameters
    ----------
    centers : np.ndarray
        Array of shape (N, 2).

    Returns
    -------
    List[Tuple[int, int]]
        List of unique index pairs (i, j) with i < j representing Delaunay edges.
    """
    pts = np.asarray(centers, dtype=float)
    if len(pts) < 3:
        if len(pts) == 2:
            return [(0, 1)]
        return []

    try:
        tri = Delaunay(pts)
        edges = set()
        for simplex in tri.simplices:
            for i in range(3):
                u, v = int(simplex[i]), int(simplex[(i + 1) % 3])
                if u > v:
                    u, v = v, u
                edges.add((u, v))
        return sorted(list(edges))
    except Exception:
        # Fallback if points are strictly collinear
        return []


def get_polygon_vertices(poly: Polygon) -> np.ndarray:
    """
    Extract counter-clockwise exterior vertices of a shapely Polygon.

    Parameters
    ----------
    poly : Polygon
        Shapely polygon.

    Returns
    -------
    np.ndarray
        Array of shape (K, 2) containing vertices without repeating the closing vertex.
    """
    if poly.is_empty:
        return np.empty((0, 2))
    coords = np.array(poly.exterior.coords)
    if len(coords) > 1 and np.allclose(coords[0], coords[-1]):
        coords = coords[:-1]
    return coords


def summarize_cell_geometry(cell: Polygon) -> Dict[str, Any]:
    """
    Compute geometric summary dictionary for a Voronoi cell.

    Returns
    -------
    Dict containing area, perimeter, centroid (cx, cy), vertices count, and bounds.
    """
    if cell.is_empty:
        return {
            "area": 0.0,
            "perimeter": 0.0,
            "centroid": (np.nan, np.nan),
            "num_vertices": 0,
            "bounds": (0.0, 0.0, 0.0, 0.0)
        }
    return {
        "area": float(cell.area),
        "perimeter": float(cell.length),
        "centroid": (float(cell.centroid.x), float(cell.centroid.y)),
        "num_vertices": len(get_polygon_vertices(cell)),
        "bounds": tuple(float(b) for b in cell.bounds)
    }
