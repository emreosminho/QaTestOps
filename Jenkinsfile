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
                    
                    echo "=== Running Tests in Docker ==="
                    docker run --name test-run-${BUILD_NUMBER} \
                        -e HEADLESS=true \
                        test-automation:${BUILD_NUMBER}
                    
                    echo "=== Copying Reports from Container ==="
                    docker cp test-run-${BUILD_NUMBER}:/app/reports/. ${WORKSPACE}/reports/
                    
                    echo "=== Cleaning Up Container ==="
                    docker rm test-run-${BUILD_NUMBER}
                    
                    echo "=== Verifying Report Files ==="
                    ls -lah ${WORKSPACE}/reports/
                    if [ -f "${WORKSPACE}/reports/report.html" ]; then
                        echo "✅ report.html found!"
                        echo "📊 Report size: $(du -h ${WORKSPACE}/reports/report.html | cut -f1)"
                    else
                        echo "❌ report.html NOT found!"
                        exit 1
                    fi
                '''
            }
        }
        
        stage('Generate Reports') {
            steps {
                script {
                    if (fileExists('reports/report.html')) {
                        publishHTML([
                            allowMissing: false,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: 'reports',
                            reportFiles: 'report.html',
                            reportName: 'Test Report'
                        ])
                        echo '✅ HTML Report published successfully!'
                    } else {
                        echo '⚠️ report.html not found, skipping HTML publish'
                    }
                }
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
