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
    # Llamar al algoritmo fuerza bruta
    # mejor_estrategia, esfuerzo_maximo, menor_extremismo, tiempo_total = modexFB(n, opiniones, receptividad, R_max)

    # # Resultado
    # print("Menor extremismo alcanzado: ", menor_extremismo)
    # print("Estrategia de moderacion: ", mejor_estrategia)
    # print("Esfuerzo total utilizado: ", esfuerzo_maximo)
    # print(f"Tiempo de ejecucion: {tiempo_total:.8f} segundos")
    print("----------------------")

    print("----------------------\nRS' PROGRAMACION DINAMICA")
    # Llamar al algoritmo dinámico
    tabla_dp, track_matrix, tiempo_totalDP = modexDP(n, opiniones, receptividad, R_max)

    # Encontrar los agentes seleccionados usando la matriz de seguimiento
    estrategiaDP, agentes_seleccionados, esfuerzo_totalDP = encontrar_agentes_seleccionados_con_tracking(track_matrix, n, opiniones, receptividad, R_max)

    # Imprimir resultados
    print(f"Menor extremismo alcanzado: {tabla_dp[n][R_max]}")
    print("Estrategia de moderación:", estrategiaDP)
    # print("Agentes seleccionados para moderación:", agentes_seleccionados)
    print("Esfuerzo total utilizado: ", esfuerzo_totalDP)
    print(f"Tiempo de ejecucion: {tiempo_totalDP:.8f} segundos")
    print("----------------------")

    # Llamar al algoritmo voraz
    print("----------------------\nRS' PROGRAMACION VORAZ")
    estrategiaV, agentes_seleccionados, extremismo_final, esfuerzo_totalV, tiempo_totalV = modexV(opiniones, receptividad, R_max)

    # Imprimir resultados
    print("Menor extremismo alcanzado: ", extremismo_final)
    print("Estrategia de moderación: ", estrategiaV)
    # print("Agentes seleccionados para moderación: ", agentes_seleccionados)
    print("Esfuerzo total utilizado: ", esfuerzo_totalV)
    print(f"Tiempo de ejecucion: {tiempo_totalV:.8f} segundos")
    print("----------------------")

def modexFB(n, opiniones, receptividad, R_max):
    # Calcular extremismo
    def calcular_extremismo(opiniones):
        return np.sqrt(np.sum(opiniones**2)) / n

    # Calcular esfuerzo de moderación
    def esfuerzo_moderacion(opiniones, nuevas_opiniones, receptividad):
        esfuerzo = 0
        for i in range (n):
            esfuerzo = esfuerzo + np.ceil(np.abs(opiniones[i] - nuevas_opiniones[i]) * (1 - receptividad[i]))
        return esfuerzo
    
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

    return mejor_estrategia, esfuerzo_maximo, menor_extremismo, tiempo_total

def modexDP(n, opiniones, receptividad, R_max):
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

def encontrar_agentes_seleccionados_con_tracking(track_matrix, n, opiniones, receptividad, R_max):
    agentes_seleccionados = []
    estrategia = np.zeros(n, dtype=int)  # Vector de ceros para la estrategia
    esfuerzo_total = 0
    j = R_max

    def esfuerzo_moderacion(opiniones, nuevas_opiniones, receptividad):
        esfuerzo = 0
        for i in range (n):
            esfuerzo = esfuerzo + np.ceil(np.abs(opiniones[i] - nuevas_opiniones[i]) * (1 - receptividad[i]))
        return esfuerzo

    for i in range(n, 0, -1):
        if j >= 0 and track_matrix[i][j] == 1:
            agentes_seleccionados.append(i - 1)  # Guardamos el índice del agente
            estrategia[i - 1] = 1
            j -= int(np.ceil(np.abs(opiniones[i - 1]) * (1 - receptividad[i - 1])))  # Reducimos el esfuerzo disponible

    nuevas_opiniones = np.where(estrategia, 0, opiniones)

    esfuerzo_total = esfuerzo_moderacion(opiniones, nuevas_opiniones, receptividad)

    return estrategia, agentes_seleccionados, esfuerzo_total

def modexV(opiniones, receptividades, R_max):
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
    return estrategia, agentes_seleccionados, extremismo_final, esfuerzo_total, tiempo_total

abrir_archivo()