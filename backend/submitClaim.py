import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Claims')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Build the claim object
        new_claim = {
            'claimId': str(uuid.uuid4()),
            'itemId': body.get('itemId', ''),
            'claimerName': body.get('claimerName', ''),
            'claimerEmail': body.get('claimerEmail', ''),
            'message': body.get('message', ''),
            'submittedAt': datetime.utcnow().isoformat()
        }
        
        # Save to the Claims table
        table.put_item(Item=new_claim)
        
        return {
            'statusCode': 201,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'message': 'Claim submitted successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }