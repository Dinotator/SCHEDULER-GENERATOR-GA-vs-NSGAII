import random
import matplotlib.pyplot as plt
import copy

# Parámetros del Algoritmo Genético
POPULATION_SIZE = 50
GENERATIONS = 100
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.8
PENALIZACION = 1000 

# Restricciones Físicas
NUM_AULAS_TOTALES = 2 

# Definición de horarios posibles
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

# Datos de prueba
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

# Clase del Individuo

class Individuo:
    def __init__(self, genes=None):
        if genes:
            self.genes = genes
        else:
            self.genes = [None] * len(asignaturas_db)
            self.inicializar_aleatorio()
        self.fitness = 0
        self.calcular_fitness()

    def inicializar_aleatorio(self):
        for i, asig in enumerate(asignaturas_db):
            prof = next(p for p in profesores_db if p.id_prof == asig.id_profesor)
            horarios_validos = list(prof.preferencias.keys())
            self.genes[i] = random.choice(horarios_validos)

    def calcular_fitness(self):
        coste = 0
        # Preferencias
        for i, horario in enumerate(self.genes):
            asig = asignaturas_db[i]
            prof = next(p for p in profesores_db if p.id_prof == asig.id_profesor)
            coste += prof.preferencias.get(horario, 100)

        # Penalización de docente duplicado
        for prof in profesores_db:
            horarios_prof = []
            for i, h in enumerate(self.genes):
                if asignaturas_db[i].id_profesor == prof.id_prof:
                    horarios_prof.append(h)
            for h in set(horarios_prof):
                nph = horarios_prof.count(h)
                if nph > 1:
                    coste += (nph - 1) * PENALIZACION

        # Penalización por falta de aulas
        all_horarios = self.genes
        for h in set(all_horarios):
            num_hor = all_horarios.count(h)
            if num_hor > NUM_AULAS_TOTALES:
                coste += (num_hor - NUM_AULAS_TOTALES) * PENALIZACION

        self.fitness = coste

# Selección de Torneo

def seleccion_torneo(poblacion, k=3):
    torneo = random.sample(poblacion, k)
    mejor = min(torneo, key=lambda ind: ind.fitness)
    return copy.deepcopy(mejor)

def cruce_monopunto(padre1, padre2):
    if random.random() < CROSSOVER_RATE:
        punto = random.randint(1, len(padre1.genes) - 1)
        h1_genes = padre1.genes[:punto] + padre2.genes[punto:]
        h2_genes = padre2.genes[:punto] + padre1.genes[punto:]
        return Individuo(h1_genes), Individuo(h2_genes)
    return copy.deepcopy(padre1), copy.deepcopy(padre2)

def mutacion(ind):
    if random.random() < MUTATION_RATE:
        idx = random.randint(0, len(ind.genes) - 1)
        asig = asignaturas_db[idx]
        prof = next(p for p in profesores_db if p.id_prof == asig.id_profesor)
        horarios_validos = list(prof.preferencias.keys())
        ind.genes[idx] = random.choice(horarios_validos)
        ind.calcular_fitness()


def visualizar_horario_bonito(mejor_individuo):
    # Crear matriz vacía para la tabla Filas=Aulas, Cols=Horarios
    tabla_datos = [["" for _ in HORARIOS] for _ in range(NUM_AULAS_TOTALES)]
    
    # Rellenar la matriz con las materias
    ocupacion_por_horario = {h: 0 for h in HORARIOS}
    
    for i, horario_asignado in enumerate(mejor_individuo.genes):
        asig = asignaturas_db[i]
        
        # Se busca el nombre del docente correspondiente
        prof = next(p for p in profesores_db if p.id_prof == asig.id_profesor)
        
        texto_celda = f"{asig.nombre}\n({prof.nombre})"
        
        if horario_asignado in HORARIOS:
            col_idx = HORARIOS.index(horario_asignado)
            
            # Asignamos el aula con un 0 o 1
            fila_aula = ocupacion_por_horario[horario_asignado]
            
            if fila_aula < NUM_AULAS_TOTALES:
                tabla_datos[fila_aula][col_idx] = texto_celda
                ocupacion_por_horario[horario_asignado] += 1
            else:
                tabla_datos[NUM_AULAS_TOTALES-1][col_idx] += f"\n!{texto_celda}!"

    # Configuración de la gráfica
    fig, ax = plt.subplots(figsize=(12, 5)) 
    ax.set_axis_off()
    
    # Crear la tabla visual
    tabla = ax.table(
        cellText=tabla_datos,
        rowLabels=[f"Aula {i+1}" for i in range(NUM_AULAS_TOTALES)],
        colLabels=HORARIOS,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1] 
    )
    
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(9)
    
    plt.title(f"Mejor Horario Encontrado (Fitness: {mejor_individuo.fitness})")
    plt.show()

def main():
    poblacion = [Individuo() for _ in range(POPULATION_SIZE)]
    
    mejor_historico = []
    promedio_historico = []

    print(f"Iniciando evolución por {GENERATIONS} generaciones")

    for gen in range(GENERATIONS):
        poblacion.sort(key=lambda x: x.fitness)
        mejor_actual = poblacion[0]
        
        mejor_historico.append(mejor_actual.fitness)
        promedio = sum(ind.fitness for ind in poblacion) / len(poblacion)
        promedio_historico.append(promedio)

        if gen % 10 == 0 or gen == GENERATIONS - 1:
            print(f"Gen {gen}: Mejor Fitness = {mejor_actual.fitness}")
           

        nueva_poblacion = [copy.deepcopy(mejor_actual)]
        while len(nueva_poblacion) < POPULATION_SIZE:
            p1 = seleccion_torneo(poblacion)
            p2 = seleccion_torneo(poblacion)
            h1, h2 = cruce_monopunto(p1, p2)
            mutacion(h1)
            mutacion(h2)
            nueva_poblacion.extend([h1, h2])
        poblacion = nueva_poblacion[:POPULATION_SIZE]

    mejor_solucion = min(poblacion, key=lambda x: x.fitness)

    # Gráfica de evolución
    plt.figure(figsize=(10, 5))
    plt.plot(mejor_historico, label='Mejor Fitness')
    plt.plot(promedio_historico, label='Promedio', linestyle='--')
    plt.title('Evolución del Fitness')
    plt.xlabel('Generación')
    plt.ylabel('Costo')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Horario generado
    print("\nGenerando tabla de horarios")
    visualizar_horario_bonito(mejor_solucion)

if __name__ == "__main__":
    main()