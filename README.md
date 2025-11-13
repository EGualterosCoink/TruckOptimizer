# TruckOptimizer (versión local académica)

**Página plana sin login** para optimización de carga y asignación de vehículos, construida en **Python** con **NumPy/Pandas/PuLP** y una UI local con Streamlit. Cumple los escenarios y requisitos funcionales/no funcionales del documento.

## Requisitos
- Python 3.10+
- Navegador de escritorio (Chrome/Firefox/Edge)

## Instalación
```bash
cd TruckOptimizer
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución (entorno local)
```bash
streamlit run app.py
```
Abrirá la UI en tu navegador.

## Plantillas de datos
En `assets/templates` hay ejemplos de archivos:

- `flota_template.csv` → columnas: `Tipo de camión, Peso que puede cargar (kg), Tarifa por kilómetro recorrido, Cantidad, Distancia (km opcional)`
- `productos_template.csv` → columnas: `Producto, Peso, Valor, Cantidad`

## Mapeo a requisitos
- **RF1.1** Parametrizar tarifas y distancias por tipo: se cargan desde el archivo de flota; si no trae distancia, se puede definir **Distancia (km) global** en la UI.
- **RF1.2–RF1.3** Carga y validación de archivo de productos y flota (.csv/.xlsx) con mensajes **exactos** del documento.
- **RF1.4** Modelo **MILP** (PuLP) que asigna unidades a vehículos con restricción de capacidad y variable binaria de uso por vehículo, minimizando `∑ (tarifa_km * distancia_km * y_veh)`.
- **RF1.5–RF1.6** Plan de acción por vehículo y métricas (kg usados, % capacidad, costo total y valor transportado) + **3 gráficos de barras**.

- **RNF1.1–RNF1.2** UI simple, consistente; navegación clara en desktop.
- **RNF1.3–RNF1.5** Proceso en memoria, tiempos interactivos para tamaños pequeños/medios.
- **RNF1.6–RNF1.7** Cálculos vectorizados (Pandas/NumPy) y solver eficiente (CBC/PuLP).
- **RNF1.8** Solo navegadores de escritorio.
- **RNF1.9–RNF1.11** Python + **NumPy, Pandas, PuLP**, diseño **POO** (clases Product, Vehicle, Fleet, Optimizer, Métricas).
- **RNF1.10** Sin nube ni BD; todo local.
- **RNF1.12** Sin salida a terceros; archivos se procesan localmente.
- **RNF1.15** Mensajes de ayuda y validación en la UI.
- **RNF1.16** Se incluyen **manual de usuario** y **guía técnica** en `docs/` (puedes exportar a PDF).

## Notas de modelo
- Variables: `x[i,v]` (enteras, unidades del producto `i` en vehículo `v`), `y[v]` (binaria: se usa vehículo `v`).
- Capacidad: `Σ_i (peso_i * x[i,v]) ≤ capacidad_v * y[v]`.
- Asignación total: `Σ_v x[i,v] = cantidad_i`.
- Costo: `Σ_v (tarifa_km_v * distancia_km_v * y[v])`.

## Errores/validaciones (mensajes exactos)
- Extensión: **"Formato o extensión de archivo no válido."**
- Vacío: **"No se ha cargado ningún archivo."**
- Columnas: **"Columnas no válidas en el archivo."**
- Nulos: **"No se pueden dejar celdas vacías."**
- Duplicados:
  - Flota: **"Existen tipos de camiones duplicados."**
  - Productos: **"Existen productos duplicados"**
- No contemplados: **"Hay productos no contemplados"**
- Valores inválidos: **"En la columna {columna_de_error} no se puede estipular el valor '{Valor_no_valido}'."**
- Exceso capacidad: **"Los productos exceden el límite de capacidad, no se pueden transportar, se solicita fraccionar el pedido."**
- Item muy pesado: **"El producto {prodcuto_muy_pesado} no se puede transportar."**
- Faltan gigantes: **"Vehículos de gran capacidad no disponibles para llevar productos pesados, se solicita fraccionar el pedido."**

## Exportables
- Plan de carga (TXT)
- Métricas por vehículo (CSV)
- 
## Comandos en powershell
- Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
- cd "C:\Users\Estefany Gualteros\Downloads\TruckOptimizer"
- .\.venv\Scripts\Activate.ps1
- pip install -r requirements.txt
- python -m pip install --upgrade pip
- python -m pip install -r requirements.txt
- streamlit run app.py
- python -m streamlit run app.py

## Estructura
```
TruckOptimizer/
  app.py
  requirements.txt
  models/
    entities.py
    io_utils.py
    optimizer.py
    metrics.py
    validators.py
  assets/
    templates/
      flota_template.csv
      productos_template.csv
  docs/
    Manual_de_Usuario.md
    Guia_Tecnica.md
```

