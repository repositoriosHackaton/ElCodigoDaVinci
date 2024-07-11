import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
import datetime
import os

# Declarar variables globales para la captura de video y etiquetas de la interfaz
cap = None
label_img = None
label_color = None
label_mask = None

def analyze_image(image_path):
    global label_img, label_color, label_mask

    # Verificar que las etiquetas estén inicializadas
    if label_color is None or label_img is None or label_mask is None:
        print("Error: Las etiquetas no están inicializadas correctamente.")
        return

    # Leer y convertir la imagen a espacio de color HSV
    image = cv2.imread(image_path)
    frameHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Definir rangos de color para detectar rojo y verde
    rojoBajo1 = np.array([0, 120, 70], np.uint8)
    rojoAlto1 = np.array([10, 255, 255], np.uint8)
    rojoBajo2 = np.array([170, 120, 70], np.uint8)
    rojoAlto2 = np.array([180, 255, 255], np.uint8)
    verdeBajo = np.array([36, 50, 70], np.uint8)
    verdeAlto = np.array([89, 255, 255], np.uint8)

    # Crear máscaras para detectar colores
    maskRojo1 = cv2.inRange(frameHSV, rojoBajo1, rojoAlto1)
    maskRojo2 = cv2.inRange(frameHSV, rojoBajo2, rojoAlto2)
    maskRojo = cv2.add(maskRojo1, maskRojo2)
    maskRojoVis = cv2.bitwise_and(image, image, mask=maskRojo)
    maskVerde = cv2.inRange(frameHSV, verdeBajo, verdeAlto)
    maskVerdeVis = cv2.bitwise_and(image, image, mask=maskVerde)

    # Calcular porcentajes de cada color
    porcentajeRojo = (cv2.countNonZero(maskRojo) / (image.shape[0] * image.shape[1])) * 100
    porcentajeVerde = (cv2.countNonZero(maskVerde) / (image.shape[0] * image.shape[1])) * 100

    # Añadir texto a la imagen con los porcentajes
    cv2.putText(image, f'Rojo: {porcentajeRojo:.2f}%', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(image, f'Verde: {porcentajeVerde:.2f}%', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # Actualizar etiqueta de color mayoritario
    if porcentajeVerde > porcentajeRojo:
        label_color.config(text="El objeto es mayoritariamente VERDE", fg='#0033FF')
    else:
        label_color.config(text="El objeto es mayoritariamente ROJO", fg='#0033FF')

    # Convertir imagen a RGB y mostrar en la interfaz
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(image_rgb)
    img = ImageTk.PhotoImage(image=img)
    label_img.img = img
    label_img.config(image=img)

    # Combinar y mostrar máscaras en la interfaz
    mask_combined = cv2.addWeighted(maskRojoVis, 1, maskVerdeVis, 1, 0)
    mask_combined = cv2.cvtColor(mask_combined, cv2.COLOR_BGR2RGB)
    mask_img = Image.fromarray(mask_combined)
    mask_img = ImageTk.PhotoImage(image=mask_img)
    label_mask.img = mask_img
    label_mask.config(image=mask_img)

    # Guardar resultados en un archivo CSV
    file_path = "resultados_deteccion.csv"
    if not os.path.isfile(file_path) or os.stat(file_path).st_size == 0:
        with open(file_path, "w") as f:
            f.write("Fecha y Hora,Porcentaje Rojo,Porcentaje Verde\n")
    with open(file_path, "a") as f:
        f.write(f"{datetime.datetime.now()}, {porcentajeRojo:.2f}, {porcentajeVerde:.2f}\n")

def open_file():
    # Abrir diálogo para seleccionar archivo de imagen
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if file_path:
        analyze_image(file_path)

def start_application():
    global cap, label_img, label_color, label_mask

    def update_frame():
        ret, frame = cap.read()
        if ret:
            frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Definir rangos de color para detectar rojo y verde en tiempo real
            rojoBajo1 = np.array([0, 120, 70], np.uint8)
            rojoAlto1 = np.array([10, 255, 255], np.uint8)
            rojoBajo2 = np.array([170, 120, 70], np.uint8)
            rojoAlto2 = np.array([180, 255, 255], np.uint8)
            verdeBajo = np.array([36, 50, 70], np.uint8)
            verdeAlto = np.array([89, 255, 255], np.uint8)

            # Crear máscaras para detectar colores en el frame de video
            maskRojo1 = cv2.inRange(frameHSV, rojoBajo1, rojoAlto1)
            maskRojo2 = cv2.inRange(frameHSV, rojoBajo2, rojoAlto2)
            maskRojo = cv2.add(maskRojo1, maskRojo2)
            maskRojoVis = cv2.bitwise_and(frame, frame, mask=maskRojo)
            maskVerde = cv2.inRange(frameHSV, verdeBajo, verdeAlto)
            maskVerdeVis = cv2.bitwise_and(frame, frame, mask=maskVerde)

            # Calcular porcentajes de cada color en el frame de video
            porcentajeRojo = (cv2.countNonZero(maskRojo) / (frame.shape[0] * frame.shape[1])) * 100
            porcentajeVerde = (cv2.countNonZero(maskVerde) / (frame.shape[0] * frame.shape[1])) * 100

            # Añadir texto a la imagen con los porcentajes
            cv2.putText(frame, f'Rojo: {porcentajeRojo:.2f}%', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f'Verde: {porcentajeVerde:.2f}%', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Actualizar etiqueta de color mayoritario
            if porcentajeVerde > porcentajeRojo:
                label_color.config(text="El objeto es mayoritariamente VERDE", fg='#0033FF')
            else:
                label_color.config(text="El objeto es mayoritariamente ROJO", fg='#0033FF')

            # Convertir frame a RGB y mostrar en la interfaz
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = ImageTk.PhotoImage(image=img)
            label_img.img = img
            label_img.config(image=img)

            # Combinar y mostrar máscaras en la interfaz
            mask_combined = cv2.addWeighted(maskRojoVis, 1, maskVerdeVis, 1, 0)
            mask_combined = cv2.cvtColor(mask_combined, cv2.COLOR_BGR2RGB)
            mask_img = Image.fromarray(mask_combined)
            mask_img = ImageTk.PhotoImage(image=mask_img)
            label_mask.img = mask_img
            label_mask.config(image=mask_img)

            # Guardar resultados en un archivo CSV
            file_path = "resultados_deteccion.csv"
            if not os.path.isfile(file_path) or os.stat(file_path).st_size == 0:
                with open(file_path, "w") as f:
                    f.write("Fecha y Hora,Porcentaje Rojo,Porcentaje Verde\n")
            with open(file_path, "a") as f:
                f.write(f"{datetime.datetime.now()}, {porcentajeRojo:.2f}, {porcentajeVerde:.2f}\n")

            # Llamar a la función de actualización de frame después de 10 ms
            label_img.after(10, update_frame)
        else:
            label_color.config(text="Error en la captura de video", fg='#000000')

    # Iniciar captura de video
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        label_color.config(text="No se puede acceder a la cámara", fg='#000000')
        return

    # Configurar la interfaz de usuario
    frame1 = tk.Frame(root)
    frame1.grid(row=0, column=0, padx=10, pady=10, sticky='n')
    frame2 = tk.Frame(root)
    frame2.grid(row=0, column=1, padx=10, pady=10, sticky='n')

    label_img = tk.Label(frame1)
    label_img.pack()
    label_color = tk.Label(frame1, font=('Arial', 14))
    label_color.pack()
    label_mask = tk.Label(frame2)
    label_mask.pack()

    # Iniciar actualización de frames de video
    update_frame()

def init_labels():
    global label_img, label_color, label_mask

    # Configurar la interfaz de usuario
    frame1 = tk.Frame(root)
    frame1.grid(row=0, column=0, padx=10, pady=10, sticky='n')
    frame2 = tk.Frame(root)
    frame2.grid(row=0, column=1, padx=10, pady=10, sticky='n')

    label_img = tk.Label(frame1)
    label_img.pack()
    label_color = tk.Label(frame1, font=('Arial', 14))
    label_color.pack()
    label_mask = tk.Label(frame2)
    label_mask.pack()

def quit_application():
    # Cerrar la aplicación
    root.destroy()

# Configurar ventana principal de la aplicación
root = tk.Tk()
root.title("Detección de colores")

# Configurar marco de botones
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0, columnspan=2, pady=10)

# Botón para iniciar la captura de video
start_button = tk.Button(button_frame, text="Iniciar", command=start_application)
start_button.grid(row=0, column=0, padx=10)

# Botón para cargar una imagen desde archivo
file_button = tk.Button(button_frame, text="Cargar Imagen", command=lambda: [init_labels(), open_file()])
file_button.grid(row=0, column=1, padx=10)

# Botón para salir de la aplicación
quit_button = tk.Button(button_frame, text="Salir", command=quit_application)
quit_button.grid(row=0, column=2, padx=10)

# Iniciar bucle principal de la interfaz de usuario
root.mainloop()
