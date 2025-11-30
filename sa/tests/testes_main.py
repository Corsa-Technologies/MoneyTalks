import math
import types
from fastapi.testclient import TestClient
import pytest

# Importa o app e funções do módulo principal
from sa import main

client = TestClient(main.app)

# =====================
# Helpers / Fixtures
# =====================
class FakeResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
    def json(self):
        return self._json

@pytest.fixture
def mock_requests_get(monkeypatch):
    """Permite configurar respostas diferentes por URL dentro do teste."""
    calls = {}

    def _register(url, response: FakeResponse):
        calls[url] = response

    def _fake_get(url, params=None):
        # monta chave de busca simples (ignora params aqui exceto OKX)
        if url == main.URL_OKX_TICKER and params:
            # diferenciando por instId para permitir múltiplos pares
            key = f"{url}?{params.get('instId')}"
            return calls.get(key, FakeResponse(status_code=404))
        return calls.get(url, FakeResponse(status_code=404))

    monkeypatch.setattr(main.requests, 'get', _fake_get)
    return _register

# =====================
# Testes: buscar_dados_forex
# =====================
def test_buscar_dados_forex_sucesso(mock_requests_get):
    mock_requests_get(main.URL_FOREX, FakeResponse(json_data={
        'USDBRL': {'bid': '4.95'},
        'EURBRL': {'bid': '5.40'}
    }))
    usd, eur = main.buscar_dados_forex()
    assert usd == pytest.approx(4.95)
    assert eur == pytest.approx(5.40)


def test_buscar_dados_forex_status_falha(mock_requests_get):
    mock_requests_get(main.URL_FOREX, FakeResponse(status_code=500))
    usd, eur = main.buscar_dados_forex()
    assert usd is None and eur is None


def test_buscar_dados_forex_excecao(monkeypatch):
    def _boom(url):
        raise RuntimeError('falha rede')
    monkeypatch.setattr(main.requests, 'get', _boom)
    usd, eur = main.buscar_dados_forex()
    assert usd is None and eur is None

# =====================
# Testes: buscar_preco_cripto_okx
# =====================
def test_buscar_preco_cripto_okx_sucesso(mock_requests_get):
    mock_requests_get(f"{main.URL_OKX_TICKER}?BTC-USDT", FakeResponse(json_data={
        'code': '0', 'data': [{'last': '52000'}]
    }))
    preco = main.buscar_preco_cripto_okx('BTC-USDT')
    assert preco == pytest.approx(52000.0)


def test_buscar_preco_cripto_okx_code_invalido(mock_requests_get):
    mock_requests_get(f"{main.URL_OKX_TICKER}?BTC-USDT", FakeResponse(json_data={
        'code': '1', 'msg': 'erro'
    }))
    preco = main.buscar_preco_cripto_okx('BTC-USDT')
    assert preco is None


def test_buscar_preco_cripto_okx_status_falha(mock_requests_get):
    mock_requests_get(f"{main.URL_OKX_TICKER}?BTC-USDT", FakeResponse(status_code=404))
    preco = main.buscar_preco_cripto_okx('BTC-USDT')
    assert preco is None


def test_buscar_preco_cripto_okx_excecao(monkeypatch):
    def _boom(url, params=None):
        raise ValueError('timeout')
    monkeypatch.setattr(main.requests, 'get', _boom)
    preco = main.buscar_preco_cripto_okx('BTC-USDT')
    assert preco is None

# =====================
# Teste endpoint /cotacoes/atuais
# =====================
def test_get_cotacoes_atuais_sucesso(mock_requests_get):
    # Forex
    mock_requests_get(main.URL_FOREX, FakeResponse(json_data={
        'USDBRL': {'bid': '5.00'},
        'EURBRL': {'bid': '5.30'}
    }))
    # Criptos
    mock_requests_get(f"{main.URL_OKX_TICKER}?BTC-USDT", FakeResponse(json_data={'code': '0', 'data': [{'last': '50000'}]}))
    mock_requests_get(f"{main.URL_OKX_TICKER}?ETH-USDT", FakeResponse(json_data={'code': '0', 'data': [{'last': '3000'}]}))
    mock_requests_get(f"{main.URL_OKX_TICKER}?SOL-USDT", FakeResponse(json_data={'code': '0', 'data': [{'last': '50'}]}))

    r = client.get('/cotacoes/atuais')
    assert r.status_code == 200
    data = r.json()
    assert data['USD_BRL'] == pytest.approx(5.00)
    assert data['EUR_BRL'] == pytest.approx(5.30)
    # Conversões
    assert data['BTC_brl'] == pytest.approx(50000 * 5.00)
    assert data['ETH_brl'] == pytest.approx(3000 * 5.00)
    assert data['SOL_brl'] == pytest.approx(50 * 5.00)


def test_get_cotacoes_atuais_falha_forex(mock_requests_get):
    mock_requests_get(main.URL_FOREX, FakeResponse(status_code=503))
    r = client.get('/cotacoes/atuais')
    assert r.status_code == 503


def test_get_cotacoes_atuais_falha_crypto_um_par(mock_requests_get):
    mock_requests_get(main.URL_FOREX, FakeResponse(json_data={
        'USDBRL': {'bid': '5.00'},
        'EURBRL': {'bid': '5.30'}
    }))
    # Só BTC falha -> others ok
    mock_requests_get(f"{main.URL_OKX_TICKER}?BTC-USDT", FakeResponse(status_code=500))
    mock_requests_get(f"{main.URL_OKX_TICKER}?ETH-USDT", FakeResponse(json_data={'code': '0', 'data': [{'last': '3000'}]}))
    mock_requests_get(f"{main.URL_OKX_TICKER}?SOL-USDT", FakeResponse(json_data={'code': '0', 'data': [{'last': '50'}]}))
    r = client.get('/cotacoes/atuais')
    assert r.status_code == 200
    data = r.json()
    assert data['BTC_brl'] is None
    assert data['ETH_brl'] == pytest.approx(3000 * 5.00)

# =====================
# Testes: taxas externas (cdi / ipca)
# =====================
def test_buscar_taxa_cdi_anual_sucesso(monkeypatch):
    # taxa diária retornada pelo BCB vem como percentual (ex: 0.040995) -> dividir por 100 depois
    def _fake_get(url):
        return FakeResponse(json_data=[{'valor': '0.040995'}])
    monkeypatch.setattr(main.requests, 'get', _fake_get)
    anual = main.buscar_taxa_cdi_anual()
    esperado = ((1 + (0.040995/100)) ** 252) - 1
    assert anual == pytest.approx(esperado)


def test_buscar_taxa_cdi_anual_fallback(monkeypatch):
    def _boom(url):
        raise RuntimeError('erro')
    monkeypatch.setattr(main.requests, 'get', _boom)
    anual = main.buscar_taxa_cdi_anual()
    assert anual == pytest.approx(0.105)


def test_buscar_taxa_ipca_anual_sucesso(monkeypatch):
    def _fake_get(url):
        return FakeResponse(json_data=[{'valor': '4.61'}])
    monkeypatch.setattr(main.requests, 'get', _fake_get)
    anual = main.buscar_taxa_ipca_anual()
    assert anual == pytest.approx(0.0461)


def test_buscar_taxa_ipca_anual_fallback(monkeypatch):
    def _boom(url):
        raise ValueError('falha')
    monkeypatch.setattr(main.requests, 'get', _boom)
    anual = main.buscar_taxa_ipca_anual()
    assert anual == pytest.approx(0.045)

# =====================
# Testes: simulador de investimento
# =====================
SIM_ENDPOINT = "/simular/investimento"


def test_simulacao_pre_sem_imposto():
    payload = {
        "tipo_investimento": "LCI_LCA",  # isento
        "tipo_rentabilidade": "PRE",
        "valor_inicial": 1000.0,
        "valor_mensal": 0.0,
        "prazo": 12,
        "prazo_unidade": "meses",
        "rentabilidade_bruta": 12.0  # 12% a.a.
    }
    r = client.post(SIM_ENDPOINT, json=payload)
    assert r.status_code == 200
    data = r.json()
    # Montante anual: 1000 * (1+0.12) = 1120 (aprox juros compostos mensais -> ligeira diferença)
    assert data['valor_total_investido'] == 1000.0
    assert data['valor_imposto_renda'] == 0.0
    assert data['taxa_efetiva_usada_anual'] == pytest.approx(0.12)


def test_simulacao_pos_com_cdi(monkeypatch):
    # força taxa CDI
    monkeypatch.setattr(main, 'buscar_taxa_cdi_anual', lambda: 0.10)  # 10% a.a.
    payload = {
        "tipo_investimento": "CDB",
        "tipo_rentabilidade": "POS",
        "valor_inicial": 1000.0,
        "valor_mensal": 100.0,
        "prazo": 12,
        "prazo_unidade": "meses",
        "rentabilidade_bruta": 110.0  # 110% do CDI => 0.10 * 1.10 = 0.11
    }
    r = client.post(SIM_ENDPOINT, json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data['taxa_cdi_usada_anual'] == pytest.approx(0.10)
    assert data['taxa_efetiva_usada_anual'] == pytest.approx(0.11)
    # imposto > 0 porque é CDB e há lucro
    assert data['valor_imposto_renda'] >= 0


def test_simulacao_ipca(monkeypatch):
    monkeypatch.setattr(main, 'buscar_taxa_ipca_anual', lambda: 0.04)  # 4% inflação
    payload = {
        "tipo_investimento": "TESOURO",
        "tipo_rentabilidade": "IPCA",
        "valor_inicial": 5000.0,
        "valor_mensal": 0.0,
        "prazo": 2,
        "prazo_unidade": "anos",
        "rentabilidade_bruta": 6.0  # +6% real
    }
    r = client.post(SIM_ENDPOINT, json=payload)
    assert r.status_code == 200
    data = r.json()
    # taxa efetiva = (1+0.04)*(1+0.06)-1 = 0.1024
    assert data['taxa_ipca_usada_anual'] == pytest.approx(0.04)
    assert data['taxa_efetiva_usada_anual'] == pytest.approx((1+0.04)*(1+0.06)-1)


def test_simulacao_tabela_ir_ate_180_dias(monkeypatch):
    monkeypatch.setattr(main, 'buscar_taxa_cdi_anual', lambda: 0.10)
    payload = {
        "tipo_investimento": "CDB",
        "tipo_rentabilidade": "POS",
        "valor_inicial": 1000.0,
        "valor_mensal": 0.0,
        "prazo": 5,  # 5 meses ~ <=180 dias
        "prazo_unidade": "meses",
        "rentabilidade_bruta": 110.0
    }
    r = client.post(SIM_ENDPOINT, json=payload)
    assert r.status_code == 200
    data = r.json()
    # alíquota esperada 22.5%
    assert data['aliquota_ir_percentual'] == pytest.approx(22.5)


def test_simulacao_tabela_ir_acima_720_dias(monkeypatch):
    monkeypatch.setattr(main, 'buscar_taxa_cdi_anual', lambda: 0.10)
    payload = {
        "tipo_investimento": "CDB",
        "tipo_rentabilidade": "POS",
        "valor_inicial": 1000.0,
        "valor_mensal": 0.0,
        "prazo": 3,  # 3 anos -> > 720 dias
        "prazo_unidade": "anos",
        "rentabilidade_bruta": 110.0
    }
    r = client.post(SIM_ENDPOINT, json=payload)
    assert r.status_code == 200
    data = r.json()
    # alíquota esperada 15.0%
    assert data['aliquota_ir_percentual'] == pytest.approx(15.0)

# Nota: Arquivo chamado testes_main.py (underscore) porque hífen impediria import / coleta.
