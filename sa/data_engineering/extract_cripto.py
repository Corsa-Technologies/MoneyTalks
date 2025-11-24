import requests
from datetime import datetime

class Process_cripto:
    """
    Classe responsável por:
      - Consultar lista de criptomoedas armazenadas no Supabase.
      - Buscar preços em tempo real na API da OKX.
      - Armazenar cada nova cotação em uma tabela no Supabase.

    Fluxo:
      1. get_criptos() → retorna {id: "BTC-USDT", ...}
      2. extract_cripto() → percorre cada símbolo, coleta o preço e salva no Supabase
    """

    def __init__(self):
        """
        Inicializa URLs e credenciais.
        """
        self.base_url = "https://www.okx.com/api/v5/market/ticker"
        self.supabase_url = "https://pltknfhvlcnfcblxcrro.supabase.co/rest/v1"
        self.supabase_key = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBsdGtuZmh2bGNuZmNibHhjcnJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgzMjUyMDUsImV4cCI6MjA3MzkwMTIwNX0.MOk0uUxA6ik8-j4BemDIsq63LCZUHqufoOe_oD-QZsE"
        )

    def get_criptos(self):
        """
        Busca no Supabase a lista de criptomoedas cadastradas.

        Returns:
            dict: Um dicionário no formato {id_cripto: "BTC-USDT"}

        Raises:
            Exception: Se a requisição falhar.
        """
        url = f"{self.supabase_url}/criptomoedas"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return {item["id"]: item["simbolo"] for item in data}
        else:
            raise Exception(f"Erro ao buscar criptomoedas: {response.text}")

    def extract_cripto(self, criptos):
        """
        Consulta o preço atual de cada criptomoeda na API da OKX
        e insere a cotação no Supabase.

        Args:
            criptos (dict): Dicionário {id_cripto: simbolo} vindo de get_criptos().

        Returns:
            bool: True se todas as requisições foram processadas.
        """

        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

        # Loop para processar cada criptomoeda cadastrada no Supabase
        for id_cripto, symbol in criptos.items():

            # API da OKX exige parâmetro instId=BTC-USDT, por exemplo
            params = {"instId": symbol}
            response = requests.get(self.base_url, params=params)

            if response.status_code == 200:
                data = response.json()

                # Extrai o último preço
                last_price = float(data["data"][0]["last"])

                # JSON enviado ao Supabase
                payload = {
                    "valor": last_price,
                    "data": datetime.utcnow().isoformat(),
                    "id_cripto": id_cripto
                }

                insert_response = requests.post(
                    f"{self.supabase_url}/historico_criptos",
                    headers=headers,
                    json=payload
                )

                if insert_response.status_code not in [200, 201]:
                    print(f"Erro ao inserir cotação ({symbol}): {insert_response.text}")

            else:
                print(f"Erro {response.status_code}: {response.text}")

        return True
