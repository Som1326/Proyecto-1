# algorithms.py
import numpy as np
import time
import itertools
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ModEx:
    def __init__(self):
        self.n = 0
        self.opiniones = np.array([])
        self.receptividad = np.array([])
        self.R_max = 0
        self.nuevas_opinionesR = np.array([])

    def iniciar_variables(self, archivo):
        with open(archivo, 'r') as file:
            lineas = file.readlines()
            self.n = int(lineas[0])  
            self.opiniones = np.array([float(linea.split(',')[0]) for linea in lineas[1:self.n+1]])
            self.receptividad = np.array([float(linea.split(',')[1]) for linea in lineas[1:self.n+1]])
            self.R_max = int(lineas[-1])
        # print(f"Archivo cargado: {self.n} agentes, {self.opiniones}, {self.receptividad}, R_max: {self.R_max}")

    def crear_grafico_dispersión(self, canvas):
        # Crear una figura con matplotlib
        fig, ax = plt.subplots(figsize=(12, 4))

        # Configurar el gráfico de dispersión
        x = self.opiniones
        y = np.random.uniform(-0.5, 0.5, size=x.shape) # El eje y será 0 para todas las opiniones
        ax.scatter(x, y, color='blue', s=5)

        # Configuración del eje x para que vaya de -100 a 100
        ax.set_xlim([-100, 100])
        ax.set_xticks(np.arange(-100, 101, 10))
        ax.set_ylim([-1, 1])  # Mantener el eje y centrado
        # ax.axhline(0, color='black',linewidth=0.5)  # Línea central en y=0
        ax.axvline(0, color='black',linewidth=0.5, linestyle=(0, (5, 5)))  # Línea central en x=0
        ax.set_xlabel("Opiniones")
        ax.set_title("Gráfico de Dispersión de Opiniones")

        # Eliminar el eje y
        ax.get_yaxis().set_visible(False)

        # Convertir el gráfico a un canvas de Tkinter
        canvas_figura = FigureCanvasTkAgg(fig, master=canvas)
        canvas_figura.draw()
        canvas_figura.get_tk_widget().pack()
        
    def rocFB(self):
        n, opiniones, receptividad, R_max = self.n, self.opiniones, self.receptividad, self.R_max
        # Calcular extremismo
        def calcular_extremismo(opiniones):
            return np.sqrt(np.sum(opiniones**2)) / n

        # Calcular esfuerzo de moderación
        def esfuerzo_moderacion(opiniones, nuevas_opiniones, receptividad):
            esfuerzo = np.ceil(np.abs(opiniones - nuevas_opiniones) * (1 - receptividad))
            return np.sum(esfuerzo)
        
        # Generar todas las posibles estrategias de moderación (2^n combinaciones)
        def generar_estrategias(n):
            for estrategia in itertools.product([0, 1], repeat=n):
                yield estrategia

        # Inicializar variables para guardar la mejor estrategia
        mejor_estrategia = None
        esfuerzo_maximo = 0
        menor_extremismo = float('inf')
        inicio = time.perf_counter()

        # Evaluar todas las estrategias
        # for idx, estrategia in enumerate(estrategias):
        for idx, estrategia in enumerate(generar_estrategias(n)):
            # Aplicar la estrategia: si e_i = 1, moderamos a 0, si e_i = 0, mantenemos la opinión original
            nuevas_opiniones = np.where(estrategia, 0, opiniones)  # Optimizado
            # Calcular esfuerzo y extremismo
            esfuerzo = esfuerzo_moderacion(opiniones, nuevas_opiniones, receptividad)
            extremismo = calcular_extremismo(nuevas_opiniones)
        
            # Verificar si la estrategia es válida (esfuerzo <= R_max)
            if esfuerzo <= R_max and extremismo < menor_extremismo:
                mejor_estrategia = estrategia
                esfuerzo_maximo = esfuerzo
                menor_extremismo = extremismo
                nuevas_opiniones_final = nuevas_opiniones
        
        # Tomar el tiempo final
        fin = time.perf_counter()
        tiempo_total = fin - inicio
        return list(mejor_estrategia), esfuerzo_maximo, menor_extremismo, tiempo_total, nuevas_opiniones_final

    def rocDP(self):
        n, opiniones, receptividad, R_max = self.n, self.opiniones, self.receptividad, self.R_max

        # Inicializar la tabla DP y la matriz de seguimiento
        DP = np.full((n + 1, R_max + 1), float('inf'))
        track_matrix = np.zeros((n + 1, R_max + 1), dtype=int)
        inicio = time.perf_counter()

        # Caso base
        for j in range(R_max + 1):
            DP[0][j] = np.sqrt(np.sum(opiniones**2)) / n
        
        # Llenar la tabla DP y la matriz de seguimiento
        for i in range(1, n + 1):
            for j in range(R_max + 1):
                esfuerzo_actual = np.ceil(np.abs(opiniones[i - 1]) * (1 - receptividad[i - 1]))
                
                if esfuerzo_actual <= j:
                    # Caso 4: Minimizar entre moderar o no moderar al agente
                    sin_modificar = np.sqrt((DP[i - 1][j] * (i - 1))**2 + opiniones[i - 1]**2) / i
                    if j - esfuerzo_actual >= 0:
                        modificar = np.sqrt((DP[i - 1][j - int(esfuerzo_actual)] * (i - 1))**2) / i
                        if modificar < sin_modificar:
                            DP[i][j] = modificar
                            track_matrix[i][j] = 1  # Marcar que moderamos al agente i-1
                        else:
                            DP[i][j] = sin_modificar
                    else:
                        DP[i][j] = sin_modificar
                else:
                    # Caso 3: Solo considerar no moderar al agente
                    DP[i][j] = np.sqrt((DP[i - 1][j] * (i - 1))**2 + opiniones[i - 1]**2) / i
        
        fin = time.perf_counter()  
        tiempo_total = fin - inicio

        return DP, track_matrix, tiempo_total

    def encontrar_agentes_seleccionados_con_tracking(self, track_matrix):
        n, opiniones, receptividad, R_max = self.n, self.opiniones, self.receptividad, self.R_max
        agentes_seleccionados = []
        estrategia = np.zeros(n, dtype=int)  # Vector de ceros para la estrategia
        esfuerzo_total = 0
        j = R_max

        # Calcular esfuerzo de moderación
        def esfuerzo_moderacion(opiniones, nuevas_opiniones, receptividad):
            esfuerzo = np.ceil(np.abs(opiniones - nuevas_opiniones) * (1 - receptividad))
            return np.sum(esfuerzo)

        for i in range(n, 0, -1):
            if j >= 0 and track_matrix[i][j] == 1:
                agentes_seleccionados.append(i - 1)  # Guardamos el índice del agente
                estrategia[i - 1] = 1
                j -= int(np.ceil(np.abs(opiniones[i - 1]) * (1 - receptividad[i - 1])))  # Reducimos el esfuerzo disponible

        nuevas_opiniones = np.where(estrategia, 0, opiniones)
        esfuerzo_total = esfuerzo_moderacion(opiniones, nuevas_opiniones, receptividad)

        return estrategia, agentes_seleccionados, esfuerzo_total, nuevas_opiniones

    def rocV(self):
        opiniones, receptividades, R_max = self.opiniones, self.receptividad, self.R_max
        # Función para calcular el extremismo de una red social
        def calcular_extremismo(opiniones):
            n = len(opiniones)
            return np.sqrt(np.sum(opiniones**2)) / n

        inicio = time.perf_counter()
        n = len(opiniones)

        # Extremismo inicial de la red sin moderar ningún agente
        extremismo_inicial = calcular_extremismo(opiniones)

        # Generar nuevas opiniones moderando cada agente (opiniones moderadas a 0)
        nuevas_opiniones = np.tile(opiniones, (n, 1))  # Crear una matriz con n filas de las opiniones originales
        np.fill_diagonal(nuevas_opiniones, 0)  # Poner 0 en las diagonales (moderar agente i)

        # Calcular el extremismo modificado para cada agente
        extremismo_modificado = np.sqrt(np.sum(nuevas_opiniones**2, axis=1)) / n

        # Calcular el beneficio para cada agente (reducción del extremismo)
        beneficio = extremismo_inicial - extremismo_modificado

        # Calcular el esfuerzo para cada agente
        esfuerzo = np.ceil(np.abs(opiniones) * (1 - receptividades))

        # Evitar divisiones por cero
        beneficio_costo = np.where(esfuerzo > 0, beneficio / esfuerzo, 0)

        # Ordenar los agentes por su relación beneficio/costo de mayor a menor
        indices_ordenados = np.argsort(-beneficio_costo)

        # Inicializar esfuerzo total y lista de agentes seleccionados
        esfuerzo_total = 0
        agentes_seleccionados = []
        estrategia = np.zeros(n, dtype=int)  # Vector de ceros para la estrategia

        # Seleccionar los agentes que caben en el presupuesto de esfuerzo R_max
        for i in indices_ordenados:
            if esfuerzo_total + esfuerzo[i] <= R_max:
                agentes_seleccionados.append(int(i))
                estrategia[i] = 1
                esfuerzo_total += esfuerzo[i]
        
        # Calcular el nuevo extremismo después de aplicar la estrategia
        nuevas_opiniones_final = opiniones.copy()
        nuevas_opiniones_final[agentes_seleccionados] = 0

        extremismo_final = calcular_extremismo(nuevas_opiniones_final)

        fin = time.perf_counter()  
        tiempo_total = fin - inicio

        # Retornar la estrategia (agentes seleccionados), el extremismo final y el esfuerzo total utilizado
        return estrategia, agentes_seleccionados, extremismo_final, esfuerzo_total, tiempo_total, nuevas_opiniones_final


    def crear_grafico_dispersión_resultados(self, canvas, nuevas_opiniones):
        for widget in canvas.winfo_children():
            widget.destroy()
            
        # Crear una figura con matplotlib
        fig, ax = plt.subplots(figsize=(12, 4))

        # Configurar el gráfico de dispersión
        x = nuevas_opiniones
        y = np.random.uniform(-0.5, 0.5, size=x.shape) # El eje y será 0 para todas las opiniones
        ax.scatter(x, y, color='blue', s=5)

        # Configuración del eje x para que vaya de -100 a 100
        ax.set_xlim([-100, 100])
        ax.set_xticks(np.arange(-100, 101, 10))
        ax.set_ylim([-1, 1])  # Mantener el eje y centrado
        # ax.axhline(0, color='black',linewidth=0.5)  # Línea central en y=0
        ax.axvline(0, color='black',linewidth=0.5, linestyle=(0, (5, 5)))  # Línea central en x=0
        ax.set_xlabel("Opiniones")
        ax.set_title("Gráfico de Dispersión de Opiniones Moderadas")

        # Eliminar el eje y
        ax.get_yaxis().set_visible(False)

        # Convertir el gráfico a un canvas de Tkinter
        
        canvas_figura = FigureCanvasTkAgg(fig, master=canvas)
        canvas_figura.draw()
        canvas_figura.get_tk_widget().pack()
        
    
