import json
import boto3
import os
import uuid
from decimal import Decimal

# Convierte floats a Decimals para DynamoDB
def convert_floats_to_decimals(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimals(i) for i in obj]
    return obj

# Clase auxiliar para convertir tipos Decimal de DynamoDB a JSON serializable
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    print("Evento recibido:", json.dumps(event))
    

    # Headers CORS para todas las respuestas
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
    }

    try:
        # Extraer información de la petición HTTP
        try:
            http_method = event.get('requestContext', {}).get('http', {}).get('method')
        except:
            http_method = None
        
        if not http_method:
            http_method = event.get('httpMethod')
            
        # Manejo de preflight CORS (OPTIONS)
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }

        path_parameters = event.get('pathParameters', {})
        
        if path_parameters is None:
            path_parameters = {}
            
        item_id = path_parameters.get('proxy') 
        
       
        body = {}
        if 'body' in event and event['body']:
            try:
                body = json.loads(event['body'])
                body = convert_floats_to_decimals(body)
            except json.JSONDecodeError:
                return {
                    'statusCode': 400, 
                    'headers': headers,
                    'body': 'JSON inválido en el cuerpo'
                }

        # si viene como "items/123", nos quedamos con "123". Si viene "items", es vacío.
        real_id = None
        if item_id:
            parts = item_id.split('/')
            if len(parts) > 0 and parts[-1] != 'items':
                 real_id = parts[-1]
        
        # GET /items
        if http_method == 'GET' and not real_id:
            response = table.scan()
            items = response.get('Items', [])
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(items, cls=DecimalEncoder)
            }
            
        # GET /items/{id}
        elif http_method == 'GET' and real_id:
            key = {'itemId': real_id}
            response = table.get_item(Key=key)
            item = response.get('Item')
            
            if not item:
                return {
                    'statusCode': 404, 
                    'headers': headers,
                    'body': json.dumps({'error': 'Ítem no encontrado'})
                }

            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(item, cls=DecimalEncoder)
            }
            
        elif http_method == 'POST':
            # Generate a UUID if the user hasn't provided one
            if 'itemId' not in body:
                body['itemId'] = str(uuid.uuid4())
            
            table.put_item(Item=body)
            return {
                'statusCode': 201, 
                'headers': headers,
                'body': json.dumps({'message': 'Ítem creado', 'item': body}, cls=DecimalEncoder)
            }
            
        # PUT /items/{id}
        elif http_method == 'PUT':
            # Si no hay ID en la URL, error
            if not real_id:
                 return {
                    'statusCode': 400, 
                    'headers': headers,
                    'body': json.dumps({'error': 'Falta ID en la URL para actualizar'})
                }
            
            # Asegurar que el ID del body coincida o asignarlo
            body['itemId'] = real_id
            
            table.put_item(Item=body)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'Ítem actualizado', 'item': body}, cls=DecimalEncoder)
            }
            
        # DELETE /items/{id}
        elif http_method == 'DELETE':
            if not real_id:
                 return {
                    'statusCode': 400, 
                    'headers': headers,
                    'body': json.dumps({'error': 'Falta ID en la URL para borrar'})
                }
                 
            key = {'itemId': real_id}
            table.delete_item(Key=key)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'Ítem eliminado'})
            }
            
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': f'Método no soportado: {http_method}'
            }

    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': str(e),
                'debug_info': {
                    'real_id': str(real_id) if 'real_id' in locals() else 'Not Defined',
                    'item_id': str(item_id) if 'item_id' in locals() else 'Not Defined',
                    'http_method': str(http_method) if 'http_method' in locals() else 'Not Defined'
                }
            })
        }
