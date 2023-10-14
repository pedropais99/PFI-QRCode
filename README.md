# PFI-QRCode

En el siguiente documento, se explica el uso y se muestran las funciones utilizadas para la lectura de Codigos QR para el proyecto final de ingenieria (PFI) por parte del equipo 29 conformado por Santiago Salvioli y Pedro Pais.

# ¿Que se necesita para utilizar las funciones que se encuentran en el repositorio?

En primer lugar es condicion necesaria y suficiente para el uso de las funciones que se encuentran en el repositorio el uso de una cuenta de AWS y manejo del lenguaje de programacion Python.
(EXPLICAR LA DESCARGA DE LAS LIBRERIAS UTILIZADAS Y LA CONFIGURACION PARA LA TOMA DE FRAMES)

# ¿En que orden corren las funciones lambda del repositorio?

El orden de ejecucion de las funciones Lambda seria el siguiente:
    1. S3toS3
    2. Read_QR_Code

# Explicacion del funcionamiento de la funcion "S3toS3".

La funcion "S3toS3" fue realizada en el lenguaje Python. Esta misma lo que hace es, gracias a la posibilidad de Lambda de agregar disparadores o "triggers" para el arranque de sus funciones, identificar en las fotografias .jpg que se van subiendo al bucket seleccionado (las cuales son frames tomados del video transmitido por AWS Kisensis Video Stream) los codigos QR por medio del uso del servicio de AWS Rekognition. Estas imagenes que cuentan con un codigo QR detectado son filtradas y enviadas a un segundo bucket donde se realizara su decodificacion y lectura.

# Explicacion del funcionamiento de la funcion "Read_QR_Code"

La funcion "Read_QR_Code", es iniciada por un disparador o "trigger" cuando las fotos filtradas por la funcion "S3toS3" llegan al bucket de destino indicado. Gracias al uso de librerias propias del lenguage Python, en este caso ZBAR, PIL y urlib 
