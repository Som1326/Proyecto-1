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
    print("----------------------\nRS'")
    modexFB(n, opiniones, receptividad, R_max)
    print("----------------------")

def modexFB(n, opiniones, receptividad, R_max):
    # Calcular extremismo
    def calcular_extremismo(opiniones):
        return np.sqrt(np.sum(opiniones**2)) / n

    # Calcular esfuerzo de moderación
    def esfuerzo_moderacion(opiniones, nuevas_opiniones, receptividad):
        return np.sum(np.abs(opiniones - nuevas_opiniones) * (1 - receptividad))

    # Generar todas las posibles estrategias de moderación (2^n combinaciones)
    estrategias = list(itertools.product([0, 1], repeat=n))
    total_estrategias = len(estrategias)

    # Inicializar variables para guardar la mejor estrategia
    mejor_estrategia = None
    menor_extremismo = float('inf')
    inicio = time.perf_counter()

    # Evaluar todas las estrategias
    for idx, estrategia in enumerate(estrategias):
        # Aplicar la estrategia: si e_i = 1, moderamos a 0, si e_i = 0, mantenemos la opinión original
        nuevas_opiniones = np.array([opiniones[i] if estrategia[i] == 0 else 0 for i in range(n)])
    
        # Calcular esfuerzo y extremismo
        esfuerzo = esfuerzo_moderacion(opiniones, nuevas_opiniones, receptividad)
        extremismo = calcular_extremismo(nuevas_opiniones)
    
        # Verificar si la estrategia es válida (esfuerzo <= R_max)
        if esfuerzo <= R_max and extremismo < menor_extremismo:
            mejor_estrategia = estrategia
            menor_extremismo = extremismo
    
        # Mostrar el progreso cada 1000 iteraciones
        if (idx + 1) % 1 == 0:
            tiempo_actual = time.perf_counter()
            tiempo_transcurrido = tiempo_actual - inicio
            print(f"Estrategia {idx + 1} de {total_estrategias} procesada. Tiempo transcurrido: {tiempo_transcurrido:.2f} segundos.")

    # Tomar el tiempo final
    fin = time.perf_counter()
    tiempo_total = fin - inicio

    # Resultado
    print("Mejor estrategia de moderación:", mejor_estrategia)
    print("Menor extremismo alcanzado:", menor_extremismo)
    print(f"Tiempo de ejecución: {tiempo_total:.8f} segundos")

# def modexPD():

# def modexV():

abrir_archivo()