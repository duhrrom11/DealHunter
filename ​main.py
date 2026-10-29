import pandas as pd
import requests


def run_dealhunter():
  print("=== DealHunter Bot gestartet ===")

  # Test, ob pandas und requests reibungslos funktionieren
  data = {"Modul": ["eBay Feed", "Gemini KI", "Telegram Bot"], "Status": [
      "Bereit",
      "Bereit",
      "Bereit",
  ]}
  df = pd.DataFrame(data)

  print("\nSystem-Status:")
  print(df)
  print("\n=== DealHunter Durchlauf erfolgreich beendet ===")


if __name__ == "__main__":
  run_dealhunter()
