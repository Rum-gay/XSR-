from flask import Flask, redirect, render_template, request

app = Flask(__name__)

# Sunucuda dosya hatası (500) vermemesi için notları hafızada tutuyoruz
notlar = []


@app.route("/")
def ana_sayfa():
  return render_template("anasayfa.html")


@app.route("/araclar")
def araclar():
  # Hafızadaki notları araraclar.html sayfasına gönderiyoruz
  return render_template("araclar.html", not_listesi=notlar)


# --- Arama ve Yönlendirme Fonksiyonları (Yeni sekmede açılır) ---


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


@app.route("/ansiklopedi", methods=["POST"])
def ansiklopedi():
  soru = request.form.get("kullanici_sorusu")
  url = f"https://tr.wikipedia.org/wiki/Special:Search?search={soru}"
  return redirect(url)


# --- Not Ekleme Özelliği (Hafızada Tutar) ---
@app.route("/not_ekle", methods=["POST"])
def not_ekle():
  alinan_not = request.form.get("kullanici_notu")
  if alinan_not:
    notlar.append(alinan_not)
  return redirect("/araclar")


if __name__ == "__main__":
  app.run(debug=True)
