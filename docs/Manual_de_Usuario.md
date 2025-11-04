# Manual de Usuario — TruckOptimizer

## 1. Inicio
Ejecuta:
```
streamlit run app.py
```
Se abrirá la UI local en tu navegador (desktop).

## 2. Escenario ESC-01 — Parametrización de flota
1. En la sección **Flota**, carga el archivo `.csv` o `.xlsx` con columnas:
   - **Tipo de camión**
   - **Peso que puede cargar (kg)**
   - **Tarifa por kilómetro recorrido**
   - **Cantidad**
   - *(Opcional)* **Distancia (km)**
2. Si el archivo no trae **Distancia (km)**, usa el campo **Distancia (km) global** para aplicarla a todos los vehículos.
3. Presiona **Cargar Flota**. Si hay errores, se muestran mensajes claros (por ejemplo: columnas inválidas, valores no numéricos/≤0, duplicados).

## 3. Escenario ESC-02 — Carga de productos y cálculo
1. En **Carga de Productos**, sube el archivo `.csv`/`.xlsx` con columnas:
   - **Producto** (solo los contemplados)
   - **Peso**
   - **Valor**
   - **Cantidad**
2. Presiona **Calcular Optimización**. El sistema valida formato, nulos, duplicados, valores, productos no contemplados y capacidad (total e individual).

## 4. Escenario ESC-03 — Resultados y métricas
- Se muestra el **plan de carga** en texto plano por vehículo.
- **Métricas**:
  - Kg totales
  - % de capacidad general
  - Costo total
  - Valor total
- **Gráficos de barras**:
  - Kg usados por vehículo
  - Costo por tipo de vehículo
  - Valor transportado por vehículo
- **Descargas**: plan (TXT) y métricas (CSV).

## 5. Ayuda contextual
- Mensajes en la UI guían los formatos y errores comunes.
- Si ocurre un error inesperado durante la lectura, intenta limpiar el archivo (encabezados exactos, sin celdas vacías, sin fórmulas).

