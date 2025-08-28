import pandas as pd

df = pd.read_csv("extratoteste.csv")

# Troca vírgula por ponto e converte para float
df["Valor"] = df["Valor"].astype(str)  # garante que está em string
df["Valor"] = df["Valor"].str.replace(",", ".", regex=False).astype(float)

print(df)
print("Soma total:", df["Valor"].sum())
