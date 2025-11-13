from __future__ import annotations
import io
import pandas as pd
from typing import Tuple
from .entities import Product, Vehicle, Fleet

def read_table(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    if file_name.lower().endswith(".csv"):
        for enc in ("utf-8-sig", "cp1252", "latin1"):
            try:
                return pd.read_csv(
                    io.BytesIO(file_bytes),
                    sep=None,
                    engine="python",
                    encoding=enc
                )
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(
            "csv", b"", 0, 1,
            "No se pudo decodificar el CSV. Guárdalo como 'CSV UTF-8 (delimitado por comas)' o envíalo como .xlsx"
        )
    elif file_name.lower().endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(file_bytes))
    else:
        raise ValueError("Formato o extensión de archivo no válido.")

def build_fleet_from_df(df: pd.DataFrame, distancia_global_km: float | None = None):
    # Ya normalizado en validators
    # Esperamos columnas: tipo_camion, capacidad_kg, tarifa_km, cantidad.
    # Cualquier columna de distancia que venga en el DF se ignora.
    vehicles = []
    counters_per_type = {}

    # Distancia que se aplicará a TODOS los camiones
    distancia_default = float(distancia_global_km or 0.0)

    for _, row in df.iterrows():
        tipo = str(row["tipo_camion"]).strip()
        capacidad = float(row["capacidad_kg"])
        tarifa = float(row["tarifa_km"])
        cantidad = int(row["cantidad"])

        counters_per_type.setdefault(tipo, 0)
        for _i in range(cantidad):
            counters_per_type[tipo] += 1
            veh_id = f"{tipo}-{counters_per_type[tipo]}"
            vehicles.append(
                Vehicle(
                    id=veh_id,
                    tipo=tipo,
                    capacidad_kg=capacidad,
                    tarifa_km=tarifa,
                    distancia_km=distancia_default,  # 👈 SIEMPRE la global
                )
            )

    return Fleet(vehicles)

def build_products_from_df(df: pd.DataFrame):
    products = []
    for _, row in df.iterrows():
        products.append(
            Product(
                nombre=str(row["producto"]).strip().lower(),
                peso=float(row["peso"]),
                valor=float(row["valor"]),
                cantidad=int(row["cantidad"]),
            )
        )
    return products
