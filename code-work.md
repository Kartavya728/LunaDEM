Code Work README
Project: Generation of High-resolution Digital Elevation Model from Lunar Images using Photoclinometry
Date: 2026-04-03
Scope: This document explains the repository structure, code flow, functions, known issues, improvements, and online references.

Section 01. Executive summary
This repository implements a single-image shape-from-shading (photoclinometry) pipeline to reconstruct a relative height map and scale it to meters. The pipeline takes a lunar image, estimates surface normals under a Lambertian model, and solves an optimization problem to recover a digital elevation model (DEM). The repo also includes a Flask web UI that accepts image uploads and returns outputs including GeoTIFF, OBJ, and visualizations.

Section 02. What the project does
The project reconstructs terrain from illumination cues in a single image, using a Lambertian reflectance model and smoothness regularization. It then scales the relative heights using camera geometry parameters and saves the output as a GeoTIFF DEM and a 3D mesh in OBJ format. It also generates 2D and 3D visualization images.

Section 03. What the project is not
It is not a full photogrammetry or stereo pipeline, and it does not ingest multiple images or photometric corrections. It does not solve for albedo or complex BRDFs. It does not include rigorous lunar geodetic CRS handling or a physical camera model beyond a simple pixel scale calculation.

Section 04. Folder structure overview
Repository root contains a Flask web app, a command line runner, an SFS library package, and static assets.
Key folders include data for example images, output for generated files, templates and static for web assets, and uploads for incoming web images.

Section 05. Folder structure tree
.
|-- app.py
|-- run_photoclinometry.py
|-- requirements.txt
|-- README.md
|-- code-work.readme
|-- data/
|-- output/
|-- sfs_photoclinometry/
|-- static/
|-- templates/
|-- uploads/

Section 06. Directory details
data contains example images, mostly PNG and JPG, used for local testing.
output holds the most recent CLI outputs, including the reconstructed DEM and visualizations.
uploads stores images uploaded through the Flask web UI.
static holds CSS, JS, and generated output subfolders for web results.
templates includes HTML templates for the Flask UI.
sfs_photoclinometry is the core Python package with the algorithm and IO.

Section 07. Files at root
app.py is the Flask web server entry point.
run_photoclinometry.py is the CLI pipeline runner.
requirements.txt is currently empty and should list dependencies.
README.md is empty.
tempCodeRunnerFile.py appears to be a temporary IDE file.

Section 08. Core package: sfs_photoclinometry
The package contains the core algorithm, IO helpers, utility math, and plotting.
Files are core.py, io_handler.py, utils.py, visualization.py, and __init__.py.

Section 09. app.py summary
Defines a Flask app with two routes: GET / and POST /run.
Accepts an image upload and JSON parameters, runs the SFS pipeline, and returns JSON with URLs to generated outputs.
Uses run_sfs_pipeline to orchestrate the entire process.

Section 10. run_photoclinometry.py summary
Defines a local SFS_INPUTS dictionary with default parameters.
Loads an image from data, runs optimization, scales DEM, saves outputs, and prints stats.

Section 11. core.py summary
Defines the optimization cost and gradient for shape-from-shading.
Uses SciPy L-BFGS-B to minimize brightness mismatch plus smoothness.
Returns a DEM in the same shape as the input image.

Section 12. io_handler.py summary
Loads images with imageio, converts to grayscale, and normalizes to [0, 1].
Writes GeoTIFF with rasterio using provided corner ground control points.
Exports OBJ mesh with simple grid connectivity.

Section 13. utils.py summary
Converts sun azimuth and elevation to a normalized light vector.
Computes surface normals from height map and predicts image intensity using Lambertian reflectance.

Section 14. visualization.py summary
Creates terrain colormap images and 3D surface plots with matplotlib.
Saves outputs to disk with consistent labeling.

Section 15. Web UI templates
templates/index.html contains the form for metadata and image upload.
templates/results.html contains a results page with 3D preview and download buttons.
Current app returns JSON, so results.html is not used by app.py as-is.

Section 16. Static assets
static/css/style.css and static/js/main.js appear to be from an older UI.
index.html includes inline CSS and JS and does not load the external static assets.

Section 17. High level pipeline (CLI)
Step 1. Load image with io_handler.load_image.
Step 2. Compute light vector from azimuth and elevation.
Step 3. Initialize a flat surface.
Step 4. Optimize using L-BFGS-B to minimize brightness error and smoothness.
Step 5. Scale relative DEM to meters using pixel scale.
Step 6. Save GeoTIFF and OBJ.
Step 7. Render 2D and 3D visualizations.

Section 18. High level pipeline (Web)
Step 1. Upload image through Flask.
Step 2. Build SFS parameter dictionary.
Step 3. Run run_sfs_pipeline on server.
Step 4. Save outputs under static/outputs/<run_id>.
Step 5. Return JSON with output URLs.

Section 19. Detailed data flow
Input image array -> normalized grayscale -> predicted image from reflectance -> optimization for Z -> scaled DEM -> files and visualizations -> URLs for download.

Section 20. Algorithm detail: reflectance model
Lambertian reflectance is used with albedo implicitly set to 1.
Predicted image I = max(0, N dot L) using surface normals N and light vector L.

Section 21. Algorithm detail: cost function
Brightness cost = 0.5 * sum((I_obs - I_pred)^2).
Smoothness cost = 0.5 * sum((laplace(Z))^2).
Total cost = brightness cost + lambda * smoothness cost.

Section 22. Algorithm detail: gradient
The gradient is derived via chain rule using surface gradients p and q.
Brightness gradient is computed as divergence of error gradients.
Smoothness gradient uses bi-Laplacian of Z.

Section 23. Coordinate conventions
Light vector assumes azimuth clockwise from north and elevation above horizon.
Surface normal assumes Z is height, gradient p is dZ/dx and q is dZ/dy.
OBJ mesh uses pixel coordinates with Z as height.

Section 24. Scaling to meters
Pixel size in meters is computed from detector pixel width, spacecraft altitude, and focal length.
Scaled DEM is dem * pixel_size_m and mean-centered.

Section 25. Georeferencing
GeoTIFF uses four corner GCPs in lat lon and EPSG:4326.
This is an Earth CRS and is not a correct lunar CRS for Selenographic data.

Section 26. Output artifacts
reconstructed_dem.tif is the GeoTIFF DEM.
reconstructed_dem.obj is a mesh with vertices and quad faces.
depth_map_visualization.png is a 2D colormap.
surface_3d_visualization.png is a 3D surface plot.

Section 27. Inputs and parameters
sun_azimuth_deg and sun_elevation_deg define lighting.
regularization_lambda controls smoothness.
max_iterations sets optimizer iterations.
spacecraft_altitude_km, focal_length_mm, detector_pixel_width_um define pixel scale.
refined_corner_coords set the GCPs for georeferencing.

Section 28. What is hardcoded
Parameters in app.py are largely hardcoded and not read from JSON.
Image normalization and albedo are fixed assumptions.
OBJ export is fixed to a simple grid without textures.

Section 29. Data normalization
Image is normalized to [0, 1] using min and max of the image.
Flat images become zeros, which can break SFS assumptions.

Section 30. Performance notes
Optimization cost is high for large images.
OBJ export is O(H*W) and can be massive in file size.
3D plotting uses stride to reduce rendering cost.

Section 31. Web server behavior
Flask runs with debug=True in app.py.
Uploads are stored on disk without cleanup.
Outputs are saved under static/outputs with run-specific folder.

Section 32. Security notes
Debug mode can leak stack traces.
Uploads are saved without size validation.
No content type validation beyond filename accept.

Section 33. Reproducibility notes
Results depend on input image normalization and lighting parameters.
No random elements are present in the optimizer by default.

Section 34. Known issues in code and UI
Issue 01. app.py returns JSON but index.html is a normal form expecting page navigation.
Issue 02. results.html is not used by app.py, so UI does not show results page.
Issue 03. static/js/main.js expects a /run-sfs endpoint that does not exist.
Issue 04. static/js/main.js refers to DOM elements not present in index.html.
Issue 05. index.html inline JS only handles filename display, not async results.
Issue 06. requirements.txt is empty but code uses Flask, numpy, scipy, rasterio, imageio, matplotlib, tqdm.
Issue 07. app.py sets spacecraft_altitude_km using focal_length_mm input key.
Issue 08. missing JSON upload handling in app.py, even though UI has a JSON upload control.
Issue 09. index.html includes disabled form fields not used by app.py.
Issue 10. templates show degree symbol encoding artifacts like "Â°" and "Ã—".
Issue 11. GeoTIFF uses EPSG:4326 which is not lunar.
Issue 12. SFS assumes Lambertian surface and constant albedo, which is not true for lunar regolith.
Issue 13. No shadow masking or photometric correction is used.
Issue 14. L-BFGS-B gradient derivation likely incomplete for correct Lambertian gradients.
Issue 15. Normalization to [0, 1] can remove absolute brightness scale.
Issue 16. Laplacian boundary mode constant can introduce edge artifacts.
Issue 17. No unit tests or validation metrics exist.
Issue 18. No parameter validation or bounds checking for sun angles.
Issue 19. OBJ file writes quads without normals or texture coordinates.
Issue 20. Output folders can accumulate large files without cleanup.

Section 35. Additional correctness risks
Single-image SFS is ill-posed and may produce concave-convex ambiguity.
SFS may fit albedo variations as terrain features.
If sun elevation is low, shadows and non-Lambertian effects dominate.
Pixel scale formula assumes a pinhole model and nadir imaging.
If focal length and altitude are not accurate, metric scaling will be wrong.

Section 36. Improvement opportunities: algorithmic
Improve photometric modeling with a lunar BRDF or Hapke model.
Add shadow detection and mask.
Use multi-image SFS or photometric stereo for better constraints.
Include albedo estimation or regularization of albedo.
Incorporate coarse DEM priors for low-frequency components.
Add slope constraints based on physical terrain limits.
Use robust loss to reduce influence of outliers.

Section 37. Improvement opportunities: engineering
Add requirements.txt and lockfile.
Add CLI arguments rather than hardcoded SFS_INPUTS.
Add logging and structured progress output.
Add caching and output cleanup policies.
Add unit tests for light vector and IO.

Section 38. Improvement opportunities: web UI
Unify UI by using index.html with proper AJAX or render results.html server side.
Implement /run-sfs or update main.js to /run.
Show progress and results inline.
Validate file types and sizes.
Add download links after completion.

Section 39. Improvement opportunities: geospatial correctness
Use a lunar CRS with correct datum.
Use proper map projection for selenographic coordinates.
Validate GCPs against image metadata.
Support reading metadata from PDS or ISIS cube files.

Section 40. Improvement opportunities: performance
Downsample for preview and optimize at full resolution.
Use GPU acceleration or parallelized gradients.
Reduce OBJ size via mesh decimation.
Use tiled GeoTIFF with compression.

Section 41. Improvement opportunities: UX and docs
Fill README.md with instructions and examples.
Add a diagram of the data flow.
Provide a sample run and expected outputs.
Document parameter meanings and units.

Section 42. Function walkthrough: app.py run_sfs_pipeline
Loads image from disk using io_handler.
Runs core.run_sfs_optimization to estimate height map.
Scales height map to meters using core.scale_dem_to_meters.
Saves outputs with io_handler and visualization.
Constructs URLs to static output files.

Section 43. Function walkthrough: app.py run_sfs
Checks that an image file is uploaded.
Reads selected form fields for sun angles and focal length.
Writes uploaded file to uploads.
Creates output folder under static/outputs.
Calls run_sfs_pipeline and returns JSON.

Section 44. Function walkthrough: core.sfs_cost_and_gradient
Reshapes flat Z to 2D.
Computes predicted image using utilities.
Computes brightness error and smoothness cost.
Computes gradient based on p and q.
Returns total cost and flattened gradient.

Section 45. Function walkthrough: core.run_sfs_optimization
Computes light vector.
Initializes Z to zeros if flat surface selected.
Sets up L-BFGS-B with callback progress bar.
Returns optimized Z as 2D array.

Section 46. Function walkthrough: core.scale_dem_to_meters
Computes pixel size in meters using instrument geometry.
Scales DEM by pixel size and mean-centers.
Returns scaled DEM.

Section 47. Function walkthrough: io_handler.load_image
Loads image using imageio.
Converts RGB to grayscale with luminosity weights.
Normalizes to [0, 1].
Returns numpy array.

Section 48. Function walkthrough: io_handler.save_dem_as_geotiff
Creates GCPs using provided corners.
Builds rasterio transform from GCPs.
Writes GeoTIFF with CRS EPSG:4326.

Section 49. Function walkthrough: io_handler.save_dem_as_obj
Writes vertices as v x y z.
Writes faces as quad f v1 v2 v3 v4 in row-major order.

Section 50. Function walkthrough: utils.get_light_vector
Converts azimuth and elevation to radians.
Computes x, y, z vector components.
Normalizes the vector.

Section 51. Function walkthrough: utils.calculate_surface_normals
Computes gradients and builds normals.
Normalizes with epsilon for stability.
Returns normal vectors per pixel.

Section 52. Function walkthrough: utils.calculate_predicted_image
Computes Lambertian reflectance.
Applies max(0, dot) clamp to avoid negative values.

Section 53. Function walkthrough: visualization.plot_depth_map
Creates 2D image with terrain colormap.
Adds labels and colorbar.
Saves PNG.

Section 54. Function walkthrough: visualization.plot_3d_surface
Creates 3D surface plot.
Uses stride to reduce rendering cost.
Saves PNG.

Section 55. Configuration assumptions
Input image is roughly photometrically corrected.
Sun azimuth and elevation are known.
Surface is diffuse and matte.
Local terrain slopes are moderate.

Section 56. Suggested CLI usage
Place a PNG or JPG in data.
Update SFS_INPUTS in run_photoclinometry.py.
Run python run_photoclinometry.py.
Inspect output folder for results.

Section 57. Suggested web usage
Run python app.py.
Open browser to http://127.0.0.1:5000/.
Upload image and click run.
Download files from generated results.

Section 58. Missing dependencies
Flask for web.
numpy, scipy, imageio, rasterio, matplotlib, tqdm for core.
Optionally gunicorn or waitress for production.

Section 59. Data quality considerations
Shadows and high albedo variations distort reconstruction.
Image compression artifacts can show up as terrain noise.
Large saturated areas reduce SFS fidelity.

Section 60. Known outputs in repo
output/reconstructed_dem.tif and .obj show a previous run.
static/outputs contains multiple run folders with outputs.
uploads contains many copies of moon1.png.

Section 61. Cleanup suggestions
Add a job to purge old uploads and outputs.
Add a max size limit and allowed file list.
Use unique temp folder per session and cleanup after download.

Section 62. Error handling gaps
No try or except around rasterio or matplotlib saves.
No recovery if optimization fails.
No safe fallback if input has zero variance.

Section 63. Testing suggestions
Unit test light vector for known azimuth and elevation.
Unit test predicted image for a flat surface.
Unit test scale_dem_to_meters with known scale.
Integration test a small 32x32 synthetic image.

Section 64. Validation suggestions
Compare reconstructed DEM with known DEM or synthetic ground truth.
Plot residuals between observed and predicted brightness.
Check histogram of residuals for bias.

Section 65. Metrics to log
Optimization convergence status.
Final cost value and gradient norm.
Processing time per phase.
Min and max DEM heights.

Section 66. Potential numerical issues
Denominator clipping in gradient can bias optimization.
Laplacian boundary assumptions may cause edge artifacts.
Large images may cause memory pressure.

Section 67. Portability notes
Rasterio requires GDAL; install can be heavy on Windows.
Matplotlib needs a non-interactive backend for server use.

Section 68. UX issues
UI indicates JSON upload but backend ignores it.
UI indicates landing suitability but no logic exists.
Button label says Download DEM, but processing is a server run.

Section 69. Documentation gaps
No instructions for installing dependencies.
No description of data sources for example images.
No explanation of parameter values.

Section 70. Suggested documentation structure
Quick start.
Theory overview.
Parameter glossary.
File outputs and formats.
Troubleshooting.

Section 71. Online related resources summary
The online ecosystem includes shape-from-shading papers, NASA and USGS lunar imaging products, and LROC PDS archives. Most official DEM products use stereo or multi-image pipelines with photometric correction, while this repo implements a simplified single-image SFS approach.

Section 72. Online resources and references
Photoclinometry overview and historical background can be found in shape-from-shading literature and reference articles.
LROC PDS and derived data products list available NAC DEM and WAC mosaics and provide product format documentation.
USGS Astropedia provides a public photoclinometry DEM example for a lunar region.
NASA science pages include examples of photoclinometry-derived topography.

Section 73. Online related links and notes
LROC PDS archive overview and product categories:
https://pds.lroc.im-ldi.com/
LROC RDR product specification PDF:
https://pds-imaging.jpl.nasa.gov/documentation/LROC_SOC_RDR_SIS_Spec_4_v1-2.pdf
LROC PDS release notes example:
https://lroc.im-ldi.com/images/1370
USGS Astropedia Haworth photoclinometry DEM:
https://astrogeology.usgs.gov/search/map/lunar_lro_nac_haworth_photoclinometry_dem_1m
NASA photoclinometry example from HiRISE:
https://science.nasa.gov/photojournal/first-hirise-image-of-mars-topographic-model-from-photoclinometry/
Shape-from-shading background and definitions:
https://en.wikipedia.org/wiki/Photoclinometry
LROC NAC processing guide PDF:
https://lroc.im-ldi.com/data/support/downloads/LROC_NAC_Processing_Guide.pdf
USGS publication on photometric functions for photoclinometry:
https://www.usgs.gov/publications/photometric-functions-photoclinometry-and-other-applications

Section 74. Link list (non-exhaustive)
LROC PDS archive:
https://pds.lroc.im-ldi.com/
LROC RDR SIS spec:
https://pds-imaging.jpl.nasa.gov/documentation/LROC_SOC_RDR_SIS_Spec_4_v1-2.pdf
LROC PDS release note example:
https://lroc.im-ldi.com/images/1370
USGS Astropedia Haworth photoclinometry DEM:
https://astrogeology.usgs.gov/search/map/lunar_lro_nac_haworth_photoclinometry_dem_1m
NASA photoclinometry example:
https://science.nasa.gov/photojournal/first-hirise-image-of-mars-topographic-model-from-photoclinometry/
Photoclinometry overview:
https://en.wikipedia.org/wiki/Photoclinometry
LROC NAC processing guide:
https://lroc.im-ldi.com/data/support/downloads/LROC_NAC_Processing_Guide.pdf
USGS photometric functions paper page:
https://www.usgs.gov/publications/photometric-functions-photoclinometry-and-other-applications

Section 75. What to add to requirements.txt
Flask
numpy
scipy
imageio
rasterio
matplotlib
tqdm

Section 76. Proposed CLI refactor
Parse CLI args with argparse.
Move SFS_INPUTS to a config file.
Add logging to a file.
Add optional output naming.

Section 77. Proposed web refactor
Serve index.html using external CSS and JS.
Use a single result page or dynamic results panel.
Add SSE or websocket progress if desired, or remove JS references.

Section 78. Proposed algorithm refactor
Add a brightness residual mask for shadows.
Add option to choose reflectance model.
Add coarse-to-fine multiscale optimization.

Section 79. Proposed geospatial refactor
Support lunar CRS via PROJ string or WKT.
Allow reading GCPs from metadata.
Write world file for simple outputs.

Section 80. Example parameter interpretation
sun_azimuth_deg controls left-right illumination direction.
sun_elevation_deg controls shadow length.
regularization_lambda controls smoothness versus detail.
max_iterations controls optimization duration.

Section 81. Output file sizes
OBJ can be extremely large for high-resolution images.
GeoTIFF size depends on resolution and compression settings.

Section 82. Compatibility with common tools
GeoTIFF can be opened in QGIS, ArcGIS, or GDAL tools.
OBJ can be opened in MeshLab or Blender.
PNG visualizations can be viewed in any image viewer.

Section 83. Summary of architectural mismatch
Web UI and backend are out of sync, likely from merging two versions.
Fixing the web flow is a priority if the web app is intended to be used.

Section 84. Suggested alignment options
Option A: Update app.py to render results.html instead of JSON.
Option B: Update index.html to fetch JSON and populate results dynamically.
Option C: Remove results.html and static/js/main.js to reduce confusion.

Section 85. Risk of wrong scaling
Pixel scale depends on accurate focal length, altitude, and pixel width.
If the parameters are not correct for the image, DEM heights are wrong.

Section 86. Suggested data sources for testing
Public LROC NAC images with known geometry.
USGS or NASA published DEM tiles for comparison.
Synthetic test surfaces to validate algorithm correctness.

Section 87. Practical limitations of single image SFS
Ambiguity between albedo and shape.
Low-frequency shape cannot be recovered reliably without prior.
Noise can produce spurious high-frequency artifacts.

Section 88. Practical improvements for robustness
Pre-filter image to reduce noise.
Add brightness bias term in the model.
Use edge-preserving regularization like total variation.

Section 89. Output naming conventions
Current output files are fixed to reconstructed_dem.*.
Consider adding date or run ID to filenames for CLI runs.

Section 90. Project maturity assessment
The project is a functional prototype with a working core algorithm.
Documentation and UX need alignment and completion.
Engineering hardening is needed for production.

Section 91. High level mistakes summary
UI and server mismatch.
Missing dependency lists.
Incorrect parameter mapping for spacecraft altitude.
Non-lunar CRS in GeoTIFF.
Encoding artifacts in HTML.

Section 92. High level improvement summary
Synchronize UI and backend.
Improve photometric modeling and validation.
Add config management and tests.

Section 93. Appendices overview
Appendix A contains a line-by-line review checklist.
Appendix B contains a parameter glossary.
Appendix C contains an improvement backlog.
Appendix D contains a troubleshooting checklist.

Appendix A. Line-by-line review checklist
A01. Confirm app.py routes match frontend endpoints.
A02. Confirm upload folder exists and is writable.
A03. Confirm output folder is cleaned periodically.
A04. Confirm run_sfs_pipeline returns expected URLs.
A05. Confirm jsonify usage in app.py returns HTTP 200.
A06. Confirm error handling returns JSON on exception.
A07. Confirm HTML uses correct form action.
A08. Confirm JavaScript is loading if expected.
A09. Confirm index.html refers to CSS and JS if required.
A10. Confirm results page is reachable.
A11. Confirm parameter names match between UI and server.
A12. Confirm spacecraft altitude is read from correct field.
A13. Confirm focal length input exists and is validated.
A14. Confirm JSON upload control is wired to backend.
A15. Confirm non-ASCII characters render properly.
A16. Confirm light vector uses correct azimuth convention.
A17. Confirm normalization handles all-black images.
A18. Confirm optimizer options are suitable for image size.
A19. Confirm laplacian boundary mode is acceptable.
A20. Confirm predicted image uses same normalization as observed.
A21. Confirm lambertian clamp does not hide negative values improperly.
A22. Confirm gradient is consistent with cost.
A23. Confirm L-BFGS-B convergence criteria are reasonable.
A24. Confirm scaled DEM is centered around zero intentionally.
A25. Confirm GeoTIFF CRS matches lunar usage.
A26. Confirm GCP coordinates are in correct order.
A27. Confirm OBJ face winding is consistent.
A28. Confirm OBJ mesh size is manageable.
A29. Confirm visualization images use correct units.
A30. Confirm error messages are visible to user.
A31. Confirm output URLs map to correct static folder.
A32. Confirm URL path separators are normalized on Windows.
A33. Confirm debug mode is disabled in production.
A34. Confirm Flask secret key if sessions are used.
A35. Confirm file extension filtering for uploads.
A36. Confirm request size limits for uploads.
A37. Confirm external JS and CSS resources are pinned to versions.
A38. Confirm model-viewer usage works for OBJ.
A39. Confirm browser CORS for local files is not an issue.
A40. Confirm large uploads do not block server threads.
A41. Confirm rasterio writes to correct location.
A42. Confirm rasterio nodata value is correct.
A43. Confirm result files are downloadable.
A44. Confirm progress feedback is accurate.
A45. Confirm landing suitability section is either implemented or removed.

Appendix B. Parameter glossary
B01. sun_azimuth_deg: Sun direction clockwise from north, degrees.
B02. sun_elevation_deg: Sun elevation above horizon, degrees.
B03. initial_surface: Starting height map type, only flat supported.
B04. regularization_lambda: Smoothness weight.
B05. max_iterations: Optimizer maximum iterations.
B06. spacecraft_altitude_km: Spacecraft altitude above surface in km.
B07. focal_length_mm: Camera focal length in mm.
B08. detector_pixel_width_um: Pixel width in micrometers.
B09. refined_corner_coords: Dict of corner lat lon.
B10. projection: Projection name or hint.
B11. output_dir: Output folder.
B12. image_path: Input image path.

Appendix C. Improvement backlog (compact list)
C01. Fill requirements.txt.
C02. Add setup instructions.
C03. Add CLI args for image, output, parameters.
C04. Add a config JSON format and loader.
C05. Add tests for utils.get_light_vector.
C06. Add tests for io_handler.load_image.
C07. Add tests for core.scale_dem_to_meters.
C08. Add logging and timing per stage.
C09. Add progress status for long optimizations.
C10. Add output cleanup on schedule.
C11. Add validation for sun angles.
C12. Add file size limits.
C13. Add file type validation for uploads.
C14. Add automatic downsampling options.
C15. Add multiscale pyramid optimization.
C16. Add albedo estimation.
C17. Add photometric correction module.
C18. Add shadow masking.
C19. Add smoother boundary conditions.
C20. Add robust loss (Huber or Tukey).
C21. Add global shape prior with coarse DEM.
C22. Add lunar CRS support.
C23. Add GCP validation with metadata.
C24. Add compression for GeoTIFF.
C25. Add mesh decimation.
C26. Add normal vectors to OBJ.
C27. Add PLY export option.
C28. Add interactive 3D viewer in UI.
C29. Add results.html integration.
C30. Add API endpoint documentation.

Appendix D. Troubleshooting checklist
D01. If image load fails, check path and format.
D02. If image looks blank, check normalization and image contrast.
D03. If optimizer fails, reduce max_iterations or increase regularization.
D04. If output is noisy, increase regularization and pre-filter image.
D05. If heights are too large, check pixel scale parameters.
D06. If GeoTIFF fails, verify rasterio installation.
D07. If UI shows no results, check endpoint and JS console.
D08. If OBJ is huge, use smaller images or mesh decimation.
D09. If plots are empty, check matplotlib backend and file path.
D10. If uploads fail, check file size limits and permissions.

Appendix E. Online related resources (short notes)
E01. Shape-from-shading and photoclinometry literature provides the theoretical foundation.
E02. NASA and USGS publish lunar imaging products and DEMs.
E03. USGS Astropedia provides sample photoclinometry DEMs.
E04. LROC PDS documentation lists derived data products including DEMs and mosaics.
E05. Multi-image SFS research highlights benefits beyond single-image SFS.

Appendix F. Suggested next steps for this repo
F01. Decide whether the primary interface is CLI or web.
F02. Align templates and API endpoints accordingly.
F03. Establish a proper dependency list and install guide.
F04. Add a config file for SFS parameters.
F05. Provide sample commands and expected outputs.

Appendix G. Quick reference of key files
G01. app.py: Flask server and pipeline integration.
G02. run_photoclinometry.py: CLI pipeline runner.
G03. sfs_photoclinometry/core.py: Optimization and scaling.
G04. sfs_photoclinometry/io_handler.py: IO for image and outputs.
G05. sfs_photoclinometry/utils.py: Lighting and reflectance utilities.
G06. sfs_photoclinometry/visualization.py: Plotting.
G07. templates/index.html: Upload form UI.
G08. templates/results.html: Results UI.
G09. static/js/main.js: Legacy JS.
G10. static/css/style.css: Legacy CSS.

Appendix H. Additional detail notes
H01. The brightness cost does not include albedo term.
H02. Using a single image assumes constant albedo and no shadows.
H03. The Laplacian smoothness may oversmooth fine features.
H04. A bi-Laplacian smoothness can bias toward flatter surfaces.
H05. The current algorithm uses a single global regularization weight.
H06. In practice, spatially varying weights may improve results.
H07. The SFS solution may be sensitive to initialization.
H08. Flat initialization is typical but not always optimal.
H09. Multi-resolution optimization can avoid local minima.
H10. Image gradients at borders are sensitive to padding mode.
H11. Use reflectance residuals to detect shadows.
H12. Solar incidence angle can be derived from geometry.
H13. The project can be extended to handle multiple images.
H14. Model-viewer is used for OBJ in results.html.
H15. Three.js and model-viewer are loaded via CDN in results.html.

Appendix I. Notation
I01. Z denotes the height map.
I02. p, q denote gradients dZ/dx and dZ/dy.
I03. L denotes light vector.
I04. N denotes surface normal.
I05. I_obs denotes observed image intensity.
I06. I_pred denotes predicted image intensity.

Appendix J. Minimal reproducibility checklist
J01. Fix requirements.txt.
J02. Provide a sample image.
J03. Document parameter values.
J04. Provide a known output sample.
J05. Provide a run script.

Appendix K. Encoding cleanup
K01. Replace "Â°" with "deg" or proper HTML entity.
K02. Replace "Ã—" with "x" or proper HTML entity.
K03. Ensure UTF-8 encoding in templates.

Appendix L. Data ethics and usage
L01. Document data source and licenses.
L02. Do not imply scientific accuracy without validation.
L03. Provide disclaimers about SFS limitations.

Appendix M. Error logging suggestions
M01. Log exceptions with stack trace in server logs.
M02. Return concise error messages to clients.
M03. Store logs per run for debugging.

Appendix N. Future feature ideas
N01. Add ROI cropping to reduce computation.
N02. Add uncertainty estimation.
N03. Add height map export as PNG or EXR.
N04. Add smoothing options in UI.
N05. Add preview results at lower resolution.

Appendix O. Final notes
O01. This project is a strong foundation for experimental SFS on lunar imagery.
O02. The primary risks are data assumptions and UI-backend mismatch.
O03. With improved documentation and alignment, it can be made much easier to use.
