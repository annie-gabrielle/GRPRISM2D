# Gravimetric Modeling with Vertical Prisms

This repository contains a Python-based forward gravimetric modeling tool implemented in a Jupyter Notebook. It is based on vertical prisms with infinite extension in one horizontal direction and is designed to approximate subsurface structures using a discrete mesh of simple geometric blocks.

## Overview

In geophysical modeling, subsurface structures are often irregular and asymmetric. However, when gravity data are acquired at some distance from the source, these structures can be approximated by simpler geometries such as vertical prisms. This tool discretizes the subsurface into 200 vertical prisms, each defined by parameters such as top and base depths, horizontal position, thickness, and density contrast.

### Key Assumptions

- Each prism extends infinitely in the *y*-direction (2D modeling).
- The modeling domain spans 2 km horizontally and 1 km in depth.
- The target region is 1 km × 1 km; the rest acts as a buffer to reduce edge effects.
- Each prism is 0.1 km wide and 0.1 km deep.

## Prism Parameters

Each prism is defined by:

- **Top Depth** `z₁`: 0 to 0.9 km  
- **Base Depth** `z₂`: 0.1 to 1.0 km  
- **Width** `t`: fixed at 0.1 km  
- **Horizontal Position** `x_q`: 0 to 1.9 km  
- **Density Contrast** `ρ`: in kg/m³  

The vertical gravity anomaly is computed using an adapted version of the formula presented by Luiz (1995), suitable for vertical-faced prisms:

![Gravimetric Equation](Figures/gravity_equation.png)

## Mesh and Acquisition Layout

The subsurface is discretized into a mesh of 20 rows (depth) by 10 columns (horizontal), totaling 200 prisms. Twenty gravimetric stations are positioned at the midpoints of each surface prism. The total gravity anomaly is the sum of the contributions from all prisms:

```
g_z200(x) = sum(g_i for i in range(1, 201))
```

![Mesh 20x10](Figures/Mesh_20x10.png)

## Validation

To validate the prismatic modeling approach, results were compared with analytical gravity responses for a sphere and a cylinder. A finer mesh (20×40 prisms) was used in these tests.

**Validation parameters:**

- Refined mesh: 40 columns × 20 rows = 800 prisms  
- Radius: 0.2 km  
- Density contrast: 200 kg/m³  
- Cylinder half-length: 100 km (to approximate infinite length in *y*)

**Analytical Equations Used:**

- **Sphere:**

```
g_ze(x) = (4πGΔρr³z_c) / [3((x−x_c)²+z_c²)^(3/2)]
```

- **Cylinder:**

```
g_zc(x) = [2πGΔρr² / z_c(1 + ((x−x_c)² / z_c²))] × 1 / sqrt(1 + ((x−x_c)² + z_c²)/L²)
```

**Validation Results:**

- Sphere approximation: **~40% RMS error**
- Cylinder approximation: **~7% RMS error**

The low error for the cylindrical case validates the use of vertical prisms to approximate elongated subsurface bodies.

![Validation Plot](Figures/gravimetric_Validation.png)

## Usage Instructions

1. Clone this repository:
   ```bash
   git clone https://github.com/annie-gabrielle/GRPRISM2D.git
   cd GRPRISM2D
   ```

2. Open and run the notebook:
   ```bash
   jupyter notebook gravimetric_modeling.ipynb
   ```

3. Edit the `density_mesh` inside the notebook to define your custom subsurface configuration.

4. Run the notebook to view the calculated gravity anomaly and 2D density model.

## Dependencies

- `numpy`
- `matplotlib`
- `ipywidgets` (for interactive input, optional)
- `json` (built-in)

You can install all required packages using:

```bash
pip install numpy matplotlib ipywidgets
```

## License

This project is licensed under the MIT License.

## Author

Developed by **Annie Gabrielle**  
Pós-Graduação em Geofísica – Observatório Nacional, Brazil  
GitHub: [annie-gabrielle](https://github.com/annie-gabrielle)

---

Feel free to open issues, contribute with suggestions, or fork the repository to build upon it!
