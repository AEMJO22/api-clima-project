import os
import json
import boto3
import pymysql
import requests
from botocore.exceptions import ClientError
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)


def get_secret(secret_name, region_name):
    # Crear un cliente de Secrets Manager
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    return get_secret_value_response['SecretString']


def consumir_api():
    try:
        secret_name = os.environ['DB_SECRET_ARN']
        region_name = os.environ['REGION_NAME']
        db_host = os.environ['DB_HOST']
        db_name = os.environ['DB_NAME']
        api_key = os.environ['API_KEY']

        # Obtener el secreto de AWS Secrets Manager
        secret_string = get_secret(secret_name, region_name)
        secret_dict = json.loads(secret_string)

        # Obtener credenciales de la base de datos
        db_user = secret_dict['username']
        db_password = secret_dict['password']

        # Conectar a la base de datos MySQL
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )

        with connection.cursor() as cursor:
            # Crear una tabla para almacenar los datos del clima si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS datos_clima (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    place_id VARCHAR(255),
                    temperature FLOAT,
                    wind_speed FLOAT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Crear una tabla para almacenar los correos electrónicos si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Emails (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL
                )
            """)

            # Obtener datos del clima desde la API
            url = f"https://www.meteosource.com/api/v1/free/point?place_id=ushuaia&sections=current%2Chourly&timezone=UTC&language=en&units=metric&key={api_key}"
            response = requests.get(url)
            response.raise_for_status()  # Levantar error si la solicitud falla
            clima_datos = response.json()

            # Insertar los datos del clima en la tabla
            cursor.execute("""
                INSERT INTO datos_clima (place_id, temperature, wind_speed, timestamp)
                VALUES (%s, %s, %s, %s)
            """, (
                clima_datos.get('place_id', ''),
                clima_datos['current']['temperature'],
                clima_datos['current']['wind']['speed'],
                # Utiliza la hora actual en UTC con conocimiento de zona horaria
                datetime.now(timezone.utc)
            ))

            # Insertar correos electrónicos en la tabla
            cursor.execute("""
                INSERT INTO Emails (email) VALUES
                ('alexisjose25@gmail.com')
            """)

            # Confirmar la transacción
            connection.commit()

        # Cerrar la conexión
        connection.close()

        return {
            'statusCode': 200,
            'body': 'Datos del clima almacenados exitosamente en la base de datos.'
        }
    except ClientError as e:
        logging.error(f"Error al obtener el secreto: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error al obtener el secreto: {str(e)}"
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al consumir la API: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error al consumir la API: {str(e)}"
        }
    except pymysql.MySQLError as e:
        logging.error(f"Error en la base de datos: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error en la base de datos: {str(e)}"
        }
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error inesperado: {str(e)}"
        }


def main():
    logging.info("El script ha comenzado.")
    resultado = consumir_api()
    logging.info(f"Resultado: {resultado}")
    logging.info("El script ha terminado.")


if __name__ == "__main__":
    main()
