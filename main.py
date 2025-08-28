import pandas as pd

# --- Base existente ---
df = pd.read_csv("extratoteste.csv")
df["Valor"] = df["Valor"].astype(float)
df["Saldo"] = df["Saldo"].astype(float)

# --- Função para adicionar movimentação ---
def adicionar_movimentacao(df, data, descricao, valor):
    """
    Adiciona uma nova movimentação ao DataFrame e atualiza o saldo.
    
    Parâmetros:
    - df: DataFrame do extrato
    - data: string no formato 'DD/MM/AAAA'
    - descricao: descrição da movimentação
    - valor: valor positivo ou negativo
    
    Retorna:
    - df atualizado
    - saldo final após a movimentação
    """
    saldo_atual = df["Saldo"].iloc[-1]  # pega saldo final atual
    saldo_novo = saldo_atual + valor
    
    nova_linha = {
        "Data": data,
        "Descrição": descricao,
        "Valor": valor,
        "Saldo": saldo_novo
    }
    
    df_atualizado = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    return df_atualizado, saldo_novo

# --- Exemplo de uso ---
df, saldo_final = adicionar_movimentacao(df, "05/08/2025", "Padaria", -30)
df, saldo_final = adicionar_movimentacao(df, "05/08/2025", "Transferência recebida", 200)

# --- Estatísticas atualizadas ---
gastos = df.loc[df["Valor"] < 0, "Valor"].sum()
receitas = df.loc[df["Valor"] > 0, "Valor"].sum()

print("Receitas:", receitas)
print("Gastos:", gastos)
print("Saldo final do extrato:", saldo_final)
print("\nExtrato atualizado:")
print(df)
