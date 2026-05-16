import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd
import time
import os
import copy


# Variables globales para mantener persistencia de datos
# durante toda la ejecucion de la interfaz
lista_datos = []
columnas_df = []


def cargar_datos():
    global lista_datos, columnas_df

    # Seleccion del archivo desde el explorador
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo de datos (CSV o TXT)",
        filetypes=[
            ("Archivos de datos", "*.csv *.txt"),
            ("Todos los archivos", "*.*")
        ]
    )

    # Si el usuario cancela no se hace nada
    if not ruta:
        return

    try:
        # Lectura dinamica dependiendo del formato
        if ruta.endswith('.csv'):
            df = pd.read_csv(ruta)
        else:
            # sep=None permite detectar separadores automaticamente
            df = pd.read_csv(ruta, sep=None, engine='python')

        # Validacion minima para permitir ordenamiento
        if len(df.columns) < 2:
            messagebox.showerror(
                "Error",
                "El archivo debe tener minimo 2 columnas para poder ordenar."
            )
            return

        columnas_df = df.columns.tolist()
        lista_datos = df.values.tolist()

        # Restriccion pedida en el taller
        if len(lista_datos) < 10000:
            messagebox.showerror(
                "Error",
                f"El archivo contiene {len(lista_datos)} registros.\n"
                "Se requieren al menos 10,000 registros."
            )

            lista_datos = []
            return

        # Configuracion dinamica del Treeview
        tabla["columns"] = columnas_df

        for col in columnas_df:
            tabla.heading(col, text=col)

            # Ajuste proporcional segun cantidad de columnas
            tabla.column(col, width=int(1000 / len(columnas_df)))

        mostrar_datos(lista_datos)

        texto_resultados.set(
            "Datos cargados con éxito\n\n"
            f"Archivo:\n{os.path.basename(ruta)}\n\n"
            f"Total de registros: {len(lista_datos):,}\n"
            "El ordenamiento se realizará usando la última columna."
        )

    except Exception as e:
        # Manejo de excepciones para evitar crasheos
        messagebox.showerror(
            "Error",
            f"No fue posible procesar el archivo.\n\nDetalle: {e}"
        )


def mostrar_datos(datos):
    # Limpieza previa de filas para evitar duplicados visuales
    for fila in tabla.get_children():
        tabla.delete(fila)

    # Vista previa limitada para evitar desbordamiento visual
    # y congelamiento de la interfaz 
    for dato in datos[:100]:
        tabla.insert("", tk.END, values=dato)


def bubble_sort(datos, col_criterio):
    n = len(datos)

    # Complejidad temporal promedio: O(n²)
    for i in range(n):

        intercambio = False

        for j in range(0, n - i - 1):

            if datos[j][col_criterio] > datos[j + 1][col_criterio]:

                # Intercambio clasico usando variable auxiliar
                aux = datos[j]
                datos[j] = datos[j + 1]
                datos[j + 1] = aux

                intercambio = True

        # Optimización: si no hubo cambios ya esta ordenado
        if not intercambio:
            break

    return datos


def insertion_sort(datos, col_criterio):

    for i in range(1, len(datos)):

        actual = datos[i]
        j = i - 1

        while j >= 0 and datos[j][col_criterio] > actual[col_criterio]:

            datos[j + 1] = datos[j]
            j -= 1

        datos[j + 1] = actual

    return datos


def selection_sort(datos, col_criterio):

    n = len(datos)

    for i in range(n):

        minimo = i

        for j in range(i + 1, n):

            if datos[j][col_criterio] < datos[minimo][col_criterio]:
                minimo = j

        # Intercambio manual para mostrar la logica del algoritmo
        aux = datos[i]
        datos[i] = datos[minimo]
        datos[minimo] = aux

    return datos


def exportar_excel(datos):
    global columnas_df

    path_salida = filedialog.asksaveasfilename(
        title="Guardar archivo Excel",
        defaultextension=".xlsx",
        filetypes=[("Archivos Excel", "*.xlsx")]
    )

    if not path_salida:
        return None

    try:
        # Reconstruccion del DataFrame para exportacion
        df = pd.DataFrame(datos, columns=columnas_df)

        df.to_excel(path_salida, index=False)

        return path_salida

    except Exception as e:

        messagebox.showerror(
            "Error al exportar",
            f"No se pudo generar el Excel:\n{e}"
        )

        return None


def ordenar(tipo):
    global lista_datos

    # Validacion basica antes de ordenar
    if len(lista_datos) == 0:

        messagebox.showwarning(
            "Advertencia",
            "Primero debe cargar un archivo CSV o TXT."
        )

        return

    # Se toma la ultima columna como criterio
    col_criterio = len(lista_datos[0]) - 1

    # Copia profunda para no modificar el array original
    copia = copy.deepcopy(lista_datos)

    inicio = time.perf_counter()

    if tipo == "Bubble":

        ordenados = bubble_sort(copia, col_criterio)

        complejidad = (
            "Algoritmo: Bubble Sort\n"
            "• Peor caso: O(n²)\n"
            "• Caso promedio: Θ(n²)\n"
            "• Mejor caso: Ω(n)"
        )

    elif tipo == "Insertion":

        ordenados = insertion_sort(copia, col_criterio)

        complejidad = (
            "Algoritmo: Insertion Sort\n"
            "• Peor caso: O(n²)\n"
            "• Caso promedio: Θ(n²)\n"
            "• Mejor caso: Ω(n)"
        )

    else:

        ordenados = selection_sort(copia, col_criterio)

        complejidad = (
            "Algoritmo: Selection Sort\n"
            "• Peor caso: O(n²)\n"
            "• Caso promedio: Θ(n²)\n"
            "• Mejor caso: Ω(n²)"
        )

    fin = time.perf_counter()

    # Conversion a milisegundos para mayor precision
    tiempo_ms = (fin - inicio) * 1000

    mostrar_datos(ordenados)

    ruta_excel = exportar_excel(ordenados)

    if ruta_excel:

        texto_resultados.set(
            "Proceso de ordenamiento finalizado\n\n"
            f"Tiempo de ejecución: {tiempo_ms:.2f} ms "
            f"({tiempo_ms/1000:.4f} s)\n\n"
            f"{complejidad}\n\n"
            f"Archivo exportado:\n{os.path.basename(ruta_excel)}"
        )

    else:

        texto_resultados.set(
            "Ordenamiento completado\n"
            "(Exportación cancelada)\n\n"
            f"Tiempo de ejecución: {tiempo_ms:.2f} ms\n\n"
            f"{complejidad}"
        )


# Configuración de la interfaz gráfica 

ventana = tk.Tk()

ventana.title("Taller_5 : Análisis y Diseño de Algoritmos")

ventana.geometry("1200x800")

ventana.config(bg="#1e1e1e")


titulo = tk.Label(
    ventana,
    text="IMPLEMENTACIÓN Y ANÁLISIS ASINTÓTICO\nDE ALGORITMOS DE ORDENAMIENTO",
    font=("Arial", 18, "bold"),
    bg="#1e1e1e",
    fg="#ffffff"
)

titulo.pack(pady=15)


frame_botones = tk.Frame(
    ventana,
    bg="#1e1e1e"
)

frame_botones.pack(pady=10)


btn_cargar = tk.Button(
    frame_botones,
    text="[1] Cargar datos\n(.txt o .csv)",
    font=("Arial", 10, "bold"),
    bg="#3498db",
    fg="white",
    width=20,
    height=3,
    command=cargar_datos
)

btn_cargar.grid(row=0, column=0, padx=5)


btn_bubble = tk.Button(
    frame_botones,
    text="[2] Ordenar usando\nBubble Sort",
    font=("Arial", 10, "bold"),
    bg="#e74c3c",
    fg="white",
    width=20,
    height=3,
    command=lambda: ordenar("Bubble")
)

btn_bubble.grid(row=0, column=1, padx=5)


btn_insertion = tk.Button(
    frame_botones,
    text="[3] Ordenar usando\nInsertion Sort",
    font=("Arial", 10, "bold"),
    bg="#2ecc71",
    fg="white",
    width=20,
    height=3,
    command=lambda: ordenar("Insertion")
)

btn_insertion.grid(row=0, column=2, padx=5)


btn_selection = tk.Button(
    frame_botones,
    text="[4] Ordenar usando\nSelection Sort",
    font=("Arial", 10, "bold"),
    bg="#f39c12",
    fg="white",
    width=20,
    height=3,
    command=lambda: ordenar("Selection")
)

btn_selection.grid(row=0, column=3, padx=5)


btn_salir = tk.Button(
    frame_botones,
    text="[5] Salir",
    font=("Arial", 10, "bold"),
    bg="#7f8c8d",
    fg="white",
    width=20,
    height=3,
    command=ventana.destroy
)

btn_salir.grid(row=0, column=4, padx=5)


# Contenedor de la tabla y scrollbar
frame_tabla = tk.Frame(ventana)

frame_tabla.pack(
    pady=15,
    fill=tk.BOTH,
    expand=True,
    padx=20
)


tabla = ttk.Treeview(
    frame_tabla,
    show="headings",
    height=15
)

tabla.pack(
    side=tk.LEFT,
    fill=tk.BOTH,
    expand=True
)


scrollbar = ttk.Scrollbar(
    frame_tabla,
    orient=tk.VERTICAL,
    command=tabla.yview
)

tabla.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(
    side=tk.RIGHT,
    fill=tk.Y
)


# Panel inferior de resultados y complejidad
texto_resultados = tk.StringVar()

texto_resultados.set(
    "Sistema listo.\n"
    "Cargue un archivo con minimo 10,000 registros."
)


label_resultados = tk.Label(
    ventana,
    textvariable=texto_resultados,
    font=("Consolas", 11),
    justify="left",
    bg="#2d2d2d",
    fg="#4af626",
    relief=tk.SOLID,
    bd=1,
    padx=15,
    pady=15
)

label_resultados.pack(
    pady=15,
    fill=tk.X,
    padx=20
)


# Inicio de la interfaz grafica
ventana.mainloop()