# importações
import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional  # para os modelos de dados

# configuração inicial
# aqui a gente cria a api
app = FastAPI(
    title="api financeira - projeto faculdade",
    description="backend em python para cotações e simulação de investimentos."
)
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "null"  # importante para permitir testes locais (o file://)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # permite todos os métodos (get, post, etc.)
    allow_headers=["*"],  # permite todos os cabeçalhos
)

# aqui guardamos as urls das apis que vamos usar
URL_FOREX = "https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL"
URL_OKX_TICKER = "https://www.okx.com/api/v5/market/ticker"
# api do bcb (sgs) para a taxa cdi diária (código 12)
URL_BCB_CDI = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados/ultimos/1?formato=json"
# api do bcb (sgs) para o ipca acumulado 12 meses (código 13522)
URL_BCB_IPCA = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados/ultimos/1?formato=json"

# pares de cripto que queremos da okx (em formato usdt)
PARES_CRIPTO = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]


# 1. lógica das cotações (funções de busca)

def buscar_dados_forex():
    """
    busca as cotações de usd-brl e eur-brl na awesomeapi.
    (função completa)
    """
    try:
        print("buscando dados de câmbio (usd/eur)...")
        response = requests.get(URL_FOREX)
        
        # checa se a chamada à api deu certo (código 200)
        if response.status_code == 200:
            data = response.json()
            
            # o 'bid' é o preço de compra (o que usamos como referência)
            preco_usd_brl = float(data['USDBRL']['bid'])
            preco_eur_brl = float(data['EURBRL']['bid'])
            
            return preco_usd_brl, preco_eur_brl
        else:
            # se a api falhar (ex: erro 500)
            print(f"erro ao buscar dados de câmbio: status {response.status_code}")
            return None, None

    except Exception as e:
        print(f"ocorreu uma exceção ao buscar dados de câmbio: {e}")
        return None, None

def buscar_preco_cripto_okx(par_id):
    """
    busca o último preço de um par específico (ex: "btc-usdt") na okx.
    (função completa)
    """
    try:
        # passamos o par como um parâmetro na url (ex: ?instid=btc-usdt)
        params = {'instId': par_id}
        response = requests.get(URL_OKX_TICKER, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # a api da okx retorna 'code: "0"' quando dá tudo certo
            if data['code'] == '0':
                # 'data[0]' pega o primeiro (e único) item da lista de dados
                # 'last' é o último preço negociado
                preco_usdt = float(data['data'][0]['last'])
                return preco_usdt
            else:
                print(f"erro da api okx ao buscar {par_id}: {data['msg']}")
                return None
        else:
            print(f"erro ao buscar {par_id} na okx: status {response.status_code}")
            return None

    except Exception as e:
        print(f"ocorreu uma exceção ao buscar {par_id}: {e}")
        return None

# endpoint de cotações

@app.get("/cotacoes/atuais")
def get_cotacoes_atuais():
    """
    endpoint para o frontend buscar as cotações atuais de todas as moedas.
    """
    print("recebida requisição para /cotacoes/atuais")
    
    # 1. buscar câmbio
    preco_usd, preco_eur = buscar_dados_forex()
    
    if preco_usd is None or preco_eur is None:
        # se a api de câmbio falhar, não dá pra converter as criptos
        raise HTTPException(status_code=503, detail="não foi possível buscar dados de câmbio (awesomeapi).")

    # 2. buscar cripto
    cripto_data = {}
    for par in PARES_CRIPTO:
        nome_moeda = par.split('-')[0]
        preco_usdt = buscar_preco_cripto_okx(par)
        
        if preco_usdt:
            # 3. calcular e converter
            # multiplica o preço da cripto em dólar pelo preço do dólar em reais
            cripto_data[f"{nome_moeda}_brl"] = preco_usdt * preco_usd
        else:
            # informa que a busca para essa cripto específica falhou
            cripto_data[f"{nome_moeda}_brl"] = None 

    # 4. formatar e devolver
    resultado_final = {
        "USD_BRL": preco_usd,
        "EUR_BRL": preco_eur,
        **cripto_data, # um truque do python para juntar os dicionários
        "ultima_atualizacao": datetime.now()
    }
    
    return resultado_final


# 2. lógica da calculadora (a parte nova)

# funções auxiliares (buscar cdi e ipca)

def buscar_taxa_cdi_anual():
    """ busca a taxa cdi diária no bcb e converte para anual. """
    try:
        response = requests.get(URL_BCB_CDI)
        data = response.json()
        # o bcb retorna o valor diário (ex: 0.040995)
        taxa_diaria = float(data[0]['valor']) / 100 
        # convertendo para anual (aprox. 252 dias úteis)
        # fórmula: (1 + taxa_diária) ** 252 - 1
        taxa_anual = ((1 + taxa_diaria) ** 252) - 1
        return taxa_anual # retorna (ex: 0.1099 -> 10.99% a.a.)
    except Exception as e:
        print(f"erro ao buscar cdi: {e}")
        # se o bcb falhar, a gente usa um valor "padrão" (ex: selic atual)
        # é uma boa prática não deixar a api quebrar por uma falha externa
        return 0.105 # 10.5% (valor de fallback)

def buscar_taxa_ipca_anual():
    """ busca o ipca acumulado dos últimos 12 meses no bcb. """
    try:
        response = requests.get(URL_BCB_IPCA)
        data = response.json()
        # o bcb retorna o % (ex: 4.61)
        taxa_anual = float(data[0]['valor']) / 100
        return taxa_anual # retorna (ex: 0.0461 -> 4.61% a.a.)
    except Exception as e:
        print(f"erro ao buscar ipca: {e}")
        return 0.045 # 4.5% (valor de fallback)


# modelos de dados (validação com pydantic)

# o que esperamos receber do frontend (input)
class SimulacaoInput(BaseModel):
    tipo_investimento: str # "cdb", "lci_lca", "tesouro"
    tipo_rentabilidade: str # "pre", "pos", "ipca"
    valor_inicial: float
    valor_mensal: float
    prazo: int
    prazo_unidade: str # "anos", "meses"
    rentabilidade_bruta: float # a taxa % que o user digitou

# um item da lista do gráfico de evolução
class PontoGrafico(BaseModel):
    mes: int
    valor: float

# o que vamos devolver para o frontend (output)
class SimulacaoOutput(BaseModel):
    valor_total_investido: float
    montante_bruto: float
    total_juros_bruto: float
    aliquota_ir_percentual: float
    valor_imposto_renda: float
    montante_liquido: float
    juros_liquido: float
    grafico_evolucao: List[PontoGrafico]
    taxa_cdi_usada_anual: Optional[float] = None
    taxa_ipca_usada_anual: Optional[float] = None
    taxa_efetiva_usada_anual: float
    
# endpoint da calculadora

@app.post("/simular/investimento", response_model=SimulacaoOutput)
def post_simular_investimento(dados_input: SimulacaoInput):
    """
    endpoint que recebe os dados do formulário e calcula a simulação.
    """
    print(f"recebida simulação: {dados_input}")

    # tarefa 3.1: padronizar os dados
    if dados_input.prazo_unidade.upper() == "ANOS":
        total_meses = dados_input.prazo * 12
    else:
        total_meses = dados_input.prazo
    
    # usamos uma média de dias no mês para a tabela do ir
    total_dias = total_meses * (365.25 / 12) 
    
    # tarefa 3.2: buscar taxas externas e definir taxa efetiva
    taxa_cdi_anual = 0.0
    taxa_ipca_anual = 0.0
    taxa_efetiva_anual = 0.0

    # rentabilidade_bruta (ex: 110%) vira rentabilidade_decimal (ex: 1.10)
    # ou (ex: 10%) vira (ex: 0.10)
    rentabilidade_decimal = dados_input.rentabilidade_bruta / 100

    if dados_input.tipo_rentabilidade.upper() == "POS":
        taxa_cdi_anual = buscar_taxa_cdi_anual()
        # ex: cdi (10.5%) * 110% = 0.105 * 1.10
        taxa_efetiva_anual = taxa_cdi_anual * rentabilidade_decimal
    
    elif dados_input.tipo_rentabilidade.upper() == "IPCA":
        taxa_ipca_anual = buscar_taxa_ipca_anual()
        # juros compostos (1 + inflação) * (1 + taxa_extra) - 1
        # ex: (1 + 0.045) * (1 + 0.06) - 1
        taxa_efetiva_anual = (1 + taxa_ipca_anual) * (1 + rentabilidade_decimal) - 1
    
    else: # "pre"
        # ex: 10%
        taxa_efetiva_anual = rentabilidade_decimal

    # tarefa 3.3: converter taxa anual para mensal
    # fórmula correta de juros compostos: (1 + taxa_anual) ** (1/12) - 1
    taxa_efetiva_mensal = (1 + taxa_efetiva_anual) ** (1/12) - 1

    # tarefa 3.4: calcular juros compostos (o "cálculo principal")
    montante_atual = dados_input.valor_inicial
    grafico_evolucao = []
    # adiciona o ponto inicial (mês 0)
    grafico_evolucao.append(PontoGrafico(mes=0, valor=round(montante_atual, 2)))

    # loop de 1 até o último mês
    for mes in range(1, total_meses + 1):
    
        # esta é a ordem correta que corrigimos
        # primeiro, aplica os juros sobre o saldo do mês anterior
        montante_atual *= (1 + taxa_efetiva_mensal)
        # depois, adiciona o aporte deste mês (só vai render no próximo mês)
        montante_atual += dados_input.valor_mensal
            
        # guarda o ponto no gráfico (arredondado)
        grafico_evolucao.append(PontoGrafico(mes=mes, valor=round(montante_atual, 2)))
    
    # !! esta linha deve ficar fora do loop !!
    montante_bruto = montante_atual

    # tarefa 3.5: calcular totais e impostos (ir)
    valor_total_investido = dados_input.valor_inicial + (dados_input.valor_mensal * total_meses)
    lucro_bruto = montante_bruto - valor_total_investido
    
    imposto_a_pagar = 0.0
    aliquota_ir = 0.0
    
    # lci/lca são isentas de imposto
    investimento_tributavel = dados_input.tipo_investimento.upper() in ["CDB", "TESOURO"]

    # só calcula imposto se for tributável e se tiver tido lucro
    if investimento_tributavel and lucro_bruto > 0:
        if total_dias <= 180:
            aliquota_ir = 0.225 # 22.5%
        elif total_dias <= 360:
            aliquota_ir = 0.200 # 20.0%
        elif total_dias <= 720:
            aliquota_ir = 0.175 # 17.5%
        else: # acima de 720 dias
            aliquota_ir = 0.150 # 15.0%
            
        imposto_a_pagar = lucro_bruto * aliquota_ir

    # tarefa 3.6: montar a resposta final
    montante_liquido = montante_bruto - imposto_a_pagar
    juros_liquido = lucro_bruto - imposto_a_pagar

    # criamos o objeto de resposta (validado pelo pydantic)
    resposta = SimulacaoOutput(
        valor_total_investido=round(valor_total_investido, 2),
        montante_bruto=round(montante_bruto, 2),
        total_juros_bruto=round(lucro_bruto, 2),
        aliquota_ir_percentual=aliquota_ir * 100,
        valor_imposto_renda=round(imposto_a_pagar, 2),
        montante_liquido=round(montante_liquido, 2),
        juros_liquido=round(juros_liquido, 2),
        grafico_evolucao=grafico_evolucao,
        taxa_cdi_usada_anual=taxa_cdi_anual if taxa_cdi_anual > 0 else None,
        taxa_ipca_usada_anual=taxa_ipca_anual if taxa_ipca_anual > 0 else None,
        taxa_efetiva_usada_anual=taxa_efetiva_anual
    )
    
    return resposta

# comando para rodar (ver documentação)
# no terminal, execute:
# python -m uvicorn main:app --reload