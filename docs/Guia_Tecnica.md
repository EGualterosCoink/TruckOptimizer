# Guía Técnica — TruckOptimizer

## Arquitectura (POO)
- **models/entities.py**: `Product`, `Vehicle`, `Fleet` y `ALLOWED_PRODUCTS`.
- **models/io_utils.py**: lectura de CSV/XLSX y construcción de objetos.
- **models/validators.py**: validaciones y mensajes **exactos** a especificación.
- **models/optimizer.py**: formulación **MILP** con PuLP (`x[i,v]` entero, `y[v]` binario).
- **models/metrics.py**: plan de acción y métricas agregadas.
- **app.py**: UI con Streamlit (página plana), escenarios ESC-01/02/03.

## Modelo MILP
- **Objetivo**: minimizar `Σ_v (tarifa_km_v * distancia_km_v * y[v])`.
- **Restricciones**:
  - `Σ_v x[i,v] = cantidad_i` (asignar todas las unidades).
  - `Σ_i (peso_i * x[i,v]) ≤ capacidad_v * y[v]` (capacidad).
  - `0 ≤ x[i,v] ≤ cantidad_i`, `y[v] ∈ {0,1}`.

## Validaciones clave
- Columnas obligatorias y tipos numéricos/positivos.
- Duplicados de tipo (flota) y producto (items).
- Productos permitidos (lista fija).
- Peso unitario no supera **capacidad máxima** de la flota.
- Peso total no supera **capacidad total** de la flota.
- Chequeo preventivo de disponibilidad de vehículos de **gran capacidad**.

## Dependencias
- **NumPy/Pandas/PuLP/Matplotlib/openpyxl/Streamlit** (todo local).
- Solver por defecto: **CBC** (vía PuLP).

## Ejecución y empaquetado
- Local: `streamlit run app.py`
- Templates de entrada en `assets/templates/`.

