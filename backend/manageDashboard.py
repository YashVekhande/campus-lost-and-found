import json
import boto3
import os
import hmac
import hashlib
import base64
import time
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Items') # <-- Correct table name

JWT_SECRET = os.environ.get('JWT_SECRET', 'campus-super-secret-key')

def base64url_decode(data):
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def verify_jwt(token):
    try:
        header_b64, payload_b64, signature_b64 = token.split('.')
        
        signature_message = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = hmac.new(JWT_SECRET.encode('utf-8'), signature_message, hashlib.sha256).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).rstrip(b'=').decode('utf-8')
        
        if not hmac.compare_digest(signature_b64, expected_sig_b64):
            return None
            
        payload = json.loads(base64url_decode(payload_b64).decode('utf-8'))
        if payload['exp'] < int(time.time()):
            return None
            
        return payload['email']
    except Exception as e:
        print(f"JWT Verification failed: {e}")
        return None

def lambda_handler(event, context):
    try:
        # Handle the preflight CORS check for browsers
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                    'Access-Control-Allow-Methods': 'OPTIONS, POST, GET, DELETE'
                }
            }

        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return {
                'statusCode': 401, 
                'headers': {'Access-Control-Allow-Origin': '*'}, 
                'body': json.dumps({'error': 'Missing or invalid Authorization header'})
            }
            
        token = auth_header.split(' ')[1]
        email = verify_jwt(token)
        
        if not email:
            return {
                'statusCode': 401, 
                'headers': {'Access-Control-Allow-Origin': '*'}, 
                'body': json.dumps({'error': 'Invalid or expired token'})
            }

        # Normalize the email to lowercase just in case there are case sensitivity issues
        email = email.lower()
        print(f"Fetching items for authenticated user: {email}")

        # If it's a DELETE request, handle resolving the item
        if event.get('httpMethod') == 'DELETE':
            body = json.loads(event.get('body', '{}'))
            item_id = body.get('itemId')
            if item_id:
                table.delete_item(Key={'itemId': item_id})
                return {
                    'statusCode': 200,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'message': 'Item deleted'})
                }

        # Fetch the items associated with this user
        response = table.scan(
            FilterExpression=Attr('contactEmail').eq(email)
        )
        
        items = response.get('Items', [])
        print(f"Found {len(items)} items for {email}")
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(items)
        }
        
    except Exception as e:
        print(f"Dashboard Error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Internal server error'})
        }