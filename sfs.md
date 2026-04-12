# Shape From Shading In lunadem

This document explains the shape-from-shading workflow used by `lunadem`.

## Intuition

Shape from shading uses brightness changes in a single image to infer local surface orientation and then reconstruct a relative height field. In lunar imagery, this is useful because low-angle sunlight often makes terrain relief visible through shading gradients.

## Core Model

The implementation uses a Lambertian-style reflectance approximation:

`I(x, y) ~= rho * max(0, n(x, y) . s)`

- `I(x, y)` is observed brightness
- `rho` is effective albedo
- `n(x, y)` is the local unit surface normal
- `s` is the unit sun vector

The surface is written as a height field:

`z = z(x, y)`

with gradients:

`p = dz/dx`

`q = dz/dy`

and normal:

`n = (-p, -q, 1) / sqrt(p^2 + q^2 + 1)`

## Optimization

`lunadem` minimizes a brightness mismatch plus smoothness regularization:

`L(z) = || I_hat(z) - I ||^2 + lambda * R(z)`

- the brightness term keeps the rendered image close to the observed image
- the regularizer discourages unstable or noisy surfaces
- `lambda` controls the balance between detail and smoothness

## Scaling

The reconstructed surface is relative first. Metric scaling happens after reconstruction by using the sensor model and pixel-scale estimation.

## Multiscale Strategy

The multiscale method solves the problem from coarse to fine resolution so the optimizer first captures broad terrain structure and then refines local detail.

## Assumptions

- Reflectance is close enough to Lambertian for deterministic inversion to be useful
- shading is informative enough to encode terrain
- shadows and albedo variation are not perfectly modeled
- single-image SFS cannot remove every ambiguity without priors or metadata

## Useful CLI Commands

```bash
lunadem sfs --maths
lunadem sfs --terms
lunadem sfs --assumptions
```

## Useful Python Calls

```python
from lunadem import get_sfs_assumptions, get_sfs_math, get_sfs_terms

print(get_sfs_math())
print(get_sfs_terms())
print(get_sfs_assumptions())
```
