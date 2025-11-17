import requests
from datetime import datetime
import time

class Extract_data:
    def __init__(self):
        self.base_url = "https://www.okx.com/api/v5/market/ticker"
        self.coins = ["BTC-USDT", 'ETH-USDT', 'SOL-USDT', 'XRP-USDT', 'ADA-USDT']
        self.supabase_url = "https://pltknfhvlcnfcblxcrro.supabase.co/rest/v1/cotacoes"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBsdGtuZmh2bGNuZmNibHhjcnJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgzMjUyMDUsImV4cCI6MjA3MzkwMTIwNX0.MOk0uUxA6ik8-j4BemDIsq63LCZUHqufoOe_oD-QZsE"

    def extract(self):
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

        for coin in self.coins:
            params = {"instId": coin}
            response = requests.get(self.base_url, params=params)

            if response.status_code == 200:
                data = response.json()
                last_price = float(data["data"][0]["last"])

                payload = {
                    "coinName": coin,
                    "coinValue": last_price,
                    "coinDate": datetime.utcnow().isoformat()
                }

                insert_response = requests.post(self.supabase_url, headers=headers, json=payload)

                if insert_response.status_code not in [200, 201]:
                    print(f"Erro ao inserir no Supabase: {insert_response.text}")
            else:
                print(f"Erro {response.status_code}: {response.text}")
        
        return True