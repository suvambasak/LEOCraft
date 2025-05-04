
'''
This script extracts the flights that are currently in the air (above 10,000 feet)
'''

import pandas as pd

df = pd.read_csv('dataset/src/flights/dataset/flight_dataset.csv')
# Altitude is above 10,000 feets
df_on_air = df[df['alt'] > 10000]
df_on_air.to_csv(
    'dataset/src/flights/dataset/flight_on_air.csv', index=False
)
