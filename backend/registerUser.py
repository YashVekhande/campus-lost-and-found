import json
import boto3
import os
import hashlib
import base64
from boto3.dynamodb.conditions import Attr

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

def lambda_handler(event, context):
    try:
        # 1. Parse the incoming request
        body_str = event.get('body', '{}')
        if not body_str:
            body_str = '{}'
        body = json.loads(body_str)
        
        email = body.get('email')
        password = body.get('password')
        username = body.get('username')

        # Require all three fields
        if not email or not password or not username:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Email, password, and username are required'})
            }

        # 2. Check if Email already exists (Primary Key lookup)
        if 'Item' in table.get_item(Key={'email': email}):
             return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'An account with this email already exists'})
            }

        # 3. Check if Username already exists (Table Scan)
        username_check = table.scan(
            FilterExpression=Attr('username').eq(username)
        )
        if len(username_check.get('Items', [])) > 0:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'This username is already taken'})
            }

        # 4. Generate Profile Pic and Hash Password
        safe_name = username.replace(' ', '+')
        profile_pic = f"https://ui-avatars.com/api/?name={safe_name}&background=random&color=fff"

        salt = os.urandom(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

        # 5. Save to DynamoDB
        table.put_item(Item={
            'email': email,
            'username': username,
            'profilePic': profile_pic,
            'password_hash': base64.b64encode(password_hash).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8')
        })

        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'User registered successfully'})
        }
        
    except Exception as e:
        print(f"Error in registerUser: {e}")
        # Returning the actual error string temporarily to help debug if it fails again
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }