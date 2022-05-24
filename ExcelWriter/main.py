import argparse
from xlsxwriter import Workbook, workbook, worksheet
import pandas as pd
from public_method import (
    get_all_commits,
)


parser = argparse.ArgumentParser(description='hub-trend')
parser.add_argument('org', help='조직')
parser.add_argument('repo', help='저장소')
parser.add_argument('since', help='시작일')
parser.add_argument('until', help='종료일')

#args = parser.parse_args()

NoneType = type(None)

def dev_view(parent_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cms = parent_df.groupby(by=['name', 'branch'])['sha'].count().reset_index()
    aoc = parent_df.groupby(by=['name', 'branch'])['amount_of_changes'].sum().reset_index()
    adds = parent_df.groupby(by=['name', 'branch'])['additions'].sum().reset_index()

    cms_pivot = cms.pivot(columns='branch', index='name', values='sha').fillna(0)
    aoc_pivot = aoc.pivot(columns='branch', index='name', values='amount_of_changes').fillna(0)
    adds_pivot = adds.pivot(columns='branch', index='name', values='additions').fillna(0)

    cms_pivot['total'] = cms_pivot.sum(axis=1)
    aoc_pivot['total'] = aoc_pivot.sum(axis=1)
    adds_pivot['total'] = adds_pivot.sum(axis=1)

    return (cms_pivot, aoc_pivot, adds_pivot)

def dev_view_to_excel(writer: pd.ExcelWriter, *dfs: tuple[pd.DataFrame]) -> NoneType:
    interval = 1
    previous_df_rowlen = 0
    previous_df_collen = 0

    for i, df in enumerate(dfs):
        if i > 0:
            if interval != 1: 
                previous_df_rowlen = previous_df_rowlen + interval + dfs[i].shape[0]
                previous_df_collen = previous_df_collen + interval + dfs[i].shape[1]
            df.to_excel(writer, 'developer', startrow=previous_df_rowlen, startcol=previous_df_collen)


def main(org: str, repo: str, since: str, until: str):
    raw_df: pd.DataFrame = get_all_commits(org, repo, since, until)
    writer = pd.ExcelWriter(path=f'{org}_{repo}_{since}_{until}.xlsx', engine='xlsxwriter')

    book: Workbook = writer.book
    chartssheet = book.add_worksheet('charts')

    dev_view_to_excel(writer, *dev_view(raw_df))
    cm_line_df = raw_df.groupby(by=['branch', 'weeknum'])['sha'].count().reset_index()
    cm_line_pivot_df = cm_line_df.pivot(index='weeknum', columns='branch', values='sha').fillna(0)
    cm_line_pivot_df.to_excel(writer, sheet_name='branch_cm')

    aoc_line_df = raw_df.groupby(by=['branch', 'weeknum'])['amount_of_changes'].sum().reset_index()
    aoc_line_pivot_df = aoc_line_df.pivot(index='weeknum', columns='branch', values='amount_of_changes').fillna(0)
    aoc_line_pivot_df.to_excel(writer, sheet_name='branch_aoc')

    cm_line_cht: workbook.ChartLine = book.add_chart({'type':'line'})
    cm_line_cht.add_series({
        'name': 'test',
        'values': ['branch_cm', 1, 1, 6, 1], # col row col row
        'categories': ['branch_cm', 1, 0, 6, 0],
        'data_labels': {'value': True},
        'marker'    : {
            'type'   : 'square',
            'size'   : 8,
            'border' : {'color':'black'},
            'fill' : {'color': 'red'},
        },
    })

    chartssheet.insert_chart('A1', chart=cm_line_cht)

    print(cm_line_pivot_df)
    print(aoc_line_pivot_df)

    raw_df.to_excel(writer, sheet_name='raw_data')
    writer.close()



main('ajou-assignment', 'seat-assignment', '2021-11-01', '2021-12-31')

    
    