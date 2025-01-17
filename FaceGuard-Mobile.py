# --------------------------------------Importamos librerias--------------------------------------------

from tkinter import *
import os
import cv2
from matplotlib import pyplot
import paho.mqtt.client as mqtt
from mtcnn.mtcnn import MTCNN
import json

# --------------------------- Configuración MQTT --------------------------------------

mqtt_broker = 'broker.emqx.io'
mqtt_topic = 'face_recognition/control'
mqtt_client_id = 'python_client'

# Función para conectar al broker MQTT
def connect_mqtt():
    client = mqtt.Client(mqtt_client_id)
    client.connect(mqtt_broker)
    return client

mqtt_client = connect_mqtt()

# Función para publicar un mensaje MQTT
def publish_message(action):
    message = {"action": action}
    mqtt_client.publish(mqtt_topic, json.dumps(message))  # Convertir a JSON
    print(f'Message published: {json.dumps(message)}')

# --------------------------- Funcion para almacenar el registro facial --------------------------------------

def registro_facial():
    # Vamos a capturar el rostro
    cap = cv2.VideoCapture(0)  # Elegimos la camara con la que vamos a hacer la deteccion
    while (True):
        ret, frame = cap.read()  # Leemos el video
        cv2.imshow('Registro Facial', frame)  # Mostramos el video en pantalla
        if cv2.waitKey(1) == 27:  # Cuando oprimamos "Escape" rompe el video
            break
    usuario_img = usuario.get()
    cv2.imwrite(usuario_img + ".jpg",
                frame)  # Guardamos la ultima caputra del video como imagen y asignamos el nombre del usuario
    cap.release()  # Cerramos
    cv2.destroyAllWindows()

    usuario_entrada.delete(0, END)  # Limpiamos los text variables
    Label(pantalla1, text="Registro Facial Exitoso", fg="green", font=("Calibri", 11)).pack()

    # ----------------- Detectamos el rostro y exportamos los pixeles --------------------------

    def reg_rostro(img, lista_resultados):
        data = pyplot.imread(img)
        for i in range(len(lista_resultados)):
            x1, y1, ancho, alto = lista_resultados[i]['box']
            x2, y2 = x1 + ancho, y1 + alto
            pyplot.subplot(1, len(lista_resultados), i + 1)
            pyplot.axis('off')
            cara_reg = data[y1:y2, x1:x2]
            cara_reg = cv2.resize(cara_reg, (150, 200),
                                  interpolation=cv2.INTER_CUBIC)  # Guardamos la imagen con un tamaño de 150x200
            cv2.imwrite(usuario_img + ".jpg", cara_reg)
            pyplot.imshow(data[y1:y2, x1:x2])
        pyplot.show()

    img = usuario_img + ".jpg"
    pixeles = pyplot.imread(img)
    detector = MTCNN()
    caras = detector.detect_faces(pixeles)
    reg_rostro(img, caras)


# ------------------------Crearemos una funcion para asignar al boton registro --------------------------------
def registro():
    global usuario
    global contra  # Globalizamos las variables para usarlas en otras funciones
    global usuario_entrada
    global contra_entrada
    global pantalla1

    pantalla1 = Toplevel(pantalla)  # Esta pantalla es de un nivel superior a la principal
    pantalla1.title("Registro - FaceGuard")
    pantalla1.geometry("720x480")  # Asignamos el tamaño de la ventana

    # --------- Empezaremos a crear las entradas ----------------------------------------

    usuario = StringVar()

    Label(pantalla1, text="Número de documento * ").pack()  # Mostramos en la pantalla 1 el usuario
    usuario_entrada = Entry(pantalla1,
                            textvariable=usuario)  # Creamos un text variable para que el usuario ingrese la info
    usuario_entrada.pack()

    # ------------ Vamos a crear el boton para hacer el registro facial --------------------
    Label(pantalla1, text="").pack()
    Button(pantalla1, text="Registro Facial", width=15, height=1, command=registro_facial).pack()


# --------------------------Funcion para el Login Facial --------------------------------------------------------
def login_facial():
    # ------------------------------Vamos a capturar el rostro-----------------------------------------------------
    cap = cv2.VideoCapture(0)  # Elegimos la camara con la que vamos a hacer la deteccion
    while (True):
        ret, frame = cap.read()  # Leemos el video
        cv2.imshow('Login Facial', frame)  # Mostramos el video en pantalla
        if cv2.waitKey(1) == 27:  # Cuando oprimamos "Escape" rompe el video
            break
    usuario_login = verificacion_usuario.get()  # Con esta variable vamos a guardar la foto pero con otro nombre para no sobreescribir
    cv2.imwrite(usuario_login + "LOG.jpg",
                frame)  # Guardamos la ultima caputra del video como imagen y asignamos el nombre del usuario
    cap.release()  # Cerramos
    cv2.destroyAllWindows()

    usuario_entrada2.delete(0, END)  # Limpiamos los text variables

    # ----------------- Funcion para guardar el rostro --------------------------

    def log_rostro(img, lista_resultados):
        data = pyplot.imread(img)
        for i in range(len(lista_resultados)):
            x1, y1, ancho, alto = lista_resultados[i]['box']
            x2, y2 = x1 + ancho, y1 + alto
            pyplot.subplot(1, len(lista_resultados), i + 1)
            pyplot.axis('off')
            cara_reg = data[y1:y2, x1:x2]
            cara_reg = cv2.resize(cara_reg, (150, 200), interpolation=cv2.INTER_CUBIC)  # Guardamos la imagen 150x200
            cv2.imwrite(usuario_login + "LOG.jpg", cara_reg)
            return pyplot.imshow(data[y1:y2, x1:x2])
        pyplot.show()

    # -------------------------- Detectamos el rostro-------------------------------------------------------

    img = usuario_login + "LOG.jpg"
    pixeles = pyplot.imread(img)
    detector = MTCNN()
    caras = detector.detect_faces(pixeles)
    log_rostro(img, caras)

    # -------------------------- Funcion para comparar los rostros --------------------------------------------
    def orb_sim(img1, img2):
        orb = cv2.ORB_create()  # Creamos el objeto de comparacion

        kpa, descr_a = orb.detectAndCompute(img1, None)  # Creamos descriptor 1 y extraemos puntos claves
        kpb, descr_b = orb.detectAndCompute(img2, None)  # Creamos descriptor 2 y extraemos puntos claves

        comp = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)  # Creamos comparador de fuerza

        matches = comp.match(descr_a, descr_b)  # Aplicamos el comparador a los descriptores

        regiones_similares = [i for i in matches if
                              i.distance < 70]  # Extraemos las regiones similares en base a los puntos claves
        if len(matches) == 0:
            return 0
        return len(regiones_similares) / len(matches)  # Exportamos el porcentaje de similitud

    # ---------------------------- Importamos las imagenes y llamamos la funcion de comparacion ---------------------------------

    im_archivos = os.listdir()  # Vamos a importar la lista de archivos con la libreria os
    if usuario_login + ".jpg" in im_archivos:  # Comparamos los archivos con el que nos interesa
        rostro_reg = cv2.imread(usuario_login + ".jpg", 0)  # Importamos el rostro del registro
        rostro_log = cv2.imread(usuario_login + "LOG.jpg", 0)  # Importamos el rostro del inicio de sesion
        similitud = orb_sim(rostro_reg, rostro_log)
        if similitud >= 0.9:
            Label(pantalla2, text="Bienvenido a [nombre propiedad horizontal]", fg="green", font=("Calibri", 11)).pack()
            print("Bienvenido al sistema usuario: ", usuario_login)
            print("Compatibilidad con la foto del registro: ", similitud)
            publish_message("open")  # Publica el mensaje para abrir la puerta
        else:
            print("Rostro incorrecto, verifique su usuario")
            print("Compatibilidad con la foto del registro: ", similitud)
            Label(pantalla2, text="Incompatibilidad de rostros", fg="red", font=("Calibri", 11)).pack()
    else:
        print("Usuario no encontrado")
        Label(pantalla2, text="Usuario no encontrado", fg="red", font=("Calibri", 11)).pack()


# ------------------------Funcion que asignaremos al boton login -------------------------------------------------

def login():
    global pantalla2
    global verificacion_usuario
    global verificacion_contra
    global usuario_entrada2
    global contra_entrada2

    pantalla2 = Toplevel(pantalla)
    pantalla2.title("Ingreso - FaceGuard")
    pantalla2.geometry("720x480")  # Creamos la ventana

    verificacion_usuario = StringVar()

    # ---------------------------------- Ingresamos los datos --------------------------
    Label(pantalla2, text="Número de documento * ").pack()
    usuario_entrada2 = Entry(pantalla2, textvariable=verificacion_usuario)
    usuario_entrada2.pack()

    # ------------ Vamos a crear el boton para hacer el login facial --------------------
    Label(pantalla2, text="").pack()
    Button(pantalla2, text="Continuar", width=20, height=1, command=login_facial).pack()


# ------------------------- Funcion de nuestra pantalla principal ------------------------------------------------

def pantalla_principal():
    global pantalla  # Globalizamos la variable para usarla en otras funciones
    pantalla = Tk()

    pantalla.geometry("720x480")  # Asignamos el tamaño de la ventana
    pantalla.title("FaceGuard - Reconocimiento Facial")  # Asignamos el titulo de la pantalla
    Label(text="FaceGuard - Nombre de la Propiedad Horizontal", bg="gray", width="300", height="2",
          font=("Verdana", 13)).pack()  # Asignamos caracteristicas de la ventana

    # ------------------------- Vamos a Crear los Botones ------------------------------------------------------

    Label(text="").pack()  # Creamos el espacio entre el titulo y el primer boton
    Button(text="Ingresar", height="2", width="30", command=login).pack()
    Label(text="").pack()  # Creamos el espacio entre el primer boton y el segundo boton
    Button(text="Registrarse", height="2", width="30", command=registro).pack()

    pantalla.mainloop()


pantalla_principal()
