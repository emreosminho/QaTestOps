pipeline {
    agent any
    
    options {
        timestamps()
        timeout(time: 1, unit: 'HOURS')
    }
    
    environment {
        HEADLESS = 'true'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Code checkout completed'
                sh '''
                    echo "=== Workspace Files ==="
                    ls -la
                    echo "=== Dockerfile Check ==="
                    if [ -f Dockerfile ]; then
                        echo "✅ Dockerfile exists"
                        head -5 Dockerfile
                    else
                        echo "❌ Dockerfile NOT found!"
                    fi
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "=== Building Docker Image ==="
                    docker build -t test-automation:${BUILD_NUMBER} -f Dockerfile .
                '''
            }
        }
        
        stage('Run Tests in Docker') {
            steps {
                sh '''
                    echo "=== Preparing Reports Directory ==="
                    mkdir -p ${WORKSPACE}/reports
                    chmod 777 ${WORKSPACE}/reports
                    
                    echo "=== Running Tests ==="
                    docker run --rm \
                        -v ${WORKSPACE}/reports:/app/reports \
                        -e HEADLESS=true \
                        test-automation:${BUILD_NUMBER}
                '''
            }
        }
        
        stage('Generate Reports') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'report.html',
                    reportName: 'Test Report'
                ])
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution completed'
            sh 'docker rmi test-automation:${BUILD_NUMBER} || true'
        }
        success {
            echo '✅ Tests passed successfully!'
        }
        failure {
            echo '❌ Tests failed!'
        }
    }
}
