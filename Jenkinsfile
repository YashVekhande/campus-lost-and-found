pipeline {
    agent any
    environment {
        AWS_CREDENTIALS = credentials('aws-credentials')
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Frontend Image') {
            steps {
                echo "Building Campus Lost & Found Image..."
                bat "docker build -t campus-lost-and-found:${env.BUILD_ID} ."
            }
        }
        stage('Test Backend Lambdas') {
            steps {
                echo "Running Python unit tests in an isolated container..."
                bat "docker run --rm -v \"%CD%\\backend\":/app -w /app python:3.9-slim python -m unittest discover"
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}