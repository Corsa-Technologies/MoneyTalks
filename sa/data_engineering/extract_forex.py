from dotenv import load_dotenv
import requests
from datetime import datetime

class Process_data:
    """
    Classe responsável por:
      - Buscar a lista de moedas (forex) no Supabase.
      - Consultar a API ForexRateAPI para obter as taxas de câmbio.
      - Inserir o histórico de preços no Supabase.

    A classe foi projetada para ser simples e direta:
    - get_criptos() → retorna dicionário {id: nome}
    - scrape_forex() → consulta API externa e grava histórico em Supabase
    """

    def __init__(self):
        """
        Inicializa URLs e chaves de autenticação.
        """
        self.base_url = "https://www.okx.com/api/v5/market/ticker"
        self.supabase_url = "https://pltknfhvlcnfcblxcrro.supabase.co/rest/v1"
        self.supabase_key = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        )

    def get_criptos(self):
        """
        Busca a lista cadastrada de forex no Supabase.

        Returns:
            dict: Um dicionário no formato {id_forex: "BRL"}.
        
        Raises:
            Exception: Se a API retornar erro.
        """
        url = f"{self.supabase_url}/forex"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return {item["id"]: item["nome"] for item in data}
        else:
            raise Exception(f"Erro ao buscar forex: {response.text}")

    def scrape_forex(self, forexes):
        """
        Consulta a API ForexRateAPI e grava os valores no Supabase.

        Args:
            forexes (dict): dicionário {id_forex: simbolo_da_moeda} vindos do Supabase.

        Processo:
            1. Monta a URL da API externa com as moedas a consultar.
            2. Faz a requisição GET para buscar as taxas.
            3. Valida retorno da API.
            4. Para cada moeda registrada no Supabase:
                 - verifica se existe na API
                 - grava no banco (tabela historico_forex)
        """
        # lista de moedas que serão consultadas na API externa
        currencies = ["BRL", "EUR", "INR", "JPY"]
        currencies_str = ",".join(currencies)

        # headers obrigatórios do Supabase
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

        # URL da API ForexRateAPI
        url = (
            "https://api.forexrateapi.com/v1/latest"
            "?api_key=870c833140235f50a45ff85161340fb9"
            f"&base=USD&currencies={currencies_str}"
        )

        response = requests.get(url)

        # validação de erro da API externa
        if response.status_code != 200:
            print(f"Erro {response.status_code}: {response.text}")
            return

        data = response.json()
        rates = data.get("rates")

        if rates is None:
            print("Erro: 'rates' não retornado pela API.")
            print(data)
            return

        # percorre cada moeda cadastrada no Supabase
        for id_forex, symbol in forexes.items():

            # verifica se moeda existe na API externa
            if symbol not in rates:
                print(f"Moeda {symbol} não está disponível na API.")
                continue

            last_price = float(rates[symbol])

            # json enviado ao Supabase
            payload = {
                "valor": last_price,
                "data": datetime.utcnow().isoformat(),
                "id_forex": id_forex
            }

            # insere registro no Supabase
            insert_response = requests.post(
                f"{self.supabase_url}/historico_forex",
                headers=headers,
                json=payload
            )

            if insert_response.status_code not in [200, 201]:
                print(f"Erro ao inserir cotação ({symbol}): {insert_response.text}")
            else:
                print(f"✔ Inserido {symbol}: {last_price}")


if __name__ == "__main__":
    """
    Execução principal:
      - cria instância da classe
      - busca lista de moedas no Supabase
      - coleta preços e salva no banco
    """
    processo = Process_data()
    
    forexes = processo.get_criptos()
    processo.scrape_forex(forexes)
    print(forexes)
