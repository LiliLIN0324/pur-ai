# Data Preprocessing Utilities

This folder contains preprocessing helpers extracted from `preprocessing.ipynb` for easier reuse.

Files:
- `preproc_utils.py`: functions for exporting aligned bounding rectangle, generating aligned grids, clipping grids to polygons, and geometry fixes.

Usage example:
```python
from preprocessing.preproc_utils import generate_aligned_grid, export_bounding_rectangle

export_bounding_rectangle("path/to/input.shp", "path/to/output_rect.shp", grid_size=256)
generate_aligned_grid("path/to/output_rect.shp", "path/to/grid_256.shp", grid_size=256)
```

Notes:
- The functions convert inputs to EPSG:32651 by default; change `target_epsg` if needed.
- Ensure dependencies are installed (`geopandas`, `shapely`, `numpy`).
