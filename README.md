# PFI-QRCode

En el siguiente documento, se explica el uso y se muestran las funciones utilizadas para la lectura de Codigos QR para el proyecto final de ingenieria (PFI) por parte del equipo 29 conformado por Santiago Salvioli y Pedro Pais.

# ¿Que se necesita para utilizar las funciones que se encuentran en el repositorio?

En primer lugar es condicion necesaria y suficiente para el uso de las funciones que se encuentran en el repositorio el uso de una cuenta de AWS, manejo de Python y Linux. 
Se necesitaran: 
- Habilitar la conexion a la camara del vehiculo autonomo sin el uso de credenciales.
- Crear maquina virtual con sistema operativo Raspberry Pi para la retransmision de video en tiempo real.
  - Descargar dentro de la maquina virtual las librerias que permitan la retrasmision de video en tiempo real.
- Registrar en AWS IoT la camara con la que se realizara el streaming de video a AWS Kinesis Video Stream.
- Crear un bucket S3 por funcion y otro para las librerias.
- Crear un SNS Topic y estar suscripto al mismo.
- Descargar librerias para la decodificacion de imagenes en AWS Lambda y configurarlas como layers de la funcion.
- Configurar evento disparador (trigger) en AWS Lambda con S3 
- Habilitacion para el guardado del video transmitio por AWS Kinesis Video Stream en formato de imagenes .jpg con el uso de del archivo "GuardarImagenes.json" del repositorio como se muestra en la imagen.

# Habilitar la conexion a la camara del vehiculo autonomo sin el uso de credenciales.

# Descargar dentro de la maquina virtual las librerias que permitan la retrasmision de video en tiempo real.

Dentro de nuestra maquina virtual (vm) iremos a la consola y correremos el siguiente comando para comenzar la configuracion. Se hace un chequeo de que la maquina tenga las librerias necesarias para comenzar con el build y en caso de que no las tenga que las descargue.
```
sudo apt-get install cmake m4 git build-essential
```
Descargaremos las dependencias dadas por AWS clonando el siguiente repositorio en nuestra vm.
```
git clone https://github.com/awslabs/amazon-kinesis-video-streams-producer-sdk-cpp.git
```
Creamos el directorio "build" dentro de la carpeta de nuestro repositorio recien clonado y nos movemos a el.
```
mkdir -p amazon-kinesis-video-streams-producer-sdk-cpp/build
cd amazon-kinesis-video-streams-producer-sdk-cpp/build
```
Ahora instalaremos las librerias requeridas dentro de este directorio
```
$ sudo apt-get install libssl-dev libcurl4-openssl-dev liblog4cplus-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev gstreamer1.0-plugins-base-apps gstreamer1.0-plugins-bad gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-tools
```
Generamos la build para crear las muestras (samples), usando el siguiente comando.
```
cmake .. -DBUILD_GSTREAMER_PLUGIN=ON
```
Terminado el proceso, hacemos uso del comando ```make```.
Chequeamos el contenido del directorio como se muestra en pantalla.

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/6fdab767-7454-4b3a-934c-74524d5fd57e)

Se puede ver que contamos con los archivos ```kvs_gstreamer_sample``` (archivo que usaremos para la retransmision de video y ```libgstkvssink.so``` (plugin que tambien podemos utilizar).

# Registrar en AWS IoT la camara con la que se realizara el streaming de video a AWS Kinesis Video Stream.

Continuando con la configuracion del entorno de streaming de video, ahora se debera ir a la consola de AWS y buscar el servicio "IoT Core"

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/2d09514f-cb34-414c-beba-58926c60d8ac)

Buscamos en la barra lateral izquierda la seccion de "Manage" --> "All devices" --> "Thing type", donde crearemos un thing type.

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/c598a1ff-8593-4336-8bd4-3c19ce902020)

Creado el thing type, iremos a "Manage" --> "All devices" --> "Things" y crearemos una de la siguiente manera.

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/aa37bbe6-6d2d-4335-836f-f43aabb8286d)

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/3b0e4f6d-6c7a-48d2-9a5f-0a6ff2d9e0bc)

En este punto nos daran la opcion de adjuntar una politica a nuestra IoT Thing, saltearemos este paso porque se necesita crear una politica nueva para que la IoT Thing funcione correctamente.

Descargamos los siguientes certificados.

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/78268c5e-4810-418d-85dd-00a7320b8d14)

Nos moveremos a AWS IAM, donde tomaremos la siguiente ruta AWS IAM --> Roles --> Create Role --> Custom Trust Policy y copiamos el siguiente json.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "credentials.iot.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```
Vamos al paso 2 y otorgamos los permisos necesarios, donde crearemos nuestra nueva policy con los siguientes permisos.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "kinesisvideo:DescribeStream",
                "kinesisvideo:PutMedia",
                "kinesisvideo:TagStream",
                "kinesisvideo:GetDataEndpoint"
            ],
            "Resource": "arn:aws:kinesisvideo:*:*:stream/${credentials-iot:ThingName}/*"
        }
    ]
}
```



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
  






