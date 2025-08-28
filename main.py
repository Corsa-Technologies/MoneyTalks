import pandas as pd

# --- Lê o CSV existente ---
df = pd.read_csv("extratoteste.csv")
df["Valor"] = df["Valor"].astype(float)
df["Saldo"] = df["Saldo"].astype(float)

# --- Função para adicionar movimentação ---
def adicionar_movimentacao(df, data, descricao, valor, arquivo_csv):
    saldo_atual = df["Saldo"].iloc[-1]
    saldo_novo = saldo_atual + valor
    nova_linha = {"Data": data, "Descrição": descricao, "Valor": valor, "Saldo": saldo_novo}
    
    df_atualizado = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    
    # Sobrescreve o CSV original
    df_atualizado.to_csv(arquivo_csv, index=False)
    
    return df_atualizado, saldo_novo

# --- Exemplo de uso ---
df, saldo_final = adicionar_movimentacao(df, "05/08/2025", "Padaria", -30, "extratoteste.csv")
df, saldo_final = adicionar_movimentacao(df, "05/08/2025", "Transferência recebida", 200, "extratoteste.csv")

# --- Estatísticas ---
gastos = df.loc[df["Valor"] < 0, "Valor"].sum()
receitas = df.loc[df["Valor"] > 0, "Valor"].sum()

print("Receitas:", receitas)
print("Gastos:", gastos)
print("Saldo final do extrato:", saldo_final)
print(df)
