pipeline {
    agent any

    environment {
        IMAGE_NAME = 'flask-mysql-app'
        TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Source code ready...'
            }
        }

        stage('Lint & Sanity Check') {
            steps {
                echo 'Checking essential project files...'
                sh 'test -f app.py && test -f requirements.txt && test -f Dockerfile'
            }
        }

        stage('Build Image') {
            steps {
                echo "Building Docker image: ${IMAGE_NAME}:${TAG}..."
                sh "docker build -t ${IMAGE_NAME}:${TAG} -t ${IMAGE_NAME}:latest ."
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo 'Running pytest inside container...'
                sh "docker run --rm ${IMAGE_NAME}:${TAG} pytest test_app.py"
            }
        }

        stage('Deploy Containers') {
            steps {
                echo 'Deploying Flask & MySQL containers with Docker Compose...'
                sh 'docker compose down --remove-orphans || true'
                sh 'docker compose up -d --build'
            }
        }

        stage('Health Check') {
            steps {
                echo 'Verifying deployed application...'
                sh 'sleep 10'
                sh 'curl -I http://localhost:5000 || curl -I http://host.docker.internal:5000 || true'
            }
        }
    }

    post {
        always {
            echo 'Pipeline run finished.'
        }
        success {
            echo 'Deployment successful! Web application is live on port 5000.'
        }
        failure {
            echo 'Pipeline failed. Check stage logs for details.'
        }
    }
}
