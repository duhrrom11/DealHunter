def fetch_ebay_deals(token):
  # Wir suchen über breite eBay-Kategorien statt über feste Wörter
  # 293 = Elektronik, 11450 = Kleidung & Accessoires, 888 = Heimwerker
  category_ids = ["293", "11450", "888"]
  all_deals = []

  headers = {
      "Authorization": f"Bearer {token}",
      "X-EBAY-C-MARKETPLACE-ID": "EBAY_DE",
  }

  for cat_id in category_ids:
    print(
        f"Scanne Kategorie-ID {cat_id} nach den neuesten Inseraten..."
    )
    # sort=newlyListed sorgt dafür, dass wir die frischesten Angebote zuerst sehen (perfekt für Glitches)
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

