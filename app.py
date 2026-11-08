from flask import Flask, redirect, render_template, request
import json
import os
import re
import statistics
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen

app = Flask(__name__)

def fiyat_degerini_ayikla(fiyat_metni):
  eslesme = re.search(r"\d[\d.]*,\d{2}|\d[\d.]*", fiyat_metni)
  if not eslesme:
    return None

  deger = eslesme.group().replace(".", "").replace(",", ".")
  try:
    return float(deger)
  except ValueError:
    return None


def fiyat_goster(deger):
  return f"{deger:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"


def google_shopping_urunleri(aranan_kelime, api_anahtari):
  parametreler = urlencode({
    "engine": "google_shopping",
    "q": aranan_kelime,
    "api_key": api_anahtari,
    "gl": "tr",
    "hl": "tr",
    "google_domain": "google.com.tr"
  })
  istek = f"https://serpapi.com/search.json?{parametreler}"

  with urlopen(istek, timeout=25) as yanit:
    veri = json.load(yanit)

  if veri.get("error"):
    raise ValueError(veri["error"])

  return veri.get("shopping_results", [])


@app.route("/")
def ana_sayfa():
  return render_template(
    "anasayfa.html",
    api_hazir=bool(os.environ.get("SERPAPI_KEY"))
  )

@app.route("/araclar")
def araclar():
  return render_template("araclar.html")

@app.route("/xsrb-urun-ara")
def urun_arama_sayfasi():
  return render_template("xsrb_urun_ara.html")

@app.route("/ara", methods=["POST"])
def ara():
  soru = (request.form.get("kullanici_sorusu") or "").strip()
  if not soru:
    return redirect("/araclar")
  url = "https://www.google.com/search?" + urlencode({"q": soru})
  return redirect(url)

@app.route("/cevapla", methods=["POST"])
def cevapla():
  soru = (request.form.get("kullanici_sorusu") or "").strip()
  if not soru:
    return redirect("/araclar")
  url = "https://www.google.com/search?" + urlencode({"q": soru, "tbm": "isch"})
  return redirect(url)

@app.route("/video", methods=["POST"])
def video():
  soru = (request.form.get("kullanici_sorusu") or "").strip()
  if not soru:
    return redirect("/araclar")
  url = "https://www.bing.com/videos?" + urlencode({"FORM": "HDRSC4", "q": soru})
  return redirect(url)

@app.route("/youtube", methods=["POST"])
def youtube():
  soru = (request.form.get("kullanici_sorusu") or "").strip()
  if not soru:
    return redirect("/araclar")
  url = "https://www.youtube.com/results?" + urlencode({"search_query": soru})
  return redirect(url)

@app.route("/haritalar", methods=["POST"])
def haritalar():
  soru = (request.form.get("kullanici_sorusu") or "").strip()
  if not soru:
    return redirect("/araclar")
  url = "https://www.bing.com/maps/search?" + urlencode({
    "FORM": "HDRSC6",
    "style": "r",
    "q": soru
  })
  return redirect(url)

@app.route("/ansiklopedi", methods=["POST"])
def ansiklopedi():
  soru = (request.form.get("kullanici_sorusu") or "").strip()
  if not soru:
    return redirect("/araclar")
  url = "https://tr.wikipedia.org/wiki/Special:Search?" + urlencode({"search": soru})
  return redirect(url)

@app.route("/ceviri", methods=["POST"])
def ceviri():
  soru = (request.form.get("kullanici_sorusu") or "").strip()
  if not soru:
    return redirect("/araclar")
  url = "https://translate.google.com/?" + urlencode({
    "sl": "auto",
    "tl": "tr",
    "text": soru,
    "op": "translate"
  })
  return redirect(url)

@app.route("/haberler", methods=["POST"])
def haberler():
  soru = (request.form.get("kullanici_sorusu") or "").strip()
  if not soru:
    return redirect("/araclar")
  url = "https://www.google.com/search?" + urlencode({"q": soru, "tbm": "nws"})
  return redirect(url)

@app.route("/urun-ara", methods=["POST"])
def urun_ara():
  aranan_kelime = (request.form.get("kullanici_sorusu") or "").strip()
  arama_url = "https://www.google.com/search?" + urlencode({
    "tbm": "shop",
    "q": aranan_kelime,
    "gl": "tr",
    "hl": "tr"
  }) if aranan_kelime else None

  if not aranan_kelime:
    return render_template(
      "xsrb_urun_sonuclari.html",
      sonuclar=[],
      ticker_feed=None,
      aranan="",
      ortalama=None,
      hata="Lütfen aramak istediğiniz ürünün adını yazın.",
      uyari=None,
      arama_url=None
    )

  api_anahtari = os.environ.get("SERPAPI_KEY")
  urunler = []
  hata = None
  uyari = None

  if not api_anahtari:
    hata = (
      "Ürünleri listelemek için SerpApi anahtarı gerekli. "
      "SerpApi hesabı oluşturup API anahtarını SERPAPI_KEY ortam değişkenine ekleyin."
    )
  else:
    try:
      ham_sonuclar = google_shopping_urunleri(aranan_kelime, api_anahtari)
      for urun in ham_sonuclar:
        sayisal_fiyat = urun.get("extracted_price")
        if not isinstance(sayisal_fiyat, (int, float)):
          sayisal_fiyat = fiyat_degerini_ayikla(urun.get("price", ""))

        link = urun.get("product_link") or urun.get("link")
        if (
          sayisal_fiyat is None
          or not isinstance(link, str)
          or urlparse(link).scheme not in {"http", "https"}
          or not urun.get("title")
        ):
          continue

        urunler.append({
          "isim": urun["title"],
          "fiyat": fiyat_goster(sayisal_fiyat),
          "sayisal_fiyat": float(sayisal_fiyat),
          "link": link,
          "site": urun.get("source") or "Mağaza bilgisi belirtilmemiş"
        })
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
      app.logger.exception("SerpApi Google Shopping araması başarısız oldu")
      hata = (
        "Ürün arama servisine erişilemedi. API anahtarını ve SerpApi hesap limitinizi "
        "kontrol edip tekrar deneyin."
      )

  ortalama = statistics.mean(urun["sayisal_fiyat"] for urun in urunler) if urunler else None
  sonuclar = sorted(
    (urun for urun in urunler if ortalama is not None and urun["sayisal_fiyat"] < ortalama),
    key=lambda urun: urun["sayisal_fiyat"]
  )

  if not hata and not urunler:
    hata = "Bu aramada fiyatı ve bağlantısı olan bir ürün bulunamadı."
  elif not hata and not sonuclar:
    hata = "Sonuç bulundu ancak ortalamanın altında fiyatlı ürün yok."

  if urunler:
    uyari = "Fiyatlar Google Shopping sonuçlarından alınmıştır; satın almadan önce mağaza sayfasında kontrol edin."

  ticker_feed = {
    "query": aranan_kelime[:80],
    "items": [
      {
        "title": urun["isim"][:100],
        "price": urun["fiyat"],
        "source": urun["site"][:60],
        "link": urun["link"]
      }
      for urun in sorted(urunler, key=lambda item: item["sayisal_fiyat"])[:6]
    ]
  } if urunler else None

  return render_template(
    "xsrb_urun_sonuclari.html",
    sonuclar=sonuclar,
    ticker_feed=ticker_feed,
    aranan=aranan_kelime,
    ortalama=fiyat_goster(ortalama) if ortalama is not None else None,
    hata=hata,
    arama_url=arama_url,
    uyari=uyari
  )

if __name__ == "__main__":
  app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "5000")),
    debug=os.environ.get("FLASK_DEBUG") == "1"
  )