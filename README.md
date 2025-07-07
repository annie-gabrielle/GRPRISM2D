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

