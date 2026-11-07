import webbrowser
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

@app.route("/")
def ana_sayfa():
  return render_template("anasayfa.html")

@app.route("/araclar")
def araclar():
  return render_template("araclar.html")


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

  
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000, debug=True)
