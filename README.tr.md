# Glyph

[![CI/CD](https://github.com/berkacunas/Glyph/actions/workflows/release.yml/badge.svg)](https://github.com/berkacunas/Glyph/actions/workflows/release.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPL_v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Latest Release](https://img.shields.io/github/v/release/berkacunas/Glyph)](https://github.com/berkacunas/Glyph/releases)
**📥 Hemen İndir:** [**En Son Windows Sürümünü İndir (.exe)**](https://github.com/berkacunas/Glyph/releases/latest)

Python ve PySide6 ile güçlendirilmiş, `QWebEngineView` tabanlı canlı önizleme özelliğine sahip, modern ve çok sekmeli bir Markdown editörü.

Bu proje, yerel (offline) çalışan, hızlı ve gelişmiş Markdown eklentilerini destekleyen güçlü bir yazma aracı sağlamak amacıyla geliştirilmiştir.

![Glyph Editor Screenshot](src/assets/screenshots/screenshot_v1.png)

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
    ```

    # On Windows:
    ```bash
    .\.venv\Scripts\activate
    ```
    
    # On macOS/Linux:
    ```bash
    source .venv/bin/activate
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

Glyph, **GNU General Public License v3.0 (GPL-3.0)** altında lisanslanmış ücretsiz ve açık kaynaklı bir yazılımdır. Bu yazılımı, lisans koşullarına uymak kaydıyla özgürce kullanabilir, değiştirebilir ve dağıtabilirsiniz. Detaylar için `LICENSE` dosyasına bakınız.

---

## ❤️ Projeyi Destekleyin

Glyph, bağımsız bir geliştirici tarafından geliştirilmekte ve sürdürülmektedir. Eğer bu aracı faydalı bulduysanız ve geliştirmeyi desteklemek (veya sadece hazır derlenmiş `.exe` için teşekkür etmek) isterseniz, lütfen bağış yapmayı düşünün!

<a href="https://github.com/sponsors/berkacunas">
  <img src="https://img.shields.io/badge/Sponsor-GitHub-pink?style=for-the-badge&logo=github-sponsors" height="50" alt="Sponsor on GitHub">
</a>

<a href="https://www.buymeacoffee.com/depones" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

* **Bu repoya yıldız verin!** ⭐ Görünürlüğe çok yardımcı olur.

---
*Glyph, (C) 2025 Berk Acunaş'ın telif hakkına sahiptir ve GNU Genel Kamu Lisansı v3.0 (GPLv3) ile lisanslanmıştır. Lisansın tam metni [LICENSE](LICENSE) dosyasında mevcuttur.*
