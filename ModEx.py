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
    print("----------------------\nRS' FUERZA BRUTA")
    modexFB(n, opiniones, receptividad, R_max)
    print("----------------------")
    print("----------------------\nRS' PROGRAMACION DINAMICA")
    # Llamamos a la función modex_dp_con_tracking para llenar la tabla DP y la matriz de seguimiento
    tabla_dp, track_matrix = modexDP(n, opiniones, receptividad, R_max)
    # Encontrar los agentes seleccionados usando la matriz de seguimiento
    agentes_seleccionados = encontrar_agentes_seleccionados_con_tracking(tabla_dp, track_matrix, n, opiniones, receptividad, R_max)
    print(f"Menor extremismo alcanzado: {tabla_dp[n][R_max]}")
    print("Agentes seleccionados para moderación:", agentes_seleccionados)
    print("----------------------")

def modexFB(n, opiniones, receptividad, R_max):
    # Calcular extremismo
    def calcular_extremismo(opiniones):
        return np.sqrt(np.sum(opiniones**2)) / n

    # Calcular esfuerzo de moderación
    def esfuerzo_moderacion(opiniones, nuevas_opiniones, receptividad):
        esfuerzo = np.round(np.abs(opiniones - nuevas_opiniones) * (1 - receptividad))
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
    
        # Mostrar el progreso cada 1000 iteraciones
        # if (idx + 1) % 10000 == 0:
        #     tiempo_actual = time.perf_counter()
        #     tiempo_transcurrido = tiempo_actual - inicio
        #     print(f"Estrategia {idx + 1} procesada. Tiempo transcurrido: {tiempo_transcurrido:.2f} segundos.")

            # print(f"Estrategia {idx + 1} de {total_estrategias} procesada. Tiempo transcurrido: {tiempo_transcurrido:.2f} segundos.")

    # Tomar el tiempo final
    fin = time.perf_counter()
    tiempo_total = fin - inicio

    # Resultado
    print("Mejor estrategia de moderacion:", mejor_estrategia)
    print("Esfuerzo maximo:", esfuerzo_maximo)
    print("Menor extremismo alcanzado:", menor_extremismo)
    print(f"Tiempo de ejecucion: {tiempo_total:.8f} segundos")

def modexDP(n, opiniones, receptividad, R_max):
    # Inicializar la tabla DP y la matriz de seguimiento
    DP = np.full((n + 1, R_max + 1), float('inf'))
    track_matrix = np.zeros((n + 1, R_max + 1), dtype=int)
    
    # Caso base
    for j in range(R_max + 1):
        DP[0][j] = np.sqrt(np.sum(opiniones**2)) / n
    
    # Llenar la tabla DP y la matriz de seguimiento
    for i in range(1, n + 1):
        for j in range(R_max + 1):
            esfuerzo_actual = np.round(np.abs(opiniones[i - 1]) * (1 - receptividad[i - 1]))
            
            if esfuerzo_actual <= j:
                # Caso 4: Minimizar entre moderar o no moderar al agente
                sin_modificar = np.sqrt((DP[i - 1][j] * (i - 1))**2 + opiniones[i - 1]**2) / i
                if j - int(esfuerzo_actual) >= 0:
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
    
    return DP, track_matrix

def encontrar_agentes_seleccionados_con_tracking(DP, track_matrix, n, opiniones, receptividad, R_max):
    agentes_seleccionados = []
    j = R_max
    for i in range(n, 0, -1):
        if j >= 0 and track_matrix[i][j] == 1:
            agentes_seleccionados.append(i - 1)  # Guardamos el índice del agente
            j -= int(np.abs(opiniones[i - 1]) * (1 - receptividad[i - 1]))  # Reducimos el esfuerzo disponible
    return agentes_seleccionados

# def modexV():

abrir_archivo()