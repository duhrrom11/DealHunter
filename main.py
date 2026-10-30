import base64
import os
from google import genai
import requests


def get_ebay_token():
  client_id = os.environ.get("EBAY_CLIENT_ID")
  client_secret = os.environ.get("EBAY_CLIENT_SECRET")

  if not client_id or not client_secret:
    print("Fehler: eBay API-Schlüssel fehlen in den GitHub Secrets!")
    return None

  token_url = "https://api.ebay.com/identity/v1/oauth2/token"
  credentials = f"{client_id}:{client_secret}"
  encoded_credentials = base64.b64encode(credentials.encode()).decode()

  headers = {
      "Authorization": f"Basic {encoded_credentials}",
      "Content-Type": "application/x-www-form-urlencoded",
  }
  data = {
      "grant_type": "client_credentials",
      "scope": "https://api.ebay.com/oauth/api_scope",
  }

  response = requests.post(token_url, headers=headers, data=data)
  if response.status_code == 200:
    return response.json().get("access_token")
  else:
    print(f"Fehler beim Token-Abruf: {response.text}")
    return None


def analyze_with_gemini(title, price):
  gemini_key = os.environ.get("GEMINI_API_KEY")
  if not gemini_key:
    return "KI-Schlüssel nicht hinterlegt."

  try:
    # Verwendung des aktuellen Modells gemäß API-Hinweis
    client = genai.Client(api_key=gemini_key)
    prompt = (
        f"Analysiere dieses eBay-Angebot:\nTitel: '{title}'\nPreis: {price}"
        " EUR\n\nBeurteile kurz und knackig (max. 2 Sätze):\n1. Gibt es"
        " Auffälligkeiten (Preisfehler, Tippfehler)?\n2. Lohnt sich der Blick"
        " darauf?"
    )

    response = client.models.generate_content(
        model="gemini-3.8-flash", contents=prompt
    )
    if response and response.text:
      return response.text.strip().replace("\n", " ")
    else:
      return "Keine Antwort von Gemini erhalten."
  except Exception as e:
    print(f"Gemini API Fehler bei '{title}': {str(e)}")
    return "KI-Analyse temporär nicht verfügbar."


def fetch_ebay_deals(token):
  category_ids = ["293", "888"]  # 293 = Elektronik, 888 = Heimwerker
  all_deals = []

  headers = {
      "Authorization": f"Bearer {token}",
      "X-EBAY-C-MARKETPLACE-ID": "EBAY_DE",
  }

  for cat_id in category_ids:
    print(f"Scanne Kategorie-ID {cat_id} nach neuesten Inseraten...")
    search_url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?category_ids={cat_id}&sort=newlyListed&limit=3"

    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
      print(f"Fehler bei Kategorie {cat_id}: {response.text}")
      continue

    items = response.json().get("itemSummaries", [])
    for item in items:
      title = item.get("title", "Unbekannter Titel")
      price_obj = item.get("price", {})
      price = price_obj.get("value", "0.00")
      currency = price_obj.get("currency", "EUR")
      item_url = item.get("itemWebUrl", "#")

      print(f"  -> Gefunden: {title} ({price} {currency})")
      ai_text = analyze_with_gemini(title, price)

      all_deals.append({
          "title": title,
          "price": f"{price} {currency}",
          "ai": ai_text,
          "url": item_url,
      })

  return all_deals


def generate_html(deals):
  cards_html = ""
  for deal in deals:
    cards_html += f"""
        <div class="deal-card">
            <div>
                <div class="deal-title">{deal['title']}</div>
                <div class="deal-price">{deal['price']} <span style="font-size: 0.6em; color: var(--accent);">⚡ Live-Fund</span></div>
                <div class="ai-box">
                    <strong>Gemini AI:</strong> {deal['ai']}
                </div>
            </div>
            <a href="{deal['url']}" target="_blank" class="btn">Zum eBay-Angebot</a>
        </div>
        """

  html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DealHunter - Live eBay Glitch & Schatz-Radar</title>
    <style>
        :root {{
            --bg-main: #1a1d20;
            --bg-card: #23272a;
            --accent: #c5a059;
            --text-main: #f4f4f2;
            --text-muted: #b0b3b8;
            --highlight: #2c4c3e;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-main);
            color:
