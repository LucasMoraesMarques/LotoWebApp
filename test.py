import pandas as pd
df = pd.read_csv('todosjogosloto.csv', header=None)
df['sum'] = df.sum(axis=1)
print(df.sort_values(by='sum').head())