import tkinter as tk
import numpy as np
import itertools
from tkinter import filedialog
import time

# Función para abrir el explorador de archivos y seleccionar un archivo .txt
def abrir_archivo():
    # Inicializamos la ventana de tkinter
    root = tk.Tk()
    root.withdraw()  # Ocultamos la ventana principal
    
    # Abrimos el diálogo para seleccionar el archivo
    archivo = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    
    # Leemos el archivo seleccionado
    if archivo:
        with open(archivo, 'r') as file:
            contenido = file.read()
            iniciar_variables(archivo)

def iniciar_variables(archivo):
    if archivo:
        with open(archivo, 'r') as file:
            lineas = file.readlines()  # Leemos todas las líneas del archivo

            if 3 <= len(lineas):
                n = int(lineas[0])  # Restamos 1 porque los índices empiezan en 0
                opiniones = np.array([])
                receptividad = np.array([])
                R_max = int(lineas[len(lineas)-1])

                for i in range(1, n+1):  # Convertimos n y m a índices de lista (empiezan en 0)
                    linea = lineas[i].strip()  # Obtenemos la línea deseada
                    valores = linea.split(',')  # Separar por coma

                    # Verificamos si tenemos exactamente dos valores
                    if len(valores) == 2:
                        valor1 = float(valores[0])
                        valor2 = float(valores[1])
                        
                        opiniones = np.append(opiniones, valor1)
                        receptividad = np.append(receptividad, valor2)

                    else:
                        print(f"La línea {i} no contiene dos valores separados por coma.")
            else:
                print(f"Tamaño del archivo de pruebas no valido.")
    print("----------------------\nRS")
    print(f"Numero de agentes: {n}", 
          f"\nOpiniones: {opiniones}", 
          f"\nReceptividad: {receptividad}", 
          f"\nValor maximo: {R_max}")
    # print("----------------------\nRS' FUERZA BRUTA")
    # modexFB(n, opiniones, receptividad, R_max)
    # print("----------------------")
    print("----------------------\nRS' PROGRAMACION DINAMICA")
    modexPD(n, opiniones, receptividad, R_max)
    print("----------------------")

def modexFB(n, opiniones, receptividad, R_max):
    # Calcular extremismo
    def calcular_extremismo(opiniones):
        return np.sqrt(np.sum(opiniones**2)) / n

    # Calcular esfuerzo de moderación
    def esfuerzo_moderacion(opiniones, nuevas_opiniones, receptividad):
        return np.sum(np.abs(opiniones - nuevas_opiniones) * (1 - receptividad))

    # Generar todas las posibles estrategias de moderación (2^n combinaciones)
    def generar_estrategias(n):
        for estrategia in itertools.product([0, 1], repeat=n):
            yield estrategia

    # Inicializar variables para guardar la mejor estrategia
    mejor_estrategia = None
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
            menor_extremismo = extremismo
    
        # Mostrar el progreso cada 1000 iteraciones
        if (idx + 1) % 10000 == 0:
            tiempo_actual = time.perf_counter()
            tiempo_transcurrido = tiempo_actual - inicio
            print(f"Estrategia {idx + 1} procesada. Tiempo transcurrido: {tiempo_transcurrido:.2f} segundos.")

            # print(f"Estrategia {idx + 1} de {total_estrategias} procesada. Tiempo transcurrido: {tiempo_transcurrido:.2f} segundos.")

    # Tomar el tiempo final
    fin = time.perf_counter()
    tiempo_total = fin - inicio

    # Resultado
    print("Mejor estrategia de moderacion:", mejor_estrategia)
    print("Menor extremismo alcanzado:", menor_extremismo)
    print(f"Tiempo de ejecucion: {tiempo_total:.8f} segundos")

def modexPD(n, opiniones, receptividad, R_max):
    def calcular_esfuerzo(opinion, receptividad):
        return abs(opinion - 0) * (1 - receptividad)
    
    # Inicializar la tabla DP con dimensiones (n+1) x (R_max+1)
    DP = np.zeros((n + 1, R_max + 1))

    # Lista para almacenar los esfuerzos de cada agente
    esfuerzos = []

    # Calcular los esfuerzos de moderación para cada agente
    for i in range(n):
        esfuerzo = calcular_esfuerzo(opiniones[i], receptividad[i])
        esfuerzos.append(esfuerzo)

    # Llenar la tabla DP
    for i in range(1, n + 1):
        for j in range(R_max + 1):
            if esfuerzos[i - 1] <= j:  # Si se puede moderar al agente con el esfuerzo disponible
                # Decidimos si moderamos o no al agente
                DP[i][j] = max(DP[i - 1][j], DP[i - 1][int(j - esfuerzos[i - 1])] + abs(opiniones[i - 1]))
            else:
                DP[i][j] = DP[i - 1][j]  # Si no se puede moderar, mantenemos el valor anterior

    # La mejor reducción de extremismo estará en DP[n][R_max]
    mejor_reduccion_extremismo = DP[n][R_max]

    # Encontrar los agentes seleccionados para moderación
    agentes_seleccionados = []
    j = R_max
    for i in range(n, 0, -1):
        if DP[i][j] != DP[i - 1][j]:  # Si hubo un cambio, significa que moderamos al agente
            agentes_seleccionados.append(i - 1)  # Guardamos el índice del agente
            j -= int(esfuerzos[i - 1])  # Reducimos el esfuerzo disponible

    def crear_estrategia(n, agentes_seleccionados):
        # Inicializar la estrategia con ceros
        estrategia = np.zeros(n, dtype=int)
        
        # Marcar los agentes seleccionados con 1
        for agente in agentes_seleccionados:
            estrategia[agente] = 1
        
        return estrategia
    
    nuevas_opiniones = np.where(crear_estrategia(n, agentes_seleccionados), 0, opiniones)

    def calcular_extremismo(opiniones):
        return np.sqrt(np.sum(opiniones**2)) / n

    extremismo = calcular_extremismo(nuevas_opiniones)

    # Mostrar resultados
    print(f"Mejor reducción de extremismo: {mejor_reduccion_extremismo}")
    print(f"Agentes seleccionados para moderación: {agentes_seleccionados}")
    print("Mejor estrategia de moderacion:", crear_estrategia(n, agentes_seleccionados))
    print("Menor extremismo alcanzado:", extremismo)

# def modexV():

abrir_archivo()