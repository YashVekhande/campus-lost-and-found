import json
import boto3
import urllib.parse

# We explicitly tell AWS exactly where everything is
REGION = 'ap-south-1'
rekognition = boto3.client('rekognition', region_name=REGION)
s3_client = boto3.client('s3', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table('Items')

def lambda_handler(event, context):
    print("Received S3 event!")
    
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(record['s3']['object']['key'])
            print(f"Processing Bucket: {bucket}, Key: {key}")
            
            try:
                # Attempt 1: Tell Rekognition to look at the S3 Bucket
                response = rekognition.detect_labels(
                    Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                    MaxLabels=4,
                    MinConfidence=95
                )
            except Exception as rek_error:
                print(f"Attempt 1 failed: {rek_error}. Switching to direct memory download...")
                
                # Attempt 2: Bypassing Rekognition's S3 reader completely
                s3_response = s3_client.get_object(Bucket=bucket, Key=key)
                image_bytes = s3_response['Body'].read()
                
                response = rekognition.detect_labels(
                    Image={'Bytes': image_bytes},
                    MaxLabels=4,
                    MinConfidence=95
                )
            
            # Extract the tags
            tags = [label['Name'] for label in response['Labels']]
            print(f"AI successfully detected tags: {tags}")
            
            # Save to database
            item_id = key.split('.')[0] 
            
            table.update_item(
                Key={'itemId': item_id},
                UpdateExpression="SET tags = :t",
                ExpressionAttributeValues={':t': tags}
            )
            
        return {'statusCode': 200, 'body': 'Image tagged successfully!'}
        
    except Exception as e:
        print(f"Fatal Error: {e}")
        return {'statusCode': 500, 'body': str(e)}