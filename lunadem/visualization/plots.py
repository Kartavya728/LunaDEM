"""Plotting utilities for DEM visual outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lunadem.branding import add_matplotlib_credit


def plot_depth_map(dem: np.ndarray, save_path: str | Path) -> str:
    """Generate and save 2D terrain map."""
    out = Path(save_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 8))
    image = ax.imshow(dem, cmap="terrain")
    ax.set_title("Reconstructed DEM")
    ax.set_xlabel("X (pixels)")
    ax.set_ylabel("Y (pixels)")
    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label("Height (m)")
    add_matplotlib_credit(fig)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return str(out)


def plot_3d_surface(dem: np.ndarray, save_path: str | Path) -> str:
    """Generate and save 3D surface rendering."""
    out = Path(save_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    height, width = dem.shape
    x, y = np.meshgrid(np.arange(width), np.arange(height))
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")

    stride = max(1, int(min(height, width) / 200))
    surf = ax.plot_surface(
        x,
        y,
        dem,
        cmap="terrain",
        rstride=stride,
        cstride=stride,
        linewidth=0,
        antialiased=False,
    )
    ax.set_title("Reconstructed 3D Surface")
    ax.set_xlabel("X (pixels)")
    ax.set_ylabel("Y (pixels)")
    ax.set_zlabel("Height (m)")
    ax.set_box_aspect((width, height, max(1.0, 0.2 * max(width, height))))
    fig.colorbar(surf, shrink=0.6, aspect=10, label="Height (m)")
    add_matplotlib_credit(fig)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return str(out)
