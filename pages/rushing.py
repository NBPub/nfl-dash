from dash import html, dcc, callback, Output, Input, register_page
import dash_daq as daq
import polars as pl

from load_data import teamcolor_data, rushing_data, html_table
from graph_maker import graph


"""Register Rushing Page, Load Data"""
register_page(__name__)
rushing_data, suggested_cutoff = rushing_data()
teamcolors = teamcolor_data()


"""Page Layout"""
layout = html.Div([ 
    
    # title
    html.H2('Rushing'),
    
    # Team Color Switch, Min Attempts Slider
    html.Div([       
        html.Div(html.Label('Color by team?', className='header-label'),
                            style={'text-align':'center', 'margin':'3px',
                                   'position':'relative', 'top':'-25px'}),
                 daq.BooleanSwitch(id='rushing-colorby_team', on=False, 
                                   color="deeppink",),
                 html.Div([
                     html.B(id='rushing-slider-label'),
                     daq.Slider(id='rushing-slider',value=suggested_cutoff[0], 
                                max=suggested_cutoff[1], color='lightseagreen'), 
                 ], className='slider-label'),                 
    ], style={'margin-bottom':'20px','display':'flex', 'flex-direction':'row', 
              'margin-left':'25vw'}),        
       
    # Graph Selection Radio Items
    html.Div(children=[
        html.Label('X-Axis\n↔', className='header-label'),
            dcc.RadioItems(options=rushing_data.columns[2:],
                       value=rushing_data.columns[10], id='rushing-x_col'),

        html.Label('Y-Axis\n↕', className='header-label'),
            dcc.RadioItems(options=rushing_data.columns[2:],
                       value=rushing_data.columns[13], id='rushing-y_col'),

        html.Label('marker style\n☸', className='header-label'),
            dcc.RadioItems(options=rushing_data.columns[2:],
                       value=rushing_data.columns[14], id='rushing-sizeby'),
        
    ], style={'display':'flex', 'flex-direction':'row', 
              'margin-bottom':'50px'}),

    
    # Graph
    html.Div(
        dcc.Graph(figure={},id='rushing-graph-content'),
        className="graph-div"
            ),

    # Table
    html.Div([
        html.H2(id='rushing-data-table-label'),                       
        html.Div([html.Label('Sort by:', className='header-label'),
                  dcc.RadioItems(id='rushing-table-sort', className='flex-rad'),
                  dcc.Clipboard(target_id='rushing-data-table', 
                                title='Copy table data',
                                className='copy-button')],
                  style={'display':'flex', 'flex-direction':'row',
                         'margin-bottom': '30px', 'margin-left':'30px'}),
        html.Div(id='rushing-data-table'),
], className='table-div'),
    # Footer
    html.Br()
                    ])

              
"""Dynamic Page Updates"""
"""Minimum Attempts Slider - update label value"""
@callback(
    Output('rushing-slider-label', 'children'), # slider label
    Input('rushing-slider', 'value') # min attempts for graph/table
)
def update_slider(value):
    return f'min attempts: {value}'

"""GRAPH: update graph with axes and styling selections"""
@callback(
    Output('rushing-graph-content', 'figure'), # add figure to graph element
    Input('rushing-x_col', 'value'), # x-axis
    Input('rushing-y_col', 'value'), # y-axis
    Input('rushing-sizeby', 'value'), # size markers by
    Input('rushing-colorby_team', 'on'), # color by team or sizeby
    Input('rushing-slider', 'value') # min attempts for graph
)
def update_figure(x_col, y_col, sizeby, colorby_team, cutoff):
    fig = graph(rushing_data.filter(pl.col('attempts') >= cutoff),
                x_col, y_col, sizeby, teamcolors, colorby_team, 'rushing') 
    return fig

"""SORT OPTIONS: update available options with graph selections"""
@callback(
    Output('rushing-table-sort', 'options'), # sort options
    Output('rushing-table-sort', 'value'), # sort selection
    Input('rushing-x_col', 'value'), # option A
    Input('rushing-y_col', 'value'), # option B
    Input('rushing-sizeby', 'value'), # option C
)
def table_sort_options(x_col,y_col,sizeby):
    sort_options = ['attempts',x_col,y_col,sizeby]

    while max([sort_options.count(val) for val in sort_options]) > 1:
        cull = set([val for val in sort_options if sort_options.count(val) > 1]) 
        for col in cull:
            sort_options.remove(col)
    
    return sort_options, sizeby

"""TABLE: update displayed columns and sort based on graph/sort selections"""
@callback(
    Output('rushing-data-table-label', 'children'), # table title
    Output('rushing-data-table', 'children'), # add table to div
    Input('rushing-table-sort', 'options'), # table columns
    Input('rushing-table-sort', 'value'), # sort table by
    Input('rushing-slider', 'value') # min targets
)
def update_table(xyz_cols, sort_col, cutoff):
    cols = ['player','team','attempts']
    cols.extend(xyz_cols)
   
    while max([cols.count(val) for val in cols]) > 1:
        cull = set([val for val in cols if cols.count(val) > 1]) 
        for col in cull:
            cols.remove(col)
            
    table = rushing_data.filter(pl.col('attempts') >= cutoff)\
                        .select(pl.col(cols)).sort(sort_col, descending=True)
            
    return f'Data Table ({table.shape[0]} RBs)', html_table(table)