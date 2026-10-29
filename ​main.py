import base64
import os
import google.generativeai as genai
import pandas as pd
import requests

# Gemini konfigurieren
gemini_key = os.environ.get("GEMINI_API_KEY")
if gemini_key:
  genai.configure(api_key=gemini_key)
  # Nutzen wir das schnelle und smarte Flash-Modell
  ai_model = genai.GenerativeModel("gemini-1.5-flash")
else:
  ai_model = None


def get_ebay_token():
  client_id = os.environ.get("EBAY_CLIENT_ID")
  client_secret = os.environ.get("EBAY_CLIENT_SECRET")

  if not client_id or not client_secret:
    print("Fehler: eBay API-Schlüssel wurden nicht gefunden!")
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
    print(
        f"Fehler beim Token-Abruf: {response.status_code} -"
        f" {response.text}"
    )
    return None


def analyze_with_gemini(title, price):
  if not ai_model:
    return "KI nicht aktiv"

  prompt = (
      f"Analysiere dieses eBay-Angebot:\nTitel: '{title}'\nPreis: {price}"
      " EUR\n\nPrüfe kurz und knackig (in maximal 2 Sätzen):\n1. Gibt es"
      " Anzeichen für einen Tippfehler im Titel oder einen potenziellen"
      " Preisfehler/Glitch?\n2. Handelt es sich um ein spannendes Schnäppchen"
      " oder einen versteckten Schatz?"
  )

  try:
    response = ai_model.generate_content(prompt)
    return response.text.strip().replace("\n", " ")
  except Exception as e:
    return f"KI-Fehler: {str(e)}"


def search_and_analyze_ebay(token, query="PlayStation 5"):
  search_url = (
      f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&limit=3"
  )
  headers = {
      "Authorization": f"Bearer {token}",
      "X-EBAY-C-MARKETPLACE-ID": "EBAY_DE",
  }

  response = requests.get(search_url, headers=headers)

  if response.status_code == 200:
    items = response.json().get("itemSummaries", [])
    print(
        f"\n{len(items)} Artikel für '{query}' gefunden. Starte KI-Analyse...\n"
    )

    for item in items:
      title = item.get("title")
      price = item.get("price", {}).get("value", "0")
      item_url = item.get("itemWebUrl")

      print(f"📦 Artikel: {title}")
      print(f"💰 Preis: {price} EUR")

      # Gemini schaut sich das Angebot an
      ai_verdict = analyze_with_gemini(title, price)
      print(f"🤖 Gemini-Analyse: {ai_verdict}")
      print("-" * 50)
  else:
    print(
        f"Fehler bei der Suche: {response.status_code} - {response.text}"
    )


def main():
  print("=== DealHunter KI-Scanner gestartet ===")
  token = get_ebay_token()

  if token:
    # Wir suchen testweise nach Produkten
    search_and_analyze_ebay(token, query="PlayStation 5")

  print("=== Skript beendet ===")


if __name__ == "__main__":
  main()
