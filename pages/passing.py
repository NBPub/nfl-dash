from dash import html, dcc, callback, Output, Input, register_page
import dash_daq as daq
import polars as pl

from load_data import teamcolor_data, passing_data, html_table
from graph_maker import graph


"""Register Passing Page, Load Data"""
register_page(__name__)
passing_data, suggested_cutoff = passing_data()
teamcolors = teamcolor_data()


"""Page Layout"""
layout = html.Div([ 
    # header
    
    # title
    html.H1(children='Passing'),
    
    # Team Color Switch, Min Attempts
    html.Div([       
        html.Div(html.Label('Color by team?', className='header-label'),
                            style={'text-align':'center', 'margin':'3px',
                                   'position':'relative', 'top':'-25px'}),
                 daq.BooleanSwitch(id='passing-colorby_team', on=False, 
                                   color="deeppink",),
                 html.Div([
                     html.B(id='passing-slider-label'),
                     daq.Slider(id='passing-slider',value=suggested_cutoff[0], 
                                max=suggested_cutoff[1], color='lightseagreen'), 
                 ], className='slider-label'),                 
    ], style={'margin-bottom':'20px','display':'flex', 'flex-direction':'row', 
              'margin-left':'25vw'}),        
       
    # Radio Items
    html.Div(children=[
        html.Label('X-Axis\n↔', className='header-label'),
            dcc.RadioItems(options=passing_data.columns[2:],
                       value=passing_data.columns[7], id='passing-x_col'),

        html.Label('Y-Axis\n↕', className='header-label'),
            dcc.RadioItems(options=passing_data.columns[2:],
                       value=passing_data.columns[4], id='passing-y_col'),

        html.Label('marker style\n☸', className='header-label'),
            dcc.RadioItems(options=passing_data.columns[2:],
                       value=passing_data.columns[16], id='passing-sizeby'),
        
    ], style={'display':'flex', 'flex-direction':'row', 
              'margin-bottom':'50px'}),

    
    # Graph
    html.Div(
        dcc.Graph(figure={},id='passing-graph-content',), # style={'min-height':'30vw'}
        className="graph-div"
            ),

    # Table
    html.Div([
        html.H2(id='passing-data-table-label'), 
        html.Div([html.Label('Sort by:', className='header-label'),
                  dcc.RadioItems(id='passing-table-sort', className='flex-rad'),
                  dcc.Clipboard(target_id='passing-data-table', 
                                title='Copy table data',
                                className='copy-button')],
                  style={'display':'flex', 'flex-direction':'row',
                         'margin-bottom': '30px', 'margin-left':'30px'}),
        html.Div(id='passing-data-table'),
], className='table-div'),
    # Footer
    html.Br()
                    ])

              
"""Dynamic Page Updates"""
"""Minimum Attempts Slider - update label value"""
@callback(
    Output('passing-slider-label', 'children'), # slider label
    Input('passing-slider', 'value') # min attempts for graph/table
)
def update_slider(value):
    return f'min attempts: {value}'

"""GRAPH: update graph with axes and styling selections"""
@callback(
    Output('passing-graph-content', 'figure'), # add figure to graph element
    Input('passing-x_col', 'value'), # x-axis
    Input('passing-y_col', 'value'), # y-axis
    Input('passing-sizeby', 'value'), # size markers by
    Input('passing-colorby_team', 'on'), # color by team or sizeby
    Input('passing-slider', 'value') # min attempts for graph
)
def update_figure(x_col, y_col, sizeby, colorby_team, cutoff):
    fig = graph(passing_data.filter(pl.col('attempts') >= cutoff),
                x_col, y_col, sizeby, teamcolors, colorby_team, 'passing') 
    return fig

"""SORT OPTIONS: update available options with graph selections"""
@callback(
    Output('passing-table-sort', 'options'), # sort options
    Output('passing-table-sort', 'value'), # sort selection
    Input('passing-x_col', 'value'), # option A
    Input('passing-y_col', 'value'), # option B
    Input('passing-sizeby', 'value'), # option C
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
    Output('passing-data-table-label', 'children'), # table title
    Output('passing-data-table', 'children'), # add table to div
    Input('passing-table-sort', 'options'), # table columns
    Input('passing-table-sort', 'value'), # sort table by
    Input('passing-slider', 'value') # min attempts for table
)
def update_table(xyz_cols, sort_col, cutoff):
    cols = ['player','team','attempts']
    cols.extend(xyz_cols)
   
    while max([cols.count(val) for val in cols]) > 1:
        cull = set([val for val in cols if cols.count(val) > 1]) 
        for col in cull:
            cols.remove(col)
    
    table = passing_data.filter(pl.col('attempts') >= cutoff)\
                        .select(pl.col(cols)).sort(sort_col, descending=True)
    
    return f'Data Table ({table.shape[0]} QBs)', html_table(table)