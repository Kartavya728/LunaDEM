# Theory

## Shape from Shading (SFS)

lunadem uses Lambertian reflectance with smoothness regularization:

- brightness residual between observed and predicted image
- Laplacian smoothness prior on the recovered surface
- L-BFGS-B optimization on flattened height map

## Multi-scale SFS

For improved stability:

1. Downsample image to coarse levels
2. Solve SFS from coarse to fine
3. Upsample previous DEM as initialization for next level

## Terrain Analytics

From reconstructed DEM:

- slope: gradient magnitude converted to degrees
- roughness: local standard deviation
- curvature: Laplacian-based curvature proxy

## Landing Suitability

Deterministic safety mask from:

- slope threshold
- roughness threshold
- hazard relief threshold (local max-min)
