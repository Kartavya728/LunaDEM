# Shape From Shading: Core Maths

The lunadem SFS implementation follows a classical single-image photoclinometry model.

1. Image formation:

`I(x, y) ~= rho * max(0, n(x, y) . s)`

- `I(x, y)` is observed brightness
- `rho` is effective albedo
- `n(x, y)` is the unit surface normal
- `s` is the unit sun/light vector

2. Surface parameterization:

`z = z(x, y)`

`p = dz/dx`

`q = dz/dy`

`n = (-p, -q, 1) / sqrt(p^2 + q^2 + 1)`

3. Predicted intensity under Lambertian reflectance:

`I_hat(x, y) = max(0, n(x, y) . s)`

4. Optimization objective:

`L(z) = || I_hat(z) - I ||^2 + lambda * R(z)`

- first term matches rendered brightness to the observed image
- `R(z)` is a smoothness regularizer
- `lambda` balances fit vs smoothness

5. Scaling:

The recovered height map is relative until camera/sensor geometry is used to scale it into meters.

6. Multiscale refinement:

The same objective is solved from coarse to fine resolution so the optimizer first captures broad terrain shape and then adds local detail.
