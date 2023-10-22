# PFI-QRCode

En el siguiente documento, se explica el uso y se muestran las funciones utilizadas para la lectura de Codigos QR para el proyecto final de ingenieria (PFI) por parte del equipo 29 conformado por Santiago Salvioli y Pedro Pais.

# ¿Que se necesita para utilizar las funciones que se encuentran en el repositorio?

En primer lugar es condicion necesaria y suficiente para el uso de las funciones que se encuentran en el repositorio el uso de una cuenta de AWS, manejo de Python y Linux. 
Se necesitaran: 
- La creacion de un bucket S3 para las funciones y otro para las librerias.
- Una maquina virtual con sistema operativo Raspberry Pi para la retransmision de video en tiempo real.
- Tener registrado en AWS IoT la camara con la que re realizara el streaming de video a AWS Kinesis Video Stream.
- Habilitacion para el guardado del video transmitio por AWS Kinesis Video Stream en formato de imagenes .jpg con el uso de del archivo "GuardarImagenes.json" del repositorio como se muestra en la imagen.
  ![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/1e5f3db5-3aa3-4f51-a021-2336221e6a1e)
  ![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/a63c06df-b83a-41cd-832a-6ad77698d23b)
  Se debera pegar en la consola el siguiente comando:
  - aws kinesisvideo update-image-generation-configuration \
--cli-input-json file://./update-image-generation-GuardarImagenes.json \
  Comprobamos que el archivo se haya actualizado con el siguiente comando:
  - aws kinesisvideo describe-image-generation-configuration --stream-name pfi_camara1
  ![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/5c49673e-1a15-428a-ae8c-a0a5b40dd40b)
- Un SNS Topic para el envio de notificaciones por las SNS subscriptions por mail y sitio web.

(EXPLICAR LA DESCARGA DE LAS LIBRERIAS UTILIZADAS, LA CONFIGURACION PARA LA TOMA DE FRAMES, CONFIGURACION DE LA HABILITACION PARA LA CONEXION ENTRE AWS KINESIS VIDEO STREAM CON EL VIDEO CAPTADO POR EL VEHICULO AUTONOMO (CONEXION POR SSH))

# Descargar librerias para la decodificacion de imagenes en AWS Lambda y configurarlas como layers de la funcion.

Para utilizar las librerias deberemos de descargarlas desde la consola de Cloudshell y guardarlas en un bucket S3 de la siguiente manera
-  

# ¿En que orden corren las funciones lambda del repositorio?

El orden de ejecucion de las funciones Lambda seria el siguiente:
    1. S3toS3
    2. Read_QR_Code

# Explicacion del funcionamiento de la funcion "S3toS3".

La funcion "S3toS3", gracias a la posibilidad de Lambda de agregar disparadores o "triggers" para el arranque de sus funciones, identifica en las fotografias .jpg que se van subiendo al bucket origen (las cuales son frames tomados del video transmitido por AWS Kisensis Video Stream) los codigos QR por medio del uso del servicio de AWS Rekognition. Estas imagenes que cuentan con un codigo QR detectado son filtradas y enviadas a un segundo bucket destino donde se realizara su decodificacion y lectura.

# Explicacion del funcionamiento de la funcion "Read_QR_Code"

La funcion "Read_QR_Code", es iniciada por un disparador o "trigger" cuando las fotos filtradas por la funcion "S3toS3" llegan al bucket de destino indicado. Gracias al uso de librerias propias del lenguage Python, en este caso ZBAR, PIL y urlib, el codigo QR identificado es decodificado, la imagen es guardada dentro del directorio "/tmp" para luego decodificarla usando uso de la funcion decode. Una vez realizada la decodificacion, se envia la misma por el uso de un SNS topic previamente proporcionado para el recibimiento de la respuesta de la funcion.
