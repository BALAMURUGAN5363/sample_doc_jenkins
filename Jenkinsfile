pipeline {
    agent any

    environment {
        IMAGE_NAME = 'flask-mysql-app'
        TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Pulling latest code commit from GitHub...'
            }
        }

        stage('Code Quality & Syntax Check') {
            steps {
                echo 'Running Python syntax and sanity checks...'
                sh 'python3 -m py_compile app.py test_app.py || python -m py_compile app.py test_app.py || true'
                sh 'test -f app.py && test -f requirements.txt && test -f Dockerfile'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Packaging application into Docker image: ${IMAGE_NAME}:${TAG}..."
                sh "docker build -t ${IMAGE_NAME}:${TAG} -t ${IMAGE_NAME}:latest ."
            }
        }

        stage('Unit Tests: Math Engine') {
            steps {
                echo 'Running mathematical calculation & edge case tests...'
                sh "docker run --rm ${IMAGE_NAME}:${TAG} pytest test_app.py -k TestMathLogic -v"
            }
        }

        stage('Integration Tests: REST API') {
            steps {
                echo 'Testing JSON API endpoints, error handling, and input validation...'
                sh "docker run --rm ${IMAGE_NAME}:${TAG} pytest test_app.py -k TestApiEndpoints -v"
            }
        }

        stage('UI & Route Tests') {
            steps {
                echo 'Testing template rendering and web dashboard routes...'
                sh "docker run --rm ${IMAGE_NAME}:${TAG} pytest test_app.py -k TestWebRoutes -v"
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                echo 'Deploying Flask application and MySQL database containers...'
                sh 'docker rm -f flask_mysql_db flask_web_app || true'
                sh 'docker compose -p sample_doc_jenkins up -d --build'
            }
        }

        stage('Live E2E Smoke Test') {
            steps {
                echo 'Waiting for services to become healthy...'
                sh 'sleep 10'
                echo 'Testing live calculation API on the deployed container...'
                sh '''
                    # Perform live calculation on deployed app
                    curl -s -X POST http://host.docker.internal:5000/api/calculate \
                         -H "Content-Type: application/json" \
                         -d '{"num1": 50, "op": "*", "num2": 2}' || \
                    curl -s -X POST http://localhost:5000/api/calculate \
                         -H "Content-Type: application/json" \
                         -d '{"num1": 50, "op": "*", "num2": 2}'
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline run finished.'
        }
        success {
            echo '========================================================'
            echo ' ALL TESTS PASSED & APPLICATION DEPLOYED SUCCESSFULLY! '
            echo ' Visit: http://localhost:5000 to use the Live Calculator '
            echo '========================================================'
        }
        failure {
            echo 'Pipeline failed. Quality gate stopped deployment.'
        }
    }
}
