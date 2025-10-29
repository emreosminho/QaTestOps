# 🚀 CI/CD Pipeline Kurulum Dokümantasyonu

## 📋 İçindekiler
1. [Proje Genel Bakış](#proje-genel-bakış)
2. [Proje Yapısı](#proje-yapısı)
3. [Dosya Açıklamaları](#dosya-açıklamaları)
4. [Jenkins Kurulumu](#jenkins-kurulumu)
5. [Adım Adım Kurulum](#adım-adım-kurulum)
6. [Sorun Giderme](#sorun-giderme)
7. [Best Practices](#best-practices)

---

## 🎯 Proje Genel Bakış

Bu dokümantasyon, **Selenium + Pytest** test otomasyon projesini **Jenkins + Docker** kullanarak **CI/CD pipeline**'a entegre etme sürecini açıklar.

### Kullanılan Teknolojiler
- **Python 3.11**: Test framework language
- **Selenium WebDriver**: Browser automation
- **Pytest**: Test runner ve reporting
- **Docker**: Containerization
- **Jenkins**: CI/CD automation server
- **Google Chrome**: Headless browser

### Pipeline Akışı
```
Developer → Git Push → Jenkins → Build Docker Image → Run Tests → Generate Reports → Cleanup
```

---

## 📁 Proje Yapısı

```
TestAutomationPipeline/
├── .gitignore                      # Git ignore rules
├── Dockerfile                      # Test ortamı containerization
├── Jenkinsfile                     # CI/CD pipeline tanımı
├── conftest.py                     # Pytest fixtures ve configuration
├── docker-compose.yml              # Local test environment (opsiyonel)
├── pytest.ini                      # Pytest configuration
├── requirements.txt                # Python dependencies
├── page_objects/                   # Page Object Model classes
│   ├── base_page.py
│   └── login_page.py
├── tests/                          # Test files
│   └── test_login_positive.py
└── reports/                        # Test reports (auto-generated)
    ├── .gitkeep
    └── report.html (ignored)
```

---

## 📝 Dosya Açıklamaları

### 1. `Dockerfile` - Test Ortamı Containerization

#### **Amaç**
Python, Chrome ve tüm test bağımlılıklarını içeren izole bir test ortamı oluşturur.

#### **İçerik**
```dockerfile
FROM python:3.11-slim

# Chrome kurulumu (modern method)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    ca-certificates \
    && wget -q -O /tmp/google-chrome-key.pub https://dl-ssl.google.com/linux/linux_signing_key.pub \
    && gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg /tmp/google-chrome-key.pub \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* /tmp/google-chrome-key.pub

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["pytest", "tests/", "--html=reports/report.html", "--self-contained-html", "-v"]
```

#### **Açıklamalar**

**Base Image Seçimi:**
```dockerfile
FROM python:3.11-slim
```
- `python:3.11-slim`: Minimal Python image (Debian tabanlı)
- Hafif (slim) versiyonu kullanarak image boyutunu küçük tutuyoruz
- Production-ready Python 3.11 sürümü

**Chrome Kurulumu (Modern Method):**
```dockerfile
# GPG key indirme ve kurulum
wget -q -O /tmp/google-chrome-key.pub https://dl-ssl.google.com/linux/linux_signing_key.pub
gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg /tmp/google-chrome-key.pub
```
- **Neden `apt-key` değil?**: `apt-key` deprecated, modern `gpg --dearmor` kullanıyoruz
- **ca-certificates**: SSL sertifikaları için gerekli

**Dependency Installation:**
```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
- **Layer caching**: requirements.txt değişmezse cache kullanılır
- **--no-cache-dir**: pip cache'i silip image boyutunu küçültür

**CMD Komutu:**
```dockerfile
CMD ["pytest", "tests/", "--html=reports/report.html", "--self-contained-html", "-v"]
```
- `--html`: HTML rapor oluştur
- `--self-contained-html`: CSS/JS embedded (tek dosya)
- `-v`: Verbose output

---

### 2. `Jenkinsfile` - CI/CD Pipeline Tanımı

#### **Amaç**
Jenkins pipeline'ın tüm stage'lerini (checkout, build, test, report) tanımlar.

#### **İçerik**
```groovy
pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 1, unit: 'HOURS')
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
                        echo "❌ Dockerfile not found!"
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
            sh "docker rmi test-automation:${BUILD_NUMBER} || true"
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

#### **Stage Açıklamaları**

**Pipeline Başlangıç:**
```groovy
agent any
```
- Herhangi bir Jenkins agent'da çalıştırılabilir

**Options:**
```groovy
options {
    timestamps()                    // Log'larda timestamp göster
    timeout(time: 1, unit: 'HOURS') // 1 saatten uzun sürerse timeout
}
```

**Stage 1: Checkout**
```groovy
checkout scm
```
- Git repository'den kodu çeker
- `scm` (Source Control Management) otomatik olarak yapılandırılmış Git repo'yu kullanır

**Stage 2: Build Docker Image**
```bash
docker build -t test-automation:${BUILD_NUMBER} -f Dockerfile .
```
- **`-t test-automation:${BUILD_NUMBER}`**: Tag with build number (örn: test-automation:18)
- **`-f Dockerfile`**: Explicit Dockerfile path
- **`${BUILD_NUMBER}`**: Jenkins environment variable (her build için unique)

**Stage 3: Run Tests in Docker**

**Neden `docker cp` kullanıyoruz?**
```bash
# Volume mount yerine (İZİN SORUNU YAŞANDI):
# docker run --rm -v ${WORKSPACE}/reports:/app/reports ...

# Docker cp kullanıyoruz (ÇALIŞTI):
docker run --name test-run-${BUILD_NUMBER} ...
docker cp test-run-${BUILD_NUMBER}:/app/reports/. ${WORKSPACE}/reports/
docker rm test-run-${BUILD_NUMBER}
```
- **Sorun**: Docker container (root) ile Jenkins workspace (jenkins user) arasında permission uyumsuzluğu
- **Çözüm**: Container'ı çalıştır, dosyaları kopyala, container'ı sil
- **`--name`**: Container'a isim vererek sonra referans edebiliyoruz
- **`--rm` YOK**: Çünkü `docker cp` için container'ın durması yeterli (silinmemesi gerek)

**Stage 4: Generate Reports**
```groovy
publishHTML([
    allowMissing: false,           // Rapor yoksa fail et
    alwaysLinkToLastBuild: true,   // Son build'e link oluştur
    keepAll: true,                  // Tüm eski raporları sakla
    reportDir: 'reports',           // Rapor dizini
    reportFiles: 'report.html',     // Rapor dosyası
    reportName: 'Test Report'       // Jenkins UI'da görünecek isim
])
```

**Post Actions:**
```groovy
post {
    always {
        sh "docker rmi test-automation:${BUILD_NUMBER} || true"
    }
}
```
- **`|| true`**: Komut başarısız olsa bile pipeline devam etsin
- Docker image'ı silerek disk alanı temizliyoruz

---

### 3. `conftest.py` - Pytest Fixtures ve Configuration

#### **Amaç**
Selenium WebDriver'ı configure eder, headless mode'u yönetir, test başlangıç/bitiş işlemlerini yapar.

#### **İçerik**
```python
import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture()
def driver():
    print("Starting driver")
    
    # Chrome options
    chrome_options = Options()
    
    # CI/CD ortamında headless çalışsın
    headless = os.getenv('HEADLESS', 'false').lower() == 'true'
    if headless:
        print("🤖 Running in HEADLESS mode")
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
    else:
        print("🖥️ Running in NORMAL mode")
    
    # Docker için gerekli argümanlar
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--remote-debugging-port=9222')
    
    # Chrome binary path (Docker'da)
    chrome_options.binary_location = '/usr/bin/google-chrome'
    
    my_driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    yield my_driver
    
    print("Shutting down driver")
    my_driver.quit()
```

#### **Açıklamalar**

**Fixture Nedir?**
```python
@pytest.fixture()
def driver():
```
- Pytest'in test öncesi/sonrası çalışan fonksiyonları
- Her test fonksiyonu `driver` parametresini alabilir
- **`yield`**: Test çalışır, sonra `yield` sonrası cleanup yapılır

**Headless Mode Detection:**
```python
headless = os.getenv('HEADLESS', 'false').lower() == 'true'
```
- Environment variable'dan `HEADLESS` değerini okur
- CI/CD'de: `HEADLESS=true` (Jenkins'te set ediyoruz)
- Local'de: `HEADLESS=false` (browser görünür)

**Kritik Chrome Arguments:**

```python
chrome_options.add_argument('--headless=new')
```
- **`--headless=new`**: Yeni Chrome headless engine (daha stabil)
- Eski: `--headless` (deprecated)

```python
chrome_options.add_argument('--no-sandbox')
```
- **Docker'da ZORUNLU**: Sandbox mode'u devre dışı bırakır
- Root user ile çalışırken gerekli

```python
chrome_options.add_argument('--disable-dev-shm-usage')
```
- **Docker'da ZORUNLU**: `/dev/shm` (shared memory) kullanımını azaltır
- Docker container'larda default shm boyutu küçük (64MB)

```python
chrome_options.add_argument('--disable-gpu')
```
- GPU rendering'i kapat (headless'te gereksiz)

```python
chrome_options.add_argument('--remote-debugging-port=9222')
```
- Debug için remote debugging port'u aç
- Chrome DevTools'a bağlanabilirsiniz

```python
chrome_options.binary_location = '/usr/bin/google-chrome'
```
- Docker'da Chrome'un tam yolunu belirt
- ChromeDriver'ın Chrome'u bulması için

**WebDriver Manager:**
```python
service=Service(ChromeDriverManager().install())
```
- Otomatik olarak doğru ChromeDriver versiyonunu indirir
- Chrome versiyonu ile uyumlu driver kullanır

---

### 4. `docker-compose.yml` - Local Test Environment

#### **Amaç**
Geliştiricilerin local ortamda Docker ile testleri çalıştırabilmesi için.

#### **İçerik**
```yaml
version: '3.8'

services:
  test-automation:
    build: .
    volumes:
      - ./reports:/app/reports
    environment:
      - HEADLESS=true
```

#### **Açıklamalar**

```yaml
build: .
```
- Mevcut dizindeki `Dockerfile`'ı kullan

```yaml
volumes:
  - ./reports:/app/reports
```
- Local `reports/` klasörünü container'a mount et
- **Not**: Jenkins'te volume mount yerine `docker cp` kullandık (izin sorunu)

```yaml
environment:
  - HEADLESS=true
```
- Container içinde `HEADLESS` environment variable'ı set et

**Kullanım:**
```bash
# Testleri çalıştır
docker-compose up

# Arka planda çalıştır
docker-compose up -d

# Logları izle
docker-compose logs -f

# Temizle
docker-compose down
```

---

### 5. `requirements.txt` - Python Dependencies

#### **İçerik**
```txt
selenium==4.36.0
webdriver-manager==4.0.2
pytest==8.4.2
pytest-html==4.1.1
pytest-xdist==3.8.0
```

#### **Açıklamalar**

```txt
selenium==4.36.0
```
- Selenium WebDriver library
- Browser automation için

```txt
webdriver-manager==4.0.2
```
- Otomatik ChromeDriver download ve management
- Chrome versiyonu ile uyumlu driver indirir

```txt
pytest==8.4.2
```
- Test framework
- Test discovery, execution, reporting

```txt
pytest-html==4.1.1
```
- HTML test report generator
- Güzel, interaktif raporlar oluşturur

```txt
pytest-xdist==3.8.0
```
- Paralel test execution
- Testleri multiple CPU'larda çalıştır
- Kullanım: `pytest -n 4` (4 worker)

---

### 6. `pytest.ini` - Pytest Configuration

#### **İçerik**
```ini
[pytest]
markers =
    # Login Testleri
    positive_login: pozitif login testleri
    login: Tüm login testleri
```

#### **Açıklamalar**

**Custom Markers:**
```python
# Test dosyasında kullanım:
@pytest.mark.positive_login
def test_valid_login():
    pass

@pytest.mark.login
def test_invalid_login():
    pass
```

**Marker'larla test filtreleme:**
```bash
# Sadece positive_login marker'lı testleri çalıştır
pytest -m positive_login

# login marker'lı TÜM testleri çalıştır
pytest -m login

# Belirli marker'ları hariç tut
pytest -m "not slow"
```

---

### 7. `.gitignore` - Git Ignore Rules

#### **İçerik**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/

# Test Reports
reports/*.html
reports/*.xml
reports/assets/
allure-results/
allure-report/

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Selenium
*.log
chromedriver.exe
geckodriver.exe

# Environment
.env
.env.local

# Jenkins
.jenkins/
```

#### **Önemli Noktalar**

```gitignore
reports/*.html
reports/*.xml
```
- **`reports/` klasörünü ignore ETMİYORUZ**
- Sadece içindeki HTML/XML dosyalarını ignore ediyoruz
- `.gitkeep` dosyası ile klasörü Git'e ekliyoruz

**Neden `.gitkeep`?**
```bash
reports/
├── .gitkeep          # Git'e commit edilir
└── report.html       # Ignore edilir
```
- Boş klasörler Git'e eklenemez
- `.gitkeep` ile klasörün varlığını Git'e bildiriyoruz

---

## 🐳 Jenkins Kurulumu

### Docker ile Jenkins Kurulumu

#### **1. Jenkins Container'ı Başlat**

**PowerShell (Windows):**
```powershell
docker run -d `
  -p 8080:8080 `
  -p 50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  -v /var/run/docker.sock:/var/run/docker.sock `
  --name jenkins `
  jenkins/jenkins:lts
```

**Bash (Linux/Mac):**
```bash
docker run -d \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --name jenkins \
  jenkins/jenkins:lts
```

#### **Parametre Açıklamaları:**

```bash
-p 8080:8080
```
- Jenkins web UI port mapping
- Host:Container

```bash
-p 50000:50000
```
- Jenkins agent connection port
- Master-slave communication için

```bash
-v jenkins_home:/var/jenkins_home
```
- Jenkins data persistence
- Volume kullanarak data kaybını engelle

```bash
-v /var/run/docker.sock:/var/run/docker.sock
```
- **Docker-in-Docker**: Jenkins container'ından host'un Docker'ını kullan
- **KRİTİK**: Pipeline'da Docker komutları çalıştırmak için gerekli

```bash
--name jenkins
```
- Container'a isim ver
- Sonra `docker exec -it jenkins bash` ile bağlanabilirsiniz

#### **2. Jenkins Container'a Docker CLI Kur**

```bash
# Container'a gir
docker exec -u root -it jenkins bash

# Docker CLI kur
apt-get update
apt-get install -y docker.io

# Docker socket izinlerini ayarla
chmod 666 /var/run/docker.sock

# Çık
exit
```

#### **3. Initial Admin Password Al**

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Çıkan şifreyi kopyala ve tarayıcıda `http://localhost:8080` adresine git.

#### **4. Jenkins Setup**

1. **Unlock Jenkins**: Initial password'u yapıştır
2. **Install Suggested Plugins**: Tıkla ve bekle
3. **Create First Admin User**: Bilgilerini doldur
4. **Jenkins URL**: `http://localhost:8080` (varsayılan)

#### **5. Gerekli Pluginleri Kur**

**Manage Jenkins → Plugins → Available Plugins**

Ara ve kur:
- ✅ **HTML Publisher Plugin** (Test raporları için)
- ✅ **Docker Pipeline** (Dockerfile agent için)
- ✅ **Git Plugin** (Zaten kurulu olmalı)

---

## 🚀 Adım Adım Kurulum

### Yeni Bir Projede CI/CD Pipeline Kurulumu

#### **Adım 1: Proje Yapısını Oluştur**

```bash
mkdir MyTestProject
cd MyTestProject

# Klasör yapısını oluştur
mkdir -p page_objects tests reports

# Boş dosyalar oluştur
touch conftest.py pytest.ini requirements.txt .gitignore
touch Dockerfile Jenkinsfile docker-compose.yml
```

#### **Adım 2: Dosyaları Kopyala**

Bu dokümantasyondaki içerikleri ilgili dosyalara kopyala:
- ✅ `Dockerfile`
- ✅ `Jenkinsfile`
- ✅ `conftest.py`
- ✅ `docker-compose.yml`
- ✅ `requirements.txt`
- ✅ `pytest.ini`
- ✅ `.gitignore`

#### **Adım 3: `.gitkeep` Ekle**

```bash
echo "# This file ensures the reports directory is tracked by Git" > reports/.gitkeep
```

#### **Adım 4: Git Repository Oluştur**

```bash
git init
git add .
git commit -m "Initial commit: CI/CD pipeline setup"

# GitHub'a push et
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

#### **Adım 5: Jenkins Job Oluştur**

**Jenkins → New Item:**

1. **Enter an item name**: `MyTestProject`
2. **Pipeline** seç
3. **OK** tıkla

**Pipeline Configuration:**

**General:**
- ✅ **GitHub project**: Repo URL'ini yapıştır

**Build Triggers:**
- ✅ **GitHub hook trigger for GITScm polling** (Webhook için)
- ⬜ **Poll SCM** (Manuel için: `H/5 * * * *` - her 5 dakikada kontrol et)

**Pipeline:**
- **Definition**: `Pipeline script from SCM`
- **SCM**: `Git`
- **Repository URL**: `https://github.com/YOUR_USERNAME/YOUR_REPO.git`
- **Branch Specifier**: `*/main`
- **Script Path**: `Jenkinsfile`

**Save** tıkla!

#### **Adım 6: İlk Build'i Çalıştır**

1. **Build Now** tıkla
2. **Console Output** izle
3. **Test Report** linkini kontrol et

---

## 🔧 Sorun Giderme

### Sık Karşılaşılan Sorunlar ve Çözümleri

#### **1. `docker: not found` Hatası**

**Sorun:** Jenkins container'ında Docker CLI yok

**Çözüm:**
```bash
docker exec -u root -it jenkins bash
apt-get update && apt-get install -y docker.io
chmod 666 /var/run/docker.sock
exit
```

#### **2. `permission denied while trying to connect to the Docker daemon socket`**

**Sorun:** Docker socket izin hatası

**Çözüm:**
```bash
docker exec -u root -it jenkins bash
chmod 666 /var/run/docker.sock
exit
```

#### **3. `SessionNotCreatedException: Chrome instance exited`**

**Sorun:** Chrome argümanları eksik veya yanlış

**Çözüm:** `conftest.py` kontrolü:
```python
chrome_options.add_argument('--no-sandbox')           # ZORUNLU
chrome_options.add_argument('--disable-dev-shm-usage') # ZORUNLU
chrome_options.binary_location = '/usr/bin/google-chrome'
```

#### **4. `report.html` Oluşmuyor**

**Sorun:** Pytest HTML plugin eksik veya CMD komutu yanlış

**Çözüm:**
```bash
# requirements.txt kontrol et
pytest-html==4.1.1

# Dockerfile CMD kontrol et
CMD ["pytest", "tests/", "--html=reports/report.html", "--self-contained-html", "-v"]
```

#### **5. Volume Mount İzin Sorunu**

**Sorun:** Docker container'dan Jenkins workspace'e yazma izni yok

**Çözüm:** Volume mount yerine `docker cp` kullan:
```bash
docker run --name test-run-${BUILD_NUMBER} ...
docker cp test-run-${BUILD_NUMBER}:/app/reports/. ${WORKSPACE}/reports/
docker rm test-run-${BUILD_NUMBER}
```

#### **6. `apt-key: not found` Hatası**

**Sorun:** Dockerfile'da deprecated `apt-key` kullanılmış

**Çözüm:** Modern GPG method:
```dockerfile
wget -q -O /tmp/google-chrome-key.pub https://dl-ssl.google.com/linux/linux_signing_key.pub
gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg /tmp/google-chrome-key.pub
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] ..." > /etc/apt/sources.list.d/google-chrome.list
```

#### **7. Workspace Temizlik Sorunu**

**Sorun:** Önceki build'lerin dosyaları kalıyor

**Çözüm:**
```bash
# Jenkins'te "Wipe Out Workspace" kullan
# VEYA Jenkinsfile'a ekle:
post {
    always {
        cleanWs()  // Workspace'i temizle
    }
}
```

---

## 📚 Best Practices

### 1. **Docker Image Layer Caching**

**İyi:**
```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```

**Kötü:**
```dockerfile
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
```

**Neden?** Kod değiştiğinde sadece son layer rebuild olur, dependencies cache'ten gelir.

---

### 2. **Environment Variables Kullanımı**

**conftest.py:**
```python
headless = os.getenv('HEADLESS', 'false').lower() == 'true'
base_url = os.getenv('BASE_URL', 'https://default-url.com')
browser = os.getenv('BROWSER', 'chrome')
```

**Jenkinsfile:**
```groovy
environment {
    HEADLESS = 'true'
    BASE_URL = 'https://staging.example.com'
    BROWSER = 'chrome'
}
```

---

### 3. **Secrets Management**

**BAD:**
```python
# ❌ YAPMA!
username = "admin"
password = "secret123"
```

**GOOD:**
```python
# ✅ YAP!
username = os.getenv('TEST_USERNAME')
password = os.getenv('TEST_PASSWORD')
```

**Jenkins Credentials:**
```groovy
environment {
    CREDENTIALS = credentials('my-credentials-id')
}
```

---

### 4. **Paralel Test Execution**

**pytest.ini:**
```ini
[pytest]
addopts = -n auto --maxfail=3
```

**Veya Jenkinsfile:**
```bash
pytest tests/ -n 4 --html=reports/report.html
```

---

### 5. **Test Retry Mechanism**

**pytest-rerunfailures plugin:**
```bash
pip install pytest-rerunfailures
```

**Kullanım:**
```bash
pytest --reruns 2 --reruns-delay 5
```

---

### 6. **Build Notifications**

**Email notification:**
```groovy
post {
    failure {
        emailext(
            to: 'team@example.com',
            subject: "❌ Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: "Check console output at ${env.BUILD_URL}"
        )
    }
}
```

---

### 7. **Docker Image Tagging Strategy**

**Versiyonlu tagging:**
```bash
docker build -t test-automation:${BUILD_NUMBER} .
docker build -t test-automation:latest .
docker build -t test-automation:v1.0.0 .
```

---

### 8. **Webhook Setup (Otomatik Build)**

**GitHub → Settings → Webhooks:**

- **Payload URL**: `http://YOUR_JENKINS_URL/github-webhook/`
- **Content type**: `application/json`
- **Events**: `Just the push event`

**Jenkins Job:**
- ✅ **GitHub hook trigger for GITScm polling**

---

## 🎯 Özet Checklist

Yeni bir proje için CI/CD pipeline kurarken:

- [ ] Jenkins Docker container'ı çalışıyor
- [ ] Docker CLI Jenkins'te kurulu
- [ ] Docker socket bağlı (`/var/run/docker.sock`)
- [ ] HTML Publisher Plugin kurulu
- [ ] Docker Pipeline Plugin kurulu
- [ ] `Dockerfile` oluşturuldu
- [ ] `Jenkinsfile` oluşturuldu
- [ ] `conftest.py` oluşturuldu
- [ ] `requirements.txt` oluşturuldu
- [ ] `pytest.ini` oluşturuldu
- [ ] `.gitignore` oluşturuldu
- [ ] `reports/.gitkeep` eklendi
- [ ] Git repository oluşturuldu
- [ ] Jenkins job configure edildi
- [ ] İlk build başarılı
- [ ] HTML rapor görünüyor

---

## 📞 Destek

Bu dokümantasyonu takip ederek diğer projelerinizde de aynı CI/CD pipeline'ı kurabilirsiniz.

**Sorularınız için:**
- Pipeline'ın her stage'ini log'lardan takip edin
- Console Output'u dikkatlice okuyun
- Docker container'ların durumunu kontrol edin: `docker ps -a`

---

**Son Güncelleme:** 29 Ekim 2025
**Versiyon:** 1.0.0
**Hazırlayan:** TestAutomationPipeline Documentation Team

---

## 🚀 Hızlı Başlangıç (TL;DR)

```bash
# 1. Jenkins başlat
docker run -d -p 8080:8080 -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock --name jenkins jenkins/jenkins:lts

# 2. Docker CLI kur
docker exec -u root -it jenkins bash
apt-get update && apt-get install -y docker.io
chmod 666 /var/run/docker.sock
exit

# 3. Dosyaları oluştur
# (Dockerfile, Jenkinsfile, conftest.py, vb.)

# 4. Git'e push et
git init && git add . && git commit -m "Initial commit"
git push origin main

# 5. Jenkins'te job oluştur
# Pipeline script from SCM → Git → Jenkinsfile

# 6. Build Now!
```

**Tebrikler! CI/CD Pipeline'ınız hazır!** 🎊

