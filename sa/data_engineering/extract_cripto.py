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
            "chave"
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

                # JSON enviado ao Supabase (histórico)
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

                # --- novo: upsert para tabela cotacoes_atuais (mantém a cotação atual) ---
                # normaliza um código curto (ex: "BTC" a partir de "BTC-USDT")
                codigo = symbol.split('-')[0] if isinstance(symbol, str) and '-' in symbol else symbol

                upsert_headers = headers.copy()
                # usa merge-duplicates para fazer upsert (requer constraint/PK em cotacoes_atuais)
                upsert_headers["Prefer"] = "resolution=merge-duplicates"

                upsert_payload = {
                    "id_cripto": id_cripto,
                    "simbolo": symbol,
                    "codigo": codigo,
                    "valor": last_price,
                    "data": datetime.utcnow().isoformat()
                }

                upsert_response = requests.post(
                    f"{self.supabase_url}/cotacoes_atuais",
                    headers=upsert_headers,
                    json=upsert_payload
                )

                if upsert_response.status_code not in [200, 201]:
                    print(f"Erro ao upsert cotação atual ({symbol}): {upsert_response.status_code} {upsert_response.text}")

            else:
                print(f"Erro {response.status_code}: {response.text}")

        return True

# --- exemplo de uso (linha ~51-59 que você mencionou) ---
if __name__ == "__main__":
    # Exemplo de execução:
    #  - A tabela 'criptomoedas' deve conter as colunas: id, nome, simbolo
    #  - O campo 'simbolo' deve armazenar o instId esperado pela OKX (ex: "BTC-USDT", "ETH-USDT")
    process = Process_cripto()
    try:
        criptos = process.get_criptos()  # retorna { id: "BTC-USDT", ... }
        process.extract_cripto(criptos)
        print("Extração de cripto finalizada.")
    except Exception as e:
        print("Erro na execução:", e)

