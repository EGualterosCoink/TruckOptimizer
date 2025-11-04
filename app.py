\
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from models.entities import Fleet
from models.io_utils import read_table, build_fleet_from_df, build_products_from_df
from models.validators import (
    validate_extension,
    validate_fleet_df,
    validate_products_df,
)
from models.optimizer import Optimizer
from models.metrics import build_plan_text, compute_metrics_df, compute_totals

st.set_page_config(page_title="TruckOptimizer", page_icon="🚚", layout="wide")

st.title("🚚 TruckOptimizer")
st.caption("Optimización de carga y asignación de vehículos — versión local académica")

if "fleet_ready" not in st.session_state:
    st.session_state["fleet_ready"] = False
if "fleet" not in st.session_state:
    st.session_state["fleet"] = None
if "fleet_df" not in st.session_state:
    st.session_state["fleet_df"] = None
if "products_df" not in st.session_state:
    st.session_state["products_df"] = None

st.markdown("### 1) Parametrización de **Flota**")
st.write("Formato requerido (.csv/.xlsx) con columnas obligatorias:")
st.code("Tipo de camión | Peso que puede cargar (kg) | Tarifa por kilómetro recorrido | Cantidad [| Distancia (km) opcional]", language="text")
fleet_file = st.file_uploader("Cargar archivo de flota", type=["csv", "xlsx"], key="fleet_uploader")
distancia_global = st.number_input("Distancia (km) global (se usará si el archivo no trae 'Distancia (km)')", min_value=0.0, step=10.0, value=0.0)

col_a, col_b = st.columns([1,1])
with col_a:
    if st.button("Cargar Flota", use_container_width=True):
        if not fleet_file:
            st.error("No se ha cargado ningún archivo.")
        else:
            ok, msg = validate_extension(fleet_file.name)
            if not ok:
                st.error(msg)
            else:
                try:
                    df = read_table(fleet_file.getvalue(), fleet_file.name)
                    st.write("Columnas leídas:", list(df.columns))
                    # --- (A) Normaliza a encabezados del DOC antes de validar ---
                    import unicodedata, re
                    def _canon(s: str) -> str:
                        s = unicodedata.normalize("NFKD", str(s))
                        s = "".join(ch for ch in s if not unicodedata.combining(ch))
                        s = s.lower()
                        s = s.replace("_", " ")
                        s = re.sub(r"\s+", " ", s).strip()
                        return s

                    RAW_STANDARD = {
                        # Tipo
                        "tipo de camion": "tipo de camión",
                        "tipo camion": "tipo de camión",
                        "tipo": "tipo de camión",
                        "tipo de camión": "tipo de camión",
                        # Capacidad
                        "peso que puede cargar (kg)": "peso que puede cargar (kg)",
                        "peso que puede cargar": "peso que puede cargar (kg)",
                        "capacidad (kg)": "peso que puede cargar (kg)",
                        "capacidad": "peso que puede cargar (kg)",
                        # Tarifa
                        "tarifa por kilometro recorrido": "tarifa por kilómetro recorrido",
                        "tarifa por kilómetro recorrido": "tarifa por kilómetro recorrido",
                        "tarifa km": "tarifa por kilómetro recorrido",
                        # Cantidad
                        "cantidad": "cantidad",
                        # Distancia (opcional)
                        "distancia (km)": "distancia (km)",
                        "distancia km": "distancia (km)",
                        "distancia_km": "distancia (km)",
                        "distancia": "distancia (km)",
                    }
                    df.columns = [RAW_STANDARD.get(_canon(c), c) for c in df.columns]

                    # --- (B) Valida con los nombres del documento ---
                    ok2, msg2 = validate_fleet_df(df.copy())
                    if not ok2:
                        st.error(msg2)
                    else:
                        # --- (C) Renombra a llaves internas para los modelos ---
                        df = df.rename(columns={
                            "tipo de camión": "tipo_camion",
                            "peso que puede cargar (kg)": "capacidad_kg",
                            "tarifa por kilómetro recorrido": "tarifa_km",
                            "cantidad": "cantidad",
                            "distancia (km)": "distancia_km",
                        })
                        # (por si viene ya como 'distancia_km')
                        df.columns = [c.strip().lower() for c in df.columns]

                        fleet = build_fleet_from_df(df.copy(), distancia_global_km=distancia_global)
                        st.session_state["fleet"] = fleet
                        st.session_state["fleet_df"] = df
                        st.session_state["fleet_ready"] = True
                        st.success("Archivo cargado correctamente.")
                except Exception as e:
                    st.error(f"Error al cargar flota: {e}")
                    st.exception(e)

with col_b:
    if st.session_state["fleet_ready"]:
        with st.expander("Ver flota procesada"):
            st.dataframe(st.session_state["fleet_df"])

st.divider()

st.markdown("### 2) Carga de **Productos** y cálculo de optimización")
st.write("Formato requerido (.csv/.xlsx) con columnas obligatorias:")
st.code("Producto | Peso | Valor | Cantidad", language="text")
products_file = st.file_uploader("Cargar archivo de productos", type=["csv", "xlsx"], key="products_uploader")

calc_col1, calc_col2 = st.columns([1,2])
with calc_col1:
    if st.button("Calcular Optimización", use_container_width=True):
        if not st.session_state["fleet_ready"]:
            st.error("Primero debe parametrizar y cargar la flota (ESC-01).")
        elif not products_file:
            st.error("No se ha cargado ningún archivo.")
        else:
            ok, msg = validate_extension(products_file.name)
            if not ok:
                st.error(msg)
            else:
                try:
                    dfp = read_table(products_file.getvalue(), products_file.name)
                    okp, msgp = validate_products_df(dfp.copy(), st.session_state["fleet"])
                    if not okp:
                        st.error(msgp)
                    else:
                        # Normaliza encabezados
                        dfp.columns = [c.strip().lower() for c in dfp.columns]
                        products = build_products_from_df(dfp.copy())
                        opt = Optimizer(products, st.session_state["fleet"])
                        result = opt.build_and_solve()
                        if result.status not in ("Optimal", "Feasible"):
                            st.error("No fue posible encontrar una solución factible.")
                        else:
                            st.session_state["products_df"] = dfp
                            st.session_state["opt_result"] = result
                            st.session_state["products"] = products
                            st.success("Optimización completada.")
                except Exception as e:
                    import traceback
                    st.error(f"Error al calcular la optimización: {e}")
                    st.exception(e)


with calc_col2:
    st.info("Ayuda contextual: Cargue primero la flota. El sistema valida columnas, datos nulos, duplicados, valores negativos / cero y productos no contemplados.")

st.divider()

st.markdown("### 3) Plan de acción y **métricas** (ESC-03)")

if "opt_result" in st.session_state:
    result = st.session_state["opt_result"]
    products = st.session_state["products"]
    fleet = st.session_state["fleet"]
    # Plan de acción en texto
    plan_text = build_plan_text(products, fleet.vehicles, result.x)
    st.subheader("Plan de carga")
    st.code(plan_text or "Sin asignaciones.", language="text")

    # Métricas por vehículo
    df_metrics = compute_metrics_df(products, fleet.vehicles, result.x)

    # Totales
    kg_totales, pct_general, costo_total, valor_total = compute_totals(df_metrics)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Kg totales transportados", f"{kg_totales:,.2f} kg")
    m2.metric("Porcentaje de capacidad general", f"{pct_general:,.2f}%")
    m3.metric("Costo de transporte total", f"${costo_total:,.2f}")
    m4.metric("Valor total transportado", f"${valor_total:,.2f}")

    # Gráfico: Kg usados por vehículo
    st.markdown("##### Kg usados por vehículo")
    fig1, ax1 = plt.subplots()
    ax1.bar(df_metrics["vehiculo_id"], df_metrics["kg_usados"])
    ax1.set_xlabel("Vehículo")
    ax1.set_ylabel("Kg usados")
    ax1.set_xticklabels(df_metrics["vehiculo_id"], rotation=45, ha="right")
    st.pyplot(fig1, clear_figure=True)

    # Gráfico: costo por tipo de vehículo (agrupado)
    st.markdown("##### Costo de transporte por tipo de vehículo")
    df_cost_tipo = df_metrics.groupby("tipo", as_index=False)["costo_transporte"].sum()
    fig2, ax2 = plt.subplots()
    ax2.bar(df_cost_tipo["tipo"], df_cost_tipo["costo_transporte"])
    ax2.set_xlabel("Tipo de vehículo")
    ax2.set_ylabel("Costo transporte")
    st.pyplot(fig2, clear_figure=True)

    # Gráfico: valor transportado por vehículo
    st.markdown("##### Valor total transportado por vehículo")
    fig3, ax3 = plt.subplots()
    ax3.bar(df_metrics["vehiculo_id"], df_metrics["valor_transportado"])
    ax3.set_xlabel("Vehículo")
    ax3.set_ylabel("Valor transportado")
    ax3.set_xticklabels(df_metrics["vehiculo_id"], rotation=45, ha="right")
    st.pyplot(fig3, clear_figure=True)

    # Descargas
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button("Descargar métricas (CSV)", data=df_metrics.to_csv(index=False).encode("utf-8"), file_name="metricas_por_vehiculo.csv", mime="text/csv", use_container_width=True)
    with col_d2:
        st.download_button("Descargar plan de carga (TXT)", data=(plan_text or "").encode("utf-8"), file_name="plan_carga.txt", mime="text/plain", use_container_width=True)

else:
    st.warning("Para ver resultados, complete los pasos 1 y 2 y ejecute la optimización.")
