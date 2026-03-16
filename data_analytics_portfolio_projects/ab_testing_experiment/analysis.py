import pandas as pd

df = pd.read_csv("ab_test_data.csv")

conversion_rate = df.groupby("variant")["converted"].mean()

print("Conversion Rate:")
print(conversion_rate)

uplift = conversion_rate["B"] - conversion_rate["A"]

print("Conversion uplift:", uplift)
