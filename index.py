#!/usr/bin/python3
import boto3
import os
import json
import pymysql
import logging
from botocore.exceptions import ClientError

# Configuracion del registro
logging.basicConfig(level=logging.INFO)

def get_secret(secret_name, region_name):
    """
    Funcion para obtener el secreto de AWS Secrets Manager.
    """
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        secret_string = get_secret_value_response['SecretString']
    except ClientError as e:
        logging.error(f"Error al obtener el secreto: {str(e)}")
        raise e

    return secret_string

def application(environ, start_response):
    # HTML headers
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)

    try:
        # Obtener variables de entorno
        secret_name = os.environ['DB_SECRET_ARN']
        region_name = os.environ['REGION_NAME']
        db_host = os.environ['DB_HOST']
        db_name = os.environ['DB_NAME']

        logging.info("Obteniendo el secreto de AWS Secrets Manager")
        secret_string = get_secret(secret_name, region_name)
        logging.info("Secreto obtenido correctamente")

        secret_dict = json.loads(secret_string)

        db_user = secret_dict['username']
        db_password = secret_dict['password']

        logging.info("Conectándose a la base de datos")
        connection = pymysql.connect(host=db_host,
                                     user=db_user,
                                     password=db_password,
                                     database=db_name,
                                     cursorclass=pymysql.cursors.DictCursor)

        place_id, temperatura, wind_speed, timestamp = execute_database_query(connection)

        logging.info("Renderizando plantilla con temperatura")
        output = render_html_output(temperatura, place_id, wind_speed, timestamp)
        
    except ClientError as e:
        logging.error(f"Error al obtener el secreto: {str(e)}")
        output = f"<html><body><h1>Error al obtener el secreto: {str(e)}</h1></body></html>"
    except pymysql.MySQLError as e:
        logging.error(f"Error en la base de datos: {str(e)}")
        output = f"<html><body><h1>Error en la base de datos: {str(e)}</h1></body></html>"
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
        output = f"<html><body><h1>Error inesperado: {str(e)}</h1></body></html>"

    return [output.encode('utf-8')]

def execute_database_query(connection):
    """
    Función para ejecutar una consulta en la base de datos.
    """
    with connection.cursor() as cursor:
        logging.info("Ejecutando consulta")
        query = "SELECT temperature, place_id, wind_speed, timestamp FROM datos_clima ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            place_id = result['place_id']
            temperatura = result['temperature']
            wind_speed = result['wind_speed']
            timestamp = result['timestamp']
        else:
            place_id = "N/A"
            temperatura = "N/A"
            wind_speed = "N/A"
            timestamp = "N/A"

    return place_id, temperatura, wind_speed, timestamp

def render_html_output(temperatura, place_id, wind_speed, timestamp):
    """
    Función para renderizar el resultado en HTML.
    """
    output = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reporte del Clima - Track0</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f0f8ff;
                color: #333;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .container {{
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                text-align: center;
            }}
            h1 {{
                font-size: 24px;
                margin-bottom: 10px;
            }}
            p {{
                font-size: 18px;
                margin: 5px 0;
            }}
            .highlight {{
                color: #007BFF;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Última temperatura obtenida: <span class="highlight">{temperatura}°C</span></h1>
            <p>Lugar: <span class="highlight">{place_id}</span></p>
            <p>Viento: <span class="highlight">{wind_speed} Km/h</span></p>
            <p>Última actualización: <span class="highlight">{timestamp}</span></p>
        </div>
    </body>
    </html>
    """
    return output

