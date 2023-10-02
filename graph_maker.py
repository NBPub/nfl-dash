import plotly.express as px
import polars as pl


def graph(data, x_col, y_col, sizeby, teamcolors, colorby_team, description):
    # base figure
    fig = px.scatter()
    
    # color settings
    colorby = 'player' if colorby_team else sizeby
    
    # fix for sizeby with negative values
    if data[sizeby].min() < 0:
        sizeby_abs = data[sizeby] + abs(data[sizeby].min()) + 1
    elif data[sizeby].min() == 0:
        sizeby_abs = data[sizeby] + 1
    else:
        sizeby_abs = data[sizeby]
    
    # hovertemplate settings, if sizeby = x_col or y_col
    ht_ind = {'player': 1, 'team': 2, 
              'sizeby': {'teamcolor': f'<br>{sizeby}: %{{customdata[0]:.3r}}',
                         'statcolor': f'<br>{sizeby}: %{{marker.color:.3r}}'}
             }
    if sizeby == x_col:
        ht_ind = {'player': 0, 'team': 1, 
                  'sizeby': {'teamcolor':'','statcolor':''}}
    elif sizeby == y_col:
        ht_ind = {'player': 0, 'team': 1, 
                  'sizeby': {'teamcolor':'','statcolor':''}}
    
    
    # create scatter points
    figdata = px.scatter(data, x=x_col, y=y_col, size=sizeby_abs,  
                         color=colorby, 
                         hover_data = dict(([
                             (x_col,':.3r'),(y_col,':.3r'),(sizeby,':.3r'),
                             ('player',True),('team',True)
                                         ])),
                         trendline="ols", trendline_scope="overall", 
                         trendline_color_override="burlywood").data
    
    # mean lines
    fig.add_trace(px.line(x=[data[x_col].mean()]*2, 
                          y=[data[y_col].min(), 
                             data[y_col].max()]).data[0]\
                  .update(\
{'line':{'color':'dimgrey','dash':'dash', 'width':2},
 'hovertemplate':f'<b>{round(data[x_col].mean(),2)}</b> {x_col.replace("_"," ")}'}
                          )
                 )
    fig.add_trace(px.line(y=[data[y_col].mean()]*2, 
                          x=[data[x_col].min(), 
                             data[x_col].max()]).data[0]\
                  .update(\
{'line':{'color':'dimgrey','dash':'dash'},
 'hovertemplate':f'<b>{round(data[y_col].mean(),2)}</b> {y_col.replace("_"," ")}'})
                 )
    
    if colorby_team:
        # add each scatter point with team colors and cleaned hover data
        for val in figdata:
            if val.name == 'Overall Trendline':
                fig.add_trace(val)
                continue
            
            # get teamcolors using player's team, adjust hoverdata
            player_team = data.filter(pl.col('player') == val.name)\
                                      .select(pl.col('team')).item()   
    
            color_data = teamcolors.filter(pl.col('team') == player_team)        
            val.marker['color'] = color_data.select(pl.col('color')).item()
            val.marker['line'] = dict(color=color_data.select(
                                      pl.col('color2')).item(),width=5)
            
            val['hovertemplate'] = \
f"""<b>%{{customdata[{ht_ind['player']}]}} (%{{customdata[{ht_ind['team']}]}})</b>
<br>{x_col}: %{{x:.3r}}
<br>{y_col}: %{{y:.3r}}
{ht_ind['sizeby']['teamcolor']}
<extra></extra>"""
    
            fig.add_trace(val)
    else:
        # no need for custom colors, update hovertemplate
        fig.add_trace(figdata[0].update({
            'hovertemplate':
f"""<b>%{{customdata[{ht_ind['player']}]}} (%{{customdata[{ht_ind['team']}]}})</b>
<br>{x_col}: %{{x:.3r}}
<br>{y_col}: %{{y:.3r}}
{ht_ind['sizeby']['statcolor']}
"""
                                         })
                      )
        fig.add_trace(figdata[1])
    
    # figure properties  
    fig.update_layout({
        'title':f'<b style="font-size:20;">\
<a href="https://nextgenstats.nfl.com/stats/{description}">\
  &nbsp; NGS</a>/\
<a href="https://www.pro-football-reference.com/years/2023/{description}_advanced.htm">\
PFR</a> {description.capitalize()} 2023</b><br> \
  &nbsp; &nbsp; markers {"sized" if colorby_team else "styled"} by \
<b>{sizeby.replace("_"," ").title()}</b> | <b>{round(data[sizeby].min(),2)}</b> \
 to <b> {round(data[sizeby].max(),2)}</b> |',
        'title.font.size':14,
        'xaxis.title':x_col.replace('_',' ').title(),
        'xaxis.title.font.size':24,
        'yaxis.title':y_col.replace('_',' ').title(),
        'yaxis.title.font.size':24,
        'plot_bgcolor':'grey',
        'paper_bgcolor':'honeydew',
    }) 
    if not colorby_team:
        fig.update_layout({
    'coloraxis_colorbar':{'title':sizeby.replace('_','<br>').title(), 'ypad':30},
    'coloraxis_colorscale':'Jet_r'
            })
        
    return fig