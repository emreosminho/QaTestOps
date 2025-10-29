# Jenkinsfile Dokümantasyonu

## 📋 Genel Bakış

Bu dokümantasyon, test otomasyon projesinin CI/CD pipeline'ını tanımlayan `Jenkinsfile`'ı detaylı olarak açıklar. Bu dosya Jenkins'te **Declarative Pipeline** syntax'ı kullanılarak yazılmıştır.

---

## 🎯 Pipeline'ın Amacı

Bu Jenkinsfile:
1. ✅ Kodu Git'ten otomatik çeker
2. ✅ Python sanal ortamı kurar
3. ✅ Test dependencies'i yükler
4. ✅ Selenium testlerini çalıştırır
5. ✅ HTML test raporları oluşturur
6. ✅ Pipeline sonuçlarını bildirir

---

## 📦 Tam Jenkinsfile İçeriği

```groovy
pipeline {
    agent any
    
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
```

---

## 🔍 Satır Satır Açıklama

### 1. Pipeline Tanımı

```groovy
pipeline {
```

**Açıklama:**
- Jenkins Declarative Pipeline'ın başlangıcı
- Tüm pipeline konfigürasyonu bu blok içinde
- `{ }` arasında tüm tanımlar yer alır

**Alternatifler:**
- **Scripted Pipeline:** Daha esnek ama karmaşık
- **Declarative Pipeline:** Daha yapısal ve okunabilir (önerilen)

---

### 2. Agent Tanımı

```groovy
    agent any
```

**Açıklama:**
- Pipeline'ın hangi Jenkins node/agent'ta çalışacağını belirtir
- `any`: Herhangi bir mevcut agent'ta çalışabilir
- Jenkins master veya herhangi bir slave node kullanılabilir

**Alternatifler:**

```groovy
# Belirli bir label'a sahip agent'ta çalışsın
agent { label 'windows' }

# Docker container içinde çalışsın
agent {
    docker {
        image 'python:3.11'
        args '-v /var/run/docker.sock:/var/run/docker.sock'
    }
}

# Hiçbir agent kullanma (her stage kendi agent'ını belirtir)
agent none
```

**Best Practice:**
- Windows testleri için: `agent { label 'windows' }`
- Docker kullanımı için: `agent { docker { ... } }`

---

### 3. Environment Variables

```groovy
    environment {
        PYTHON_VERSION = '3.11'
        VIRTUAL_ENV = 'venv'
    }
```

**Açıklama:**
- Pipeline boyunca kullanılacak ortam değişkenleri
- Tüm stage'lerde erişilebilir
- `${VIRTUAL_ENV}` veya `%VIRTUAL_ENV%` ile kullanılır

**Kullanım Yerleri:**
- `PYTHON_VERSION`: Dokümantasyon amaçlı
- `VIRTUAL_ENV`: Sanal ortam klasör adı

**Genişletilmiş Örnek:**

```groovy
environment {
    PYTHON_VERSION = '3.11'
    VIRTUAL_ENV = 'venv'
    HEADLESS = 'true'
    BASE_URL = 'https://www.saucedemo.com/'
    REPORT_DIR = 'reports'
    BUILD_TIMESTAMP = "${new Date().format('yyyyMMdd-HHmmss')}"
}
```

**Sensitive Data (Credentials):**

```groovy
environment {
    // Jenkins credentials store'dan çek
    API_KEY = credentials('api-key-id')
    DB_PASSWORD = credentials('db-password')
}
```

---

### 4. Stages Bloğu

```groovy
    stages {
```

**Açıklama:**
- Pipeline'daki tüm stage'lerin tanımlandığı ana blok
- Her stage sırayla çalışır (paralel yapılmadıysa)
- Bir stage başarısız olursa pipeline durur

---

## 📊 Stage'ler Detaylı Açıklama

### Stage 1: Checkout

```groovy
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Code checkout completed'
            }
        }
```

**Açıklama:**
- **Amaç:** Kod deposundan kaynak kodu çeker
- `checkout scm`: Jenkins'in yapılandırılan SCM'den (Git) kodu çeker
- `scm`: Source Code Management (Git, SVN, vb.)
- `echo`: Console'a mesaj yazdırır

**SCM Nedir?**
- Jenkins job'ında yapılandırdığınız Git repository
- Branch, credentials otomatik kullanılır

**Manuel Git Checkout:**

```groovy
stage('Checkout') {
    steps {
        git branch: 'main',
            url: 'https://github.com/username/TestAutomationPipline.git',
            credentialsId: 'github-credentials'
        echo 'Code checkout completed'
    }
}
```

**Birden Fazla Repository:**

```groovy
stage('Checkout') {
    steps {
        // Ana proje
        checkout scm
        
        // Test data repository
        dir('test-data') {
            git url: 'https://github.com/username/test-data.git'
        }
        
        echo 'All repositories checked out'
    }
}
```

**Neden Bu Stage Önemli?**
- ✅ En güncel kodu çeker
- ✅ Branch değişikliklerini yakalar
- ✅ Commit history'si korunur

---

### Stage 2: Setup Environment

```groovy
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
```

**Açıklama:**
- **Amaç:** Python sanal ortamı kurar ve dependencies yükler
- `bat`: Windows batch komutları çalıştırır
- `'''`: Multi-line string (Groovy syntax)

**Komutların Detayı:**

#### 1. Sanal Ortam Oluşturma
```batch
python -m venv %VIRTUAL_ENV%
```
- `python -m venv`: Python'ın venv modülünü çalıştır
- `%VIRTUAL_ENV%`: `venv` klasörü oluşturur
- **Neden?** Sistem Python'unu kirletmemek için

#### 2. Sanal Ortamı Aktive Etme
```batch
call %VIRTUAL_ENV%\\Scripts\\activate.bat
```
- Windows'ta sanal ortamı aktive eder
- `\\`: Escape edilmiş backslash (Groovy string içinde)
- `call`: Batch script'i çalıştırır ve context'i korur

#### 3. Pip Güncelleme
```batch
python -m pip install --upgrade pip
```
- pip'i en son versiyona günceller
- **Neden?** Eski pip'te bazı paketler hata verebilir

#### 4. Dependencies Yükleme
```batch
pip install -r requirements.txt
```
- Projenin gereksinimlerini yükler
- Selenium, pytest, vb.

**Linux/Mac için:**

```groovy
stage('Setup Environment') {
    steps {
        sh '''
            python3 -m venv ${VIRTUAL_ENV}
            . ${VIRTUAL_ENV}/bin/activate
            pip install --upgrade pip
            pip install -r requirements.txt
        '''
    }
}
```

**Docker Agent ile:**

```groovy
agent {
    docker {
        image 'python:3.11'
    }
}

stage('Setup Environment') {
    steps {
        sh '''
            pip install --upgrade pip
            pip install -r requirements.txt
        '''
    }
}
```

**Cache Kullanımı (Hızlandırma):**

```groovy
stage('Setup Environment') {
    steps {
        // Pip cache'i kullan
        bat '''
            python -m venv %VIRTUAL_ENV%
            call %VIRTUAL_ENV%\\Scripts\\activate.bat
            pip install --upgrade pip
            pip install -r requirements.txt --cache-dir .pip-cache
        '''
    }
}
```

**Hata Durumunda Retry:**

```groovy
stage('Setup Environment') {
    steps {
        retry(3) {
            bat '''
                python -m venv %VIRTUAL_ENV%
                call %VIRTUAL_ENV%\\Scripts\\activate.bat
                python -m pip install --upgrade pip
                pip install -r requirements.txt
            '''
        }
    }
}
```

---

### Stage 3: Run Tests

```groovy
        stage('Run Tests') {
            steps {
                bat '''
                    call %VIRTUAL_ENV%\\Scripts\\activate.bat
                    pytest tests/ --html=reports/report.html --self-contained-html -v
                '''
            }
        }
```

**Açıklama:**
- **Amaç:** Selenium testlerini çalıştırır
- Sanal ortamı tekrar aktive eder
- pytest ile tüm testleri çalıştırır

**Pytest Parametreleri:**
- `tests/`: Test klasörü
- `--html=reports/report.html`: HTML rapor oluştur
- `--self-contained-html`: Tek dosyada rapor (CSS/JS embedded)
- `-v`: Verbose mode (detaylı çıktı)

**Gelişmiş Test Çalıştırma:**

```groovy
stage('Run Tests') {
    steps {
        bat '''
            call %VIRTUAL_ENV%\\Scripts\\activate.bat
            set HEADLESS=true
            pytest tests/ ^
                --html=reports/report.html ^
                --self-contained-html ^
                -v ^
                --tb=short ^
                --maxfail=5 ^
                --reruns=2 ^
                --reruns-delay=1
        '''
    }
}
```

**Parametre Açıklamaları:**
- `--tb=short`: Kısa traceback
- `--maxfail=5`: 5 test başarısız olunca dur
- `--reruns=2`: Başarısız testleri 2 kez tekrar dene
- `--reruns-delay=1`: Tekrar denemeler arası 1 saniye bekle

**Paralel Test Çalıştırma:**

```groovy
stage('Run Tests') {
    steps {
        bat '''
            call %VIRTUAL_ENV%\\Scripts\\activate.bat
            pytest tests/ -n 4 --html=reports/report.html --self-contained-html -v
        '''
    }
}
```
- `-n 4`: 4 paralel worker ile çalıştır
- **Gereksinim:** `pytest-xdist` paketi

**Marker ile Çalıştırma:**

```groovy
stage('Run Tests') {
    steps {
        bat '''
            call %VIRTUAL_ENV%\\Scripts\\activate.bat
            pytest tests/ -m login --html=reports/report.html --self-contained-html -v
        '''
    }
}
```
- `-m login`: Sadece `@pytest.mark.login` işaretli testler

**Test Başarısız Olsa Bile Devam Et:**

```groovy
stage('Run Tests') {
    steps {
        script {
            try {
                bat '''
                    call %VIRTUAL_ENV%\\Scripts\\activate.bat
                    pytest tests/ --html=reports/report.html --self-contained-html -v
                '''
            } catch (Exception e) {
                echo "Tests failed but continuing..."
                currentBuild.result = 'UNSTABLE'
            }
        }
    }
}
```

---

### Stage 4: Generate Reports

```groovy
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
```

**Açıklama:**
- **Amaç:** HTML test raporlarını Jenkins'e yayınlar
- HTML Publisher Plugin gerektirir
- Jenkins UI'da rapor linkini gösterir

**Parametrelerin Açıklaması:**

#### `allowMissing: false`
- Rapor dosyası bulunamazsa hata ver
- `true`: Dosya yoksa geç (hata verme)

#### `alwaysLinkToLastBuild: true`
- Her zaman son build'in raporuna link ver
- Dashboard'da hızlı erişim için

#### `keepAll: true`
- Tüm build'lerin raporlarını sakla
- `false`: Sadece son raporu sakla

#### `reportDir: 'reports'`
- Rapor dosyalarının bulunduğu klasör
- Workspace içinde relatif yol

#### `reportFiles: 'report.html'`
- Yayınlanacak dosya adı
- Birden fazla dosya: `'report.html, coverage.html'`

#### `reportName: 'Test Report'`
- Jenkins UI'da görünecek isim
- Build sayfasında link olarak gösterilir

**Birden Fazla Rapor:**

```groovy
stage('Generate Reports') {
    steps {
        // HTML Test Report
        publishHTML([
            allowMissing: false,
            alwaysLinkToLastBuild: true,
            keepAll: true,
            reportDir: 'reports',
            reportFiles: 'report.html',
            reportName: 'Test Report'
        ])
        
        // Coverage Report
        publishHTML([
            allowMissing: true,
            alwaysLinkToLastBuild: true,
            keepAll: true,
            reportDir: 'htmlcov',
            reportFiles: 'index.html',
            reportName: 'Coverage Report'
        ])
    }
}
```

**Allure Report (Alternatif):**

```groovy
stage('Generate Reports') {
    steps {
        allure([
            includeProperties: false,
            jdk: '',
            results: [[path: 'allure-results']]
        ])
    }
}
```

**JUnit XML Report:**

```groovy
stage('Generate Reports') {
    steps {
        bat '''
            call %VIRTUAL_ENV%\\Scripts\\activate.bat
            pytest tests/ --junitxml=reports/junit.xml -v
        '''
        
        junit 'reports/junit.xml'
    }
}
```

---

## 🔄 Post Actions

```groovy
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
```

**Açıklama:**
- Pipeline tamamlandıktan sonra çalışan bloklar
- Pipeline sonucuna göre farklı action'lar

---

### Post: Always

```groovy
        always {
            echo 'Pipeline execution completed'
            cleanWs()
        }
```

**Açıklama:**
- **Her zaman çalışır** (başarılı/başarısız fark etmez)
- `cleanWs()`: Workspace'i temizler

**Neden Workspace Temizlenir?**
- ✅ Disk alanı tasarrufu
- ✅ Her build temiz başlar
- ✅ Eski dosyalar karışmaz

**Alternatif Temizlik:**

```groovy
always {
    echo 'Pipeline execution completed'
    
    // Sadece belirli dosyaları temizle
    bat 'rmdir /S /Q venv'
    bat 'rmdir /S /Q __pycache__'
    
    // Veya seçici temizlik
    cleanWs(
        deleteDirs: true,
        patterns: [
            [pattern: 'venv/**', type: 'INCLUDE'],
            [pattern: 'reports/**', type: 'EXCLUDE']
        ]
    )
}
```

**Arşivleme:**

```groovy
always {
    // Raporları arşivle
    archiveArtifacts artifacts: 'reports/*.html', allowEmptyArchive: true
    
    // Logları arşivle
    archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
    
    echo 'Pipeline execution completed'
    cleanWs()
}
```

---

### Post: Success

```groovy
        success {
            echo '✅ Tests passed successfully!'
        }
```

**Açıklama:**
- **Sadece pipeline başarılı olursa çalışır**
- Tüm testler geçti ve hata yok

**Gelişmiş Success Actions:**

```groovy
success {
    echo '✅ Tests passed successfully!'
    
    // Slack bildirimi
    slackSend(
        color: 'good',
        message: "✅ Tests Passed: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
    )
    
    // Email bildirimi
    emailext(
        subject: "✅ Tests Passed: ${env.JOB_NAME}",
        body: "Build ${env.BUILD_NUMBER} successfully completed.",
        to: 'team@example.com'
    )
    
    // Deployment trigger
    build job: 'Deploy-to-Staging', wait: false
}
```

---

### Post: Failure

```groovy
        failure {
            echo '❌ Tests failed!'
        }
```

**Açıklama:**
- **Sadece pipeline başarısız olursa çalışır**
- Test hataları veya pipeline hatası

**Gelişmiş Failure Actions:**

```groovy
failure {
    echo '❌ Tests failed!'
    
    // Slack bildirimi (kırmızı)
    slackSend(
        color: 'danger',
        message: "❌ Tests Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}\nCheck: ${env.BUILD_URL}"
    )
    
    // Email ile rapor gönder
    emailext(
        subject: "❌ Tests Failed: ${env.JOB_NAME}",
        body: """
            Build ${env.BUILD_NUMBER} failed.
            
            Check console output: ${env.BUILD_URL}console
            Test report: ${env.BUILD_URL}Test_Report/
        """,
        to: 'team@example.com',
        attachLog: true
    )
    
    // Screenshot'ları arşivle
    archiveArtifacts artifacts: 'screenshots/*.png', allowEmptyArchive: true
}
```

---

### Diğer Post Conditions

```groovy
post {
    always {
        echo 'Always runs'
    }
    
    success {
        echo 'Only on success'
    }
    
    failure {
        echo 'Only on failure'
    }
    
    unstable {
        echo 'Tests passed but marked as unstable'
    }
    
    changed {
        echo 'Pipeline result changed from last run'
    }
    
    fixed {
        echo 'Pipeline was broken, now fixed'
    }
    
    regression {
        echo 'Pipeline was successful, now failed'
    }
    
    aborted {
        echo 'Pipeline was manually aborted'
    }
    
    unsuccessful {
        echo 'Pipeline failed or unstable'
    }
}
```

---

## 🚀 Gelişmiş Pipeline Özellikleri

### 1. Parametreli Build

```groovy
pipeline {
    agent any
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'production'],
            description: 'Select environment'
        )
        
        choice(
            name: 'BROWSER',
            choices: ['chrome', 'firefox', 'edge'],
            description: 'Select browser'
        )
        
        string(
            name: 'TEST_TAG',
            defaultValue: 'login',
            description: 'Pytest marker tag'
        )
        
        booleanParam(
            name: 'HEADLESS',
            defaultValue: true,
            description: 'Run in headless mode'
        )
    }
    
    environment {
        PYTHON_VERSION = '3.11'
        VIRTUAL_ENV = 'venv'
    }
    
    stages {
        stage('Run Tests') {
            steps {
                bat """
                    call %VIRTUAL_ENV%\\Scripts\\activate.bat
                    set HEADLESS=${params.HEADLESS}
                    set BROWSER=${params.BROWSER}
                    pytest tests/ -m ${params.TEST_TAG} --html=reports/report.html -v
                """
            }
        }
    }
}
```

**Kullanım:**
- Jenkins UI'da "Build with Parameters" butonu görünür
- Kullanıcı parametreleri seçer
- Build başlar

---

### 2. Triggers (Otomatik Tetikleme)

```groovy
pipeline {
    agent any
    
    triggers {
        // Her gün saat 22:00'de çalış
        cron('0 22 * * *')
        
        // Her 5 dakikada Git'i kontrol et, değişiklik varsa çalış
        pollSCM('H/5 * * * *')
        
        // GitHub webhook ile tetikle
        githubPush()
        
        // Upstream job tamamlandığında çalış
        upstream(
            upstreamProjects: 'Build-Project',
            threshold: hudson.model.Result.SUCCESS
        )
    }
    
    // ... rest of pipeline
}
```

**Cron Syntax:**
```
# Dakika (0-59) Saat (0-23) Gün (1-31) Ay (1-12) Hafta Günü (0-7)
  0         22        *         *        *        # Her gün 22:00
  H         */4       *         *        1-5      # Haftaiçi her 4 saatte
  H         H         *         *        0        # Pazar günleri
```

---

### 3. Paralel Stage'ler

```groovy
pipeline {
    agent any
    
    stages {
        stage('Parallel Tests') {
            parallel {
                stage('Chrome Tests') {
                    steps {
                        bat '''
                            call venv\\Scripts\\activate.bat
                            set BROWSER=chrome
                            pytest tests/ --html=reports/chrome-report.html -v
                        '''
                    }
                }
                
                stage('Firefox Tests') {
                    steps {
                        bat '''
                            call venv\\Scripts\\activate.bat
                            set BROWSER=firefox
                            pytest tests/ --html=reports/firefox-report.html -v
                        '''
                    }
                }
                
                stage('Edge Tests') {
                    steps {
                        bat '''
                            call venv\\Scripts\\activate.bat
                            set BROWSER=edge
                            pytest tests/ --html=reports/edge-report.html -v
                        '''
                    }
                }
            }
        }
    }
}
```

---

### 4. Timeout ve Retry

```groovy
pipeline {
    agent any
    
    options {
        // Pipeline toplam 1 saat timeout
        timeout(time: 1, unit: 'HOURS')
        
        // Maksimum 3 concurrent build
        disableConcurrentBuilds()
        
        // Build'leri sakla
        buildDiscarder(logRotator(numToKeepStr: '10'))
        
        // Timestamp'li console output
        timestamps()
    }
    
    stages {
        stage('Setup Environment') {
            options {
                // Bu stage için 10 dakika timeout
                timeout(time: 10, unit: 'MINUTES')
                
                // Başarısız olursa 2 kez tekrar dene
                retry(2)
            }
            steps {
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate.bat
                    pip install -r requirements.txt
                '''
            }
        }
    }
}
```

---

### 5. Conditional Stages

```groovy
pipeline {
    agent any
    
    stages {
        stage('Run Tests') {
            steps {
                bat '''
                    call venv\\Scripts\\activate.bat
                    pytest tests/ --html=reports/report.html -v
                '''
            }
        }
        
        stage('Deploy to Staging') {
            when {
                // Sadece main branch'te ve testler başarılı olursa
                branch 'main'
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo 'Deploying to staging...'
            }
        }
        
        stage('Deploy to Production') {
            when {
                // Sadece tag build'lerinde
                tag "release-*"
            }
            steps {
                echo 'Deploying to production...'
            }
        }
    }
}
```

---

## 📊 Build Bilgilerine Erişim

```groovy
pipeline {
    agent any
    
    stages {
        stage('Print Build Info') {
            steps {
                script {
                    echo "Job Name: ${env.JOB_NAME}"
                    echo "Build Number: ${env.BUILD_NUMBER}"
                    echo "Build URL: ${env.BUILD_URL}"
                    echo "Workspace: ${env.WORKSPACE}"
                    echo "Branch: ${env.BRANCH_NAME}"
                    echo "Git Commit: ${env.GIT_COMMIT}"
                    echo "Git URL: ${env.GIT_URL}"
                    echo "Jenkins URL: ${env.JENKINS_URL}"
                    echo "Build User: ${env.BUILD_USER}"
                }
            }
        }
    }
}
```

---

## 📧 Bildirim Entegrasyonları

### Email Bildirimi

```groovy
post {
    success {
        emailext(
            subject: "✅ Tests Passed: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
            body: """
                <h2>Test Automation Build Success</h2>
                <p>Build: <a href="${env.BUILD_URL}">#${env.BUILD_NUMBER}</a></p>
                <p>Test Report: <a href="${env.BUILD_URL}Test_Report/">View Report</a></p>
                <p>Duration: ${currentBuild.durationString}</p>
            """,
            to: 'team@example.com',
            mimeType: 'text/html'
        )
    }
    
    failure {
        emailext(
            subject: "❌ Tests Failed: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
            body: """
                <h2>Test Automation Build Failed</h2>
                <p>Build: <a href="${env.BUILD_URL}">#${env.BUILD_NUMBER}</a></p>
                <p>Console: <a href="${env.BUILD_URL}console">View Console Output</a></p>
                <p>Please check the logs for details.</p>
            """,
            to: 'team@example.com',
            mimeType: 'text/html',
            attachLog: true
        )
    }
}
```

### Slack Bildirimi

```groovy
post {
    success {
        slackSend(
            channel: '#test-automation',
            color: 'good',
            message: "✅ Tests Passed: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n${env.BUILD_URL}"
        )
    }
    
    failure {
        slackSend(
            channel: '#test-automation',
            color: 'danger',
            message: "❌ Tests Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n${env.BUILD_URL}console"
        )
    }
}
```

### Microsoft Teams Bildirimi

```groovy
post {
    always {
        office365ConnectorSend(
            webhookUrl: 'YOUR_TEAMS_WEBHOOK_URL',
            message: "Build ${currentBuild.currentResult}",
            status: currentBuild.currentResult,
            color: currentBuild.currentResult == 'SUCCESS' ? '00FF00' : 'FF0000'
        )
    }
}
```

---

## 🐛 Debug ve Troubleshooting

### Console Output'a Debug Bilgisi Ekleme

```groovy
stage('Debug Info') {
    steps {
        bat 'echo Current directory: %CD%'
        bat 'dir'
        bat 'python --version'
        bat 'pip list'
        bat 'echo VIRTUAL_ENV: %VIRTUAL_ENV%'
    }
}
```

### Script Bloğu ile Kompleks Mantık

```groovy
stage('Conditional Logic') {
    steps {
        script {
            def testsPassed = true
            
            try {
                bat '''
                    call venv\\Scripts\\activate.bat
                    pytest tests/ -v
                '''
            } catch (Exception e) {
                testsPassed = false
                echo "Tests failed: ${e.message}"
            }
            
            if (testsPassed) {
                echo "All tests passed, proceeding to deployment"
            } else {
                echo "Tests failed, skipping deployment"
                currentBuild.result = 'FAILURE'
            }
        }
    }
}
```

---

## 📝 Best Practices

### 1. ✅ Stage İsimlendirme
- Açıklayıcı isimler kullanın
- Fiil ile başlayın: "Run Tests", "Deploy", "Build"

### 2. ✅ Error Handling
- `try-catch` blokları kullanın
- Anlamlı hata mesajları verin
- `retry()` ile geçici hataları yönetin

### 3. ✅ Workspace Yönetimi
- `cleanWs()` ile temizlik yapın
- Gereksiz dosyaları arşivlemeyin
- `.gitignore` benzeri dosyaları checkout etmeyin

### 4. ✅ Credentials Yönetimi
- Asla plaintext password kullanmayın
- Jenkins Credentials Store kullanın
- Environment variables ile çekin

### 5. ✅ Performance
- Paralel stage'ler kullanın
- Cache mekanizmaları kullanın
- Gereksiz stage'leri atlayın (conditional)

### 6. ✅ Monitoring
- Test raporlarını her zaman yayınlayın
- Kritik metrikler ölçün
- Bildirim sistemleri kurun

---

## 📚 Yararlı Komutlar ve Snippets

### Jenkins Pipeline Syntax Generator

Jenkins'te:
1. Job → Pipeline Syntax
2. Snippet Generator kullanarak kod üretin
3. Jenkinsfile'a kopyalayın

### Groovy Script Console

Jenkins'te test için:
1. Manage Jenkins → Script Console
2. Groovy kodunu test edin

### Pipeline Validation

```bash
# Jenkinsfile syntax'ını validate et
java -jar jenkins-cli.jar -s http://localhost:8080/ declarative-linter < Jenkinsfile
```

---

## 🔗 Kaynaklar

- Jenkins Pipeline Syntax: https://www.jenkins.io/doc/book/pipeline/syntax/
- Pipeline Steps Reference: https://www.jenkins.io/doc/pipeline/steps/
- Jenkinsfile Examples: https://github.com/jenkinsci/pipeline-examples
- Blue Ocean UI: https://www.jenkins.io/doc/book/blueocean/

---

## 📅 Son Güncelleme

Tarih: 29 Ekim 2025
Proje: TestAutomationPipline
Jenkins: 2.x+
Pipeline Type: Declarative Pipeline

