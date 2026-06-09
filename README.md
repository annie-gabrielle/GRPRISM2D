# GRPRISM2D — Interactive 2D Gravimetric Modeling Platform

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.10-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**GRPRISM2D** is an interactive computational tool developed in Python designed to bridge the gap between theoretical gravitational geophysics and practical numerical programming. Engineered for students, researchers, and educators, the platform features an intuitive Graphical User Interface (GUI) to perform forward 2D gravity modeling using right rectangular prisms, allowing real-time geological hypothesis testing and data fitting.

Traditional 2D gravimetric modeling commonly employs the Talwani method using irregular polygons; however, our approach simplifies the mathematical formulation by approximating the subsurface with horizontal prisms of infinite extent along the strike direction, where each prism contributes independently to the calculated anomaly. The main objective of this article is to enhance teaching and learning in geophysics by introducing an accessible, simplified Python-based modeling software utilizing these prismatic units. 

To serve different pedagogical purposes, the tool is delivered both as a [standalone script with an interactive Graphical User Interface (GUI)](GUI-Interface/), offering students a dynamic introduction with six pre-configured prism scenarios, and a set of other three distinct Jupyter Notebooks:

* The **first notebook** demonstrates [synthetic scenarios](./Notebooks/Notebook1-Sensitivity/), such as contacts between iron formations and quartzites, to assess gravity curve sensitivities to structural variations.
* The **second** focuses on [code validation](./Notebooks/Notebook2-Validation/) by refining the mesh with an increasing number of prisms.
* The **third** provides a [real-world geological application](./Notebooks/) using gravity data from the Alagoas basin (Sub-AL-Basin).

Ultimately, these computational environments highlight how easily the core functions can be adapted to any required geological situation, providing an intuitive, efficient approach that helps students grasp how density contrasts and structural geometries influence gravity responses.

---

## 🖥️ Software Architecture & GUI Modes

The **GRPRISM2D** platform features a dual-execution architecture designed to accommodate different computational environments seamlessly, using Python's native `tkinter` library for window management and `matplotlib` for dynamic geophysical rendering.

### 🗺️ Workflow Architecture

* **1. Execution Gateway**
  * ├─ **Standalone Script:** Executed locally via Terminal, Anaconda Prompt, or your preferred IDE.
  * └─ **Embedded Jupyter Cell:** Executed directly inside a native notebook cell (Literate Programming Workspace).
                                            
* **2. Initial Parameters Window**
  * ├─ *Survey Geometry Setup:* Define total profile length ($km$), baseline limits, and station intervals ($m$).
  * ├─ *Field Data Ingestion:* Select an optional `*.txt` file (with auto-sanitization of commas to dots).
  * └─ *Progressive Mesh Selector:* Choose from 6 discretization levels (from $5\times19$ up to $10\times20$).
  
* **3. Prismatic Modeling Panel**
  * ├─ **Top Axis:** Real-time 3-signal curve fitting plot (Observed, Calculated, and Residual Error) with live RMS computation.
  * └─ **Bottom Axis:** Tabular interactive Matrix Editor grid with locked peripheral padding frames ($0.0 \text{ g/cm}^3$).

To maximize academic workflow flexibility, the exact same GUI architecture runs either as a standalone script or **directly embedded inside a Jupyter Notebook cell**. When executed within a notebook, the `tkinter` main loop instantiates independent, interactive windows that overlay the web interface. This bridges the gap between desktop deployment and literate programming, keeping students within a unified notebook sheet where they can document markdown code alongside interactive dashboards.

### 2. Initial Parameters Window
Upon launch, users encounter the **Initial Parameters Window**, which sets the spatial and resolution boundary conditions of the experiment:
* **Geometry Setup:** Defines total profile length ($km$), maximum depth investigation limit ($km$), and spatial distance intervals between acquisition stations ($m$).
* **Field Data Ingestion:** Includes an optional data loader accepting plain-text `*.txt` files. It features real-time decimal formatting sanitization (automatically converting commas to dots) and auto-isolates the last column as the target observed signal.
* **Progressive Grids:** Users can select six discretization profiles, ranging from a coarse $5\times19$ grid up to a highly refined $10\times20$ mesh (100 active units), introducing students to the core trade-offs between resolution and non-uniqueness.

### 3. The Prismatic Modeling Panel
Triggering the modeling environment launches a synchronized, dual-module maximized viewport layout:
* **Visual Viewports (Top):**
  * *Upper axes:* Tracks real-time curve fitting by plotting observed points (stippled black circles), calculated response (solid black curve), and the residual error curve (red dashed line) alongside the total Root-Mean-Square (RMS) error.
  * *Lower axes:* Renders the continuous cross-section geology map driven by a multi-chromatic `jet` colormap.
* **Matrix Editor (Bottom):** A tabular text-entry grid. Users insert localized density perturbations ($\Delta\rho$ in $\text{g/cm}^3$) into white active cells. Peripheral black cells represent non-reflective boundary padding zones fixed at $0.0\text{ g/cm}^3$ to prevent edge reflections and are locked in a `readonly` state. The colormap scales dynamically to view negative structures (e.g., basins or salt domes) or positive targets.

---

## 🛠️ User Manual

### 1. Environment Replication via Conda
To ensure full reproducibility and bypass dependency conflicts across different OS platforms, the repository includes a pre-configured `GRPRISM2D.yml` environment file.

Open your terminal or Anaconda Prompt and execute the following commands:

```bash
# 1. Navigate to your project folder
cd /path/to/your/GRPRISM2D-directory

# 2. Create the isolated virtual environment
conda env create -f GRPRISM2D.yml

# 3. Activate the profile
conda activate GRPRISM2D

# 4. Launch the application inside your Jupyter interface
jupyter notebook
```

### 2. Parameters Reference

When starting a new model session, configure the following structural boundary values:

| Parameter | UI Keyword | Unit | Description |
| :--- | :--- | :---: | :--- |
| **Length** | `label_comp` | km | Total horizontal profile span of the useful research area. |
| **Maximum Depth** | `label_prof` | km | Explored baseline limit setting the lower matrix boundary. |
| **Station Spacing** | `label_dist` | m | Spatial distance intervals governing data acquisition stations. |

### 3. Real-Time Math & Fitting Evaluation

When you input values in the Matrix Editor and press **`UPDATE MODEL`**, the system evaluates the root-mean-square error over $N$ stations:

$$\text{RMS} = \sqrt{\frac{1}{N}\sum_{j=1}^{N} \left( g_{z,j}^{\text{obs}} - g_{z,j}^{\text{calc}} \right)^2}$$

* **Negative Contrast Support:** Entering negative values adjusts the dynamic bounds of the colorbar color map, allowing the interpretation of low-density targets.
* **1D Linear Interpolation:** If field data station positions do not match the grid nodes, the system runs a `np.interp` filter to seamlessly align coordinates.

### 4. Data Exportation & Termination

Clicking **`CLOSE AND SAVE`** safely closes the GUI threads and flushes all computational matrices into a newly allocated directory named `GRPRISM2D-Resultados`. It saves:

* `matriz_densidades_final.txt`: Tab-separated array mapping the finalized numerical density contrasts.
* `dado_modelado_final.txt`: 1D text column containing the calculated synthetic gravity curve points ($g_z$).
* `modelo_gravimetrico_final.png`: A publication-ready, 300 DPI high-resolution image capturing both fitting charts and the geological section map.

