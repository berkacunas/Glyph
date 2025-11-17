# Glyph

[](https://www.google.com/search?q=https://github.com/berkacunas/Glyph/actions/workflows/release.yml)
[](https://www.gnu.org/licenses/gpl-3.0)
[](https://www.google.com/search?q=https://github.com/berkacunas/Glyph/releases)

Python ve PySide6 ile güçlendirilmiş, `QWebEngineView` tabanlı canlı önizleme özelliğine sahip, modern ve çok sekmeli bir Markdown editörü.

Bu proje, yerel (offline) çalışan, hızlı ve gelişmiş Markdown eklentilerini destekleyen güçlü bir yazma aracı sağlamak amacıyla geliştirilmiştir.

`[Glyph arayüzünün ekran görüntüsünü buraya ekleyin]`

-----

## 🧭 Temel Özellikler

"Glyph", standart bir metin editörünün ötesinde, modern Markdown iş akışları için tasarlanmış bir dizi özelliğe sahiptir:

  * **Canlı Önizleme:** Yan yana açılabilen (`Ctrl+Shift+V`) ve siz yazdıkça güncellenen Chromium tabanlı bir önizleme paneli.
  * **Çoklu Sekme (Multi-Tab):** Tıpkı modern kod editörleri gibi, birden fazla belgeyi aynı anda açın ve yönetin.
  * **Gelişmiş Markdown Desteği:** `python-markdown` ve `Pymdown` eklentileri sayesinde:
      * **GitHub Emojileri:** `:rocket:`, `:smile:` gibi kısa kodları 🚀 ve 😄 olarak render eder.
      * **Uyarı Kutuları (Admonitions):** `!!! note "Başlık"` veya `!!! warning` gibi özel not kutuları oluşturur.
      * **Kod Vurgulama:** `Pygments` destekli sözdizimi renklendirmesi.
      * **Diğer Eklentiler:** Tablolar, Dipnotlar, İçindekiler Tablosu ([TOC]).
  * **Dosya Yönetimi:**
      * VS Code benzeri açılıp kapanabilir `QDockWidget` dosya gezgini.
      * `Save All` (Tümünü Kaydet) ve `Close All` (Tümünü Kapat) özellikleri.
  * **Dışa Aktarma (Export):**
      * PDF olarak dışa aktarma.
      * `Export As...` (Farklı Dışa Aktar): Saf HTML/XHTML, düz metin (.txt) veya `.md`.
      * `Send...` (E-posta ile Gönder).
  * **Özelleştirme:**
      * Tüm ayarları (`QSettings` ile) kalıcı olarak kaydeden Ayarlar paneli.
      * Editör ve Önizleme paneli için **Font Seçimi**.
      * Dil desteği (TR/EN).
      * Tüm önizleme stilleri, harici bir `main.css` dosyası üzerinden yönetilir ve özelleştirilebilir.

-----

## 🚀 Kurulum ve Çalıştırma

Bu projeyi kaynaktan çalıştırmak için:

1.  Depoyu klonlayın:

    ```bash
    git clone https://github.com/berkacunas/Glyph.git
    cd Glyph
    ```

2.  Sanal bir Python ortamı oluşturun ve aktifleştirin:

    ```bash
    python -m venv .venv
    # Windows:
    .\.venv\Scripts\activate
    # macOS/Linux:
    # source .venv/bin/activate
    ```

3.  Gerekli bağımlılıkları kurun:

    ```bash
    pip install -r requirements.txt
    ```

4.  Programı çalıştırın:

    ```bash
    python program.py
    ```

-----

## 👨‍💻 Geliştiriciler İçin (Katkıda Bulunma)

Bu proje, profesyonel CI/CD (Sürekli Entegrasyon) ve Kalite Kontrol (QA) standartlarını takip eder.

  * **Commit Standardı:** Tüm commit mesajları [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `chore:`) standardına uymalıdır.
  * **Commit Kancaları (Hooks):** Proje, `husky` ve `commitlint` kullanarak bu standartları zorunlu kılar.
  * **Test:** Tüm commit'ler, `pre-commit` kancasına (hook) bağlı olan `pytest` testlerinden geçmelidir.
  * **Sürümleme:** Sürümler ve `CHANGELOG.md` dosyası, `main` dalına yapılan birleştirmelerde `semantic-release` tarafından otomatik olarak yönetilir.

Katkıda bulunmak için lütfen `main` dalından yeni bir dal (branch) açın ve Pull Request gönderin.

-----

## ⚖️ Lisans

`Glyph`, **Çifte Lisanslama (Dual-Licensing)** modeli altında sunulmaktadır.

### 1\. Açık Kaynak Lisansı

Bu proje, açık kaynaklı projelerde ve kişisel kullanımda **GNU General Public License v3.0 (GPL-3.0)** koşulları altında ücretsiz olarak kullanılabilir. Detaylar için `LICENSE` dosyasına bakın.

### 2\. Ticari Lisans

"Glyph"i, GPL-3.0'ın "bulaşıcı" kısıtlamaları olmaksızın **kapalı kaynaklı (proprietary)** bir ticari ürüne entegre etmek için alternatif bir **Ticari Lisans** gereklidir.

Ticari lisanslama koşulları ve fiyatlandırma için lütfen **[...BURAYA E-POSTA ADRESİNİZİ YAZIN...]** üzerinden iletişime geçin.