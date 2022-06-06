import argparse, random
from xlsxwriter import Workbook, workbook
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


def make_line_chart(book: Workbook, df: pd.DataFrame, chartname: str, sheetname: str) -> workbook.ChartLine:
    chart: workbook.ChartLine = book.add_chart({'type':'line'})
    chart.set_title({'name':chartname})
    chart.set_style(random.randint(1, 20))

    row = df.shape[0]
    branches = df.columns.to_list()[0:]
    
    for branch in branches:
        chart.add_series({
            'name': branch,
            'values': [sheetname, 1, 1, row + 1, 1], # row col row col
            'categories': [sheetname, 1, 0, row + 1, 0],
            'data_labels': {'value': True},
        })
        """
        'marker'    : {
                'type'   : 'square',
                'size'   : 8,
                'border' : {'color':'black'},
                'fill' : {'color': 'red'},
            },
        """

    return chart


def main(org: str, repo: str, since: str, until: str):
    raw_df: pd.DataFrame = get_all_commits(org, repo, since, until)
    writer = pd.ExcelWriter(path=f'{org}_{repo}_{since}_{until}.xlsx', engine='xlsxwriter')
    book: Workbook = writer.book
    title = book.add_format({'bold': 1, 'font_size': 25})
    chartssheet = book.add_worksheet('charts')

    dev_view_to_excel(writer, *dev_view(raw_df))
    cm_line_df = raw_df.groupby(by=['branch', 'weeknum'])['sha'].count().reset_index()
    cm_line_pivot_df = cm_line_df.pivot(index='weeknum', columns='branch', values='sha').fillna(0)
    cm_line_pivot_df.to_excel(writer, sheet_name='branch_cm')

    adds_line_df = raw_df.groupby(by=['branch', 'weeknum'])['additions'].sum().reset_index()
    adds_line_pivot_df = adds_line_df.pivot(index='weeknum', columns='branch', values='additions').fillna(0)
    adds_line_pivot_df.to_excel(writer, sheet_name='branch_adds')

    dels_line_df = raw_df.groupby(by=['branch', 'weeknum'])['deletions'].sum().reset_index()
    dels_line_pivot_df = dels_line_df.pivot(index='weeknum', columns='branch', values='deletions').fillna(0)
    dels_line_pivot_df.to_excel(writer, sheet_name='branch_dels')

    aoc_line_df = raw_df.groupby(by=['branch', 'weeknum'])['amount_of_changes'].sum().reset_index()
    aoc_line_pivot_df = aoc_line_df.pivot(index='weeknum', columns='branch', values='amount_of_changes').fillna(0)
    aoc_line_pivot_df.to_excel(writer, sheet_name='branch_aoc')

    tc_line_df = raw_df.groupby(by=['branch', 'weeknum'])['total_changes'].sum().reset_index()
    tc_line_pivot_df = tc_line_df.pivot(index='weeknum', columns='branch', values='total_changes').fillna(0)
    tc_line_pivot_df.to_excel(writer, sheet_name='branch_tc')

    cm_line_cht: workbook.ChartLine = make_line_chart(book, cm_line_pivot_df, 'Commits', 'branch_cm')
    adds_line_cht: workbook.ChartLine = make_line_chart(book, adds_line_pivot_df, 'Additions', 'branch_adds')
    dels_line_cht: workbook.ChartLine = make_line_chart(book, dels_line_pivot_df, 'Deletions', 'branch_dels')
    aoc_line_cht: workbook.ChartLine = make_line_chart(book, cm_line_pivot_df, 'AmountOfChanges', 'branch_aoc')
    tc_line_cht: workbook.ChartLine = make_line_chart(book, tc_line_pivot_df, 'TotalChanges', 'branch_tc')
    
    chartssheet.write('B3', f'{org}/{repo}', title)
    chartssheet.insert_chart('C5', cm_line_cht, {'x_offset': 10, 'y_offset': 10, 'x_scale': 2})
    chartssheet.insert_chart('C20', adds_line_cht, {'x_offset': 10, 'y_offset': 10, 'x_scale': 2})
    chartssheet.insert_chart('C35', dels_line_cht, {'x_offset': 10, 'y_offset': 10, 'x_scale': 2})
    chartssheet.insert_chart('C50', aoc_line_cht, {'x_offset': 10, 'y_offset': 10, 'x_scale': 2})
    chartssheet.insert_chart('C65', tc_line_cht, {'x_offset': 10, 'y_offset': 10, 'x_scale': 2})

    raw_df.to_excel(writer, sheet_name='raw_data')
    writer.close()


#main('facebook', 'react', '2021-06-01', '2022-04-30')
#main('ajou-assignment', 'seat-assignment', '2021-11-01', '2021-12-31')

    
    
if __name__=='__main__':
    args = parser.parse_args()    

    main(args.org, args.repo, args.since, args.until)