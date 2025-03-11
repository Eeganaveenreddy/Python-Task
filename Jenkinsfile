pipeline {
    agent any
    environment {
        DOCKER_IMAGE = "my-dockerhub-user/fastapi-app"
    }
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/myrepo/fastapi-k8s.git'
            }
        }
        stage('Build & Test') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pytest tests/'
            }
        }
        stage('Docker Build & Push') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE:latest .'
                sh 'echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin'
                sh 'docker push $DOCKER_IMAGE:latest'
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                sh 'kubectl apply -f k8s/deployment.yaml'
                sh 'kubectl apply -f k8s/service.yaml'
                sh 'kubectl rollout restart deployment/fastapi-app'
            }
        }
    }
    post {
        success {
            echo '✅ Deployment Successful!'
        }
        failure {
            echo '❌ Deployment Failed!'
        }
    }
}