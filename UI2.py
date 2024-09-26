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
        self.resultados = {
            'fuerza_bruta': '',
            'programacion_dinamica': '',
            'voraz': ''
        }
        self.ultimo_algoritmo = ''

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
        image_path0 = os.path.join(current_dir, 'img', 'NMuser.png')
        image_path1 = os.path.join(current_dir, 'img', 'Muser.png')
        red_img = Image.open(image_path)
        self.img_0 = ImageTk.PhotoImage(Image.open(image_path0).resize((30, 30)))
        self.img_1 = ImageTk.PhotoImage(Image.open(image_path1).resize((30, 30)))
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
            self.nombre_archivo = os.path.basename(archivo)
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
        
        tk.Label(scrollable_frame, text=f"Esfuerzo Maximo: {self.modex.R_max}").grid(row=0, column=2, padx=10, pady=5)
        
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
        self.titulo_prueba_label.grid(row=5, column=1, columnspan=2, padx=10, pady=5)
        
        tk.Label(scrollable_frame, text="Menor extremismo:").grid(row=6, column=0, padx=10, pady=5)
        self.menor_extremismo_label = tk.Label(scrollable_frame, text="")
        self.menor_extremismo_label.grid(row=6, column=1,  columnspan=2,padx=10, pady=5)

        tk.Label(scrollable_frame, text="Esfuerzo total utilizado:").grid(row=7, column=0, padx=10, pady=5)
        self.esfuerzo_label = tk.Label(scrollable_frame, text="")
        self.esfuerzo_label.grid(row=7, column=1, columnspan=2, padx=10, pady=5)

        tk.Label(scrollable_frame, text="Tiempo de ejecución:").grid(row=8, column=0, padx=10, pady=5)
        self.tiempo_label = tk.Label(scrollable_frame, text="")
        self.tiempo_label.grid(row=8, column=1,  columnspan=2,padx=10, pady=5)
        
        tk.Label(scrollable_frame, text="Estrategia de moderación:").grid(row=9, column=1, columnspan=2, padx=10, pady=5)
        # self.estrategia_label = tk.Label(scrollable_frame, text="")
        # self.estrategia_label.grid(row=7, column=1, padx=10, pady=5)
        
        # Canva para visualizacion de agentes 
        self.estrategia_canvas = tk.Canvas(scrollable_frame, width=1000, height=30)
        self.estrategia_canvas.grid(row=10, column=0, columnspan=4, padx=10, pady=5)
        
        scrollbar_horizontal = tk.Scrollbar(scrollable_frame, orient='horizontal', command=self.estrategia_canvas.xview)
        scrollbar_horizontal.grid(row=11, column=1, columnspan=2, sticky='ew')
        self.estrategia_canvas.configure(xscrollcommand=scrollbar_horizontal.set)
        self.estrategia_canvas.configure(scrollregion=self.estrategia_canvas.bbox("all"))
        
        self.grafico_canvas_res = tk.Canvas(scrollable_frame, width=500, height=400)
        self.grafico_canvas_res.grid(row=12, column=0, columnspan=6, pady=10 ,padx=1)
        
        
    def guardar_resultados(self, algoritmo, resultado):
        self.resultados[algoritmo] = resultado
        self.ultimo_algoritmo = algoritmo
    
    def donwload(self):
        # Permitir al usuario seleccionar dónde guardar el archivo
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        
        # if archivo:  # Si el usuario selecciona una ruta
        #     with open(archivo, 'w') as file:
        #         # Escribir los resultados del último algoritmo ejecutado
        #         if self.ultimo_algoritmo in self.resultados:
        #             file.write(self.resultados[self.ultimo_algoritmo] + "\n\n")
        #         else:
        #             file.write("No se han encontrado resultados.\n")
                
        if archivo:  # Si el usuario selecciona una ruta
            with open(archivo, 'w') as file:
                # # Escribir los resultados de cada algoritmo en el archivo
                file.write(self.resultados['fuerza_bruta'] + "\n\n")
                file.write(self.resultados['programacion_dinamica'] + "\n\n")
                file.write(self.resultados['voraz'] + "\n\n")
            
            # Mensaje para indicar que el archivo ha sido guardado
            tk.messagebox.showinfo("Éxito", "El archivo se ha descargado correctamente.")

    def execute_fb(self):
        if self.modex.n > 25:
            messagebox.showerror("Error", "Esta solucion permite un maximo de 25 Agentes")
            return  
        
        mejor_estrategia, esfuerzo_maximo, menor_extremismo, tiempo_total,nuevas_opinionesFB = self.modex.rocFB()
        
        #Actualizar las etiquetas con los resultados
        self.titulo_prueba_label.config(text="Resultados algoritmo de fuerza bruta")
        self.menor_extremismo_label.config(text=f"{menor_extremismo}")
        # self.estrategia_label.config(text=f"{mejor_estrategia}")
        # print("Estrategia de moderación FB: ", mejor_estrategia)
        self.mostrar_estrategia(mejor_estrategia)
        self.esfuerzo_label.config(text=f"{esfuerzo_maximo} / {self.modex.R_max}")
        self.tiempo_label.config(text=f"{tiempo_total:.8f} segundos")
        self.grafico_canvas_res.delete("all")
        self.modex.crear_grafico_dispersión_resultados(self.grafico_canvas_res, nuevas_opinionesFB)
        
        
        resultado_fb = (
            f"Resultados Algoritmo de fuerza bruta: {self.nombre_archivo}\n"
            f"Estrategia de Moderacion: {mejor_estrategia}\n"
            f"Menor extremismo alcanzado: {menor_extremismo}\n"
            f"Esfuerzo total utilizado: {esfuerzo_maximo} \n"
            f"Tiempo de ejecucion: {tiempo_total:.8f} segundos\n"
        )    
        self.guardar_resultados('fuerza_bruta', resultado_fb)
    
    def execute_dp(self):
        tabla_dp, track_matrix, tiempo_totalDP = self.modex.rocDP()
        menor_extremismo = tabla_dp[self.modex.n][self.modex.R_max]
        estrategiaDP, agentes_seleccionados, esfuerzo_totalDP, Nuevas_OpinionesDP = self.modex.encontrar_agentes_seleccionados_con_tracking(track_matrix)

        # Actualizar etiquetas con los resultados
        self.titulo_prueba_label.config(text="Resultados algoritmo de programacion dinamica")
        self.menor_extremismo_label.config(text=f"{menor_extremismo}")
        # self.estrategia_label.config(text=f"{estrategiaDP}")
        # print("Estrategia de moderación Dinamica: ", estrategiaDP)
        self.mostrar_estrategia(estrategiaDP)
        self.esfuerzo_label.config(text=f"{esfuerzo_totalDP} / {self.modex.R_max}")
        self.tiempo_label.config(text=f"{tiempo_totalDP:.8f} segundos")
        self.grafico_canvas_res.delete("all")
        self.modex.crear_grafico_dispersión_resultados(self.grafico_canvas_res,  Nuevas_OpinionesDP)
        
        resultado_dp = (
            f"Resultados Algoritmo de programacion dinamica: {self.nombre_archivo}\n"
            f"Estrategia de Moderacion: {estrategiaDP}\n"
            f"Menor extremismo alcanzado: {menor_extremismo}\n"
            f"Esfuerzo total utilizado: {esfuerzo_totalDP} \n"
            f"Tiempo de ejecucion: {tiempo_totalDP:.8f} segundos\n"
        )    
        self.guardar_resultados('programacion_dinamica', resultado_dp)

    def execute_v(self):
        estrategiaV, agentes_seleccionados, extremismo_final, esfuerzo_totalV, tiempo_totalV, Nuevas_OpinionesV = self.modex.rocV()
        
        #Actualizar las etiquetas con los resultados
        self.titulo_prueba_label.config(text="Resultados algoritmo Voraz")
        self.menor_extremismo_label.config(text=f"{extremismo_final}")
        # self.estrategia_label.config(text=f"{estrategiaV}")
        # print("Estrategia de moderación Voraz: ", estrategiaV)
        self.mostrar_estrategia(estrategiaV)
        self.esfuerzo_label.config(text=f"{esfuerzo_totalV} / {self.modex.R_max}")
        self.tiempo_label.config(text=f"{tiempo_totalV:.8f} segundos")
        self.grafico_canvas_res.delete("all")
        self.modex.crear_grafico_dispersión_resultados(self.grafico_canvas_res, Nuevas_OpinionesV)
        
        resultado_v = (
            f"Resultados Algoritmo Voraz: {self.nombre_archivo}\n"
            f"Estrategia de Moderacion: {estrategiaV}\n"
            f"Menor extremismo alcanzado: {extremismo_final}\n"
            f"Esfuerzo total utilizado: {esfuerzo_totalV} \n"
            f"Tiempo de ejecucion: {tiempo_totalV:.8f} segundos\n"
        )    
        self.guardar_resultados('voraz', resultado_v)
        
    def mostrar_estrategia(self, estrategia):
        # Limpiar el canvas
        self.estrategia_canvas.delete("all")

        # Iterar sobre estrategiaDP y colocar la imagen correspondiente
        for i, valor in enumerate(estrategia):
            if valor == 1:
                self.estrategia_canvas.create_image(i * 40 + 20, 20, image=self.img_1)
            else:
                self.estrategia_canvas.create_image(i * 40 + 20, 20, image=self.img_0)

        # Asegurarse de que las imágenes no sean eliminadas por el recolector de basura
        self.estrategia_canvas.image = [self.img_1, self.img_0]
        
        total_width = len(estrategia) * 40
        self.estrategia_canvas.configure(scrollregion=(0, 0, total_width, 100))
