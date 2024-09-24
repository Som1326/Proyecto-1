import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import tkinter.font as tkFont

class Application2:
    def __init__(self, modex):
        self.modex = modex
        self.root = tk.Tk()
        self.root.title("Proyecto ModEx")
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family="Roboto", size=12, weight="normal")

    def run(self):
        self.create_main_window()
        self.root.mainloop()

    def create_main_window(self, width=700, height=600):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.resizable(False, False)
        
        tk.Label(self.root).pack(pady=50)

        current_dir = os.path.dirname(__file__)
        image_path = os.path.join(current_dir, 'img', 'cliente.png')
        red_img = Image.open(image_path)
        resized_image = red_img.resize((200, 200), Image.LANCZOS)
        self.img = ImageTk.PhotoImage(resized_image)
        image_label = tk.Label(self.root, image=self.img)
        image_label.pack(pady=10)
        
        tk.Label(self.root, text="Extremisto de Opinion", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Abrir Archivo", command=self.open_file, font=("Arial", 12)).pack(pady=10)

    def open_file(self):
        archivo = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if archivo:
            self.modex.iniciar_variables(archivo)
            self.create_algorithm_window()
        else:
            messagebox.showerror("Error", "No se ha seleccionado ningún archivo")

    def create_algorithm_window(self):
        custom_font = tkFont.Font(family="Roboto", size=12, weight="normal")
        new_window = tk.Toplevel(self.root)
        new_window.title("Información de Agentes y Algoritmos")
        new_window.state('zoomed')  
        
        canvas = tk.Canvas(new_window)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Añadir la scrollbar
        scrollbar = tk.Scrollbar(new_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Elementos dentro del frame "añadimos los Widgets"
        tk.Label(scrollable_frame, text=f"Número de agentes: {self.modex.n}",).grid (row=0, column=0, padx=10, pady=5)
        
        tk.Label(scrollable_frame, text=f"Valor Maximo: {self.modex.R_max}").grid(row=0, column=2, padx=10, pady=5)
        
        #----- Visualizacion de grafico ----       
        grafico_canvas = tk.Canvas(scrollable_frame, width=500, height=400)
        grafico_canvas.grid(row=2, column=0, columnspan=6, pady=10 ,padx=1)
        self.modex.crear_grafico_dispersión(grafico_canvas)

        text_widget = tk.Text(scrollable_frame, height=1, wrap='none') 
        text_widget.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        receptividad_str = ', '.join(map(str, self.modex.receptividad))
        text_widget.insert(tk.END, f"Receptividad: {receptividad_str}")
        text_widget.config(state='disabled')
        h_scroll = tk.Scrollbar(scrollable_frame, orient='horizontal', command=text_widget.xview)
        h_scroll.grid(row=4, column=1, sticky='ew')
        text_widget['xscrollcommand'] = h_scroll.set

        tk.Button(scrollable_frame, text="Fuerza Bruta", command=self.execute_fb).grid(row=4, column=3, padx=5, pady=5)
        tk.Button(scrollable_frame, text="Programación Dinámica", command=self.execute_dp).grid(row=5, column=3, padx=5, pady=5)
        tk.Button(scrollable_frame, text="Algoritmo Voraz", command=self.execute_v).grid(row=6, column=3, padx=5, pady=5)
        tk.Button(scrollable_frame, text="Descargar resultado", command=self.donwload).grid(row=7, column=3, padx=5, pady=5)
       
        # Etiquetas vacías para mostrar los resultados
        self.titulo_prueba_label = tk.Label(scrollable_frame,text="")
        self.titulo_prueba_label.grid(row=5, column=1, padx=10, pady=5)
        
        tk.Label(scrollable_frame, text="Menor extremismo:").grid(row=6, column=0, padx=10, pady=5)
        self.menor_extremismo_label = tk.Label(scrollable_frame, text="")
        self.menor_extremismo_label.grid(row=6, column=1, padx=10, pady=5)

        tk.Label(scrollable_frame, text="Estrategia de moderación:").grid(row=7, column=0, padx=10, pady=5)
        self.estrategia_label = tk.Label(scrollable_frame, text="")
        self.estrategia_label.grid(row=7, column=1, padx=10, pady=5)

        tk.Label(scrollable_frame, text="Esfuerzo total utilizado:").grid(row=8, column=0, padx=10, pady=5)
        self.esfuerzo_label = tk.Label(scrollable_frame, text="")
        self.esfuerzo_label.grid(row=8, column=1, padx=10, pady=5)

        tk.Label(scrollable_frame, text="Tiempo de ejecución:").grid(row=9, column=0, padx=10, pady=5)
        self.tiempo_label = tk.Label(scrollable_frame, text="")
        self.tiempo_label.grid(row=9, column=1, padx=10, pady=5)

    def execute_fb(self):
        if self.modex.n >= 20:
            messagebox.showerror("Error", "Esta solucion permite un maximo de 20 Agentes")
            return  
        
        mejor_estrategia, esfuerzo_maximo, menor_extremismo, tiempo_total = self.modex.modexFB()
        
        #Actualizar las etiquetas con los resultados
        self.titulo_prueba_label.config(text="Resultados algoritmo de fuerza bruta")
        self.menor_extremismo_label.config(text=f"{menor_extremismo}")
        self.estrategia_label.config(text=f"{mejor_estrategia}")
        self.esfuerzo_label.config(text=f"{esfuerzo_maximo}")
        self.tiempo_label.config(text=f"{tiempo_total:.8f} segundos")
        
    def execute_dp(self):
        tabla_dp, track_matrix, tiempo_totalDP = self.modex.modexDP()
        menor_extremismo = tabla_dp[self.modex.n][self.modex.R_max]
        estrategiaDP, agentes_seleccionados, esfuerzo_totalDP = self.modex.encontrar_agentes_seleccionados_con_tracking(track_matrix)

        # Actualizar etiquetas con los resultados
        self.titulo_prueba_label.config(text="Resultados algoritmo de programacion dinamica")
        self.menor_extremismo_label.config(text=f"{menor_extremismo}")
        self.estrategia_label.config(text=f"{estrategiaDP}")
        self.esfuerzo_label.config(text=f"{esfuerzo_totalDP}")
        self.tiempo_label.config(text=f"{tiempo_totalDP:.8f} segundos")

    def execute_v(self):
        estrategiaV, agentes_seleccionados, extremismo_final, esfuerzo_totalV, tiempo_totalV = self.modex.modexV()
        
        #Actualizar las etiquetas con los resultados
        self.titulo_prueba_label.config(text="Resultados algoritmo Voraz")
        self.menor_extremismo_label.config(text=f"{extremismo_final}")
        self.estrategia_label.config(text=f"{estrategiaV}")
        self.esfuerzo_label.config(text=f"{esfuerzo_totalV}")
        self.tiempo_label.config(text=f"{tiempo_totalV:.8f} segundos")

    def donwload(self):
        i = 4