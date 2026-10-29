import base64
import os
import pandas as pd
import requests


def get_ebay_token():
  client_id = os.environ.get("EBAY_CLIENT_ID")
  client_secret = os.environ.get("EBAY_CLIENT_SECRET")

  if not client_id or not client_secret:
    print("Fehler: eBay API-Schlüssel wurden nicht gefunden!")
    return None

  # eBay OAuth Token URL (Production)
  token_url = "https://api.ebay.com/identity/v1/oauth2/token"

  # Zugangsdaten im Base64-Format kodieren
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
    print("Erfolgreich mit eBay API verbunden!")
    return response.json().get("access_token")
  else:
    print(
        f"Fehler beim Token-Abruf: {response.status_code} -"
        f" {response.text}"
    )
    return None


def search_ebay_items(token, query="iPhone"):
  # eBay Browse API Endpoint für Produktsuche
  search_url = (
      f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&limit=5"
  )

  headers = {
      "Authorization": f"Bearer {token}",
      "X-EBAY-C-MARKETPLACE-ID": "EBAY_DE",  # Deutscher eBay-Marktplatz
  }

  response = requests.get(search_url, headers=headers)

  if response.status_code == 200:
    items = response.json().get("itemSummaries", [])
    print(f"\nGefundene Artikel für '{query}': {len(items)}")

    deal_list = []
    for item in items:
      title = item.get("title")
      price = item.get("price", {}).get("value")
      currency = item.get("price", {}).get("currency")
      item_url = item.get("itemWebUrl")

      deal_list.append({"Titel": title, "Preis": f"{price} {currency}"})
      print(f"- {title} | Preis: {price} {currency}")

    return deal_list
  else:
    print(
        f"Fehler bei der Produktsuche: {response.status_code} -"
        f" {response.text}"
    )
    return []


def main():
  print("=== DealHunter eBay Live-Abruf gestartet ===")
  token = get_ebay_token()

  if token:
    # Testweise nach einem Suchbegriff suchen
    search_ebay_items(token, query="PlayStation 5")

  print("=== Skript beendet ===")


if __name__ == "__main__":
  main()
