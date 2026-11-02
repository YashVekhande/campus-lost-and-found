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
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Campus Lost & Found Image..."
                    appImage = docker.build("campus-lost-and-found:${env.BUILD_ID}")
                }
            }
        }
        stage('Install Frontend Dependencies') {
            steps {
                script {
                    appImage.inside {
                        sh 'npm ci'
                    }
                }
            }
        }
        stage('Test Backend Lambdas') {
            steps {
                script {
                    appImage.inside {
                        // Assuming you add pytest to your requirements in the future
                        echo "Running Python unit tests..."
                        sh 'python3 -m unittest discover -s backend'
                    }
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}