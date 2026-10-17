import pandas as pd
from data_profiler import profile_dataset

df = pd.read_csv("data/sample.csv")

result = profile_dataset(df)

print(result)