# Jenkins Docker Kurulum ve Kullanım Rehberi

## 📋 Genel Bakış

Bu dokümantasyon, Jenkins'i Docker container içinde nasıl çalıştıracağınızı adım adım açıklar. Bu yöntemle Windows masaüstünüze kurulum yapmadan Jenkins kullanabilirsiniz.

---

## 🎯 Avantajlar

- ✅ Windows sistemine kurulum gerektirmez
- ✅ İzole çalışır, sistemi kirletmez
- ✅ Kolay başlatma/durdurma
- ✅ İstediğiniz zaman tamamen silebilirsiniz
- ✅ Volume ile verileriniz kalıcı

---

## 📦 Ön Gereksinimler

### Docker Desktop Kurulumu

1. **Docker Desktop'ı indirin:**
   - https://www.docker.com/products/docker-desktop/
   - Windows 10/11 için

2. **Kurulum sonrası kontrol:**
   ```powershell
   docker --version
   ```
   
   Beklenen çıktı: `Docker version 24.x.x, build xxxxx`

3. **Docker Desktop'ı çalıştırın:**
   - Sistem tray'inde Docker simgesi yeşil olmalı

---

## 🚀 Jenkins Container Kurulumu

### Adım 1: PowerShell'i Yönetici Olarak Açın

- `Win + X` → **Windows PowerShell (Admin)**
- Veya: Windows Search → "PowerShell" → Sağ tık → **Run as Administrator**

### Adım 2: Jenkins Container'ını Başlatın

**Tek komutla başlatma:**

```powershell
docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home --name jenkins jenkins/jenkins:lts
```

**Komut açıklaması:**
- `-d` : Arka planda (detached mode) çalıştır
- `-p 8080:8080` : Jenkins web arayüzü portu
- `-p 50000:50000` : Jenkins agent bağlantı portu
- `-v jenkins_home:/var/jenkins_home` : Volume (veri kalıcılığı için)
- `--name jenkins` : Container adı
- `jenkins/jenkins:lts` : Jenkins LTS (Long Term Support) image

**Not:** İlk çalıştırmada Jenkins image'ı indirilecek (2-3 dakika sürebilir)

### Adım 3: Container'ın Çalıştığını Kontrol Edin

```powershell
docker ps
```

Çıktıda `jenkins` container'ı görünmeli:
```
CONTAINER ID   IMAGE                 STATUS         PORTS                                              NAMES
abc123def456   jenkins/jenkins:lts   Up 2 minutes   0.0.0.0:8080->8080/tcp, 0.0.0.0:50000->50000/tcp   jenkins
```

### Adım 4: Initial Admin Password'u Alın

```powershell
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Örnek çıktı: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

**Bu password'u kopyalayın!**

---

## 🌐 Jenkins Web Arayüzüne Erişim

### Adım 1: Tarayıcıda Açın

```
http://localhost:8080
```

### Adım 2: Unlock Jenkins

- Initial admin password'u yapıştırın
- **Continue** tıklayın

### Adım 3: Plugin Kurulumu

- **Install suggested plugins** seçin
- Plugin kurulumu otomatik başlayacak (5-10 dakika)

### Adım 4: Admin Kullanıcı Oluşturun

Aşağıdaki bilgileri doldurun:
- Username: `admin`
- Password: `güvenli_bir_şifre`
- Full name: `Admin`
- E-mail: `admin@example.com`

**Save and Continue** → **Save and Finish** → **Start using Jenkins**

---

## 🔧 Pipeline Job Oluşturma

### Adım 1: New Item

1. Jenkins Dashboard → **New Item**
2. Item name: `TestAutomationPipeline`
3. Tip: **Pipeline**
4. **OK**

### Adım 2: Pipeline Konfigürasyonu

**General:**
- Description: `Test Automation CI/CD Pipeline`

**Build Triggers (Opsiyonel):**
- ☑️ Poll SCM
- Schedule: `H/5 * * * *` (her 5 dakikada Git'i kontrol et)

**Pipeline:**
- Definition: **Pipeline script from SCM**
- SCM: **Git**
- Repository URL: `<your-git-repo-url>`
  - Örnek: `https://github.com/username/TestAutomationPipline.git`
- Branch: `*/main`
- Script Path: `Jenkinsfile`

**Save**

### Adım 3: İlk Build'i Çalıştırın

- **Build Now** tıklayın
- Sol tarafta build history'de #1 görünecek
- Build'e tıklayarak **Console Output** görebilirsiniz

---

## 📊 Test Raporlarını Görüntüleme

### HTML Publisher Plugin Kurulumu

1. **Manage Jenkins** → **Plugins**
2. **Available plugins** sekmesi
3. Arama: `HTML Publisher`
4. ☑️ **HTML Publisher Plugin** seçin
5. **Install** → **Restart Jenkins**

### Rapor Görüntüleme

Build tamamlandıktan sonra:
- Build sayfasında **Test Report** linki görünecek
- HTML raporunu görüntüleyebilirsiniz

---

## 🛠️ Jenkins Container Yönetimi

### Container Durumunu Kontrol Etme

```powershell
# Tüm container'ları listele
docker ps -a

# Sadece çalışan container'lar
docker ps

# Jenkins loglarını görüntüle
docker logs jenkins

# Canlı log takibi
docker logs -f jenkins
```

### Container'ı Durdurma ve Başlatma

```powershell
# Durdur
docker stop jenkins

# Başlat
docker start jenkins

# Yeniden başlat
docker restart jenkins
```

### Container'ın İçine Girme

```powershell
# Bash shell ile container'a gir
docker exec -it jenkins bash

# Çıkmak için
exit
```

### Jenkins Volume İçeriğini Görüntüleme

```powershell
# Volume bilgilerini göster
docker volume inspect jenkins_home

# Volume içeriğini listele (Linux container'dan)
docker exec jenkins ls -la /var/jenkins_home
```

---

## 🗑️ Temizlik İşlemleri

### Container'ı Tamamen Silme

```powershell
# Container'ı durdur ve sil
docker stop jenkins
docker rm jenkins
```

**Not:** Volume hala kalır, veriler kaybolmaz.

### Volume'u da Silme (Tüm Verileri Sil)

```powershell
# UYARI: Tüm Jenkins konfigürasyonları ve job'lar silinir!
docker volume rm jenkins_home
```

### Yeniden Temiz Kurulum

```powershell
# Her şeyi sil
docker stop jenkins
docker rm jenkins
docker volume rm jenkins_home

# Yeniden başlat
docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home --name jenkins jenkins/jenkins:lts
```

---

## 🔍 Sorun Giderme

### Port 8080 Zaten Kullanılıyor

**Hata:** `Bind for 0.0.0.0:8080 failed: port is already allocated`

**Çözüm:** Farklı port kullanın:

```powershell
docker run -d -p 9090:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home --name jenkins jenkins/jenkins:lts
```

Tarayıcıda: `http://localhost:9090`

### Container Başlamıyor

```powershell
# Logları kontrol et
docker logs jenkins

# Container'ı kaldırıp yeniden dene
docker rm -f jenkins
docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home --name jenkins jenkins/jenkins:lts
```

### Initial Password Görünmüyor

```powershell
# Logları kontrol et
docker logs jenkins | Select-String "password"

# Veya direkt dosyadan oku
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Jenkins Web Arayüzüne Erişilemiyor

1. Docker Desktop çalışıyor mu kontrol edin
2. Container çalışıyor mu: `docker ps`
3. Firewall ayarlarını kontrol edin
4. `http://localhost:8080` yerine `http://127.0.0.1:8080` deneyin

---

## 📱 Günlük Kullanım Senaryoları

### Sabah İşe Başlarken

```powershell
# Jenkins'i başlat (eğer durdurulmuşsa)
docker start jenkins

# Tarayıcıda aç
start http://localhost:8080
```

### Bilgisayarı Kapatmadan Önce

```powershell
# Jenkins'i durdur (opsiyonel - kapatınca otomatik durur)
docker stop jenkins
```

### Yeni Build Çalıştırma

1. Jenkins Dashboard → `TestAutomationPipeline`
2. **Build Now**
3. Console Output'u izle

---

## 🔐 Güvenlik Önerileri

1. **Güçlü admin şifresi kullanın**
2. **Yerel ağda çalıştırın** (public IP'ye expose etmeyin)
3. **Düzenli olarak Jenkins'i güncelleyin:**
   ```powershell
   docker pull jenkins/jenkins:lts
   docker stop jenkins
   docker rm jenkins
   docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home --name jenkins jenkins/jenkins:lts
   ```

---

## 📚 Yararlı Komutlar Özeti

```powershell
# Jenkins başlat
docker start jenkins

# Jenkins durdur
docker stop jenkins

# Jenkins loglarını gör
docker logs jenkins

# Jenkins container'ını sil
docker rm -f jenkins

# Jenkins image'ını güncelle
docker pull jenkins/jenkins:lts

# Tüm Docker container'larını listele
docker ps -a

# Volume listesi
docker volume ls

# Disk kullanımını kontrol et
docker system df
```

---

## 🎯 Bu Projede Kullanım

### Jenkinsfile Yapısı

Bu projede `Jenkinsfile` mevcut ve 4 stage içerir:

1. **Checkout** - Kodu Git'ten çeker
2. **Setup Environment** - Python venv kurar ve dependencies yükler
3. **Run Tests** - Pytest testlerini çalıştırır
4. **Generate Reports** - HTML test raporları oluşturur

### İlk Çalıştırma

1. Docker'da Jenkins başlatın
2. Pipeline job oluşturun (yukarıdaki adımlar)
3. Git repository URL'inizi girin
4. Build Now tıklayın

### Beklenen Sonuç

- ✅ Testler headless Chrome'da çalışır
- ✅ HTML raporu oluşturulur
- ✅ Pipeline başarılı/başarısız durumu gösterilir

---

## 📝 Notlar

- Jenkins container kapatıldığında veriler kaybolmaz (volume sayesinde)
- Windows yeniden başlatıldığında container otomatik başlamaz
- Manuel olarak `docker start jenkins` yapmanız gerekir
- Otomatik başlatma için Docker Desktop ayarlarından "Start Docker Desktop when you log in" aktif olmalı

---

## 📞 Destek

Sorun yaşarsanız:
1. Container loglarını kontrol edin: `docker logs jenkins`
2. Docker Desktop'ın çalıştığından emin olun
3. Firewall/Antivirus ayarlarını kontrol edin

---

## 📅 Son Güncelleme

Tarih: 29 Ekim 2025
Proje: TestAutomationPipline
Jenkins Version: LTS (Long Term Support)
Docker: Desktop for Windows

