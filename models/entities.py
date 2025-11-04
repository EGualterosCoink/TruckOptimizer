from dataclasses import dataclass
from typing import List, Dict, Optional

ALLOWED_PRODUCTS = [
    "computadores portátiles",
    "computadores de escritorio",
    "televisores inteligentes",
    "smartphones",
    "auriculares",
    "neveras",
    "lavadoras",
    "estufas",
]

@dataclass
class Product:
    nombre: str
    peso: float      # kg por unidad
    valor: float     # moneda por unidad
    cantidad: int    # unidades requeridas

@dataclass
class Vehicle:
    id: str
    tipo: str                # mediano, rígido, tractocamión, etc.
    capacidad_kg: float
    tarifa_km: float
    distancia_km: float = 0  # si no se provee por archivo, se asigna globalmente

class Fleet:
    def __init__(self, vehicles: List[Vehicle]):
        self.vehicles = vehicles

    @property
    def capacidad_total(self) -> float:
        return sum(v.capacidad_kg for v in self.vehicles)

    @property
    def tipos(self) -> List[str]:
        return list(sorted({v.tipo for v in self.vehicles}))

    def por_tipo(self) -> Dict[str, List[Vehicle]]:
        d: Dict[str, List[Vehicle]] = {}
        for v in self.vehicles:
            d.setdefault(v.tipo, []).append(v)
        return d

    def max_capacidad(self) -> float:
        return max((v.capacidad_kg for v in self.vehicles), default=0.0)

    def second_max_capacidad(self) -> float:
        caps = sorted({v.capacidad_kg for v in self.vehicles}, reverse=True)
        return caps[1] if len(caps) >= 2 else (caps[0] if caps else 0.0)
