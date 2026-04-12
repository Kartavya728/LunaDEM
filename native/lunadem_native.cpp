#include <cmath>
#include <stdexcept>
#include <vector>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

py::array_t<double> compute_light_vector(double sun_azimuth_deg, double sun_elevation_deg) {
    const double pi = 3.14159265358979323846;
    const double az_rad = sun_azimuth_deg * pi / 180.0;
    const double el_rad = sun_elevation_deg * pi / 180.0;

    const double z = std::sin(el_rad);
    const double xy_proj = std::cos(el_rad);
    const double x = xy_proj * std::sin(az_rad);
    const double y = xy_proj * std::cos(az_rad);
    const double norm = std::sqrt(x * x + y * y + z * z);
    if (norm <= 0.0) {
        throw std::runtime_error("Invalid light vector norm; check illumination angles.");
    }

    auto result = py::array_t<double>(3);
    auto buffer = result.mutable_unchecked<1>();
    buffer(0) = x / norm;
    buffer(1) = y / norm;
    buffer(2) = z / norm;
    return result;
}

py::array_t<float> hazard_map(py::array_t<float, py::array::c_style | py::array::forcecast> dem, int window) {
    if (window <= 0) {
        throw std::runtime_error("window must be positive.");
    }
    auto input = dem.unchecked<2>();
    const py::ssize_t rows = input.shape(0);
    const py::ssize_t cols = input.shape(1);
    const int radius = window / 2;

    auto output = py::array_t<float>({rows, cols});
    auto result = output.mutable_unchecked<2>();

    for (py::ssize_t row = 0; row < rows; ++row) {
        for (py::ssize_t col = 0; col < cols; ++col) {
            float local_min = input(row, col);
            float local_max = input(row, col);
            for (int dy = -radius; dy <= radius; ++dy) {
                const py::ssize_t yy = std::min<py::ssize_t>(std::max<py::ssize_t>(row + dy, 0), rows - 1);
                for (int dx = -radius; dx <= radius; ++dx) {
                    const py::ssize_t xx = std::min<py::ssize_t>(std::max<py::ssize_t>(col + dx, 0), cols - 1);
                    const float value = input(yy, xx);
                    if (value < local_min) {
                        local_min = value;
                    }
                    if (value > local_max) {
                        local_max = value;
                    }
                }
            }
            result(row, col) = local_max - local_min;
        }
    }
    return output;
}

PYBIND11_MODULE(_native, module) {
    module.doc() = "Optional native accelerators for lunadem";
    module.def("compute_light_vector", &compute_light_vector, py::arg("sun_azimuth_deg"), py::arg("sun_elevation_deg"));
    module.def("hazard_map", &hazard_map, py::arg("dem"), py::arg("window"));
}
