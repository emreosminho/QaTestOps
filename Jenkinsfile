pipeline {
    agent {
        label 'master'
    }
    
    options {
        timestamps()
        timeout(time: 1, unit: 'HOURS')
    }
    
    environment {
        PYTHON_VERSION = '3.11'
        VIRTUAL_ENV = 'venv'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Code checkout completed'
            }
        }
        
        stage('Setup Environment') {
            steps {
                bat '''
                    python -m venv %VIRTUAL_ENV%
                    call %VIRTUAL_ENV%\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                bat '''
                    call %VIRTUAL_ENV%\\Scripts\\activate.bat
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
            cleanWs()
        }
        success {
            echo '✅ Tests passed successfully!'
        }
        failure {
            echo '❌ Tests failed!'
        }
    }
}