#!python3

import json
import requests
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

CBS_BASE_URL = 'https://opendata.cbs.nl/ODataApi/odata/'
TABLE_ID = '80072ned'
TABLE_PATH = Path(f'data/{TABLE_ID}')


def get_cbs_url(part: str or None = None):
    if part is None:
        return f'{CBS_BASE_URL}{TABLE_ID}'

    return f'{CBS_BASE_URL}{TABLE_ID}/{part}'


def get_data_frame(url: str) -> pd.DataFrame:
    return pd.DataFrame([value for value in requests.get(url).json()['value']])


def get_dict(url: str) -> dict:
    return requests.get(url).json()['value'][0]


def get_df_value(
        df: pd.DataFrame,
        select_column: str,
        select_value: str,
        get_column: str) -> str:
    return df[df[select_column] == select_value][get_column].values[0]


def get_url_value(df: pd.DataFrame, name: str) -> str:
    return get_df_value(df=df, select_column='name', select_value=name, get_column='url')


def main():
    table_infos = {}
    if TABLE_PATH.is_dir():
        logging.info(f'Table path: {TABLE_PATH} exists')
        table_infos_file = Path(TABLE_PATH / f'{TABLE_ID}_TableInfos.json')
        try:
            with open(table_infos_file, 'rb') as f:
                table_infos = json.load(f)
        except FileNotFoundError:
            logging.error(f'TableInfos file not found: {table_infos_file}')
            exit(1)
        except OSError as e:
            raise e

        logging.info(f'Checking if {table_infos["Modified"]} has changed')
        table_base = pd.read_csv(TABLE_PATH / f'{TABLE_ID}.csv')
        table_infos_new = get_dict(get_url_value(table_base, 'TableInfos'))
        if table_infos['Modified'] != table_infos_new['Modified']:
            logging.info(f'Table infos indicatie modification: {table_infos_new["Modified"]}')
            logging.info(f'Reason for modification: {table_infos_new["ReasonDelivery"]}')
            logging.info(f'Please archive folder {TABLE_PATH} to proceed')
            exit(1)
        else:
            logging.info(f'Local {table_infos["Modified"]} == {table_infos_new["Modified"]} Remotely')
            logging.info(f'TableInfos Modified value has NOT changed, we are done')
            exit(0)
    else:
        logging.info(f'Table path: {TABLE_PATH} does not exist, creating it now')
        TABLE_PATH.mkdir(parents=True, exist_ok=True)

    logging.info('Getting table base for %s' % TABLE_ID)
    table_base = get_data_frame(f'{CBS_BASE_URL}/{TABLE_ID}')
    table_base.to_csv(f'{TABLE_PATH}/{TABLE_ID}.csv', index=False)

    for _, row in table_base.iterrows():
        logging.info(f'Getting %s for %s' % (row['name'], row['url']))

        if row['name'] == 'TableInfos':
            table = get_dict(row['url'])
            with open(TABLE_PATH / f'{TABLE_ID}_{row["name"]}.json', 'w') as j:
                json.dump(table, j)
        else:
            table = get_data_frame(row['url'])
            table.to_csv(f'{TABLE_PATH}/{TABLE_ID}_{row["name"]}.csv', index=False)


if __name__ == '__main__':
    main()
