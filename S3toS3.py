import boto3

rekognition_client = boto3.client('rekognition')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Obtener detalles del evento S3
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # Detectar labels en la imagen
    response = rekognition_client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': 'pfi-qr-code-bucket-1',
                'Name': object_key
            }
        }
    )

    # Verificar si el label deseado está presente en los resultados
    desired_label = 'QR Code'
    for label in response['Labels']:
        if label['Name'] == desired_label:
            # Copiar la imagen a otro bucket o ubicación en S3
            new_object_key = object_key
            s3_client.copy_object(
                CopySource={'Bucket': bucket_name, 'Key': object_key},
                Bucket="pfi-qr-code-bucket-3",
                Key=new_object_key
            )
            break