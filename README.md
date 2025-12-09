# Generador de horarios usando Algoritmos Genético (GA) y NSGA-II

Este repositorio contiene dos implementaciones distintas para resolver el problema de planificación de horarios.

El objetivo es explicar la comparación de un **Algoritmo Genético** y **NSGA-II** en la resolución de generador de horarios.

## Comparaciones

### Diferencia Principal
* **Algoritmos Genéticos:** Convierte el problema en una sola dimensión. Mezcla todas las restricciones sumando castigos en una sola variable `fitness`.
* **NSGA-II:** Mantiene los objetivos separados. Es decir, para este proyecto minimiza conflictos ($f_1$) y optimiza el espacio ($f_2$), ya que son metas que compiten entre sí, generando un conjunto de soluciones, llamado **Frente de Pareto**.

### Tabla Conceptual Comparativa

| Concepto | Algoritmos Genéticos | NSGA-II |
| :--- | :--- | :--- |
| **Evaluación** | Suma todo en un único valor | Son múltiples objetivos |
| **Resolución de Conflictos** | Basada en las restricciones dadas | Basada en dominancia |
| **Salida** | Una única mejor solución | Un conjunto de soluciones óptimas llamada **Frente de Pareto** |

## Resultados
Se realizaron pruebas de ejecución con ambos algoritmos utilizando el mismo dataset para que sea una comparación justa.

### Tabla Comparativa de Rendimiento
| Métrica | Algoritmos Genéticos | NSGA-II |
| :--- | :--- | :--- |
| **Tiempo de Convergencia** | Rápido (< 30 segundos) | Moderado (aprox. 2 minutos) |
| **Tipo de Solución** | Una única solución mejor (Mejor Fitness) | Un conjunto de soluciones (Frente de Pareto). |
| **Conflictos Finales** | 0 Conflictos | 0 Conflictos en soluciones seleccionadas. |
| **Uso de Memoria** | Bajo. | Medio (Almacena frentes y distancias). |

### Outputs de los algoritmos
#### Resultados del Algoritmo Genético

`![Gráfica GA](imagenes/grafica_ga.png)`

El GA mostró una convergencia lineal. Al sumar todas las penalizaciones en una sola variable, el algoritmo corre directamente hacia la solución con el puntaje más alto, el cual fue 1.0
* **Ventaja:** Encuentra un horario válido muy rápido.
* **Desventaja:** No nos permite ver si estamos desperdiciando salones grandes para grupos pequeños, ya que ese detalle se pierde en la suma total del fitness.

`![Consola GA](imagenes/consola_ga.png)`

#### Resultados del NSGA-II
El enfoque multi-objetivo generó un **Frente de Pareto**. En lugar de darnos un solo horario, el sistema nos entregó múltiples opciones no dominadas.

`![Gráfica NSGA-II](imagenes/grafica_nsgaii.png)`

* **Eje X ($f_1$):** Minimización de Conflictos.
* **Eje Y ($f_2$):** Optimización de Espacio.

Se observó el fenómeno de **"Trade-off" (Compromiso)**:
* Las soluciones con **0 conflictos** a veces tenían un uso de espacio menos eficiente.
* Al forzar una optimización de espacio perfecta ($f_2$), a veces surgían conflictos menores en $f_1$.

`![Consola NSGA-II](imagenes/consola_nsgaii.png)`


### Tabla Comparativa en generador de horarios``

| Característica | Algoritmos Genéticos | NSGA-II |
| :--- | :--- | :--- |
| **Complejidad Computacional** | Baja $O(N)$, por lo que es más rápido por generación | Alta $O(MN^2)$, por lo que requiere un ordenamiento no dominado |
| **Tiempo de Ejecución** | **Más Rápido.** Al solo calcular una suma, es más rápido | **Más Lento.** El cálculo de las soluciones consume más recursos |
| **Calidad de la Solución** | Tiende a estancarse a un solo óptimo local | Ofrece múltiples soluciones óptimas, teniendo diversidad |
| **Flexibilidad** | Rígido. Si se quiere priorizar el espacio, se debe cambiar los pesos manualmente | Flexible. Se puede elegir al final qué solución se prefiere del conjunto |

### ¿Cuál es mejor?
Depende del escenario que se quiere aplicar:

* **El Algoritmo Genético es mejor solo si:** La prioridad es la **velocidad** y se tiene muy claro qué restricciones importan más (ej. "el choque de horario es 10 veces peor que un salón vacío"). Es ideal para sistemas en tiempo real o hardware limitado para múltiples objetivos.
* **El NSGA-II es mejor si:** Se busca una **toma de decisiones**. Es mejor en escenarios más complejos donde no sabemos exactamente cuánto pesa cada objetivo. Esto permite decidir si *"¿Prefiero 0 conflictos con salones llenos, o aceptar 1 conflicto mínimo a cambio de salones perfectos?"*.

## Conclusiones

1.  El **Algoritmo Genético** logró encontrar soluciones válidas en menos generaciones debido a la presión selectiva directa.
2.  El **NSGA-II** tardó más, pero entregó más opciones, permitiendo visualizar cómo la optimización del espacio a veces presionaba la creación de conflictos.
3.  Para el problema específico de horarios, donde la validez puede ser negociable, el Algoritmo Genético resulta suficiente, pero el NSGA-II ofrece una herramienta de análisis mejor para la gestión de recursos.
