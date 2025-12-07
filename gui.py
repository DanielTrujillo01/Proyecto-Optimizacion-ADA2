import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

# ------------------------------------------------------------------
# INTENTOS DE IMPORTACIÓN DE LÓGICA Y LIBRERÍAS
# ------------------------------------------------------------------
# 1. Lógica de conversión (tu archivo convertidor.py)
try:
    import convertidor
    CONVERTIDOR_LOADED = True
except ImportError:
    CONVERTIDOR_LOADED = False

# 2. Librería oficial de MiniZinc para Python
try:
    import minizinc
    MINIZINC_LIB_LOADED = True
except ImportError:
    MINIZINC_LIB_LOADED = False

# ------------------------------------------------------------------
# CLASE PRINCIPAL DE LA GUI
# ------------------------------------------------------------------
class MiniZincApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Optimización MiniZinc")
        self.root.geometry("700x650")
        
        # Validaciones iniciales
        if not CONVERTIDOR_LOADED:
            messagebox.showwarning("Aviso", "No se encontró 'convertidor.py'. La pestaña 'Desde Archivo TXT' estará deshabilitada.")
        
        if not MINIZINC_LIB_LOADED:
            messagebox.showwarning("Aviso", "No tienes instalada la librería 'minizinc'.\nEjecuta: pip install minizinc\nLa pestaña de ejecución no funcionará.")

        # --- SISTEMA DE PESTAÑAS ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Pestaña 1: Convertir Archivo TXT
        self.tab_file = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_file, text="1. Convertir TXT a DZN")
        self.setup_tab_file()

        # Pestaña 2: Crear Manualmente
        self.tab_manual = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_manual, text="2. Crear DZN Manual")
        self.setup_tab_manual()

        # Pestaña 3: Ejecutar Modelo (NUEVA)
        self.tab_run = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_run, text="3. Ejecutar Modelo")
        self.setup_tab_run()

    # =================================================================
    # PESTAÑA 1: DESDE ARCHIVO
    # =================================================================
    def setup_tab_file(self):
        frame = ttk.Frame(self.tab_file, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Usa la lógica de 'convertidor.py' para transformar tus datos.").pack(pady=10)
        
        btn = ttk.Button(frame, text="Seleccionar TXT y Convertir", command=self.procesar_archivo_txt)
        btn.pack(pady=10, ipadx=10)
        
        if not CONVERTIDOR_LOADED: btn.state(['disabled'])

    def procesar_archivo_txt(self):
        input_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not input_path: return
        output_path = filedialog.asksaveasfilename(defaultextension=".dzn", filetypes=[("MiniZinc Data", "*.dzn")])
        if not output_path: return

        try:
            convertidor.convertir_txt_a_dzn(input_path, output_path)
            messagebox.showinfo("Éxito", f"DZN generado en:\n{output_path}")
            self.entry_dzn_path.delete(0, tk.END)
            self.entry_dzn_path.insert(0, output_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =================================================================
    # PESTAÑA 2: MANUAL
    # =================================================================
    def setup_tab_manual(self):
        canvas = tk.Canvas(self.tab_manual)
        scrollbar = ttk.Scrollbar(self.tab_manual, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        self.entries = {}
        def add_row(label, key):
            f = ttk.Frame(scroll_frame); f.pack(fill='x', pady=2)
            ttk.Label(f, text=label, width=15).pack(side='left')
            e = ttk.Entry(f); e.pack(side='left', fill='x', expand=True)
            self.entries[key] = e
        
        add_row("n:", "n"); add_row("m:", "m"); add_row("p:", "p"); add_row("v:", "v")
        ttk.Label(scroll_frame, text="Matriz s (fila por línea):").pack(pady=5)
        self.txt_s = tk.Text(scroll_frame, height=4, width=40); self.txt_s.pack()
        add_row("Costo Total:", "ct"); add_row("Max Movs:", "maxMovs")

        ttk.Button(scroll_frame, text="Guardar DZN", command=self.procesar_manual).pack(pady=10)

    def procesar_manual(self):
        try:
            save_path = filedialog.asksaveasfilename(defaultextension=".dzn", filetypes=[("Data", "*.dzn")])
            if save_path:
                with open(save_path, 'w') as f:
                    f.write("% DZN Generado Manualmente (Implementar lógica completa aquí)\n") 
                
                messagebox.showinfo("Info", "Archivo guardado.")
                self.entry_dzn_path.delete(0, tk.END)
                self.entry_dzn_path.insert(0, save_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =================================================================
    # PESTAÑA 3: EJECUTAR MODELO (MODIFICADA: CARPETA SOLUCIONES)
    # =================================================================
    def setup_tab_run(self):
        frame = ttk.Frame(self.tab_run, padding=20)
        frame.pack(fill='both', expand=True)

        # 1. Selector de Modelo (.mzn)
        f_mzn = ttk.Frame(frame); f_mzn.pack(fill='x', pady=5)
        ttk.Label(f_mzn, text="Modelo (.mzn):").pack(side='left')
        self.entry_mzn_path = ttk.Entry(f_mzn)
        self.entry_mzn_path.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(f_mzn, text="Buscar", command=lambda: self.buscar_fichero(self.entry_mzn_path, "*.mzn")).pack(side='left')

        # 2. Selector de Datos (.dzn)
        f_dzn = ttk.Frame(frame); f_dzn.pack(fill='x', pady=5)
        ttk.Label(f_dzn, text="Datos (.dzn):  ").pack(side='left')
        self.entry_dzn_path = ttk.Entry(f_dzn)
        self.entry_dzn_path.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(f_dzn, text="Buscar", command=lambda: self.buscar_fichero(self.entry_dzn_path, "*.dzn")).pack(side='left')

        # 3. Selector de Solver
        f_solver = ttk.Frame(frame); f_solver.pack(fill='x', pady=5)
        ttk.Label(f_solver, text="Solver:").pack(side='left')
        self.combo_solver = ttk.Combobox(f_solver, values=["gecode", "coin-bc", "chuffed"], state="readonly")
        self.combo_solver.current(0)
        self.combo_solver.pack(side='left', padx=5)

        # 4. Botón Ejecutar
        self.btn_run = ttk.Button(frame, text="EJECUTAR MODELO Y GUARDAR", command=self.ejecutar_minizinc)
        self.btn_run.pack(pady=15, ipadx=20, ipady=5)
        
        if not MINIZINC_LIB_LOADED: self.btn_run.state(['disabled'])

        # 5. Área de Resultados
        ttk.Label(frame, text="Salida del Solver:").pack(anchor='w')
        self.txt_output = tk.Text(frame, height=15)
        self.txt_output.pack(fill='both', expand=True)
        
        scroll_out = ttk.Scrollbar(self.txt_output, command=self.txt_output.yview)
        self.txt_output['yscrollcommand'] = scroll_out.set
        scroll_out.pack(side='right', fill='y')

    def buscar_fichero(self, entry_widget, extension):
        path = filedialog.askopenfilename(filetypes=[("Archivos", extension)])
        if path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, path)

    def ejecutar_minizinc(self):
        mzn_file = self.entry_mzn_path.get()
        dzn_file = self.entry_dzn_path.get()
        solver_name = self.combo_solver.get()

        if not os.path.exists(mzn_file):
            messagebox.showerror("Error", "El archivo del modelo (.mzn) no existe.")
            return
        if not os.path.exists(dzn_file):
            messagebox.showerror("Error", "El archivo de datos (.dzn) no existe.")
            return

        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, "Ejecutando... por favor espere.\n")
        self.root.update()

        try:
            # 1. Crear el modelo
            model = minizinc.Model(mzn_file)
            model.add_file(dzn_file)
            solver = minizinc.Solver.lookup(solver_name)
            instance = minizinc.Instance(solver, model)
            
            # 2. Resolver
            result = instance.solve()
            
            self.txt_output.insert(tk.END, "-"*40 + "\n")
            self.txt_output.insert(tk.END, f"Estado: {result.status}\n")
            self.txt_output.insert(tk.END, "-"*40 + "\n")
            
            # 3. Procesar Solución
            if result.solution:
                solucion_texto = str(result)
                self.txt_output.insert(tk.END, solucion_texto)
                
                # --- NUEVA LÓGICA DE GUARDADO EN CARPETA 'Soluciones' ---
                
                # A. Nombre base del archivo
                nombre_base = os.path.splitext(os.path.basename(dzn_file))[0]
                nombre_archivo = f"solucion{nombre_base}.txt"
                
                # B. Definir y crear carpeta "Soluciones"
                carpeta_destino = "Soluciones"
                if not os.path.exists(carpeta_destino):
                    os.makedirs(carpeta_destino) # Crea la carpeta si no existe
                
                # C. Crear ruta completa (carpeta + nombre archivo)
                ruta_completa = os.path.join(carpeta_destino, nombre_archivo)
                
                try:
                    with open(ruta_completa, "w", encoding="utf-8") as f:
                        f.write(solucion_texto)
                    
                    self.txt_output.insert(tk.END, f"\n\n[INFO] Solución guardada en: {ruta_completa}")
                    messagebox.showinfo("Guardado", f"Archivo generado correctamente en la carpeta 'Soluciones':\n\n{nombre_archivo}")
                
                except Exception as e_file:
                    self.txt_output.insert(tk.END, f"\n\n[ERROR] No se pudo guardar el archivo: {e_file}")
                # --------------------------------------------------------
            else:
                self.txt_output.insert(tk.END, "No se encontró solución (UNSATISFIABLE o Error).")

        except minizinc.error.MiniZincError as me:
            self.txt_output.insert(tk.END, f"\nError de MiniZinc:\n{me}")
        except Exception as e:
            self.txt_output.insert(tk.END, f"\nError general:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MiniZincApp(root)
    root.mainloop()