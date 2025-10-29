pipeline {
    agent {
        dockerfile {
            filename 'Dockerfile'
            additionalBuildArgs '--build-arg BUILDKIT_INLINE_CACHE=1'
            args '-v /tmp:/tmp'
            reuseNode true
        }
    }
    
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
            }
        }
        
        stage('Verify Environment') {
            steps {
                sh '''
                    echo "=== Environment Info ==="
                    python --version
                    google-chrome --version
                    pip list
                    echo "Working directory: $(pwd)"
                    ls -la
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    export HEADLESS=true
                    pytest tests/ --html=reports/report.html --self-contained-html -v
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
            archiveArtifacts artifacts: 'reports/*.html', allowEmptyArchive: true
        }
        success {
            echo '✅ Tests passed successfully!'
        }
        failure {
            echo '❌ Tests failed!'
        }
    }
}
