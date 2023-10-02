from dash import html, dcc, callback, Output, Input, register_page
import dash_daq as daq
import polars as pl

from load_data import teamcolor_data, receiving_data, html_table
from graph_maker import graph


"""Register Receiving Page, Load Data. dcc.Store ??? """
register_page(__name__)
receiving_data, suggested_cutoff = receiving_data()
teamcolors = teamcolor_data()


"""Page Layout"""
layout = html.Div([ 
    
    # dcc.Store(id='memory-df'), dcc.Store(id='teamcolors-df'),
    
    # title
    html.H2('Receiving'),
    
    # Team Color Switch, Min Targets Slider
    html.Div([            
        html.Div(html.Label('Color by team?', className='header-label'),
                            style={'text-align':'center', 'margin':'3px',
                                   'position':'relative', 'top':'-25px'}),
                 daq.BooleanSwitch(id='receiving-colorby_team', on=False, 
                                   color="deeppink",),
                 html.Div([
                     html.B(id='receiving-slider-label'),
                     daq.Slider(id='receiving-slider',value=suggested_cutoff[0], 
                                max=suggested_cutoff[1], color='lightseagreen'), 
                 ], className='slider-label'),
    ], style={'margin-bottom':'20px','display':'flex', 'flex-direction':'row', 
              'margin-left':'25vw', }),        
       
    # Graph Selection Radio Items
    html.Div(children=[
        html.Label('X-Axis\n↔', className='header-label'),
            dcc.RadioItems(options=receiving_data.columns[2:],
                       value=receiving_data.columns[4], id='receiving-x_col'),

        html.Label('Y-Axis\n↕', className='header-label'),
            dcc.RadioItems(options=receiving_data.columns[2:],
                       value=receiving_data.columns[5], id='receiving-y_col'),

        html.Label('marker style\n☸', className='header-label'),
            dcc.RadioItems(options=receiving_data.columns[2:],
                       value=receiving_data.columns[8], id='receiving-sizeby'),
        
    ], style={'display':'flex', 'flex-direction':'row', 
              'margin-bottom':'50px'}),

    
    # Graph
    html.Div(
        dcc.Graph(figure={},id='receiving-graph-content'),
        className="graph-div"
            ),

    # Table
    html.Div([
        html.H2(id='receiving-data-table-label'),                        
        html.Div([html.Label('Sort by:', className='header-label'),
                  dcc.RadioItems(id='receiving-table-sort', className='flex-rad'),
                  dcc.Clipboard(target_id='receiving-data-table', 
                                title='Copy table data',
                                className='copy-button')],
                  style={'display':'flex', 'flex-direction':'row',
                         'margin-bottom': '30px', 'margin-left':'30px'}),
        html.Div(id='receiving-data-table'),
], className='table-div'),
    # Footer
    html.Br()
                    ])

              
"""Dynamic Page Updates"""
# """Store DataFrame after initial load?"""
# @callback(
#     Output('teamcolors-df','data'), # teamcolor df
#     Output('memory-df', 'data'), # data df
#     Input('receiving-slider', 'value'), # min targets
# )
# def select_data(cutoff):
#     return teamcolors.write_json(row_oriented=True),
#     receiving_data.filter(pl.col('targets') >= cutoff).write_json(row_oriented=True)
        

"""Minimum Targets Slider - update label value"""
@callback(
    Output('receiving-slider-label', 'children'), # slider label
    Input('receiving-slider', 'value') # min targets for graph/table
)
def update_slider(value):
    return f'min targets: {value}'

"""GRAPH: update graph with axes and styling selections"""
@callback(
    Output('receiving-graph-content', 'figure'), # add figure to graph element
    Input('receiving-x_col', 'value'), # x-axis
    Input('receiving-y_col', 'value'), # y-axis
    Input('receiving-sizeby', 'value'), # size markers by
    Input('receiving-colorby_team', 'on'), # color by team or sizeby
    Input('receiving-slider', 'value') # min targets for graph
)
def update_figure(x_col, y_col, sizeby, colorby_team, cutoff):
    fig = graph(receiving_data.filter(pl.col('targets') >= cutoff), 
                x_col, y_col, sizeby, teamcolors, colorby_team, 'receiving') 
    return fig

"""SORT OPTIONS: update available options with graph selections"""
@callback(
    Output('receiving-table-sort', 'options'), # sort options
    Output('receiving-table-sort', 'value'), # sort selection
    Input('receiving-x_col', 'value'), # option A
    Input('receiving-y_col', 'value'), # option B
    Input('receiving-sizeby', 'value'), # option C
)
def table_sort_options(x_col,y_col,sizeby):
    sort_options = ['targets',x_col,y_col,sizeby]

    while max([sort_options.count(val) for val in sort_options]) > 1:
        cull = set([val for val in sort_options if sort_options.count(val) > 1]) 
        for col in cull:
            sort_options.remove(col)
    
    return sort_options, sizeby

"""TABLE: update displayed columns and sort based on graph/sort selections"""
@callback(
    Output('receiving-data-table-label', 'children'), # table title
    Output('receiving-data-table', 'children'), # add table to div
    Input('receiving-table-sort', 'options'), # table columns
    Input('receiving-table-sort', 'value'), # sort table by
    Input('receiving-slider', 'value') # min targets for table
)
def update_table(xyz_cols, sort_col, cutoff):
    cols = ['player','team','targets']
    cols.extend(xyz_cols)
   
    while max([cols.count(val) for val in cols]) > 1:
        cull = set([val for val in cols if cols.count(val) > 1]) 
        for col in cull:
            cols.remove(col)
            
    table = receiving_data.filter(pl.col('targets') >= cutoff)\
                          .select(pl.col(cols))\
                          .sort(sort_col, descending=True)
            
    return f'Data Table ({table.shape[0]} WRs)', html_table(table)