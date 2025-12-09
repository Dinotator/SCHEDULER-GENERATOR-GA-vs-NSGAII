import random
import matplotlib.pyplot as plt
import copy
import math

# Parámetros del Algoritmo

POPULATION_SIZE = 50
GENERATIONS = 100
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.9 
NUM_AULAS_TOTALES = 2 
HORARIOS = ['H1', 'H2', 'H3', 'H4', 'H5']

class Asignatura:
    def __init__(self, id_asig, nombre, id_profesor):
        self.id_asig = id_asig
        self.nombre = nombre
        self.id_profesor = id_profesor

class Profesor:
    def __init__(self, id_prof, nombre, preferencias):
        self.id_prof = id_prof
        self.nombre = nombre
        self.preferencias = preferencias

# Dataset de prueba
profesores_db = [
    Profesor(1, "Prof. A", {'H1': 0, 'H2': 1, 'H3': 0, 'H4': 1, 'H5': 0}),
    Profesor(2, "Prof. B", {'H2': 0, 'H3': 0, 'H4': 1}),
    Profesor(3, "Prof. C", {'H1': 1, 'H2': 0, 'H5': 0}),
]

asignaturas_db = [
    Asignatura(101, "Sistemas Exp.", 1),
    Asignatura(102, "Prog. Avanzada", 1),
    Asignatura(103, "Redes", 2),
    Asignatura(104, "Bases de Datos", 2),
    Asignatura(105, "Ing. Software", 3),
    Asignatura(106, "Algoritmos", 3),
]

# Clase Individuo para NSGA-II

class Individuo:
    def __init__(self, genes=None):
        if genes:
            self.genes = genes
        else:
            self.genes = [None] * len(asignaturas_db)
            self.inicializar_aleatorio()
        
        # Primer Objetivo: Minimizar conflictos, 
        # Segundo Objetivo: Preferencias
        self.objectives = [0, 0] 
        self.rank = 0
        self.crowding_dist = 0
        self.domination_count = 0
        self.dominated_solutions = []
        
        self.calcular_objetivos()

    def inicializar_aleatorio(self):
        for i, asig in enumerate(asignaturas_db):
            prof = next(p for p in profesores_db if p.id_prof == asig.id_profesor)
            horarios_validos = list(prof.preferencias.keys())
            self.genes[i] = random.choice(horarios_validos)

    def calcular_objetivos(self):
        # Hard constraints
        conflictos = 0
        
        # Docente duplicado
        for prof in profesores_db:
            horarios_prof = []
            for i, h in enumerate(self.genes):
                if asignaturas_db[i].id_profesor == prof.id_prof:
                    horarios_prof.append(h)
            for h in set(horarios_prof):
                nph = horarios_prof.count(h)
                if nph > 1:
                    conflictos += (nph - 1) #

        # Falta de aulas
        all_horarios = self.genes
        for h in set(all_horarios):
            num_hor = all_horarios.count(h)
            if num_hor > NUM_AULAS_TOTALES:
                conflictos += (num_hor - NUM_AULAS_TOTALES) #

        # Soft constraint
        # Preferencias
        costo_preferencias = 0
        for i, horario in enumerate(self.genes):
            asig = asignaturas_db[i]
            prof = next(p for p in profesores_db if p.id_prof == asig.id_profesor)
            costo_preferencias += prof.preferencias.get(horario, 100)

        self.objectives = [conflictos, costo_preferencias]

# Lógica de NSGA-II

def domina(ind1, ind2):
    """Devuelve True si ind1 domina a ind2 (Menor es mejor en ambos objetivos)"""
    and_condition = True
    or_condition = False
    for i in range(len(ind1.objectives)):
        if ind1.objectives[i] > ind2.objectives[i]:
            and_condition = False
        if ind1.objectives[i] < ind2.objectives[i]:
            or_condition = True
    return and_condition and or_condition

def fast_non_dominated_sort(poblacion):
    fronts = [[]]
    for p in poblacion:
        p.dominated_solutions = []
        p.domination_count = 0
        for q in poblacion:
            if domina(p, q):
                p.dominated_solutions.append(q)
            elif domina(q, p):
                p.domination_count += 1
        if p.domination_count == 0:
            p.rank = 0
            fronts[0].append(p)
    
    i = 0
    while len(fronts[i]) > 0:
        next_front = []
        for p in fronts[i]:
            for q in p.dominated_solutions:
                q.domination_count -= 1
                if q.domination_count == 0:
                    q.rank = i + 1
                    next_front.append(q)
        i += 1
        fronts.append(next_front)
    
    return fronts[:-1]

def calculate_crowding_distance(front):
    if len(front) == 0: return
    l = len(front)
    for ind in front:
        ind.crowding_dist = 0
    
    num_obj = len(front[0].objectives)
    
    for m in range(num_obj):
        # Ordenar por el objetivo m
        front.sort(key=lambda x: x.objectives[m])
        
        # Puntos extremos tienen distancia infinita
        front[0].crowding_dist = float('inf')
        front[l-1].crowding_dist = float('inf')
        
        m_min = front[0].objectives[m]
        m_max = front[l-1].objectives[m]
        
        if m_max == m_min: continue

        for i in range(1, l-1):
            front[i].crowding_dist += (front[i+1].objectives[m] - front[i-1].objectives[m]) / (m_max - m_min)

def operador_cruce_mutacion(poblacion):
    # Generar descendencia
    offspring = []
    while len(offspring) < len(poblacion):
        # Torneo Binario basado en Rank y Crowding Distance
        p1 = torneo_nsga2(poblacion)
        p2 = torneo_nsga2(poblacion)
        
        if random.random() < CROSSOVER_RATE:
            # Cruce Monopunto
            punto = random.randint(1, len(p1.genes) - 1)
            h1_genes = p1.genes[:punto] + p2.genes[punto:]
            h2_genes = p2.genes[:punto] + p1.genes[punto:]
            h1, h2 = Individuo(h1_genes), Individuo(h2_genes)
        else:
            h1, h2 = copy.deepcopy(p1), copy.deepcopy(p2)
        
        # Mutación
        mutar(h1)
        mutar(h2)
        offspring.extend([h1, h2])
    return offspring

def torneo_nsga2(poblacion):
    i1, i2 = random.sample(poblacion, 2)
    # Gana quien tenga mejor rango (menor número)
    if i1.rank < i2.rank: return i1
    elif i2.rank < i1.rank: return i2
    # Si empatan en rango, gana quien tenga mayor distancia (el más aislado)
    else:
        if i1.crowding_dist > i2.crowding_dist: return i1
        else: return i2

def mutar(ind):
    if random.random() < MUTATION_RATE:
        idx = random.randint(0, len(ind.genes) - 1)
        asig = asignaturas_db[idx]
        prof = next(p for p in profesores_db if p.id_prof == asig.id_profesor)
        horarios_validos = list(prof.preferencias.keys())
        ind.genes[idx] = random.choice(horarios_validos)
        ind.calcular_objetivos()

# Mostrar horario
def visualizar_horario(mejor_individuo):
    tabla_datos = [["" for _ in HORARIOS] for _ in range(NUM_AULAS_TOTALES)]
    ocupacion = {h: 0 for h in HORARIOS}
    
    for i, h_asig in enumerate(mejor_individuo.genes):
        asig = asignaturas_db[i]
        prof = next(p for p in profesores_db if p.id_prof == asig.id_profesor)
        texto = f"{asig.nombre}\n({prof.nombre})"
        
        if h_asig in HORARIOS:
            idx = HORARIOS.index(h_asig)
            fila = ocupacion[h_asig]
            if fila < NUM_AULAS_TOTALES:
                tabla_datos[fila][idx] = texto
                ocupacion[h_asig] += 1
            else:
                tabla_datos[NUM_AULAS_TOTALES-1][idx] += f"\n!{texto}!"

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_axis_off()
    tabla = ax.table(cellText=tabla_datos, rowLabels=[f"Aula {i+1}" for i in range(NUM_AULAS_TOTALES)],
                     colLabels=HORARIOS, cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(9)
    plt.title(f"Mejor Solución NSGA-II\nConflictos: {mejor_individuo.objectives[0]} | Costo Pref: {mejor_individuo.objectives[1]}")
    plt.show()

# Clase main

def main():
    # Población Inicial
    poblacion = [Individuo() for _ in range(POPULATION_SIZE)]
    
    print(f"Ejecutando NSGA-II por {GENERATIONS} generaciones...")
    
    # Historial para graficar el Frente de Pareto final
    history_frentes = []

    for gen in range(GENERATIONS):
        # 2. Generar Hijos
        offspring = operador_cruce_mutacion(poblacion)
        
        # 3. Combinar
        union_poblacion = poblacion + offspring
        
        # 4. Clasificación por Frentes
        frentes = fast_non_dominated_sort(union_poblacion)
        
        # 5. Crear nueva población
        nueva_poblacion = []
        i = 0
        while len(nueva_poblacion) + len(frentes[i]) <= POPULATION_SIZE:
            calculate_crowding_distance(frentes[i])
            nueva_poblacion.extend(frentes[i])
            i += 1
            if i >= len(frentes): break
        
        if len(nueva_poblacion) < POPULATION_SIZE and i < len(frentes):
            calculate_crowding_distance(frentes[i])
            frentes[i].sort(key=lambda x: x.crowding_dist, reverse=True)
            faltantes = POPULATION_SIZE - len(nueva_poblacion)
            nueva_poblacion.extend(frentes[i][:faltantes])
            
        poblacion = nueva_poblacion
        
        # Respuesta en consola
        mejor_conflictos = min(p.objectives[0] for p in poblacion)
        print(f"Gen {gen}: Min Conflictos = {mejor_conflictos}")

    # Filtramos solo las soluciones del Frente 1
    frente_pareto = [ind for ind in poblacion if ind.rank == 0]
    
    # Buscamos una solución balanceada 
    # Priorizamos Cero conflictos y menor costo de preferencias
    soluciones_validas = [ind for ind in frente_pareto if ind.objectives[0] == 0]
    
    if soluciones_validas:
        mejor_solucion = min(soluciones_validas, key=lambda x: x.objectives[1])
        print("\n¡Solución Válida Encontrada!")
    else:
        mejor_solucion = min(frente_pareto, key=lambda x: x.objectives[0]) 
        print("\nNo se halló solución perfecta, mostrando la mejor aproximación.")

    # Mostrar en gráfica la frente de pareto
    obj1 = [ind.objectives[0] for ind in poblacion] # Conflictos
    obj2 = [ind.objectives[1] for ind in poblacion] # Preferencias
    
    plt.figure(figsize=(10, 6))
    plt.scatter(obj2, obj1, c='blue', alpha=0.5, label='Individuos finales')
    plt.xlabel('Objetivo 2: Costo de Preferencias (Minimizar)')
    plt.ylabel('Objetivo 1: Conflictos/Restricciones (Minimizar)')
    plt.title('Frente de Pareto Final (NSGA-II)')
    plt.axhline(y=0, color='r', linestyle='--', label='Zona Válida (0 conflictos)')
    plt.legend()
    plt.grid(True)
    plt.show()

    visualizar_horario(mejor_solucion)

if __name__ == "__main__":
    main()