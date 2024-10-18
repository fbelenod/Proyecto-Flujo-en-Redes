import gurobipy as gp
from gurobipy import GRB

# Parámetros
num_horas = "....xlsx"  # Número de horas del día (índice i)
num_trayectos = "....xlsx"  # Número de trayectos (índice j)
num_buses = "....xlsx"  # Número total de buses en la flota (índice k)

Cap = 50  # Capacidad máxima del bus (50 pasajeros por bus)
h_min = 2  # Frecuencia mínima de viajes por hora para cada bus
h_max = 5  # Frecuencia máxima de viajes por hora para cada bus

# Datos ficticios para costos, precios y satisfacción (se corrigen para la siguiente entrega)
c_ijk = [[[1000 for k in range(num_buses)] for j in range(num_trayectos)] for i in range(num_horas)]
C_fijo_k = [10000 for k in range(num_buses)]
p_ijk = [[[1500 for k in range(num_buses)] for j in range(num_trayectos)] for i in range(num_horas)]
S_ijk = [[[500 for k in range(num_buses)] for j in range(num_trayectos)] for i in range(num_horas)]

# Crear el modelo
model = gp.Model("Optimización_de_autobuses")


# Variables de decisión
# X[i, j, k] es la cantidad de pasajeros transportados en la hora i, trayecto j, bus k
X = model.addVars(num_horas, num_trayectos, num_buses, vtype=GRB.CONTINUOUS, name="X")
# Y[k] es una variable binaria que indica si el bus k está en operación (1) o no (0)
Y = model.addVars(num_buses, vtype=GRB.BINARY, name="Y")



# Funciones Objetivo
# 1. Minimizar los costos totales de operación
# Incluye costos variables asociados con el número de pasajeros y costos fijos por usar cada bus
objetivo1 = gp.quicksum(c_ijk[i][j][k] * X[i, j, k] for i in range(num_horas) for j in range(num_trayectos) for k in range(num_buses)) + \
            gp.quicksum(C_fijo_k[k] * Y[k] for k in range(num_buses))

# 2. Maximizar el beneficio obtenido por los viajes
objetivo2 = gp.quicksum((p_ijk[i][j][k] - c_ijk[i][j][k]) * X[i, j, k] for i in range(num_horas) for j in range(num_trayectos) for k in range(num_buses))

# 3. Minimizar el número de autobuses necesarios
# Reduce la cantidad total de buses en operación, minimizando la suma de Y[k]
objetivo3 = gp.quicksum(Y[k] for k in range(num_buses))

# 4. Maximizar la satisfacción de los pasajeros
# Basado en el tiempo de espera y la regularidad del servicio
objetivo4 = gp.quicksum(S_ijk[i][j][k] * X[i, j, k] for i in range(num_horas) for j in range(num_trayectos) for k in range(num_buses))



# Restricciones
# Restricción 1: Capacidad de los buses
# La cantidad total de pasajeros en cada bus no puede superar su capacidad máxima
model.addConstrs(
    (gp.quicksum(X[i, j, k] for i in range(num_horas)) <= Cap for j in range(num_trayectos) for k in range(num_buses)),
    name="Capacidad")

# Restricción 2: Frecuencia mínima y máxima de viajes para garantizar la calidad del servicio
# Cada bus debe operar dentro de un rango de frecuencia para mantener el servicio regular
model.addConstrs(
    (h_min <= gp.quicksum(X[i, j, k] for i in range(num_horas)) <= h_max for j in range(num_trayectos) for k in range(num_buses)),
    name="Frecuencia")

# Restricción 3: Los autobuses deben comenzar y terminar en el depósito
# Solo los autobuses que inicien o terminen sus trayectos en el depósito son válidos
model.addConstrs(
    (X[i, j, k] >= 0 for i in range(num_horas) for j in range(num_trayectos) for k in range(num_buses)),
    name="Deposito")

# Restricción 4: Unicidad por trayecto
# Cada trayecto entre el origen y el destino debe ser realizado por un solo bus a la vez
model.addConstrs(
    (gp.quicksum(X[i, j, k] for k in range(num_buses)) <= 1 for i in range(num_horas) for j in range(num_trayectos)),
    name="Unicidad")

# Restricción 5: Balance de flujo en nodos
# Asegura que el número de pasajeros que entra y sale en cada nodo sea constante
model.addConstrs(
    (gp.quicksum(X[i, j, k] for j in range(num_trayectos)) - gp.quicksum(X[i, j_prime, k] for j_prime in range(num_trayectos)) == 0
     for i in range(num_horas) for k in range(num_buses)),
    name="Flujo")

#===================================== de aquí para abajo no va incluido en la entrega===============================================
# Optimización para varios objetivos (investigar si se puede optimizar varios objetivos a la vez acá en gurobi)
#optimizamos primero el costo (objetivo1)
#model.setObjective(objetivo1, GRB.MINIMIZE)

# Optimizar el modelo
#model.optimize()

# Evaluar si el modelo encontró una solución óptima
#if model.status == GRB.OPTIMAL:
#    print("\nResultados Óptimos:")
#    for i in range(num_horas):
#        for j in range(num_trayectos):
#            for k in range(num_buses):
#                if X[i, j, k].X > 0:
#                    print(f"Hora {i}, Trayecto {j}, Bus {k}: Pasajeros transportados = {X[i, j, k].X}")
#    for k in range(num_buses):
#        print(f"Bus {k} en operación: {Y[k].X}")
#else:
#    print("No se encontró una solución óptima.")
