# Shape From Shading: Assumptions

- Surface brightness is driven mainly by illumination geometry.
- Reflectance is close enough to Lambertian for deterministic inversion to be useful.
- The image is sufficiently calibrated for brightness gradients to carry shape information.
- Shadows, saturation, and extreme albedo changes are not perfectly modelled.
- The recovered DEM is relative first and is metric only after sensor scaling is applied.
- Single-image SFS cannot fully disambiguate all terrain shapes without additional priors or metadata.
- Low sun angles increase contrast but can also exaggerate shadow-driven uncertainty.
- Output quality improves when sun geometry, camera geometry, and scene metadata are supplied.
