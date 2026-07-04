"""Minimal remote-sensing helpers for flood impact extraction.

This file is intentionally dependency-light. It demonstrates the thesis logic:
- Optical water index: NDWI = (Green - NIR) / (Green + NIR)
- SAR change proxy: pre-flood backscatter - during-flood backscatter

In production, connect these functions to rasterio/xarray/Google Earth Engine and
write outputs to GeoTIFF or Cloud Optimized GeoTIFF.
"""

from __future__ import annotations

import numpy as np


def ndwi(green: np.ndarray, nir: np.ndarray, eps: float = 1e-9) -> np.ndarray:
    """Compute Normalized Difference Water Index."""
    green = np.asarray(green, dtype=float)
    nir = np.asarray(nir, dtype=float)
    return (green - nir) / (green + nir + eps)


def water_mask_from_ndwi(green: np.ndarray, nir: np.ndarray, threshold: float = 0.15) -> np.ndarray:
    """Return binary water mask from green/NIR bands."""
    return ndwi(green, nir) >= threshold


def sar_flood_change(pre_event: np.ndarray, event: np.ndarray, threshold: float = 1.5) -> np.ndarray:
    """Detect likely new floodwater using a simple SAR backscatter drop proxy.

    Parameters are generic demo defaults. Calibrate thresholds for real sensors,
    incidence angles, land cover, and preprocessing choices.
    """
    pre_event = np.asarray(pre_event, dtype=float)
    event = np.asarray(event, dtype=float)
    delta = pre_event - event
    return delta >= threshold


def flood_fraction(mask: np.ndarray) -> float:
    """Calculate flooded fraction in a binary mask."""
    arr = np.asarray(mask, dtype=bool)
    if arr.size == 0:
        raise ValueError("mask cannot be empty")
    return float(arr.mean())
