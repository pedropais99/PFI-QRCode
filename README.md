# PFI-QRCode

En el siguiente documento, se explica el uso y se muestran las funciones utilizadas para la lectura de Codigos QR para el proyecto final de ingenieria (PFI) por parte del equipo 29 conformado por Santiago Salvioli y Pedro Pais.

# ¿Que se necesita para utilizar las funciones que se encuentran en el repositorio?

En primer lugar es condicion necesaria y suficiente para el uso de las funciones que se encuentran en el repositorio el uso de una cuenta de AWS, manejo de Python y Linux. 
Se necesitaran: 
- Crear maquina virtual con sistema operativo Raspberry Pi para la retransmision de video en tiempo real.
  - Descargar dentro de la maquina virtual las librerias que permitan la retrasmision de video en tiempo real.
- Habilitar la conexion a la camara del vehiculo autonomo sin el uso de credenciales.
- Registrar en AWS IoT la camara con la que se realizara el streaming de video a AWS Kinesis Video Stream.
- Crear un bucket S3 por funcion y otro para las librerias.
- Crear un SNS Topic y estar suscripto al mismo.
- Descargar librerias para la decodificacion de imagenes en AWS Lambda y configurarlas como layers de la funcion.
- Configurar evento disparador (trigger) en AWS Lambda con S3 
- Habilitacion para el guardado del video transmitio por AWS Kinesis Video Stream en formato de imagenes .jpg con el uso de del archivo "GuardarImagenes.json" del repositorio como se muestra en la imagen.

# Descargar dentro de la maquina virtual las librerias que permitan la retrasmision de video en tiempo real.

# Habilitar la conexion a la camara del vehiculo autonomo sin el uso de credenciales.

# Crear un bucket S3 por funcion y otro para las librerias.

# Crear un SNS Topic y estar suscripto al mismo.

# Descargar librerias para la decodificacion de imagenes en AWS Lambda y configurarlas como layers de la funcion.

Para utilizar las librerias deberemos de descargarlas desde la consola de Cloudshell y guardarlas en un bucket S3 de la siguiente manera
-  Deberemos de movernos nuevamente a Cloudlshell y copiar el siguiente comando de git
  ```
  git clone https://github.com/aws-samples/Barcode-QR-Decoder-Lambda.git
  ```
- Tendremos que correr el archivo ```setup.sh``` para generar las lambda layers que seran guardadas en el bucket s3 especificado.
    - ``` sh Barcode-QR-Decoder-Lambda/src/code/setup.sh -b <BUCKET_NAME> ```
- Una vez que termine el script, dentro del bucket especificado tendremos los archivos .zip.
  
![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/ad242291-27f2-4274-af0c-641d7599a9a0)

- Dentro de AWS Lambda iremos a la seccion de Layers y crearemos las layers correspondientes.
  
![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/dbbdf5c1-ad50-4b35-ba5b-b6f0ce31b6e7)
![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/b3a5d047-6136-4a03-8fb1-3a18e3e1ae04)

- Creadas las layers, nos moveremos a nuestra funcion "ReadQRCode" y dentro de la solapa de "Code" al fondo de la pagina tendremos la opcion de agregar layers
- Seleccionamos "Add a Layer" y cargamos las layers creadas anteriormente.
  
![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/5953c900-203d-4682-b11d-c0a4d119da60)

# Configurar evento disparador (trigger) en AWS Lambda con S3
- Estando en nuestra funcion Lambda, nos dirigiremos a la opcion de "Add trigger".

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/3e74d2b7-df9a-4c37-a313-2496c842d958)

- Dentro de esta opcion, crearemos el trigger para que la funcion lambda corra siempre que un objeto sea creado dentro del bucket seleccionado.

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/64e75e59-9f3f-4716-8534-1cb6fbb58257)

- Una vez terminado, seleccionamos "Add" y ya queda nuestro trigger configurado para la correcta ejecucion de la funcion.

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/466677e4-8c68-42e0-ae6a-fae48cf233d9)

# Habilitacion para el guardado del video transmitio por AWS Kinesis Video Stream en formato de imagenes .jpg con el uso de del archivo "GuardarImagenes.json" del repositorio como se muestra en la imagen.
  
  ![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/1e5f3db5-3aa3-4f51-a021-2336221e6a1e)
  ![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/a63c06df-b83a-41cd-832a-6ad77698d23b)
  
  Se debera pegar en la consola el siguiente comando:
  ```
  - aws kinesisvideo update-image-generation-configuration \
  --cli-input-json file://./update-image-generation-GuardarImagenes.json \
  ```
  Comprobamos que el archivo se haya actualizado con el siguiente comando:
  ```
  - aws kinesisvideo describe-image-generation-configuration --stream-name pfi_camara1
  ```
  ![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/5c49673e-1a15-428a-ae8c-a0a5b40dd40b)
  






