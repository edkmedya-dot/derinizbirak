# derinizbirak — otomatik Instagram paylaşımı kurulumu

Sistem: GitHub Actions her gün 20:00'de `hazir/` klasöründen sıradaki görseli alır ve
Instagram'ın resmi API'siyle paylaşır. Paylaşılanlar `paylasildi.json` dosyasına yazılır,
böylece aynı gönderi iki kez paylaşılmaz. Bilgisayarının açık olması gerekmez.

## 1. Instagram hesabını profesyonel yap
Instagram → Ayarlar → Hesap türü ve araçlar → **Profesyonel hesaba geç** → İçerik üreticisi.
(Ücretsiz. Kişisel hesaplarda API ile paylaşım yapılamaz.)

## 2. Meta geliştirici uygulaması aç
1. https://developers.facebook.com → Uygulamalarım → **Uygulama oluştur**
2. Kullanım durumu: **Instagram'dan mesajları ve içeriği yönet** (Instagram API, Instagram ile giriş)
3. Instagram → API kurulumu → **Hesap ekle** → derinizbirak hesabıyla giriş yap
4. İzinler: `instagram_business_basic`, `instagram_business_content_publish`
5. **Erişim token'ı oluştur** → çıkan uzun token'ı kopyala (60 gün geçerli, sistem kendisi yeniler)

> Uygulama "geliştirme modunda" kalabilir. Sadece kendi hesabına paylaşım yaptığın için
> Meta incelemesine (App Review) gerek yok.

## 3. GitHub deposu
1. Bu klasörü **herkese açık** bir GitHub deposuna yükle. Instagram görseli bir URL'den çeker;
   görseller zaten Instagram'da paylaşılacağı için açık olmaları sorun değil.
   Token depoda değil, gizli secret'ta durur.
2. Depo → Settings → Secrets and variables → Actions → **New repository secret**:
   - `IG_TOKEN` = 2. adımdaki token
   - `GH_PAT` = GitHub → Settings → Developer settings → Fine-grained token
     (sadece bu depo, izin: *Secrets: Read and write*). Haftalık token yenilemesi için gerekir.
3. Actions sekmesi → "Günlük Instagram paylaşımı" → **Run workflow** ile ilk paylaşımı elle dene.

## Günlük kullanım
- Yeni gönderi: `posts.json`'a ekle → `render.py` → çıkan jpg'yi `hazir/` klasörüne koy → push.
- Sıra dosya adına göredir (01, 02, …). Paylaşım saatini `.github/workflows/paylas.yml`
  içindeki `cron` satırından değiştir (saat UTC; Türkiye = UTC+3).
- Paylaşmadan önce kontrol: `python paylas.py --dene`
- Limit: Instagram API günde en fazla 100 paylaşıma izin verir.
