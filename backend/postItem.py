import json
import boto3
import uuid
from datetime import datetime

# We declare the DynamoDB table only once, outside the main handler
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Items')

def lambda_handler(event, context):
    print("Received postItem event!")
    
    try:
        # 1. Read the raw data sent from the React frontend
        body = json.loads(event.get('body', '{}'))
        
        # 2. Extract the data. NOTICE WE ARE TAKING THE 'itemId' FROM THE FRONTEND.
        # This is the crucial fix on line 11!
        frontend_item_id = body.get('itemId')
        timestamp = datetime.utcnow().isoformat()
        
        # We build a single source of truth for the ID
        final_item_id = frontend_item_id
        
        # 3. Add a SAFETY NET (lesson from our previous debugs!)
        # If for some reason the frontend sends an empty ID, we have a fallback.
        if not final_item_id:
            print("WARNING: Frontend sent no itemId. Creating a backend-generated fallback ID.")
            final_item_id = str(uuid.uuid4()) # Fallback only
        
        # 4. Build the final, complete item object
        new_item = {
            'itemId': final_item_id, # Use the ONE and ONLY single source of truth ID
            'type': body.get('type', 'lost'),
            'description': body.get('description', ''),
            'tags': body.get('tags', []), # The processImage function will update this later
            'imageUrl': body.get('imageUrl', ''),
            'contactEmail': body.get('contactEmail', ''),
            'status': 'open',
            'postedAt': timestamp
        }
        
        # 5. Save it to DynamoDB. If a "shell" ghost item already exists, this overwrites it!
        table.put_item(Item=new_item)
        print(f"Successfully saved item with ID: {final_item_id}")
        
        return {
            'statusCode': 201,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'message': 'Item posted successfully', 'itemId': final_item_id})
        }
        
    except Exception as e:
        print(f"Fatal Error in postItem: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }