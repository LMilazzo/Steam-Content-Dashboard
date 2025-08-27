
import os
import pandas as pd


with open('Project/datasets/steam.csv', 'r', encoding='utf-8') as file:

    df = pd.read_csv(file)

    df = df[['appid', 'name']]

    with open('appIdList.json', 'w', encoding='utf-8') as json_file:
        df.to_json(json_file, orient='records', lines=False)