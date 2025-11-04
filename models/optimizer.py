from __future__ import annotations
from typing import Dict, Tuple, List
import pandas as pd
import pulp
from .entities import Product, Vehicle, Fleet

class OptimizationResult:
    def __init__(self, x: Dict[Tuple[int, int], int], y: Dict[int, int], status: str):
        self.x = x  # unidades del producto i asignadas al vehículo j
        self.y = y  # 1 si se usa el vehículo j
        self.status = status

class Optimizer:
    def __init__(self, products: List[Product], fleet: Fleet):
        self.products = products
        self.fleet = fleet

    def build_and_solve(self) -> OptimizationResult:
        n_i = len(self.products)
        n_v = len(self.fleet.vehicles)

        # Modelo
        prob = pulp.LpProblem("TruckOptimizer_MILP", pulp.LpMinimize)

        # Variables
        x = pulp.LpVariable.dicts("x", (range(n_i), range(n_v)), lowBound=0, cat=pulp.LpInteger)
        y = pulp.LpVariable.dicts("y", range(n_v), lowBound=0, upBound=1, cat=pulp.LpBinary)

        # Costos por vehículo: tarifa_km * distancia_km (si distancia=0, costo=0, UI lo manejará)
        costos = [v.tarifa_km * (v.distancia_km if v.distancia_km > 0 else 0) for v in self.fleet.vehicles]

        # Objetivo: minimizar costo total
        prob += pulp.lpSum(costos[j] * y[j] for j in range(n_v))

        # Restricciones de asignación: todas las unidades de cada producto deben asignarse
        for i, prod in enumerate(self.products):
            prob += pulp.lpSum(x[i][j] for j in range(n_v)) == prod.cantidad, f"asignacion_total_prod_{i}"

        # Capacidad por vehículo
        for j, veh in enumerate(self.fleet.vehicles):
            prob += pulp.lpSum(self.products[i].peso * x[i][j] for i in range(n_i)) <= veh.capacidad_kg * y[j], f"capacidad_veh_{j}"

        # Límite superior por producto-vehículo (no puedes asignar más unidades que las que existen)
        for i, prod in enumerate(self.products):
            for j in range(n_v):
                prob += x[i][j] <= prod.cantidad, f"upper_x_{i}_{j}"

        # Resolver
        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        status = pulp.LpStatus[prob.status]
        x_sol: Dict[Tuple[int, int], int] = {}
        y_sol: Dict[int, int] = {}

        if status not in ("Optimal", "Feasible"):
            return OptimizationResult(x_sol, y_sol, status)

        for i in range(n_i):
            for j in range(n_v):
                val = int(round(pulp.value(x[i][j]) or 0))
                if val > 0:
                    x_sol[(i, j)] = val

        for j in range(n_v):
            val = int(round(pulp.value(y[j]) or 0))
            y_sol[j] = val

        return OptimizationResult(x_sol, y_sol, status)
