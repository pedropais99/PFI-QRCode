# PFI-QRCode

En el siguiente documento, se explica el uso y se muestran las funciones utilizadas para la lectura de Codigos QR para el proyecto final de ingenieria (PFI) por parte del equipo 29 conformado por Santiago Salvioli y Pedro Pais.

# ¿Que se necesita para utilizar las funciones que se encuentran en el repositorio?

En primer lugar es condicion necesaria y suficiente para el uso de las funciones que se encuentran en el repositorio el uso de una cuenta de AWS, manejo de Python y Linux. 
Se necesitaran: 
- Habilitar la conexion a la camara del vehiculo autonomo sin el uso de credenciales.
- Crear maquina virtual con sistema operativo Raspberry Pi para la retransmision de video en tiempo real.
  - Descargar dentro de la maquina virtual las librerias que permitan la retrasmision de video en tiempo real.
- Registrar en AWS IoT la camara con la que se realizara el streaming de video a AWS Kinesis Video Stream.
- Crear un video stream en AWS Kinesis Video Stream.
- Crear un bucket S3 por funcion y otro para las librerias.
- Habilitacion para el guardado del video transmitio por AWS Kinesis Video Stream en formato de imagenes .jpg con el uso de del archivo "GuardarImagenes.json" del repositorio como se muestra en la imagen.
- Configurar evento disparador (trigger) en AWS Lambda con S3.
- Descargar librerias para la decodificacion de imagenes en AWS Lambda y configurarlas como layers de la funcion.
- Crear un SNS Topic y estar suscripto al mismo.

# Habilitar la conexion a la camara del vehiculo autonomo sin el uso de credenciales.

Para habilitar la conexion al vehiculo autonomo para la retransmision de video deberemos de conectarnos al mismo mediante ssh con las credenciales dadas por la institucion.
```
ssh usuario:password@[IPVehiculoAutonmo]
```
Dentro del mismo, corremos el siguiente comando para generar un backup del archivo que vamos a modificar
```
mkdir -p /home/deepracer/backup
cp /opt/aws/deepracer/lib/device_console/static/bundle.js /home/deepracer/backup/
cp /etc/nginx/sites-enabled/default /home/deepracer/backup/site-config
```
Generado el backup, ahora corremos este comando
```
sudo sed -i "s/isVideoPlaying\: true/isVideoPlaying\: false/" /opt/aws/deepracer/lib/device_console/static/bundle.js
sudo sed -i "s/auth_request \/auth;/#auth_request \/auth;/" /etc/nginx/sites-enabled/default
systemctl restart nginx
```

Se agredece a Matias Kreder por habernos ayudado a realizar la configuracion recien vista.

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
- Es imperativo que, como lo seteamos en el json, aws kinesis video stream retransmitira unicamente el video proveniente de una IoT Thing con su mismo nombre. Como llamamos a nuestra IoT Thing "pfi_camara1" nuestro kinesis video stream debera llamarse "pfi_camara1".

Seleccionamos nuestra policy recien creada para nuestro IAM role, le damos un nombre y lo creamos.

En el servicio de IoT Core ahora seleccionamos la opcion "Role aliases" dentro de la pestaña de "Security" y creamos un role alias para nuestro IAM role recien creado.

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/dfdb72e7-7909-4572-876e-b31e380f86be)

Nos moveremos a la pestaña de Policies, crearemos una IoT policy para nuestro role alias (copiamos la arn de nuestro role alias).

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/36062c31-d3c6-4be8-bc58-05eb96cce491)

Adjuntamos esta nueva policy a nuestra IoT Thing creada anteriormente.

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/5477fda8-e680-4ed8-a2d8-1193aa3e31e4)

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/3741844e-7246-479e-909b-a98bfe8ebbba)

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/3d965254-c536-45cf-a1e9-1238d4a42867)

# Crear un video stream en AWS Kinesis Video Stream (kvs).

Crearemos un video stream en kvs para la retransmision de video en tiempo real de la camara del vehiculo autonomo pasando por nuestra vm y IoT Thing (recordar que el nombre del video stream debe ser el mismo que el de la IoT Thing creada previamente).

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/42f0b8c1-41f0-46ca-8aaa-8c3fd2178ebb)

Para utilizar nuestro video stream, debemos de copiar los certificados descargados en pasos anteriores dentro de nuestra vm en el directorio /build creado como se muestra en pantalla.

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/2ba3bebe-7a21-4f8e-9de9-d862df060ac8)

Hecho esto comenzamos a probar nuestro streaming de video con los siguientes comandos para setear las variables de entorno, parados en el directorio ```/amazon-kinesis-video-streams-producer-sdk-cpp/build```
 - Obtenemos la variable "IOT_GET_CREDENTIAL_ENDPOINT" usando el comando ```aws iot describe-endpoint --endpoint-type iot:CredentialProvider``` en AWS Cloudshell
```
export AWS_DEFAULT_REGION=us-east-1
export CERT_PATH=certs/certificate.pem.crt
export PRIVATE_KEY_PATH=certs/private.pem.key
export CA_CERT_PATH=certs/AmazonRootCA1.pem
export ROLE_ALIAS=CamaraIoTRoleAlias
export IOT_GET_CREDENTIAL_ENDPOINT=c1vj04g5aoy6qs.credentials.iot.us-east-1.amazonaws.com
```

Seteadas las variables de entorno corremos el siguiente comando para comenzar a transmitir.
```
./kvs_gstreamer_sample pfi_camara1 https://[ip del vehiculo autonomo]/route?topic=/camera_pkg/display_mjpeg&width=[valor a eleccion]$height=[valor a eleccion]
```

# Crear un bucket S3 por funcion y otro para las librerias.

Para guardar las fotografias tomadas por AWS KVS y las librerias utilizadas en las funciones lambda crearemos 3 buckets S3 (uno para guardar las librerias y otros 2 para el guardado de imagenes). 

Seguimos los siguientes pasos, hay que tener en cuenta que los buckets S3 y las funciones lambda deben de estar en la misma region (en nuestro caso es us-east-1).

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/66d12a30-b647-4ce6-965a-08edd795d244)

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/1376657f-b86f-4f81-b7e9-08815a2a9f4e)

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/6f4a7ec5-fd16-41c2-a51e-9bd8c1e51290)

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/64701656-dbfd-41e0-b812-7ee29cfd60be)

Dejamos los demas campos y creamos el bucket. Repetimos el proceso hasta crear la cantidad de buckets necesarios.

# Habilitacion para el guardado del video transmitio por AWS Kinesis Video Stream en formato de imagenes .jpg con el uso de del archivo "GuardarImagenes.json" del repositorio como se muestra en la imagen.
  
  ![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/1e5f3db5-3aa3-4f51-a021-2336221e6a1e)
  ![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/a63c06df-b83a-41cd-832a-6ad77698d23b)
  
  Se debera pegar en la consola el siguiente comando:
  ```
  aws kinesisvideo update-image-generation-configuration \
  --cli-input-json file://./GuardarImagenes.json \
  ```
  Comprobamos que el archivo se haya actualizado con el siguiente comando:
  ```
  aws kinesisvideo describe-image-generation-configuration --stream-name pfi_camara1
  ```
  ![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/5c49673e-1a15-428a-ae8c-a0a5b40dd40b)

# Configurar evento disparador (trigger) en AWS Lambda con S3
- Estando en nuestra funcion Lambda, nos dirigiremos a la opcion de "Add trigger".

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/3e74d2b7-df9a-4c37-a313-2496c842d958)

- Dentro de esta opcion, crearemos el trigger para que la funcion lambda corra siempre que un objeto sea creado dentro del bucket seleccionado.

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/64e75e59-9f3f-4716-8534-1cb6fbb58257)

- Una vez terminado, seleccionamos "Add" y ya queda nuestro trigger configurado para la correcta ejecucion de la funcion.

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/466677e4-8c68-42e0-ae6a-fae48cf233d9)

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

# Crear un SNS Topic y estar suscripto al mismo.

Para poder enviar las respuestas de los codigos QR a los usuarios, se estara utilizando el servicio AWS SNS. Mostramos los pasos para su configuracion.

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/10a17eab-f45a-44e9-aaf1-17ef6f09b848)

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/7850be02-c189-418a-9b75-87e70a5c3b68)

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/6090a106-ba45-478b-91b9-2fac859bd808)

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/f7aef784-5ecf-4463-a068-1575c6736f2e)

![image](https://github.com/pedropais99/PFI-QRCode/assets/89282156/f8201974-ce59-405d-811e-f208b2098b85)

Una vez confirmadada la subscripcion a nuestro topico, pasaremos a recibir las lecturas de los codigos QR como mensajes de SNS.





