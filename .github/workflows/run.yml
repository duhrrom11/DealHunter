name: DealHunter Automation

on:
  workflow_dispatch:
  schedule:
    - cron: '0 8 * * *'

permissions:
  contents: write

jobs:
  run-dealhunter:
    runs-on: ubuntu-latest
    steps:
      - name: Repository auschecken
        uses: actions/checkout@v4

      - name: Python einrichten
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Abhängigkeiten installieren
        run: |
          python -m pip install --upgrade pip
          pip install requests pandas google-generativeai

      - name: 🔍 Ordnerinhalt anzeigen (Debug)
        run: |
          echo "Aktuelles Verzeichnis:"
          pwd
          echo "Inhalt des Verzeichnisses:"
          ls -la

      - name: Hauptskript ausführen
        env:
          EBAY_CLIENT_ID: ${{ secrets.EBAY_CLIENT_ID }}
          EBAY_CLIENT_SECRET: ${{ secrets.EBAY_CLIENT_SECRET }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python main.py

      - name: Änderungen automatisch committen
        run: |
          git config --global user.name "DealHunter Bot"
          git config --global user.email "bot@users.noreply.github.com"
          git add index.html
          git commit -m "Auto-Update: Neue eBay Deals gefunden" || exit 0
          git push
