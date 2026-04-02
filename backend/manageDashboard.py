import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
items_table = dynamodb.Table('Items')
claims_table = dynamodb.Table('Claims')

def lambda_handler(event, context):
    method = event.get('httpMethod', '')

    try:
        if method == 'POST':
            # 1. FETCH DASHBOARD DATA
            body = json.loads(event.get('body', '{}'))
            email = body.get('email')
            
            if not email:
                return {'statusCode': 400, 'body': 'Email is required'}
            
            # Find all items posted by this email
            items_response = items_table.scan(FilterExpression=Attr('contactEmail').eq(email))
            user_items = items_response.get('Items', [])
            
            # Find all claims attached to those items
            for item in user_items:
                claims_response = claims_table.scan(FilterExpression=Attr('itemId').eq(item['itemId']))
                item['claims'] = claims_response.get('Items', [])
                
            return {
                'statusCode': 200,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps(user_items)
            }
            
        elif method == 'DELETE':
            # 2. RESOLVE & DELETE ITEM
            body = json.loads(event.get('body', '{}'))
            item_id = body.get('itemId')
            
            # Delete the original item from the home page
            items_table.delete_item(Key={'itemId': item_id})
            
            # Delete all claims associated with it
            claims_response = claims_table.scan(FilterExpression=Attr('itemId').eq(item_id))
            for claim in claims_response.get('Items', []):
                claims_table.delete_item(Key={'claimId': claim['claimId']})
                
            return {
                'statusCode': 200,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Item officially resolved and removed!'})
            }

    except Exception as e:
        print(f"Dashboard Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
