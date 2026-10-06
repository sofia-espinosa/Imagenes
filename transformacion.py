#Convierte una imagen en un dibujo de líneas y puntos (PNG y SVG).

import cv2
import numpy as np

# PARÁMETROS (puedes cambiarlos para probar resultados)
RUTA_ENTRADA = "1.png"            # imagen de entrada
RUTA_PNG = "salida_puntos.png"    # imagen de salida
RUTA_SVG = "salida.svg"           # archivo vectorial de salida

TAMANO_MAXIMO = 900     # la imagen se reduce si es más grande que esto (en píxeles)
CANNY_BAJO = 50         # umbral bajo para detectar bordes
CANNY_ALTO = 150        # umbral alto para detectar bordes

# Qué tanto se simplifica cada línea
# Número alto (ej. 10): pocos puntos, dibujo más "cuadrado".
# Número bajo (ej. 1): muchos puntos, dibujo más fiel a la imagen.
EPSILON = 3.0 

# Las líneas más cortas que este valor (en píxeles) se borran, porque normalmente son manchas o detalles sin importancia.
LARGO_MINIMO = 40 
MOSTRAR_NUMEROS = False # True para escribir el número de cada punto

# FUNCIONES
def cargar_imagen(ruta):
    imagen = cv2.imread(ruta)
    if imagen is None:
        raise FileNotFoundError("No se pudo leer la imagen: " + ruta)
    return imagen


# ajusta la imagen si es muy grande pero mantiene su proporción
def reducir_imagen(imagen, tamano_maximo):
    alto, ancho = imagen.shape[:2]
    lado_mayor = max(alto, ancho)

    if lado_mayor > tamano_maximo:
        factor = tamano_maximo / lado_mayor
        nuevo_ancho = int(ancho * factor)
        nuevo_alto = int(alto * factor)
        imagen = cv2.resize(imagen, (nuevo_ancho, nuevo_alto),
                            interpolation=cv2.INTER_AREA)
    return imagen


#Devuelve una imagen en blanco y negro donde solo se ven los bordes.
def detectar_bordes(imagen):
    # Pasar a escala de grises
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Suavizar para eliminar ruido pequeño
    gris = cv2.GaussianBlur(gris, (5, 5), 0)

    # Detectar bordes con el algoritmo de Canny
    bordes = cv2.Canny(gris, CANNY_BAJO, CANNY_ALTO)

    # Unir bordes que quedaron muy cerca entre sí
    kernel = np.ones((3, 3), np.uint8)
    bordes = cv2.morphologyEx(bordes, cv2.MORPH_CLOSE, kernel)

    return bordes

#Busca los contornos en la imagen de bordes y los simplifica
def encontrar_polilineas(bordes):
    contornos, _ = cv2.findContours(bordes, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    polilineas = []
    for contorno in contornos:
        # Descartar contornos muy cortos (probablemente ruido)
        largo = cv2.arcLength(contorno, False)
        if largo < LARGO_MINIMO:
            continue

        # Simplificar el contorno (algoritmo Douglas-Peucker)
        simplificado = cv2.approxPolyDP(contorno, EPSILON, False)

        # Convertir al formato simple: lista de tuplas (x, y)
        puntos = []
        for punto in simplificado:
            x = int(punto[0][0])
            y = int(punto[0][1])
            puntos.append((x, y))

        # Una línea necesita al menos 2 puntos
        if len(puntos) >= 2:
            polilineas.append(puntos)

    return polilineas

#Cuenta cuántos puntos hay en total en todas las polilíneas
def contar_puntos(polilineas):
    total = 0
    for puntos in polilineas:
        total = total + len(puntos)
    return total

#Dibuja las líneas y los puntos sobre blanco
def dibujar_resultado(polilineas, alto, ancho):
    NEGRO = (0, 0, 0)
    lienzo = np.full((alto, ancho, 3), 255, np.uint8)  # 255 = blanco

    numero_punto = 1
    for puntos in polilineas:
        # Dibujar las líneas que unen un punto con el siguiente
        for i in range(len(puntos) - 1):
            cv2.line(lienzo, puntos[i], puntos[i + 1], NEGRO, 1, cv2.LINE_AA)

        # Dibujar cada punto 
        for punto in puntos:
            cv2.circle(lienzo, punto, 2, NEGRO, -1)
            if MOSTRAR_NUMEROS:
                posicion_texto = (punto[0] + 4, punto[1] - 4)
                cv2.putText(lienzo, str(numero_punto), posicion_texto,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, NEGRO, 1, cv2.LINE_AA)
            numero_punto = numero_punto + 1

    return lienzo

#Guarda las polilíneas en un archivo SVG
def guardar_svg(polilineas, alto, ancho, ruta):
    with open(ruta, "w") as archivo:
        
        # Encabezado del SVG
        archivo.write('<svg xmlns="http://www.w3.org/2000/svg" '
                      'width="' + str(ancho) + '" height="' + str(alto) + '" '
                      'viewBox="0 0 ' + str(ancho) + ' ' + str(alto) + '">\n')

        # Fondo blanco
        archivo.write('<rect width="100%" height="100%" fill="white"/>\n')

        # Una línea (polyline) por cada polilínea
        for puntos in polilineas:
            texto_puntos = ""
            for x, y in puntos:
                texto_puntos = texto_puntos + str(x) + "," + str(y) + " "

            archivo.write('<polyline points="' + texto_puntos + '" '
                          'fill="none" stroke="black" stroke-width="1"/>\n')

        archivo.write('</svg>')


# PROGRAMA PRINCIPAL
def main():
    # 1. Cargar y preparar la imagen
    imagen = cargar_imagen(RUTA_ENTRADA)
    imagen = reducir_imagen(imagen, TAMANO_MAXIMO)
    alto, ancho = imagen.shape[:2]

    # 2. Detectar bordes
    bordes = detectar_bordes(imagen)

    # 3. Encontrar contornos y simplificarlos
    polilineas = encontrar_polilineas(bordes)
    print("Contornos:", len(polilineas))
    print("Puntos totales:", contar_puntos(polilineas))

    # 4. Dibujar y guardar el PNG
    lienzo = dibujar_resultado(polilineas, alto, ancho)
    cv2.imwrite(RUTA_PNG, lienzo)

    # 5. Guardar el SVG
    guardar_svg(polilineas, alto, ancho, RUTA_SVG)

    print("Listo:", RUTA_PNG, "y", RUTA_SVG)


# Esto hace que main() se ejecute solo si corres este archivo directamente
if __name__ == "__main__":
    main()