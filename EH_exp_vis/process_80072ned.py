#!python3

import logging
from pathlib import Path
import pandas as pd


TABLE_ID = '80072ned'
TABLE_PATH = Path(f'./data/{TABLE_ID}')

logging.basicConfig(level=logging.INFO)


def main():

    logging.info("Merge SBI df with groups and keep group title only")
    sbi: pd.DataFrame = pd.read_csv(TABLE_PATH / f'{TABLE_ID}_BedrijfskenmerkenSBI2008.csv',sep=',')
    cat_groups: pd.DataFrame = pd.read_csv(TABLE_PATH / f'{TABLE_ID}_CategoryGroups.csv', sep=',')

    sbi_cat_groups = pd.merge(
        left=sbi,
        right=cat_groups,
        left_on='CategoryGroupID',
        right_on='ID',
        how='left',
        suffixes=(None, "_cat_group")
    ).drop(
        ['DimensionKey', 'Description_cat_group', 'ParentID', 'ID'],
        axis='columns'
    ).rename(columns={
        'CategoryGroupID': 'category_group_id',
        'Title_cat_group': 'category_group_title',
    })

    logging.info("Processing period key format into separate columns")
    # The periods table describes the periods
    # the period key is yyyy(KW|JJ)qq
    # yyyy is the year
    # KW indicates it is a quarter : qq is the quarter number
    # JJ indicates it is a year : qq is equal to 00
    # split the period key into separate columns for easy slicing further down the line
    periods: pd.DataFrame = pd.read_csv(TABLE_PATH / f'{TABLE_ID}_Perioden.csv', sep=',')
    periods[['period_year', 'period_type', 'period_quarter_number']] = periods['Key'].str.extract(r'(\d+)(KW|JJ)(\d+)',
                                                                                                  expand=True)
    periods['period_year'] = periods['period_year'].astype(int)
    periods['period_quarter_number'] = periods['period_quarter_number'].astype(int)
    periods['period_quarter'] = periods.apply(lambda row: row['period_year'] * 10 + row['period_quarter_number'],
                                              axis=1)

    logging.info("Merge sick_leave_percentage with periods and keep period status and description and calculated fields")
    sick_leave_percentage: pd.DataFrame = pd.read_csv(TABLE_PATH / f'{TABLE_ID}_UntypedDataSet.csv',
                                                      sep=',',
                                                      na_values='       .'
                                                      )

    slp_periods = pd.merge(
        left=sick_leave_percentage,
        right=periods,
        left_on='Perioden',
        right_on='Key',
        how='left',
        suffixes=(None, "_periods")
    ).drop(
        labels=['Key', 'Description'],
        axis='columns'
    ).rename(columns={'Title': 'period_title', 'Status': 'period_status'})

    logging.info("Merge slp_periods with sbi information")
    slp_periods_sbi = pd.merge(
        left=slp_periods,
        right=sbi_cat_groups,
        left_on='BedrijfskenmerkenSBI2008',
        right_on='Key',
        how='left',
        suffixes=(None, "_sbi")
    ).drop(
        labels=['Key'],
        axis='columns'
    ).rename(columns={'Title': 'sbi_title', 'Description': 'sbi_description'})

    logging.info("Converting column names to uniform column")
    slp_periods_sbi = slp_periods_sbi.rename(columns={
        'ID': 'id',
        'BedrijfskenmerkenSBI2008': 'sbi',
        'Perioden': 'period',
        'Ziekteverzuimpercentage_1': 'sick_leave_percentage',
    })

    # Convert columns to categorical
    categorical_columns = ['sbi', 'period', 'period_title', 'period_status', 'period_type',
                           'sbi_title', 'sbi_description', 'category_group_title']

    for column in categorical_columns:
        slp_periods_sbi[column] = slp_periods_sbi[column].astype('category')

    if logging.INFO >= logging.root.level:
        slp_periods_sbi.info()

    parquet_file = TABLE_PATH / f'{TABLE_ID}.parquet'
    if parquet_file.exists():
        logging.error("%s already exists, not writing output" % parquet_file)
    else:
        slp_periods_sbi.to_parquet(parquet_file)
        logging.info("%s has been saved" % parquet_file)


if __name__ == '__main__':
    main()
