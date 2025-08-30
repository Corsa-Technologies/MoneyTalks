import pandas as pd

# -----------------------------
# Funções principais
# -----------------------------

def carregar_extrato(caminho_csv: str) -> pd.DataFrame:
    """Carrega o extrato de um CSV e garante tipos numéricos."""
    df = pd.read_csv(caminho_csv)
    df["Valor"] = df["Valor"].astype(float)
    df["Saldo"] = df["Saldo"].astype(float)
    return df


def calcular_resumo(df: pd.DataFrame) -> dict:
    """Calcula receitas, gastos e saldo final."""
    receitas = df.loc[df["Valor"] > 0, "Valor"].sum()
    gastos = df.loc[df["Valor"] < 0, "Valor"].sum()
    saldo_final = df["Saldo"].iloc[-1]

    return {
        "receitas": receitas,
        "gastos": gastos,
        "saldo_final": saldo_final
    }


def adicionar_movimentacao(df: pd.DataFrame, data: str, descricao: str, valor: float) -> pd.DataFrame:
    """Adiciona uma nova movimentação ao extrato."""
    saldo_atual = df["Saldo"].iloc[-1]
    novo_saldo = saldo_atual + valor

    nova_linha = {
        "Data": data,
        "Descrição": descricao,
        "Valor": valor,
        "Saldo": novo_saldo
    }

    df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    return df


def salvar_extrato(df: pd.DataFrame, caminho_csv: str):
    """Salva o extrato atualizado no CSV."""
    df.to_csv(caminho_csv, index=False)


# -----------------------------
# Exemplo de uso (teste local)
# -----------------------------
if __name__ == "__main__":
    caminho = "extratoteste.csv"

    # Carregar
    df = carregar_extrato(caminho)

    # Mostrar resumo
    resumo = calcular_resumo(df)
    print("Receitas:", resumo["receitas"])
    print("Gastos:", resumo["gastos"])
    print("Saldo final:", resumo["saldo_final"])

    # Adicionar movimentação
    df = adicionar_movimentacao(df, "05/08/2025", "Lanche", -35)

    # Salvar
    salvar_extrato(df, caminho)
    print("Nova movimentação adicionada com sucesso!")
