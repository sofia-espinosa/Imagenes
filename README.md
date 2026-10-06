# Imagenes
El script transforma imágenes PNG o JPG en dibujos de líneas y puntos, exportándolos en PNG y SVG. Reescala la imagen, la convierte a escala de grises, reduce el ruido y detecta bordes con Canny. Luego extrae y simplifica los contornos con Douglas-Peucker y genera el resultado final mediante polilíneas.

Flujo de trabajo del código:
1. Carga y ajuste de tamaño: Lee la imagen de entrada y la escala proporcionalmente si supera el tamaño máximo configurado (TAMANO_MAXIMO = 900).
2. Detección de bordes: Convierte la imagen a escala de grises, aplica un desenfoque Gaussiano para reducir el ruido y utiliza el algoritmo Canny con operaciones morfológicas para aislar las líneas principales.
3. Extracción y simplificación de contornos: Encuentra los contornos, filtra los que son demasiado cortos (LARGO_MINIMO) y los simplifica mediante el algoritmo Douglas-Peucker (EPSILON) para reducirlos a puntos clave.
4. Generación de archivos de salida:
   4.1 PNG: Crea una imagen de fondo blanco donde dibuja los puntos y las líneas que los conectan (opcionalmente puede numerar cada punto).
   4.2 SVG: Exporta las coordenadas obtenidas a un archivo de vectores escalable mediante etiquetas <polyline>.   
