# Dockerfile ve Docker Compose Dokümantasyonu

## 📋 Genel Bakış

Bu dokümantasyon, test otomasyon projesini Docker container'ında çalıştırmak için hazırlanmış `Dockerfile` ve `docker-compose.yml` dosyalarını detaylı olarak açıklar.

---

## 🎯 Neden Docker Kullanıyoruz?

- ✅ **Tutarlı Ortam**: Her yerde aynı şekilde çalışır (Dev, CI/CD, Production)
- ✅ **İzolasyon**: Sistem bağımlılıkları container içinde
- ✅ **Taşınabilirlik**: Herhangi bir Docker destekli sistemde çalışır
- ✅ **Headless Testing**: GUI olmadan testler çalışabilir
- ✅ **CI/CD Uyumlu**: Jenkins, GitHub Actions vb. ile kolay entegrasyon

---

## 📦 Dockerfile Açıklaması

### Tam Dockerfile İçeriği

```dockerfile
FROM python:3.11-slim

# Chrome kurulumu
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["pytest", "tests/", "--html=reports/report.html", "--self-contained-html", "-v"]
```

---

### Satır Satır Açıklama

#### 1. Base Image Seçimi
```dockerfile
FROM python:3.11-slim
```

**Açıklama:**
- `python:3.11-slim`: Resmi Python 3.11 slim image'ı
- **Slim nedir?** Minimal Python image'ı (daha küçük boyut)
- **Boyut:** ~120 MB (full Python ~900 MB)
- **İçerik:** Python + pip + temel sistem araçları

**Alternatifler:**
- `python:3.11` - Daha büyük, daha fazla araç içerir
- `python:3.11-alpine` - En küçük (~50 MB), ama uyumluluk sorunları olabilir

---

#### 2. Chrome Browser Kurulumu

```dockerfile
# Chrome kurulumu
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
```

**Açıklama:**
- `apt-get update`: Paket listesini günceller
- `wget`: Dosya indirme aracı (Chrome key için)
- `gnupg`: GPG key doğrulama için
- `unzip`: Sıkıştırılmış dosyaları açmak için

---

```dockerfile
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
```

**Açıklama:**
- Chrome'un resmi GPG key'ini indirir ve ekler
- `-q`: Quiet mode (sessiz)
- `-O -`: Output'u stdout'a yönlendir
- `apt-key add -`: Key'i apt'ye ekle

---

```dockerfile
    && echo "deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/google.list \
```

**Açıklama:**
- Chrome repository'sini apt sources'a ekler
- Bu sayede `apt-get install` ile Chrome kurulabilir

---

```dockerfile
    && apt-get update \
    && apt-get install -y google-chrome-stable \
```

**Açıklama:**
- Paket listesini yeniden günceller (yeni repo için)
- Chrome'un stable versiyonunu kurar

---

```dockerfile
    && rm -rf /var/lib/apt/lists/*
```

**Açıklama:**
- Gereksiz apt cache'lerini siler
- **Neden?** Image boyutunu küçültmek için
- ~20-30 MB tasarruf sağlar

---

#### 3. Çalışma Dizini

```dockerfile
WORKDIR /app
```

**Açıklama:**
- Container içinde `/app` dizinini oluşturur
- Sonraki tüm komutlar bu dizinde çalışır
- `cd /app` komutu gibi düşünün

---

#### 4. Python Dependencies Kurulumu

```dockerfile
COPY requirements.txt .
```

**Açıklama:**
- `requirements.txt` dosyasını host'tan container'a kopyalar
- `.` = `/app` dizinine (WORKDIR'e)

**Neden önce sadece requirements.txt?**
- Docker layer caching için
- requirements.txt değişmediğinde bu layer cache'den kullanılır
- Daha hızlı build

---

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

**Açıklama:**
- Python paketlerini yükler
- `--no-cache-dir`: pip cache'i saklamaz (image boyutu azalır)
- `-r requirements.txt`: Dosyadan paket listesini okur

**Yüklenen Paketler:**
- selenium
- webdriver-manager
- pytest
- pytest-html
- pytest-xdist

---

#### 5. Proje Dosyalarını Kopyalama

```dockerfile
COPY . .
```

**Açıklama:**
- Tüm proje dosyalarını container'a kopyalar
- İlk `.`: Host'taki mevcut dizin (proje kök dizini)
- İkinci `.`: Container'daki `/app` dizini

**Kopyalanan dosyalar:**
- `page_objects/`
- `tests/`
- `conftest.py`
- `pytest.ini`
- vb.

**Kopyalanmayan dosyalar:**
- `.gitignore` ile belirtilenler
- `.dockerignore` ile belirtilenler (varsa)

---

#### 6. Default Komut

```dockerfile
CMD ["pytest", "tests/", "--html=reports/report.html", "--self-contained-html", "-v"]
```

**Açıklama:**
- Container başlatıldığında çalışacak komut
- `pytest tests/`: tests klasöründeki tüm testleri çalıştır
- `--html=reports/report.html`: HTML rapor oluştur
- `--self-contained-html`: Tek dosyada rapor (CSS/JS embedded)
- `-v`: Verbose mode (detaylı çıktı)

**Not:** Bu komut override edilebilir:
```bash
docker run test-automation pytest tests/test_login_positive.py
```

---

## 🐳 Docker Compose Açıklaması

### Tam docker-compose.yml İçeriği

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

---

### Satır Satır Açıklama

#### 1. Version

```yaml
version: '3.8'
```

**Açıklama:**
- Docker Compose file format versiyonu
- 3.8: Modern özellikler desteklenir
- Compose V2 ile uyumlu

---

#### 2. Services Tanımı

```yaml
services:
  test-automation:
```

**Açıklama:**
- `services`: Container servislerinin tanımlandığı bölüm
- `test-automation`: Servis adı (istediğiniz gibi adlandırabilirsiniz)

---

#### 3. Build Configuration

```yaml
    build: .
```

**Açıklama:**
- `.`: Mevcut dizindeki `Dockerfile`'ı kullan
- Image'ı otomatik build et

**Alternatifler:**
```yaml
    build:
      context: .
      dockerfile: Dockerfile
```

---

#### 4. Volume Mapping

```yaml
    volumes:
      - ./reports:/app/reports
```

**Açıklama:**
- Host ve container arasında klasör paylaşımı
- `./reports`: Host'taki reports klasörü (Windows: `C:\Users\User\PycharmProjects\TestAutomationPipline\reports`)
- `/app/reports`: Container içindeki reports klasörü
- **Sonuç:** Container içinde oluşan raporlar host'ta da görünür

**Volume Tipleri:**
- `./path:/container/path` - Bind mount (host klasörü)
- `volume_name:/container/path` - Named volume (Docker yönetir)

---

#### 5. Environment Variables

```yaml
    environment:
      - HEADLESS=true
```

**Açıklama:**
- Container içinde environment variable tanımlar
- `HEADLESS=true`: Chrome headless modda çalışır
- `conftest.py` bu değişkeni okur ve browser'ı headless başlatır

**Ek environment variable eklemek:**
```yaml
    environment:
      - HEADLESS=true
      - BASE_URL=https://www.saucedemo.com/
      - TIMEOUT=30
```

---

## 🚀 Docker Image Build Etme

### 1. Manuel Build

```bash
# Basit build
docker build -t test-automation .

# Tag ile build
docker build -t test-automation:v1.0 .

# No cache ile build (temiz build)
docker build --no-cache -t test-automation .
```

**Komut Açıklaması:**
- `docker build`: Image build komutu
- `-t test-automation`: Image'a tag/isim ver
- `.`: Dockerfile'ın bulunduğu dizin

---

### 2. Docker Compose ile Build

```bash
# Build et
docker-compose build

# Build et ve çalıştır
docker-compose up --build
```

---

## ▶️ Container Çalıştırma

### 1. Docker Run ile

#### Basit Çalıştırma
```bash
docker run test-automation
```

**Sonuç:**
- Testler çalışır
- Raporlar container içinde kalır
- Container durduğunda silinir

---

#### Volume ile Çalıştırma
```bash
docker run -v ${PWD}/reports:/app/reports test-automation
```

**PowerShell'de:**
```powershell
docker run -v ${PWD}/reports:/app/reports test-automation
```

**CMD'de:**
```cmd
docker run -v %cd%\reports:/app/reports test-automation
```

**Sonuç:**
- Raporlar `./reports` klasöründe görünür

---

#### Environment Variable ile
```bash
docker run -e HEADLESS=false -v ${PWD}/reports:/app/reports test-automation
```

**Sonuç:**
- Browser headless değil, normal modda açılır (ama göremezsiniz container içinde)

---

#### Özel Komut ile
```bash
docker run test-automation pytest tests/test_login_positive.py -v
```

**Sonuç:**
- Sadece `test_login_positive.py` çalışır
- Default CMD override edildi

---

### 2. Docker Compose ile

#### Basit Çalıştırma
```bash
docker-compose up
```

**Sonuç:**
- Image varsa kullanır, yoksa build eder
- Container başlatır ve testleri çalıştır
- Logları ekrana basar
- Ctrl+C ile durdurabilirsiniz

---

#### Detached Mode (Arka planda)
```bash
docker-compose up -d
```

**Sonuç:**
- Container arka planda çalışır
- Terminal'i bloklamaz

**Logları görmek:**
```bash
docker-compose logs -f
```

---

#### Build ve Çalıştır
```bash
docker-compose up --build
```

**Sonuç:**
- Her zaman yeniden build eder
- Kod değişikliklerinde kullanın

---

## 📊 Raporları Görüntüleme

### 1. Volume ile (Önerilen)

```bash
docker-compose up
```

**Sonuç:**
- Raporlar `./reports/report.html` dosyasında
- Windows Explorer'dan açabilirsiniz
- Tarayıcıda görüntüleyin

---

### 2. Container'dan Kopyalama

```bash
# Container'ı çalıştır
docker run --name test-run test-automation

# Raporları kopyala
docker cp test-run:/app/reports ./reports

# Container'ı sil
docker rm test-run
```

---

## 🛠️ Dockerfile Optimizasyonları

### .dockerignore Dosyası Oluşturma

Proje kök dizininde `.dockerignore` dosyası oluşturun:

```
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
env/

# Test outputs
reports/
*.html

# Git
.git/
.gitignore

# IDE
.idea/
.vscode/

# Docs
*.md
```

**Avantajı:**
- Build daha hızlı
- Image boyutu küçülür
- Gereksiz dosyalar kopyalanmaz

---

### Multi-stage Build (İleri Seviye)

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Chrome kurulumu
RUN apt-get update && apt-get install -y \
    wget gnupg unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python packages'i builder'dan kopyala
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

CMD ["pytest", "tests/", "--html=reports/report.html", "--self-contained-html", "-v"]
```

**Avantajı:**
- Daha küçük final image
- Build cache daha iyi kullanılır

---

## 🔍 Debugging ve Troubleshooting

### Container İçine Girme

```bash
# Container'ı bash ile başlat
docker run -it test-automation bash

# Çalışan container'a gir
docker exec -it <container_id> bash
```

**İçeride yapabilecekleriniz:**
```bash
# Chrome versiyonunu kontrol et
google-chrome --version

# Python versiyonu
python --version

# Yüklü paketler
pip list

# Test çalıştır (manuel)
pytest tests/ -v

# Dizin yapısını gör
ls -la
```

---

### Build Hatalarını Debug Etme

```bash
# Detaylı build çıktısı
docker build --progress=plain --no-cache -t test-automation .

# Belirli bir layer'a kadar build et
docker build --target builder -t test-automation .
```

---

### Log Kontrolü

```bash
# Container loglarını gör
docker logs <container_name>

# Canlı log takibi
docker logs -f <container_name>

# Son 100 satır
docker logs --tail 100 <container_name>
```

---

### Resource Kullanımı

```bash
# Container stats
docker stats <container_name>

# Image boyutu
docker images test-automation

# Detaylı image bilgisi
docker image inspect test-automation
```

---

## 🎯 Farklı Kullanım Senaryoları

### Senaryo 1: Lokal Development

```bash
# Raporları görmek için volume ile
docker-compose up

# Veya
docker run -v ${PWD}/reports:/app/reports test-automation
```

---

### Senaryo 2: CI/CD Pipeline'da

**Jenkinsfile'da:**
```groovy
stage('Run Tests in Docker') {
    steps {
        sh 'docker-compose up --abort-on-container-exit'
    }
}
```

**GitHub Actions'da:**
```yaml
- name: Run tests in Docker
  run: docker-compose up --abort-on-container-exit
```

---

### Senaryo 3: Paralel Test Çalıştırma

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  test-login:
    build: .
    command: pytest tests/test_login_positive.py -v
    volumes:
      - ./reports:/app/reports
    environment:
      - HEADLESS=true

  test-other:
    build: .
    command: pytest tests/test_other.py -v
    volumes:
      - ./reports:/app/reports
    environment:
      - HEADLESS=true
```

**Çalıştırma:**
```bash
docker-compose up
```

---

### Senaryo 4: Farklı Browser'lar

**Dockerfile.firefox:**
```dockerfile
FROM python:3.11-slim

# Firefox kurulumu
RUN apt-get update && apt-get install -y \
    firefox-esr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["pytest", "tests/", "-v"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  chrome-tests:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./reports:/app/reports

  firefox-tests:
    build:
      context: .
      dockerfile: Dockerfile.firefox
    volumes:
      - ./reports:/app/reports
```

---

## 📊 Best Practices

### 1. Image Boyutunu Küçük Tutun
- ✅ Slim base image kullanın
- ✅ Multi-stage build kullanın
- ✅ Cache'leri temizleyin
- ✅ .dockerignore kullanın

### 2. Layer Caching
- ✅ requirements.txt'i önce kopyalayın
- ✅ Sık değişmeyen dosyaları üstte tutun

### 3. Security
- ✅ Latest yerine spesifik version kullanın
- ✅ Root user kullanmayın (production'da)
- ✅ Secrets'i image'a gömmeyin

### 4. Testing
- ✅ Volume ile raporları host'a aktarın
- ✅ Headless mode kullanın
- ✅ Exit code'ları kontrol edin

---

## 📝 Yararlı Komutlar Özeti

```bash
# BUILD
docker build -t test-automation .
docker-compose build

# RUN
docker run test-automation
docker run -v ${PWD}/reports:/app/reports test-automation
docker-compose up
docker-compose up -d

# MANAGE
docker ps                           # Çalışan container'lar
docker ps -a                        # Tüm container'lar
docker images                       # Image'lar
docker logs <container>             # Loglar
docker exec -it <container> bash    # Container'a gir
docker stop <container>             # Durdur
docker rm <container>               # Container sil
docker rmi <image>                  # Image sil

# CLEANUP
docker system prune                 # Kullanılmayan her şeyi sil
docker container prune              # Durdurulmuş container'ları sil
docker image prune                  # Kullanılmayan image'ları sil
docker volume prune                 # Kullanılmayan volume'ları sil

# DOCKER COMPOSE
docker-compose up                   # Başlat
docker-compose up -d                # Arka planda başlat
docker-compose down                 # Durdur ve sil
docker-compose logs                 # Logları gör
docker-compose ps                   # Container'ları listele
docker-compose build --no-cache     # Cache'siz build
```

---

## 🔗 Kaynaklar

- Docker Official Docs: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- Python Docker Image: https://hub.docker.com/_/python
- Dockerfile Best Practices: https://docs.docker.com/develop/dev-best-practices/

---

## 📅 Son Güncelleme

Tarih: 29 Ekim 2025
Proje: TestAutomationPipline
Docker Version: 24.x+
Docker Compose Version: 2.x+

