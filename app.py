from flask import Flask, redirect, render_template, request

app = Flask(__name__)


# 1. Ana Karşılama Sayfası
@app.route("/")
def ana_sayfa():
  return render_template("anasayfa.html")


# 2. Araçlar Paneli Sayfası
@app.route("/araclar")
def araclar():
  return render_template("araclar.html")


# --- Arama ve Yönlendirme Fonksiyonları (Sunucu Uyumlu) ---


@app.route("/ara", methods=["POST"])
def ara():
  soru = request.form.get("kullanici_sorusu")
  url = f"https://www.google.com/search?q={soru}"
  return redirect(url)


@app.route("/cevapla", methods=["POST"])
def cevapla():
  soru = request.form.get("kullanici_sorusu")
  url = f"https://www.google.com/search?q={soru}&tbm=isch"
  return redirect(url)


@app.route("/video", methods=["POST"])
def video():
  soru = request.form.get("kullanici_sorusu")
  url = f"https://www.bing.com/videos?FORM=HDRSC4&q={soru}"
  return redirect(url)


@app.route("/haritalar", methods=["POST"])
def haritalar():
  soru = request.form.get("kullanici_sorusu")
  url = f"https://www.bing.com/maps/search?FORM=HDRSC6&style=r&q={soru}"
  return redirect(url)


# --- Yeni Eklenen Özellik: Wikipedia / Ansiklopedi ---
@app.route("/ansiklopedi", methods=["POST"])
def ansiklopedi():
  soru = request.form.get("kullanici_sorusu")
  url = f"https://tr.wikipedia.org/wiki/Special:Search?search={soru}"
  return redirect(url)


# --- Yeni Eklenen Özellik: Hızlı Not Kaydetme (Metin Dosyasına Yazar) ---
@app.route("/not_ekle", methods=["POST"])
def not_ekle():
  alinan_not = request.form.get("kullanici_notu")
  if alinan_not:
    # Sunucuda "notlarim.txt" adında bir dosyaya alt alta kaydeder
    with open("notlarim.txt", "a", encoding="utf-8") as dosya:
      dosya.write(alinan_not + "\n")
  return redirect("/araclar")


if __name__ == "__main__":
  app.run(debug=True)
