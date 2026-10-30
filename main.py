import base64
import os
import requests


def get_ebay_token():
  client_id = os.environ.get("EBAY_CLIENT_ID")
  client_secret = os.environ.get("EBAY_CLIENT_SECRET")

  if not client_id or not client_secret:
    print("Fehler: eBay API-Schlüssel fehlen!")
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
    return "KI-Schlüssel fehlt."

  # Direkter REST-API Aufruf für Gemini 1.5 Flash (absolut stabil)
  url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
  headers = {"Content-Type": "application/json"}

  prompt = (
      f"Analysiere dieses eBay-Angebot:\nTitel: '{title}'\nPreis: {price}"
      " EUR\n\nBeurteile kurz und knackig (max. 2 Sätze):\n1. Gibt es"
      " Auffälligkeiten (Preisfehler, Tippfehler)?\n2. Lohnt sich der Blick"
      " darauf?"
  )

  data = {"contents": [{"parts": [{"text": prompt}]}]}

  try:
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
      result = response.json()
      text = (
          result.get("candidates", [{}])[0]
          .get("content", {})
          .get("parts", [{}])[0]
          .get("text", "Keine Antwort")
      )
      return text.strip().replace("\n", " ")
    else:
      return f"API-Fehler ({response.status_code})"
  except Exception as e:
    return f"KI-Fehler: {str(e)}"


def fetch_ebay_deals(token):
  category_ids = ["293", "888"]
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
            color: var(--text-main);
            margin: 0;
            padding: 20px;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        header {{
            text-align: center; padding: 40px 20px; background: var(--bg-card);
            border-radius: 12px; margin-bottom: 30px; border-bottom: 3px solid var(--accent);
        }}
        h1 {{ color: var(--accent); margin: 0 0 10px 0; font-size: 2.2em; }}
        p.subtitle {{ color: var(--text-muted); font-size: 1.1em; margin: 0; }}
        .status-badge {{
            display: inline-block; background: var(--highlight); color: #fff;
            padding: 6px 14px; border-radius: 20px; font-size: 0.85em; margin-top: 15px; font-weight: bold;
        }}
        .deals-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .deal-card {{
            background: var(--bg-card); border-radius: 12px; padding: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2); display: flex; flex-direction: column;
            justify-content: space-between; border: 1px solid rgba(255,255,255,0.05);
        }}
        .deal-title {{ font-size: 1.1em; font-weight: bold; margin-bottom: 10px; color: var(--text-main); }}
        .deal-price {{ font-size: 1.4em; color: var(--accent); font-weight: bold; margin-bottom: 15px; }}
        .ai-box {{
            background: rgba(44, 76, 62, 0.2); border-left: 3px solid var(--highlight);
            padding: 10px; border-radius: 4px; font-size: 0.9em; color: var(--text-muted); margin-bottom: 15px;
        }}
        .ai-box strong {{ color: var(--text-main); }}
        .btn {{
            display: block; text-align: center; background: var(--accent); color: #1a1d20;
            padding: 10px; border-radius: 6px; text-decoration: none; font-weight: bold;
        }}
        footer {{ text-align: center; margin-top: 40px; color: var(--text-muted); font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>DealHunter</h1>
            <p class="subtitle">Der automatisierte Radar für eBay-Preisfehler & KI-analysierte Deals.</p>
            <div class="status-badge">🟢 Live aktualisiert via GitHub & Gemini</div>
        </header>

        <div class="deals-grid">
            {cards_html}
        </div>

        <footer>
            &copy; 2026 DealHunter. Automatisiert gesteuert über die Cloud.
        </footer>
    </div>
</body>
</html>"""

  with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
  print("index.html erfolgreich aktualisiert!")


def main():
  print("=== DealHunter Direct-API gestartet ===")
  token = get_ebay_token()
  if token:
    deals = fetch_ebay_deals(token)
    if deals:
      generate_html(deals)
  print("=== Durchlauf beendet ===")


if __name__ == "__main__":
  main()
