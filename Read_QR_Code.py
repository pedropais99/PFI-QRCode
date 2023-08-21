import json, boto3, urllib, time
from pyzbar.pyzbar import decode
from urllib.parse import unquote_plus
from PIL import Image

print('cargando funcion')

s3 = boto3.client('s3')
sns = boto3.client('sns')

# ARN del SNS topic con el que enviaremos el mensaje con la respuesta del codigo QR
topic_arn = 'arn:aws:sns:us-east-1:733758592716:PFI-QR-Topic'

def lambda_handler(event, context):
    print("archivo recibido")
    print(event)
    # La funcion toma al bucket S3 y la key del objeto por el trigger
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    print("Imagen: " + key)

    try:
        # La funcion lambda descargara la imagen del S3 y la guardara en su propia carpeta temp
        temp = '/tmp/{}'.format(str(time.time()))
        s3.download_file(bucket, key, temp)
        # Extraemos el codigo de la imagen
        qr = decode(Image.open(temp))
        # Creamos una lista en caso de que se detecten multiples codigos QR
        data = []
        i = 0
        # print(qr)
        if (len(qr) > 0):
            for code in qr:
                print("Se econtro el link: " + (code.data).decode('UTF-8'))
                data.append((code.data).decode('UTF-8'))
                while i < len(data):
                    message = 'El codigo QR es ' + data[i]
                    subject = 'Respuesta lectura de codigo QR'
                    # Envía el mensaje al tema de SNS
                    response = sns.publish (TopicArn = topic_arn, Message = message, Subject = subject )
                    print(response)
                    i = i + 1
                    print(data)
                
            return {
                'statusCode': 200,
                'body': json.dumps(data)
            }
        else:
            print("No QR detected")
            return {
                'statusCode': 200,
                'body': "No hay codigo QR"
            }
                

    except Exception as e:
        print(e)
        raise e