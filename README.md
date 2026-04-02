#  Campus Lost & Found (Serverless AI Platform)

A cloud-native web application designed to help university students recover lost items using AI image recognition. Built completely serverless on AWS.

##  Features
* **AI Image Tagging:** Uploaded photos are automatically analyzed by AWS Rekognition to generate search tags (e.g., "Electronics", "Keys").
* **Direct-to-S3 Uploads:** The React frontend securely uploads high-res images directly to Amazon S3, bypassing backend bottlenecks.
* **Serverless Architecture:** API Gateway routes traffic to independent Python Lambda functions, ensuring the app scales automatically and costs $0 when not in use.
* **Verification Dashboard:** Users can log in to a private dashboard to view claims on their items and securely resolve/delete them from the database.

##  Tech Stack
* **Frontend:** React, Vite, CSS (Dark Theme), Axios
* **Backend Compute:** AWS Lambda (Python 3.10)
* **Database:** Amazon DynamoDB (NoSQL)
* **Storage:** Amazon S3
* **AI / ML:** Amazon Rekognition
* **API Routing:** Amazon API Gateway

##  Cloud Architecture
1. Frontend uploads image to **S3**.
2. S3 triggers `processImage` **Lambda**.
3. Lambda sends image to **Rekognition**, receives tags, and updates **DynamoDB**.
4. Frontend posts text data via **API Gateway** to `postItem` **Lambda**, saving to **DynamoDB**.
