from __future__ import annotations
import math
import pandas as pd
from typing import List, Tuple, Dict, Any
from .entities import ALLOWED_PRODUCTS
from .entities import Vehicle, Fleet

# Helpers
def _is_number(x) -> bool:
    try:
        if pd.isna(x):
            return False
        float(x)
        return True
    except Exception:
        return False

def validate_extension(file_name: str) -> Tuple[bool, str]:
    if not file_name:
        return False, "No se ha cargado ningún archivo."
    if not (file_name.lower().endswith(".csv") or file_name.lower().endswith(".xlsx")):
        return False, "Formato o extensión de archivo no válido."
    return True, ""

def validate_fleet_df(df: pd.DataFrame) -> Tuple[bool, str]:
    # Columnas requeridas (distancia_km es opcional; RF1.1 pide distancias, se permite aquí o vía UI)
    required = {"tipo de camión", "peso que puede cargar (kg)", "tarifa por kilómetro recorrido", "cantidad"}
    # Normalizar columnas
    cols_norm = [c.strip().lower() for c in df.columns]
    df.columns = cols_norm

    # map human-friendly to normalized keys
    mapping = {
        "tipo de camión": "tipo_camion",
        "peso que puede cargar (kg)": "capacidad_kg",
        "tarifa por kilómetro recorrido": "tarifa_km",
        "cantidad": "cantidad",
        "distancia (km)": "distancia_km",
        "distancia_km": "distancia_km",
        "distancia": "distancia_km",
    }
    # Check required set present (allow extra columns)
    raw_required = {"tipo de camión", "peso que puede cargar (kg)", "tarifa por kilómetro recorrido", "cantidad"}
    if not raw_required.issubset(set(cols_norm)):
        return False, "Columnas no válidas en el archivo."

    # rename
    df = df.rename(columns=mapping)

    # nulos
    if df.isna().any().any():
        return False, "No se pueden dejar celdas vacías."

    # duplicados de tipo de camión (debe haber un solo registro por tipo; la cantidad indica cuántos hay)
    if df.duplicated(subset=["tipo_camion"]).any():
        return False, "Existen tipos de camiones duplicados."

    # valores no válidos
    for col in ["capacidad_kg", "tarifa_km", "cantidad"]:
        for v in df[col].tolist():
            if not _is_number(v) or float(v) <= 0 or (col == "cantidad" and float(v) != int(float(v))):
                return False, f"En la columna {col} no se puede estipular el valor '{v}'."

    # distancia_km (si existe)
    if "distancia_km" in df.columns:
        for v in df["distancia_km"].tolist():
            if not _is_number(v) or float(v) <= 0:
                return False, f"En la columna distancia_km no se puede estipular el valor '{v}'."

    return True, ""

def validate_products_df(df: pd.DataFrame, fleet: Fleet) -> Tuple[bool, str]:
    # Normalizar columnas
    cols_norm = [c.strip().lower() for c in df.columns]
    df.columns = cols_norm
    # Required
    required = {"producto", "peso", "valor", "cantidad"}
    if not required.issubset(set(cols_norm)):
        return False, "Columnas no válidas en el archivo."

    # nulos
    if df.isna().any().any():
        return False, "No se pueden dejar celdas vacías."

    # duplicados de producto
    if df.duplicated(subset=["producto"]).any():
        return False, "Existen productos duplicados"

    # producto no contemplado
    # Normalizamos a minúsculas con tildes tal cual en ALLOWED_PRODUCTS
    allowed_lower = set([p.lower() for p in ALLOWED_PRODUCTS])
    for p in df["producto"].astype(str).str.strip().str.lower().tolist():
        if p not in allowed_lower:
            return False, "Hay productos no contemplados"

    # números válidos (>0 y numéricos)
    for col in ["peso", "valor", "cantidad"]:
        for v in df[col].tolist():
            if not _is_number(v) or float(v) <= 0 or (col == "cantidad" and float(v) != int(float(v))):
                return False, f"En la columna {col} no se puede estipular el valor '{v}'."

    # producto individual demasiado pesado
    max_cap = fleet.max_capacidad()
    if any(float(w) > max_cap for w in df["peso"].tolist()):
        # Encontrar el producto
        row = df.iloc[[float(w) > max_cap for w in df["peso"].tolist()]].iloc[0]
        return False, f"El producto {row['producto']} no se puede transportar."

    # exceso de capacidad total
    total_peso = float((df["peso"] * df["cantidad"]).sum())
    if total_peso > fleet.capacidad_total:
        return False, "Los productos exceden el límite de capacidad, no se pueden transportar, se solicita fraccionar el pedido."

    # vehículos de gran capacidad llenos... (heurística de validación previa)
    # Detectamos items que solo caben en el vehículo de mayor capacidad (peso > segunda mayor capacidad)
    second_max = fleet.second_max_capacidad()
    # peso unitario de productos "muy pesados" (requieren max)
    pesados = df[df["peso"] > second_max] if second_max > 0 else df.iloc[0:0]
    if not pesados.empty:
        # capacidad total de los vehículos de máxima capacidad
        max_cap = fleet.max_capacidad()
        from collections import Counter
        # contar vehículos de capacidad máxima
        caps = [v.capacidad_kg for v in fleet.vehicles]
        if not caps:
            return False, "Los productos exceden el límite de capacidad, no se pueden transportar, se solicita fraccionar el pedido."
        max_c = max(caps)
        n_max = sum(1 for v in fleet.vehicles if v.capacidad_kg == max_c)
        capacidad_total_max = n_max * max_c
        # peso requerido por productos que solo caben en max
        peso_requerido_pesados = float((pesados["peso"] * pesados["cantidad"]).sum())
        if peso_requerido_pesados > capacidad_total_max:
            return False, "Vehículos de gran capacidad no disponibles para llevar productos pesados, se solicita fraccionar el pedido."

    return True, ""
