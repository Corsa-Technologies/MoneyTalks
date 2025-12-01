from fastapi.testclient import TestClient
import pytest

from sa import main
from testes_main import (
    FakeResponse,
    mock_requests_get,  # fixture reutilizada
)

client = TestClient(main.app)

# Reexporta testes principais para garantir coleta pelo pytest e reune em um arquivo

def test_buscar_dados_forex_sucesso_wrapper(mock_requests_get):
    from testes_main import test_buscar_dados_forex_sucesso as orig
    orig(mock_requests_get)

def test_buscar_dados_forex_status_falha_wrapper(mock_requests_get):
    from testes_main import test_buscar_dados_forex_status_falha as orig
    orig(mock_requests_get)

def test_buscar_dados_forex_excecao_wrapper(monkeypatch):
    from testes_main import test_buscar_dados_forex_excecao as orig
    orig(monkeypatch)

def test_buscar_preco_cripto_okx_sucesso_wrapper(mock_requests_get):
    from testes_main import test_buscar_preco_cripto_okx_sucesso as orig
    orig(mock_requests_get)

def test_buscar_preco_cripto_okx_code_invalido_wrapper(mock_requests_get):
    from testes_main import test_buscar_preco_cripto_okx_code_invalido as orig
    orig(mock_requests_get)

def test_buscar_preco_cripto_okx_status_falha_wrapper(mock_requests_get):
    from testes_main import test_buscar_preco_cripto_okx_status_falha as orig
    orig(mock_requests_get)

def test_buscar_preco_cripto_okx_excecao_wrapper(monkeypatch):
    from testes_main import test_buscar_preco_cripto_okx_excecao as orig
    orig(monkeypatch)

def test_get_cotacoes_atuais_sucesso_wrapper(mock_requests_get):
    from testes_main import test_get_cotacoes_atuais_sucesso as orig
    orig(mock_requests_get)

def test_get_cotacoes_atuais_falha_forex_wrapper(mock_requests_get):
    from testes_main import test_get_cotacoes_atuais_falha_forex as orig
    orig(mock_requests_get)

def test_get_cotacoes_atuais_falha_crypto_um_par_wrapper(mock_requests_get):
    from testes_main import test_get_cotacoes_atuais_falha_crypto_um_par as orig
    orig(mock_requests_get)

def test_buscar_taxa_cdi_anual_sucesso_wrapper(monkeypatch):
    from testes_main import test_buscar_taxa_cdi_anual_sucesso as orig
    orig(monkeypatch)

def test_buscar_taxa_cdi_anual_fallback_wrapper(monkeypatch):
    from testes_main import test_buscar_taxa_cdi_anual_fallback as orig
    orig(monkeypatch)

def test_buscar_taxa_ipca_anual_sucesso_wrapper(monkeypatch):
    from testes_main import test_buscar_taxa_ipca_anual_sucesso as orig
    orig(monkeypatch)

def test_buscar_taxa_ipca_anual_fallback_wrapper(monkeypatch):
    from testes_main import test_buscar_taxa_ipca_anual_fallback as orig
    orig(monkeypatch)

def test_simulacao_pre_sem_imposto_wrapper():
    from testes_main import test_simulacao_pre_sem_imposto as orig
    orig()

def test_simulacao_pos_com_cdi_wrapper(monkeypatch):
    from testes_main import test_simulacao_pos_com_cdi as orig
    orig(monkeypatch)

def test_simulacao_ipca_wrapper(monkeypatch):
    from testes_main import test_simulacao_ipca as orig
    orig(monkeypatch)

def test_simulacao_tabela_ir_ate_180_dias_wrapper(monkeypatch):
    from testes_main import test_simulacao_tabela_ir_ate_180_dias as orig
    orig(monkeypatch)

def test_simulacao_tabela_ir_acima_720_dias_wrapper(monkeypatch):
    from testes_main import test_simulacao_tabela_ir_acima_720_dias as orig
    orig(monkeypatch)
