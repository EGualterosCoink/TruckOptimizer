from __future__ import annotations
from typing import Dict, Tuple, List
import pandas as pd
from .entities import Product, Vehicle, Fleet

def build_plan_text(products: List[Product], vehicles: List[Vehicle], x_sol: Dict[Tuple[int, int], int]) -> str:
    # Agrupar por vehículo
    by_vehicle: Dict[int, Dict[str, int]] = {}
    for (i, j), units in x_sol.items():
        prod_name = products[i].nombre
        by_vehicle.setdefault(j, {})
        by_vehicle[j][prod_name] = by_vehicle[j].get(prod_name, 0) + units

    lines: List[str] = []
    # Orden por índice de vehículo
    for j in sorted(by_vehicle.keys()):
        veh = vehicles[j]
        lines.append(f"Vehículo {veh.id} {veh.tipo}:")
        for prod_name, qty in by_vehicle[j].items():
            lines.append(f"{qty} cantidad de {prod_name}")
        lines.append("")

    return "\n".join(lines).strip()

def compute_metrics_df(products: List[Product], vehicles: List[Vehicle], x_sol: Dict[Tuple[int, int], int]):
    # Por vehículo
    records = []
    for j, veh in enumerate(vehicles):
        used_kg = 0.0
        value_total = 0.0
        for (i, jj), units in x_sol.items():
            if jj == j:
                used_kg += products[i].peso * units
                value_total += products[i].valor * units
        cost = veh.tarifa_km * (veh.distancia_km if veh.distancia_km > 0 else 0) if used_kg > 0 else 0.0
        pct = (used_kg / veh.capacidad_kg * 100.0) if veh.capacidad_kg > 0 else 0.0
        records.append({
            "vehiculo_id": veh.id,
            "tipo": veh.tipo,
            "kg_usados": used_kg,
            "capacidad_kg": veh.capacidad_kg,
            "porcentaje_capacidad": pct,
            "costo_transporte": cost,
            "valor_transportado": value_total,
        })
    df = pd.DataFrame.from_records(records)
    return df

def compute_totals(df_metrics: pd.DataFrame):
    kg_totales = float(df_metrics["kg_usados"].sum())
    capacidad_total = float(df_metrics["capacidad_kg"].sum())
    pct_general = (kg_totales / capacidad_total * 100.0) if capacidad_total > 0 else 0.0
    costo_total = float(df_metrics["costo_transporte"].sum())
    valor_total = float(df_metrics["valor_transportado"].sum())
    return kg_totales, pct_general, costo_total, valor_total
