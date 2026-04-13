"""Production shape-from-shading implementation."""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
from scipy.ndimage import gaussian_filter, laplace, median_filter, zoom
from scipy.optimize import OptimizeResult, minimize

from lunadem.core.config import ReconstructionConfig
from lunadem.geometry.lighting import get_light_vector
from lunadem.geometry.surface import calculate_predicted_image
from lunadem.methods.base import MethodResult, ReconstructionMethod
from lunadem.utils.arrays import normalize_to_unit_range


def _prepare_observation(
    image: np.ndarray,
    config: ReconstructionConfig,
) -> Tuple[np.ndarray, np.ndarray, float]:
    observed = image.astype(np.float32)
    if config.preprocessing.normalize:
        observed = normalize_to_unit_range(observed)
    if config.preprocessing.gaussian_sigma > 0:
        observed = gaussian_filter(observed, sigma=config.preprocessing.gaussian_sigma)
    if config.preprocessing.median_size > 0:
        observed = median_filter(observed, size=config.preprocessing.median_size)

    shadow_threshold = (
        config.preprocessing.shadow_threshold
        if config.preprocessing.shadow_threshold is not None
        else float(np.percentile(observed, 5.0))
    )
    if config.preprocessing.shadow_mask:
        mask = (observed >= shadow_threshold).astype(np.float32)
    else:
        mask = np.ones_like(observed, dtype=np.float32)
    return observed, mask, shadow_threshold


def _resize_surface(surface: np.ndarray, target_shape: Tuple[int, int]) -> np.ndarray:
    y_scale = target_shape[0] / surface.shape[0]
    x_scale = target_shape[1] / surface.shape[1]
    return zoom(surface, zoom=(y_scale, x_scale), order=1).astype(np.float32)


def _prepare_working_surface(
    image: np.ndarray,
    config: ReconstructionConfig,
) -> tuple[np.ndarray, float]:
    max_long_side = int(config.sfs.max_long_side_px)
    long_side = max(image.shape)
    if long_side <= max_long_side:
        return image.astype(np.float32), 1.0

    scale = max_long_side / float(long_side)
    target_shape = (
        max(int(round(image.shape[0] * scale)), 1),
        max(int(round(image.shape[1] * scale)), 1),
    )
    return _resize_surface(image.astype(np.float32), target_shape), scale


def sfs_cost_and_gradient(
    z_flat: np.ndarray,
    observed_image: np.ndarray,
    light_vec: np.ndarray,
    lambda_reg: float,
    shape: Tuple[int, int],
    valid_mask: np.ndarray,
) -> Tuple[float, np.ndarray]:
    """Compute SFS objective and gradient for L-BFGS-B."""
    z = z_flat.reshape(shape).astype(np.float32)

    predicted = calculate_predicted_image(z, light_vec).astype(np.float32)
    brightness_error = (observed_image - predicted) * valid_mask
    brightness_cost = 0.5 * float(np.sum(brightness_error**2))

    laplacian_z = laplace(z, mode="nearest")
    smoothness_cost = 0.5 * float(np.sum(laplacian_z**2))
    total_cost = brightness_cost + lambda_reg * smoothness_cost

    p, q = np.gradient(z)
    denom = np.power(1.0 + p**2 + q**2, 1.5)
    denom = np.maximum(denom, 1e-9)

    term_p = light_vec[0] - light_vec[2] * p
    term_q = light_vec[1] - light_vec[2] * q

    d_e_dp = brightness_error * (term_p / denom)
    d_e_dq = brightness_error * (term_q / denom)
    _, d_dx = np.gradient(d_e_dp)
    d_dy, _ = np.gradient(d_e_dq)
    brightness_gradient = -(d_dx + d_dy)

    smoothness_gradient = laplace(laplacian_z, mode="nearest")
    total_gradient = brightness_gradient + lambda_reg * smoothness_gradient

    return total_cost, total_gradient.ravel().astype(np.float64)


def run_sfs_optimization(
    image: np.ndarray,
    config: ReconstructionConfig,
    initial_dem: np.ndarray | None = None,
) -> Tuple[np.ndarray, Dict[str, float | str | bool]]:
    """Run single-scale SFS optimization."""
    if image.ndim != 2:
        raise ValueError("SFS expects a single-channel image.")

    observed, valid_mask, threshold = _prepare_observation(image, config)
    light_vec = get_light_vector(
        config.illumination.sun_azimuth_deg,
        config.illumination.sun_elevation_deg,
    )

    if initial_dem is None:
        z0 = np.zeros_like(observed, dtype=np.float64)
    else:
        if initial_dem.shape != observed.shape:
            raise ValueError("initial_dem shape must match image shape.")
        z0 = initial_dem.astype(np.float64)

    result: OptimizeResult = minimize(
        fun=sfs_cost_and_gradient,
        x0=z0.flatten(),
        args=(
            observed,
            light_vec,
            config.sfs.regularization_lambda,
            observed.shape,
            valid_mask,
        ),
        method="L-BFGS-B",
        jac=True,
        options={
            "maxiter": config.sfs.max_iterations,
            "ftol": config.sfs.convergence_tol,
        },
    )

    dem = result.x.reshape(observed.shape).astype(np.float32)
    diagnostics: Dict[str, float | str | bool] = {
        "success": bool(result.success),
        "message": str(result.message),
        "iterations": float(result.nit),
        "function_evaluations": float(result.nfev),
        "final_cost": float(result.fun),
        "shadow_threshold": float(threshold),
    }
    return dem, diagnostics


class SFSMethod(ReconstructionMethod):
    """Single-scale SFS method."""

    name = "sfs"

    def run(
        self,
        image: np.ndarray,
        config: ReconstructionConfig,
        initial_dem: np.ndarray | None = None,
    ) -> MethodResult:
        original_shape = image.shape
        working_image, resample_scale = _prepare_working_surface(image, config)
        working_initial_dem = None
        if initial_dem is not None:
            working_initial_dem = (
                initial_dem.astype(np.float32)
                if initial_dem.shape == working_image.shape
                else _resize_surface(initial_dem.astype(np.float32), working_image.shape)
            )
        dem, diagnostics = run_sfs_optimization(
            image=working_image,
            config=config,
            initial_dem=working_initial_dem,
        )
        if dem.shape != original_shape:
            dem = _resize_surface(dem, original_shape)
        diagnostics.update(
            {
                "original_height": float(original_shape[0]),
                "original_width": float(original_shape[1]),
                "working_height": float(working_image.shape[0]),
                "working_width": float(working_image.shape[1]),
                "resample_scale": float(resample_scale),
                "used_working_resolution": bool(resample_scale != 1.0),
            }
        )
        return MethodResult(dem=dem, diagnostics=diagnostics)
