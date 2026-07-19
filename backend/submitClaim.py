import json
import boto3
import uuid
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
# FIX: Change this to target the 'Items' table so they are linked!
table = dynamodb.Table('Items')

def lambda_handler(event, context):
    try:
        # Handle CORS Preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                }
            }

        body = json.loads(event.get('body', '{}'))
        item_id = body.get('itemId')

        if not item_id:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'itemId is required'})
            }
        
        # Build the claim object
        new_claim = {
            'claimId': str(uuid.uuid4()),
            'claimerName': body.get('claimerName', 'Anonymous'),
            'claimerEmail': body.get('claimerEmail', ''),
            'message': body.get('message', ''),
            'submittedAt': datetime.utcnow().isoformat()
        }
        
        # FIX: Safely append the claim into the item's "claims" array in DynamoDB
        # if_not_exists creates the array if this is the very first claim on the item
        table.update_item(
            Key={'itemId': item_id},
            UpdateExpression="SET claims = list_append(if_not_exists(claims, :empty_list), :new_claim)",
            ExpressionAttributeValues={
                ':empty_list': [],
                ':new_claim': [new_claim]
            },
            ReturnValues="UPDATED_NEW"
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'message': 'Claim submitted successfully'})
        }
    except Exception as e:
        print(f"Error submitting claim: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Internal server error'})
        }